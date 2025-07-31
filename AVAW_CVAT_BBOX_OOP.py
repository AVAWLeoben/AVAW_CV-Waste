# Updates:
    # check if new bounding box is inside image size
    # 0.71 Added Zoom Window, open with "z"


import tkinter as tk
from tkinter import Canvas, ttk
#from tkinter import ALL, EventType
from PIL import Image, ImageTk
import cv2
import os
from pathlib import Path
from ultralytics import YOLO  # Using the Ultralytics YOLO model
import copy
from tkinter import messagebox, Message, filedialog, Scale
from tkinter import colorchooser
import colorsys
import webbrowser
import numpy as np
import natsort


class Archive:
    def __init__(self,owner):
        self.archive = []
        self.nUndoes = 10
        self.owner = owner
    
    def clear_archive(self):
        self.archive = []
        
    def fill_archive(self):
        # Avoid archiving if dragging
        if not self.owner.dragging:
            # Only add to archive if the new state is different
            if not self.archive or self.owner.ANNOTATION_HANDLER.annotations != self.archive[-1]:
                if len(self.archive) >= self.nUndoes:
                    self.archive.pop(0)  # Maintain a fixed number of undos by removing the oldest
                self.archive.append(copy.deepcopy(self.owner.ANNOTATION_HANDLER.annotations))  # Archive a deep copy of masks
        if len(self.archive) == 0:
            self.archive.append(copy.deepcopy(self.owner.ANNOTATION_HANDLER.annotations))
            
    def undo(self, event=None):
        if len(self.archive) > 1:
            # Remove the current state and revert to the previous one
            self.archive.pop()
            self.owner.ANNOTATION_HANDLER.annotations = copy.deepcopy(self.archive[-1])  # Revert to the previous state
            self.owner.update_display()
        else:
            print("Nothing to undo")  

class DataAugmentor:
    def __init__(self,owner):
        self.owner = owner
    def flip_lr(self):
        self.owner.image = cv2.flip(self.owner.image,0)
        self.flip_annotations_lr()
        #delete_all_annotations()
        self.owner.update_display()

    def flip_annotations_lr(self):
        flipped_annotations = []
        for annotation in self.owner.ANNOTATION_HANDLER.annotations:
            class_id, x1, y1, x2, y2 = annotation
            y1 = self.owner.image.shape[0] - y1  # Mirror the x-coordinate
            y2 = self.owner.image.shape[0] - y2  # Mirror the x-coordinate
            y1,y2 = min(y1,y2),max(y1,y2)
            flipped_annotations.append([class_id, x1, y1, x2, y2])
        self.owner.ANNOTATION_HANDLER.annotations = flipped_annotations
        self.owner.update_display()
        
    def flip_ud(self):
        self.owner.image = cv2.flip(self.owner.image,1)
        self.flip_annotations_ud()
        #delete_all_annotations()
        self.owner.update_display()

    def flip_annotations_ud(self):
        flipped_annotations = []
        for annotation in self.owner.ANNOTATION_HANDLER.annotations:
            class_id, x1, y1, x2, y2 = annotation
            x1 = 640 - x1  # Mirror the x-coordinate
            x2 = 640 - x2  # Mirror the x-coordinate
            x1,x2 = min(x1,x2),max(x1,x2)
            flipped_annotations.append([class_id, x1, y1, x2, y2])
        self.owner.ANNOTATION_HANDLER.annotations = flipped_annotations
        self.owner.update_display()

class ImageHandler:
    def __init__(self, owner):
        self.owner = owner

    def load_image(self, index):
        """Load image by index and update the canvas + annotations."""
        if 0 <= index < len(self.owner.image_paths):
            # Update current image index and paths
            self.owner.ZOOMER.reset_zoom()
            self.owner.current_image_index = index
            self.owner.image_path = self.owner.image_paths[index]
            self.owner.annotations_path = os.path.splitext(self.owner.image_path)[0] + ".txt"

            # Reset selection and dragging
            self.owner.selected_box = None
            self.owner.dragging = False

            # Load image using OpenCV
            self.owner.image = cv2.imread(self.owner.image_path)
            self.owner.image = cv2.resize(self.owner.image, (640, 640))
            self.owner.image_rgb = cv2.cvtColor(self.owner.image, cv2.COLOR_BGR2RGB)
            self.owner.image_pil = Image.fromarray(self.owner.image_rgb)
            self.owner.image_tk = ImageTk.PhotoImage(self.owner.image_pil)

            # Store image dimensions
            img_width, img_height = self.owner.image_pil.size

            # Load YOLO annotations
            annotations = self.owner.ANNOTATION_HANDLER.load_yolo_annotations(
                self.owner.annotations_path, img_width, img_height
            )

            # Keep a backup of last saved annotations
            self.owner.last_save = copy.deepcopy(annotations)

            # Update title label (assuming title_label is owned by BBOX_App)
            image_name = Path(self.owner.image_paths[self.owner.current_image_index]).stem
            self.owner.title_label.config(text=image_name)

            # Draw image on canvas
            self.owner.update_display()

    def next_image(self, event=None):
        """Go to the next image."""
        if self.owner.current_image_index + 1 < len(self.owner.image_paths):
            self.owner.USER_INPUT_HANDLER.prompt_saving()

            self.owner.ARCHIVE.clear_archive()
            self.owner.USER_INPUT_HANDLER.stop_multiselect()
            self.owner.number.set(self.owner.current_image_index + 1)

            self.owner.last_annotations = copy.deepcopy(self.owner.ANNOTATION_HANDLER.annotations)
            self.load_image(self.owner.current_image_index + 1)
            self.owner.selected_box = None

            # Refresh BoxList if available
            try:
                self.owner.BOX_LIST.refresh_boxlist()
            except Exception:
                pass

    def previous_image(self, event=None):
        """Go to the previous image."""
        if self.owner.current_image_index - 1 >= 0:
            if len(self.owner.archive) > 1:
                self.owner.USER_INPUT_HANDLER.prompt_saving()

            self.owner.ARCHIVE.clear_archive()
            self.owner.USER_INPUT_HANDLER.stop_multiselect()
            self.owner.number.set(self.owner.current_image_index - 1)

            self.load_image(self.owner.current_image_index - 1)
            self.owner.selected_box = None

            try:
                self.owner.BOX_LIST.refresh_boxlist()
            except Exception:
                pass

    def load_new_image(self, image_listbox):
        """Load an image from a listbox selection."""
        selected_idx = image_listbox.curselection()[0]
        self.load_image(selected_idx)
        self.owner.number.set(selected_idx)
        self.owner.USER_INPUT_HANDLER.jump_to_image()

    def save_image(self):
        """Save the current image to disk."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            title="Save Image as PNG",
            initialfile=Path(self.owner.image_paths[self.owner.current_image_index]).stem + "_.png",
        )

        if file_path:
            cv2.imwrite(file_path, cv2.cvtColor(np.array(self.owner.image_pil), cv2.COLOR_RGB2BGR))
            print(f"Image saved at {file_path}")

            self.owner.image_paths.append(file_path)
            self.load_image(len(self.owner.image_paths) - 1)
            self.owner.number.set(len(self.owner.image_paths) - 1)
            self.owner.USER_INPUT_HANDLER.jump_to_image()
            self.owner.update_display()
        else:
            print("Save operation canceled.")

    def select_image_dir(self):
        """Allow user to select a directory and load images."""
        directory = filedialog.askdirectory(title="Select Directory")
        if not directory:
            print("No Directory Selected!")
            messagebox.showinfo("showinfo", "No Directory Selected \nStaying in previous directory")
            return

        image_extensions = ['.png', '.jpg', '.jpeg']
        self.owner.image_paths = [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if os.path.splitext(f)[1].lower() in image_extensions
        ]

        self.owner.image_paths = natsort.natsorted(self.owner.image_paths)

        if not self.owner.image_paths:
            print("No images found in the folder! Valid Formats: png, jpg, jpeg")
            messagebox.showinfo("showinfo", "No Images Found in Folder. \nValid Formats: png, jpg, jpeg")
            return

        self.owner.current_image_index = 0
        self.load_image(0)
        self.owner.update_display()
 

class AnnotationHandler:
    def __init__(self, owner):
        self.annotations = []
        self.owner = owner
    # Function to load YOLO annotations from .txt file
    def load_yolo_annotations(self,annotations_path, image_width, image_height):
        self.annotations = []
        if os.path.exists(annotations_path):
            with open(annotations_path, 'r') as file:
                for line in file:
                    label, x_center, y_center, box_width, box_height = map(float, line.strip().split())
                    
                    # Convert YOLO format (relative) to absolute pixel values
                    x_center *= image_width
                    y_center *= image_height
                    box_width *= image_width
                    box_height *= image_height
                    
                    # Calculate top-left and bottom-right coordinates
                    x1 = int(x_center - (box_width / 2))
                    y1 = int(y_center - (box_height / 2))
                    x2 = int(x_center + (box_width / 2))
                    y2 = int(y_center + (box_height / 2))
                    
                    self.annotations.append([int(label), x1, y1, x2, y2])  # Save the box with the label

    # Function to save YOLO annotations to .txt file
    def save_yolo_annotations(self,annotations_path, annotations, image_width, image_height):
        self.owner.ZOOMER.reset_zoom()
        with open(annotations_path, 'w') as file:
            for box in self.annotations:
                label, x1, y1, x2, y2 = box
                # Convert back to YOLO relative format
                box_width = abs(x2 - x1) / image_width
                box_height = abs(y2 - y1) / image_height
                x_center = (x1 + x2) / 2 / image_width
                y_center = (y1 + y2) / 2 / image_height
                file.write(f"{label} {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}\n")

    def are_coordinates_valid(self,x1,y1,x2,y2):
        # Store image dimensions
        img_width, img_height = self.owner.image_pil.size
        return 0 <= x1 and 0 <= y1 and 0 <= x2 <= img_width and 0 <= y2 <= img_height

    def clamp_all_coordinates(self):
        for annotation in self.annotations:
            if not self.are_coordinates_valid(annotation[1],annotation[2],annotation[3],annotation[4]):
                annotation[1],annotation[2] = self.clamp_coordinates(annotation[1],annotation[2])
                annotation[3],annotation[4] = self.clamp_coordinates(annotation[3],annotation[4])
        return self.annotations

    def remove_dim1_annotations(self):
        removable_idx = []
        for idx, annotation in enumerate(self.annotations):
            if abs(annotation[1]-annotation[3]) <= 1 or abs(annotation[2] - annotation[4])  <= 1:
                removable_idx.append(idx)

        removable_idx.sort(reverse=True)
        for idx in removable_idx:
            del self.annotations[idx]

    def clamp_coordinates(self, x, y):
        img_width, img_height = self.owner.image_pil.size
        # Clamp x within [0, image_width]
        x = max(0, min(x, img_width))
        # Clamp y within [0, image_height]
        y = max(0, min(y, img_height))
        return x, y
    
    def translate_down(self,event=None):
        for annotation in self.annotations:
            for i in range(2, len(annotation), 2):
                annotation[i] += 1
        self.clamp_all_coordinates()
        self.remove_dim1_annotations()
        self.owner.update_display()

    def translate_up(self, event=None):
        for annotation in self.annotations:
            for i in range(2, len(self.annotation), 2):
                annotation[i] -= 1
        self.clamp_all_coordinates()
        self.remove_dim1_annotations()
        self.owner.update_display()

    def translate_right(self, event=None):
        for annotation in self.annotations:
            for i in range(1, len(annotation), 2):
                annotation[i] += 1
        self.clamp_all_coordinates()
        self.remove_dim1_annotations()
        self.owner.update_display()
        
    def translate_left(self, event=None):
        for annotation in self.annotations:
            for i in range(1, len(annotation), 2):
                annotation[i] -= 1
        self.clamp_all_coordinates()
        self.remove_dim1_annotations()
        self.owner.update_display()
    
    def reset_translation(self, event=None):             
        self.w1.set(0)
        self.w2.set(0)   
        self.owner.root.update_idletasks()
        
        self.annotations = copy.deepcopy(self.owner.annotation_backup_before_translation)  
        self.owner.update_display()        
       
    def translate_vertical(self, event=None):
        new_value = self.owner.TRANSLATE_ANNOTATIONS_WINDOW.w1.get()
        difference = self.owner.TRANSLATE_ANNOTATIONS_WINDOW.last_translate_value_y.get() - int(new_value)
        self.add_vertical_translation_to_annotations(difference)
        self.clamp_all_coordinates()
        self.remove_dim1_annotations()
        self.owner.update_display()
        self.owner.last_translate_value_y.set(new_value)

    def add_vertical_translation_to_annotations(self, difference):
        for annotation in self.annotations:
            annotation[2]=annotation[2]+difference
            annotation[4]=annotation[4]+difference

    def translate_horizontal(self, event=None):
        new_value = self.owner.TRANSLATE_ANNOTATIONS_WINDOW.w2.get()
        difference = self.owner.TRANSLATE_ANNOTATIONS_WINDOW.last_translate_value_x.get() - int(new_value)
        self.add_horizontal_translation_to_annotations(difference)
        self.clamp_all_coordinates()
        self.remove_dim1_annotations()
        self.owner.update_display()
        self.owner.last_translate_value_x.set(new_value)

    def add_horizontal_translation_to_annotations(self,difference):
        for annotation in self.annotations:
            annotation[1]=annotation[1]+difference
            annotation[3]=annotation[3]+difference


    def get_last_annotations(self):
        self.annotations = copy.deepcopy(self.owner.last_annotations)
        self.owner.update_display()
        
    def delete_duplicates(self, event=None):
        len_old = len(self.annotations)
        self.annotations = list(map(list, set(map(tuple, self.annotations))))
        len_new = len(self.annotations)
        diff = len_old - len_new
        messagebox.showinfo("Information", "Found and Deleted "+str(diff)+" duplicates")
        
    def delete_all_annotations(self, event=None):
        self.annotations = []
        self.owner.update_display()

class PredictionModelHandler:
    def __init__(self, owner):
        self.owner = owner

    def load_model(self, model_path):
        """Load a YOLO model and return it."""
        try:
            model = YOLO(model_path)
            return model
        except Exception:
            print("Only Ultralytics YOLO Models are loadable")

    def load_new_model(self):
        """Prompt user to select a new YOLO model and load it."""
        model_path = filedialog.askopenfilename(title="Select Model")
        if not model_path:
            print("No model selected!")
            messagebox.showinfo("showinfo", "No model selected!")
            return

        try:
            # Load and validate model
            new_yolo_model = self.load_model(model_path)
            # Test prediction on logo to ensure model works
            new_yolo_model("files_bbox/logo.png")
            messagebox.showinfo("showinfo", "New YOLO Model loaded")

            # Store in owner
            self.owner.yolo_model = new_yolo_model
        except Exception as e:
            print(f"Model loading failed: {e}")
            messagebox.showinfo(
                "showinfo",
                "New YOLO Model loading failed - reverting to last model\n"
            )

    
    def run_yolo_inference(self, event=None):
        """Run YOLO inference on the current image and update annotations."""
        if not hasattr(self.owner, "yolo_model") or self.owner.yolo_model is None:
            print("No YOLO model loaded.")
            messagebox.showinfo("showinfo", "No YOLO model loaded!")
            return

        # Prepare current image for inference
        image = self.owner.image

        # Perform inference
        results = self.owner.yolo_model(
            image,
            agnostic_nms=True,
            conf=self.owner.set_conf,
            iou=self.owner.set_iou,
            augment=True
        )

        # Clear previous annotations and confidences
        self.owner.ANNOTATION_HANDLER.delete_all_annotations()
        self.owner.confidences.clear()

        # Add detected boxes to annotations
        for result in results[0].boxes:
            x1, y1, x2, y2 = result.xyxy[0].tolist()
            cls = int(result.cls)
            conf = float(np.round(float(result.conf), 2))

            # Ensure class index is valid
            if cls >= len(self.owner.class_names):
                cls = 0

            self.owner.confidences.append(conf)
            self.owner.ANNOTATION_HANDLER.annotations.append([cls, int(x1), int(y1), int(x2), int(y2)])

        # Redraw updated image
        self.owner.update_display()


        
class ZoomWindow:
    def __init__(self, owner, event=None):
        self.owner = owner
        self.shown = False
        self.zoom_factor = 1
        # Create the top-level window and hide it initially
        self.zoom_window = tk.Toplevel(self.owner.root)
        self.zoom_window.withdraw()
        self.zoom_window.title("Zoom Window")
        self.zoom_window.geometry("400x450")
        self.zoom_window.protocol("WM_DELETE_WINDOW", self.on_close_zoom_window)

        # Prepare initial zoomed image
        zoomed_image_rgb = self.owner.image_rgb.copy()
        cv2.drawMarker(
            zoomed_image_rgb, (self.owner.start_x, self.owner.start_y),
            color=(0, 0, 0), thickness=2,
            markerType=cv2.MARKER_TILTED_CROSS,
            line_type=cv2.LINE_AA, markerSize=10
        )

        image_pil = Image.fromarray(zoomed_image_rgb)
        image_pil_zoomed = image_pil.resize((400, 400))  # Resize to fit window
        image_pil_cropped = image_pil_zoomed.crop(
            (self.owner.start_x-200, self.owner.start_y-200, self.owner.start_x+200, self.owner.start_y+200)
        )
        image_tk = ImageTk.PhotoImage(image_pil_cropped)

        # Attach widgets to the Toplevel (not root)
        self.zoom_label = tk.Label(self.zoom_window, image=image_tk)
        self.zoom_label.image = image_tk  # Keep reference
        self.zoom_label.pack()

        self.reset_button = tk.Button(self.zoom_window, text="Reset Zoom", command=self.reset_zoom)
        self.reset_button.pack(pady=10)
    
    def on_mousewheel(self,event):
        scale_factor = 1.1 if event.delta > 0 else 0.9
        self.zoom_factor *= scale_factor
        self.owner.ZOOM_WINDOW.update_zoom_window()
    
    def toggle(self, event=None):
        """Show/hide the zoom window."""
        if not self.shown:
            self.zoom_window.deiconify()
            self.shown = True
        else:
            self.zoom_window.withdraw()
            self.shown = False

    def update_zoom_window(self, event=None):
        """Update the zoomed image display."""
        # Determine position
        zoom_window_x, zoom_window_y = self.owner.start_x, self.owner.start_y
        if event is not None:
            x, y = self.owner.canvas.canvasx(event.x), self.owner.canvas.canvasy(event.y)
            # You can update zoom_window_x, zoom_window_y here if needed

        # Create new zoomed image
        zoomed_image_rgb = self.owner.image_rgb.copy()
        cv2.drawMarker(
            zoomed_image_rgb, (zoom_window_x, zoom_window_y),
            color=(0, 0, 0), thickness=2,
            markerType=cv2.MARKER_TILTED_CROSS,
            line_type=cv2.LINE_AA,
            markerSize=int(10 / self.zoom_factor)
        )
        image_pil = Image.fromarray(zoomed_image_rgb)

        # Scale up
        new_x = int(np.round(image_pil.size[0] * self.zoom_factor))
        new_y = int(np.round(image_pil.size[1] * self.zoom_factor))
        image_pil_zoomed = image_pil.resize((new_x, new_y), Image.NEAREST)

        # Crop centered
        image_pil_cropped = image_pil_zoomed.crop((
            zoom_window_x * self.zoom_factor - 200,
            zoom_window_y * self.zoom_factor - 200,
            zoom_window_x * self.zoom_factor + 200,
            zoom_window_y * self.zoom_factor + 200
        ))

        image_tk = ImageTk.PhotoImage(image_pil_cropped)

        # Update label
        self.zoom_label.config(image=image_tk)
        self.zoom_label.image = image_tk  # Prevent garbage collection

    def on_close_zoom_window(self):
        """Close the zoom window properly."""
        self.zoom_window_open = False
        self.zoom_window.destroy()
        print("Zoom window closed")

    def reset_zoom(self, event=None):
        """Reset zoom factor to default and update."""
        self.zoom_factor = 1
        self.update_zoom_window()
        
    def on_close_zoom_window(self):
        """Hide instead of destroy when X is clicked."""
        self.zoom_window.withdraw()
        self.shown = False

class BoxList:
    def __init__(self, owner, event=None):
        self.owner = owner
        self.buttons = []
        self.shown = False

        # Create a new Toplevel window for the box list
        self.boxlist = tk.Toplevel(self.owner.root)
        self.boxlist.title("Boxlist")
        self.boxlist.geometry("200x600")
        self.boxlist.withdraw()  # Hide initially
        self.boxlist.protocol("WM_DELETE_WINDOW", self.on_close)

        # Set custom icon
        p1 = tk.PhotoImage(file='files_bbox/logo.png')
        self.boxlist.iconphoto(False, p1)
        self.icon_image = p1  # prevent garbage collection

        # Key bindings
        self.boxlist.bind("<Delete>", self.owner.USER_INPUT_HANDLER.delete_selected_box)
        self.boxlist.bind("<Enter>", lambda event: self.boxlist.focus_set())

        # Canvas + scrollbar
        self.canvas = tk.Canvas(self.boxlist, width=180, height=600)
        scrollbar = tk.Scrollbar(self.boxlist, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        # Scroll region config
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add initial content
        self.refresh_boxlist()

    def toggle(self, event=None):
        """Show/hide the boxlist window."""
        if not self.shown:
            self.boxlist.deiconify()
            self.shown = True
        else:
            self.boxlist.withdraw()
            self.shown = False

    def close_boxlist(self):
        """Destroy the boxlist window."""
        self.boxlist.destroy()

    def set_selectedBox(self, index):
        """Set which box is selected and refresh display."""
        self.owner.selected_box = index
        self.refresh_boxlist()
        self.owner.update_display()  # external function to redraw main image

    def refresh_boxlist(self):
        """Rebuild the buttons list when annotations change."""
        # Clear existing buttons
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.buttons = []

        # Add entry counter
        entry_counter = tk.Message(self.scrollable_frame, text=f"Objects in Image: {len(self.owner.ANNOTATION_HANDLER.annotations)}", width=600)
        entry_counter.pack()

        # Create buttons for each annotation
        for i, ann in enumerate(self.owner.ANNOTATION_HANDLER.annotations):
            color_hex = self.rgb2hex(self.owner.class_colors[ann[0]])
            try:
                box_class_name = self.owner.class_names[ann[0]]
            except:
                box_class_name = "N.A."

            btn = tk.Button(
                self.scrollable_frame,
                text=f"Box {i} {box_class_name}",
                bg="yellow" if i == self.owner.selected_box else color_hex,
                command=lambda i=i: self.set_selectedBox(i)
            )
            btn.pack(pady=2, padx=10, fill="x")
            self.buttons.append(btn)

    def rgb2hex(self, rgb):
        """Convert RGB tuple to hex color."""
        return "#%02x%02x%02x" % (rgb[0], rgb[1], rgb[2])

    def on_close(self):
        """Hide instead of destroy when X is clicked."""
        self.boxlist.withdraw()
        self.shown = False



class ImageListWindow:
    def __init__(self, owner, event=None):
        self.owner = owner
        self.shown = False

        # Create the new Toplevel window
        self.image_window = tk.Toplevel(self.owner.root)
        self.image_window.title("Select an Image")
        self.image_window.geometry("600x400")
        self.image_window.withdraw()  # Hide initially
        self.image_window.protocol("WM_DELETE_WINDOW", self.on_close)

        # Create a frame to hold the listbox and scrollbar
        frame = tk.Frame(self.image_window)
        frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # Add a vertical scrollbar
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add a listbox to display the image paths
        self.image_listbox = tk.Listbox(frame, height=15, width=50, yscrollcommand=scrollbar.set)
        self.image_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Link the scrollbar to the listbox
        scrollbar.config(command=self.image_listbox.yview)

        # Populate the listbox with image names (Path.stem removes folder + extension)
        for path in self.owner.image_paths:
            self.image_listbox.insert(tk.END, Path(path).stem)

        # Add a "Load Image" button
        load_button = tk.Button(
            self.image_window,
            text="Load Image",
            command=lambda: self.owner.IMAGE_HANDLER.load_new_image(self.image_listbox)
        )
        load_button.pack(pady=10)

        # Add a label to display the loaded image (if needed later)
        self.img_label = tk.Label(self.image_window)
        self.img_label.pack(pady=10)

    def toggle(self, event=None):
        """Show/hide the image list window."""
        if self.shown:
            self.image_window.withdraw()
            self.shown = False
        else:
            self.image_window.deiconify()
            self.shown = True
            
    def on_close(self):
        """Hide instead of destroy when X is clicked."""
        self.image_window.withdraw()
        self.shown = False

class ModelSettingsWindow:
    def __init__(self, owner):
        self.owner = owner
        self.shown = False

        # Create the window
        self.model_window = tk.Toplevel(self.owner.root)
        self.model_window.title("Model Setting")
        self.model_window.geometry("400x400")
        self.model_window.withdraw()  # Hide initially
        self.model_window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.model_window.bind("<Enter>", lambda event: self.model_window.focus_set())

        # Set icon
        p1 = tk.PhotoImage(file='files_bbox/logo.png')
        self.model_window.iconphoto(False, p1)

        # Confidence scale
        self.w3 = tk.Scale(
            self.model_window, from_=0, to=1,
            tickinterval=0.1, resolution=0.1,
            orient=tk.HORIZONTAL, command=self.change_conf,
            length=300, label="Set Min Confidence", font=("TkDefaultFont", 10)
        )
        self.w3.set(self.owner.set_conf)
        self.w3.pack()

        # IoU scale
        self.w4 = tk.Scale(
            self.model_window, from_=0, to=1,
            tickinterval=0.1, resolution=0.1,
            orient=tk.HORIZONTAL, command=self.change_IoU,
            length=300, label="Set IoU", font=("TkDefaultFont", 10)
        )
        self.w4.set(self.owner.set_iou)
        self.w4.pack()

    def toggle(self, event=None):
        """Show/hide the window."""
        if self.shown:
            self.model_window.withdraw()
            self.shown = False
        else:
            self.model_window.deiconify()
            self.shown = True

    def change_conf(self, event=None):
        """Update global confidence value."""
        self.owner.set_conf = self.w3.get()

    def change_IoU(self, event=None):
        """Update global IoU value."""
        self.owner.set_iou = self.w4.get()
        
    def on_close(self):
        """Hide instead of destroy when X is clicked."""
        self.model_window.withdraw()
        self.shown = False

class TranslateAnnotationsWindow:
    def __init__(self, owner, event=None):        
        self.owner = owner
        # Backup annotations before translation
        self.owner.annotation_backup_before_translation = copy.deepcopy(self.owner.ANNOTATION_HANDLER.annotations)

        self.shown = False

        # Create window
        self.translate_window = tk.Toplevel(self.owner.root)
        self.translate_window.title("Boxlist")
        self.translate_window.geometry("400x400")
        self.translate_window.withdraw()  # Hide initially
        self.translate_window.protocol("WM_DELETE_WINDOW", self.on_close)

        # Set icon
        p1 = tk.PhotoImage(file='files_bbox/logo.png')
        self.translate_window.iconphoto(False, p1)

        # Vertical scale
        self.w1 = tk.Scale(
            self.translate_window,
            from_=200, to=-200,
            tickinterval=10,
            command=self.owner.ANNOTATION_HANDLER.translate_vertical,
            length=300
        )
        self.w1.set(0)
        self.w1.pack()

        # Horizontal scale
        self.w2 = tk.Scale(
            self.translate_window,
            from_=200, to=-200,
            tickinterval=10,
            orient=tk.HORIZONTAL,
            command=self.owner.ANNOTATION_HANDLER.translate_horizontal,
            length=300
        )
        self.w2.set(0)
        self.w2.pack()

        # Store translation values as attributes instead of globals
        self.last_translate_value_x = tk.IntVar(value=0)
        self.last_translate_value_y = tk.IntVar(value=0)

        # Reset button
        reset_translate_btn = tk.Button(
            self.translate_window,
            text="Reset",
            command=self.owner.ANNOTATION_HANDLER.reset_translation
        )
        reset_translate_btn.pack()

    def toggle(self, event=None):
        """Show/hide the window."""
        if self.shown:
            self.translate_window.withdraw()
            self.shown = False
        else:
            self.translate_window.deiconify()
            self.shown = True
            
    def on_close(self):
        """Hide instead of destroy when X is clicked."""
        self.translate_window.withdraw()
        self.shown = False

class Window:
    def __init__(self,owner,title="Window", size="400x400"):
        self.owner = owner
        self.shown = False
        # Create Toplevel window
        self.window = tk.Toplevel(self.owner.root)
        self.window.title(title)
        self.window.geometry(size)
        self.window.withdraw()  # Start hidden
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def toggle(self, event=None):
        """Show/hide the colour selection window."""
        if self.shown:
            self.window.withdraw()
            self.shown = False
        else:
            self.window.deiconify()
            self.shown = True

    def on_close(self):
        """Hide instead of destroy when X is clicked."""
        self.window.withdraw()
        self.shown = False

class ChangeClassNamesWindow(Window):    
    def __init__(self,owner):
        super().__init__(owner,title="Change Class Names",size="400x200")

        self.label = tk.Label(self.window, text="Edit class names (comma-separated):")
        self.label.pack(pady=10)

        self.text_input = tk.Text(self.window, height=4, width=40)
        self.text_input.pack(padx=10)
        self.text_input.insert(tk.END, ", ".join(self.owner.class_names))  # Show current class names

        self.save_button = tk.Button(self.window, text="Save", command=self.save_changes)
        self.save_button.pack(pady=10)
    
    def save_changes(self):
        input_text = self.text_input.get("1.0", tk.END).strip()
        class_names = []
        if input_text:
            class_names[:] = [name.strip() for name in input_text.split(',') if name.strip()]
            self.owner.class_names = class_names
            self.generate_colors(len(class_names))
            messagebox.showinfo("Success", "Class names updated!")
            if self.owner.class_dropdown:
                self.owner.class_dropdown.configure(values=class_names)
                self.owner.class_dropdown.current(0)
            if self.owner.CHANGE_CLASS_NAMES_WINDOW:
                self.owner.COLOUR_SELECT_WINDOW.update_on_class_name_change()
            if self.owner.USERINTERFACE:    
                self.owner.USERINTERFACE.create_context_sensitive_drop_down_menu()
            self.toggle()
            
        else:
            messagebox.showwarning("Empty Input", "Class names cannot be empty.")

    def generate_colors(self,n):
        global colors
        base_colors = [
            (255, 0, 0),       # Red
            (0, 128, 0),       # Green
            (0, 0, 255),       # Blue
            (255, 165, 0),     # Orange
            (128, 0, 128),     # Purple
            (0, 255, 255),     # Cyan
            (0, 0, 0),         # Black
            (255, 192, 203),   # Pink
            (139, 69, 19),     # Brown
        ]
        # Repeat colors if more are needed, but preserve order
        self.owner.class_colors = [base_colors[i % len(base_colors)] for i in range(n)]

class ColourSelectWindow(Window):
    def __init__(self, owner):
        # Call base class constructor
        super().__init__(owner, title="Class Colour Selection", size="400x400")

        # Get class names and colours
        self.class_names = self.owner.class_names
        self.colour_list = self.owner.class_colors  # Shared reference

        # Left frame for class buttons
        self.left_frame = tk.Frame(self.window, width=200, bg="lightgray")
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Right frame for colour selector (MS Paint style)
        self.right_frame = tk.Frame(self.window, width=400, bg="white")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Build class buttons
        self.class_buttons = []
        for idx, name in enumerate(self.class_names):
            color_hex = self.rgb_to_hex(self.colour_list[idx])
            btn = tk.Button(
                self.left_frame,
                text=name,
                bg=color_hex,
                fg="white",
                command=lambda i=idx: self.open_color_picker(i)
            )
            btn.pack(fill=tk.X, padx=5, pady=5)
            self.class_buttons.append(btn)

        # Build palette UI
        self.build_palette()
    
    def update_on_class_name_change(self):
        self.class_names = self.owner.class_names
        self.colour_list = self.owner.class_colors  # Shared reference
        
        # Clear existing widgets in left_frame
        for widget in self.left_frame.winfo_children():
            widget.destroy()
        
        # Build class buttons
        self.class_buttons = []
        for idx, name in enumerate(self.class_names):
            color_hex = self.rgb_to_hex(self.colour_list[idx])
            btn = tk.Button(
                self.left_frame,
                text=name,
                bg=color_hex,
                fg="white",
                command=lambda i=idx: self.open_color_picker(i)
            )
            btn.pack(fill=tk.X, padx=5, pady=5)
            self.class_buttons.append(btn)
        
    def rgb_to_hex(self, rgb):
        """Convert (R,G,B) list or tuple to hex string."""
        r, g, b = rgb
        return "#%02x%02x%02x" % (r, g, b)

    def build_palette(self):
        """Draw a simple palette similar to MS Paint with preset colors."""
        preset_colors = [
            "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF",
            "#000000", "#FFFFFF", "#808080", "#800000", "#008000", "#000080"
        ]
        rows, cols = 3, 4
        for i, color in enumerate(preset_colors):
            row, col = divmod(i, cols)
            canvas = tk.Canvas(self.right_frame, bg=color, width=50, height=50, highlightthickness=1, highlightbackground="black")
            canvas.grid(row=row, column=col, padx=5, pady=5)
            canvas.bind("<Button-1>", lambda e, c=color: self.set_selected_color(c))

        # Add "Custom Color..." button (like MS Paint)
        tk.Button(self.right_frame, text="Custom Color...", command=self.choose_custom_color).grid(row=rows, column=0, columnspan=cols, pady=10)

        # Label to show selected color
        self.selected_color_preview = tk.Label(self.right_frame, text="Selected Color", width=20, height=2, relief=tk.SUNKEN)
        self.selected_color_preview.grid(row=rows+1, column=0, columnspan=cols, pady=10)

    def set_selected_color(self, hex_color):
        """Set selected color from palette and preview it."""
        self.selected_color_preview.config(bg=hex_color)
        self.current_color = hex_color
        if hasattr(self, 'current_class_idx'):
            # Update class button color immediately
            self.class_buttons[self.current_class_idx].config(bg=hex_color)
            self.colour_list[self.current_class_idx] = self.hex_to_rgb(hex_color)
            self.owner.class_colors[self.current_class_idx] = self.hex_to_rgb(hex_color)
            self.owner.update_display()

    def choose_custom_color(self):
        """Open system color chooser dialog."""
        color_code = colorchooser.askcolor(title="Choose a custom color")
        if color_code[1]:
            self.set_selected_color(color_code[1])

    def open_color_picker(self, class_idx):
        """When a class button is clicked, mark it active and preview its color."""
        self.current_class_idx = class_idx
        current_hex = self.rgb_to_hex(self.colour_list[class_idx])
        self.set_selected_color(current_hex)

    def hex_to_rgb(self, hex_color):
        """Convert hex (#RRGGBB) to (R,G,B)."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def toggle(self, event=None):
        """Show/hide the colour selection window."""
        if self.shown:
            self.window.withdraw()
            self.shown = False
        else:
            self.window.deiconify()
            self.shown = True

    def on_close(self):
        """Hide instead of destroy when X is clicked."""
        self.window.withdraw()
        self.shown = False

class MenuBar:    
    def __init__(self, owner):
        self.owner = owner
        # Adding a 'File' menu to the menu bar
        menu_bar = tk.Menu(self.owner.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Load Images", command=self.owner.IMAGE_HANDLER.select_image_dir)
        file_menu.add_command(label="Load Model", command=self.owner.PREDICTION_MODEL_HANDLER.load_new_model)
        file_menu.add_command(label="Save Annotation", command=self.owner.USER_INPUT_HANDLER.on_save)
        file_menu.add_separator()  # Adds a separator line
        file_menu.add_command(label="Exit", command=self.owner.exit_app)
        # Add the File menu to the menu bar
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Controls", command=self.owner.HELPER.show_help)
        help_menu.add_command(label="Ultralytics", command=self.owner.HELPER.open_ultralytics_webpage)
        menu_bar.add_cascade(label="Help",menu=help_menu)
        
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="Annotations List", command=self.owner.BOX_LIST.toggle)
        view_menu.add_command(label="Image List", command=self.owner.IMAGE_LIST_WINDOW.toggle)
        view_menu.add_command(label="Zoom Window", command=self.owner.ZOOM_WINDOW.toggle)
        menu_bar.add_cascade(label="View",menu=view_menu)
        
        global_menu = tk.Menu(menu_bar, tearoff=0)
        global_menu.add_command(label="Translate Annotations", command=self.owner.TRANSLATE_ANNOTATIONS_WINDOW.toggle)
        global_menu.add_command(label="Delete Duplicates", command=self.owner.ANNOTATION_HANDLER.delete_duplicates)
        global_menu.add_separator()  # Adds a separator line
        global_menu.add_command(label="Delete All Annotations", command=self.owner.ANNOTATION_HANDLER.delete_all_annotations)
        #view_menu.add_command(label="Reset Zoom", command=reset_zoom)
        menu_bar.add_cascade(label="Global",menu=global_menu)
        
        Augmentation_menu = tk.Menu(menu_bar, tearoff=0)
        Augmentation_menu.add_command(label="Flip Image Vertically", command=self.owner.DATA_AUGMENTOR.flip_lr)    
        #Augmentation_menu.add_command(label="Flip Anotations Vertically", command=flip_annotations_lr)    
        Augmentation_menu.add_command(label="Flip Image Horizontally", command=self.owner.DATA_AUGMENTOR.flip_ud)
        #Augmentation_menu.add_command(label="Flip Anotations Horizontally", command=flip_annotations_ud)
        Augmentation_menu.add_separator()  # Adds a separator line
        Augmentation_menu.add_command(label="Save Image", command=self.owner.IMAGE_HANDLER.save_image)
        #view_menu.add_command(label="Reset Zoom", command=reset_zoom)
        menu_bar.add_cascade(label="Augmentation",menu=Augmentation_menu)
        
        model_menu = tk.Menu(menu_bar, tearoff=0)
        model_menu.add_command(label="Change Model Setting", command=self.owner.MODEL_SETTINGS_WINDOW.toggle)
        #view_menu.add_command(label="Reset Zoom", command=reset_zoom)
        menu_bar.add_cascade(label="Model",menu=model_menu)
        
        # Display the menu bar
        self.owner.root.config(menu=menu_bar)

class UserInterface:
    def __init__(self, owner):
        self.owner = owner
        self.bind_key_controls()
        self.bind_mouse_controls()
        self.create_buttons()
        self.create_context_sensitive_drop_down_menu()
        self.menubar = MenuBar(self.owner)
        
    def bind_key_controls(self):
        # Bind key press events for new bounding box creation and deletion
        self.owner.root.bind("<KeyPress>", self.owner.USER_INPUT_HANDLER.on_key_press)
        
        # Bind F1 Key to open the HELP Menu
        self.owner.root.bind("<F1>", self.owner.HELPER.show_help)
        self.owner.root.bind("<F2>", self.owner.BOX_LIST.toggle)
        self.owner.root.bind("<F3>", self.owner.IMAGE_LIST_WINDOW.toggle)
        self.owner.root.bind("<F4>", self.owner.COLOUR_SELECT_WINDOW.toggle)
        self.owner.root.bind("<F5>", self.owner.CHANGE_CLASS_NAMES_WINDOW.toggle)
        self.owner.root.bind("<F12>",self.owner.USER_INPUT_HANDLER.take_screenshot)
        self.owner.root.bind("<p>", self.owner.USER_INPUT_HANDLER.set_save_flag)
        self.owner.root.bind("<h>", self.owner.USER_INPUT_HANDLER.show_confidences)
        self.owner.root.bind("<e>", self.owner.IMAGE_HANDLER.next_image)
        self.owner.root.bind("<q>", self.owner.IMAGE_HANDLER.previous_image)
        self.owner.root.bind("<d>", self.owner.IMAGE_HANDLER.next_image)
        self.owner.root.bind("<a>", self.owner.IMAGE_HANDLER.previous_image)
        
        self.owner.root.bind("<Control-a>", self.owner.USER_INPUT_HANDLER.select_all)
        self.owner.root.bind("<y>", self.owner.PREDICTION_MODEL_HANDLER.run_yolo_inference)
        self.owner. root.bind("<z>", self.owner.ZOOM_WINDOW.toggle)
        self.owner.root.bind("<App>", self.owner.USER_INPUT_HANDLER.show_context_menu)
        
        self.owner.root.bind("<Enter>", lambda event: self.owner.root.focus_set())
        
        # Bind keys to copy paste
        self.owner.root.bind("<c>", lambda event: self.owner.USER_INPUT_HANDLER.on_copy())
        self.owner.root.bind("<v>", lambda event: self.owner.USER_INPUT_HANDLER.on_paste())
        
        # bind a specific right and left key to next_image and previous_image button
        self.owner.root.bind('<Right>', lambda event: self.owner.IMAGE_HANDLER.next_image())
        self.owner.root.bind('<Left>', lambda event: self.owner.IMAGE_HANDLER.previous_image())
        
        # Bind Keys for saving
        self.owner.root.bind('<s>', lambda event: self.owner.USER_INPUT_HANDLER.on_save())
        self.owner.root.bind('<Up>', lambda event: self.owner.USER_INPUT_HANDLER.on_save())
        
        # Translate Annotations
        self.owner.root.bind("2",self.owner.ANNOTATION_HANDLER.translate_down)
        self.owner.root.bind("8",self.owner.ANNOTATION_HANDLER.translate_up)
        self.owner.root.bind("6",self.owner.ANNOTATION_HANDLER.translate_right)
        self.owner.root.bind("4",self.owner.ANNOTATION_HANDLER.translate_left)
        
        # Jump to image
        self.owner.root.bind("<Return>",self.owner.USER_INPUT_HANDLER.jump_to_image)

    def bind_mouse_controls(self):
        # Bind mouse events for interaction
        self.owner.canvas.bind("<Button-1>", self.owner.USER_INPUT_HANDLER.on_click)
        self.owner.canvas.bind("<B1-Motion>", self.owner.USER_INPUT_HANDLER.on_drag)
        self.owner.canvas.bind("<Control-B1-Motion>",self.owner.USER_INPUT_HANDLER.on_multi_drag)
        self.owner.canvas.bind("<ButtonRelease-1>", self.owner.USER_INPUT_HANDLER.on_release)
        
        self.owner.canvas.bind("<Button-3>", self.owner.USER_INPUT_HANDLER.show_context_menu)      
        
        self.owner.canvas.bind("<MouseWheel>", self.owner.ZOOM_WINDOW.on_mousewheel)
        self.owner.canvas.bind("<Motion>", self.owner.ZOOM_WINDOW.update_zoom_window)
        
        self.owner.canvas.bind("<Control-Button-1>", self.owner.USER_INPUT_HANDLER.on_multiselect)
        self.owner.canvas.bind("<Control-Button-3>", self.owner.USER_INPUT_HANDLER.stop_multiselect)

    def create_buttons(self):
        # Frame for dropdown
        dropdown_frame = tk.Frame(self.owner.root)
        dropdown_frame.pack(pady=5)  # Slight padding

        self.owner.class_dropdown = ttk.Combobox(dropdown_frame, values=[str(i) for i in self.owner.class_names], state="readonly")
        self.owner.class_dropdown.current(0)
        self.owner.class_dropdown.bind("<<ComboboxSelected>>", self.owner.USER_INPUT_HANDLER.update_class)
        self.owner.class_dropdown.pack()

        # Frame for actions (Undo, Run YOLO, Save)
        action_frame = tk.Frame(self.owner.root)
        action_frame.pack(pady=5)

        undo_button = tk.Button(action_frame, text="Undo", command=self.owner.ARCHIVE.undo)
        undo_button.pack(side=tk.LEFT, padx=5)

        yolo_button = tk.Button(action_frame, text="Run YOLO Inference", command=self.owner.PREDICTION_MODEL_HANDLER.run_yolo_inference)
        yolo_button.pack(side=tk.LEFT, padx=5)

        save_button = tk.Button(action_frame, text="Save Annotations", command=self.owner.USER_INPUT_HANDLER.on_save)
        save_button.pack(side=tk.LEFT, padx=5)

        # Frame for navigation (Previous, Jump, Next)
        nav_frame = tk.Frame(self.owner.root)
        nav_frame.pack(pady=5)

        prev_button = tk.Button(nav_frame, text="Previous", command=self.owner.IMAGE_HANDLER.previous_image)
        prev_button.pack(side=tk.LEFT, padx=5)

        jump_button = tk.Button(nav_frame, text="Jump To Image", command=self.owner.USER_INPUT_HANDLER.jump_to_image)
        jump_button.pack(side=tk.LEFT, padx=5)

        next_button = tk.Button(nav_frame, text="Next", command=self.owner.IMAGE_HANDLER.next_image)
        next_button.pack(side=tk.LEFT, padx=5)

    def create_context_sensitive_drop_down_menu(self):
        # Create Drop Down Menu at Cursor when box is selected
        self.owner.context_menu_mask_selected = tk.Menu(self.owner.root, tearoff=0)
        self.owner.context_menu_mask_selected.add_command(label="Delete Box", command=self.owner.USER_INPUT_HANDLER.delete_selected_box_menu)
        self.owner.context_menu_mask_selected.add_command(label="Copy Box", command=self.owner.USER_INPUT_HANDLER.on_copy)
        for idx, class_name in enumerate(self.owner.class_names):
                self.owner.context_menu_mask_selected.add_command(label=class_name, command=lambda i=idx: self.owner.USER_INPUT_HANDLER.change_class_from_context_menu(i))

        # Create Drop Down Menu at Cursor when box is not selected
        self.owner.context_menu_mask_not_selected = tk.Menu(self.owner.root, tearoff=0)
        self.owner.context_menu_mask_not_selected.add_command(label="Undo", command=self.owner.ARCHIVE.undo)
        self.owner.context_menu_mask_not_selected.add_command(label="Save Annotations", command=self.owner.USER_INPUT_HANDLER.on_save)
        self.owner.context_menu_mask_not_selected.add_command(label="Paste Box", command=self.owner.USER_INPUT_HANDLER.on_paste)   
        self.owner.context_menu_mask_not_selected.add_command(label="Track Annotations", command=self.owner.ANNOTATION_HANDLER.get_last_annotations)   
        self.owner.context_menu_mask_not_selected.add_command(label="New Box", command=self.owner.USER_INPUT_HANDLER.new_BB_from_context_menu)  


class UserInputHandler:
    def __init__(self, owner):
        self.owner = owner
    def show_confidences(self,event=None):
        self.owner.show_conf = not self.owner.show_conf
        self.owner.update_display()
    def getBox(self,event):        
        a = []
        x, y = self.owner.ZOOMER.convert_coordinates(event)
        
        self.owner.start_x, self.owner.start_y = event.x, event.y
        selected_box = None
        self.owner.resize_corner = None
        self.owner.resizing = False
        
        # Check if the click is near the edges for resizing
        margin = 10 # Sensitivity for selecting corners or edges        
        
        for i, box in enumerate(self.owner.ANNOTATION_HANDLER.annotations):
            _ ,x1, y1, x2, y2, = box            
            if x > x1-margin and x < x2+margin and y > y1-margin and y < y2+margin:
                if x1 - margin < x < x1 + margin and y1 - margin < y < y1 + margin:
                    selected_box = i
                    a.append(i)
                    self.owner.resize_corner = 'top_left'
                    self.owner.resizing = True
                    break
                elif x2 - margin < x < x2 + margin and y1 - margin < event.y < y1 + margin:
                    selected_box = i
                    a.append(i)
                    self.owner.resize_corner = 'top_right'
                    self.owner.resizing = True
                    break
                elif x1 - margin < x < x1 + margin and y2 - margin < y < y2 + margin:
                    selected_box = i
                    a.append(i)
                    self.owner.resize_corner = 'bottom_left'
                    self.owner.resizing = True
                    break
                elif x2 - margin < x < x2 + margin and y2 - margin < y < y2 + margin:
                    selected_box = i
                    a.append(i)
                    self.owner.resize_corner = 'bottom_right'
                    self.owner.resizing = True
                    break
                elif x1 < x < x2 and y1 < y < y2:
                    selected_box = i
                    a.append(i)
                    self.owner.dragging = True
                    # When selecting a bounding box, update the class dropdown to show the current class
                    if box[0] < len(self.owner.class_names):
                        self.owner.class_dropdown.set(str(self.owner.class_names[box[0]]))  # Set dropdown to the class of the selected box
                    else:
                        print(f"Class: {box[0]} not yet in class names list")
                    #break
                
                smallest_size = 9999999
                if len(a) > 1:
                    for idx in a:
                        box = self.owner.ANNOTATION_HANDLER.annotations[idx]
                        _ ,x1, y1, x2, y2, = box
                        curr_size = (x2-x1)*(y2-y1)                
                        if curr_size < smallest_size:
                            smallest_size = curr_size
                            print(smallest_size)
                            selected_box = idx
        
        return selected_box
    
    # Mouse click event to select a bounding box (for moving or resizing)
    def on_click(self,event):        
        self.owner.USER_INPUT_HANDLER.stop_multiselect()
        x, y = self.owner.ZOOMER.convert_coordinates(event)
        
        # Check if we are adding a new box
        if self.owner.adding_new_box:
            self.owner.selected_box = None
            self.owner.new_box_start = (event.x, event.y)  # Record the starting point
            return

        self.owner.selected_box = self.getBox(event)
            
        self.owner.update_display()  # Redraw the image to highlight the selected box

    def select_all(self, event = None):        
        self.owner.multiselect_on = True
        for idx in range(len(self.owner.ANNOTATION_HANDLER.annotations)):
            if idx not in self.owner.multiselect_idx:
                self.owner.multiselect_idx.append(idx)
        self.owner.update_display()

    def on_multiselect(self, event):        
        self.owner.multiselect_on = True
        
        if self.owner.selected_box is not None and self.owner.selected_box not in self.owner.multiselect_idx:        
            self.owner.multiselect_idx.append(self.owner.selected_box)
            self.owner.selected_box = None
        
        selected_box_idx = self.getBox(event)
        if self.owner.multiselect_on and selected_box_idx not in self.owner.multiselect_idx and self.owner.selected_box_idx is not None:
            self.owner.multiselect_idx.append(selected_box_idx)
            
        self.owner.update_display()  # Redraw the image to highlight the selected box

    def on_multi_drag(self, event):
        dx = event.x - self.owner.start_x
        dy = event.y - self.owner.start_y
        
        for idx in self.owner.multiselect_idx:
            curr_box = self.owner.ANNOTATION_HANDLER.annotations[idx]
            curr_box[1] = curr_box[1]+dx
            curr_box[2] = curr_box[2]+dy
            curr_box[3] = curr_box[3]+dx
            curr_box[4] = curr_box[4]+dy
            self.owner.ANNOTATION_HANDLER.annotations[idx] = curr_box
        
        start_x, start_y = event.x, event.y
        self.owner.ANNOTATION_HANDLER.clamp_all_coordinates()
        
        for idx in self.owner.multiselect_idx:
            curr_box = self.owner.ANNOTATION_HANDLER.annotations[idx]
            if abs(curr_box[1]-curr_box[3]) <= 1 or abs(curr_box[2] - curr_box[4])  <= 1:
                self.owner.USER_INPUT_HANDLER.stop_multiselect()
        
        self.owner.ANNOTATION_HANDLER.remove_dim1_annotations()
        
        self.owner.update_display()
        
            
    # Mouse drag event to move or resize the selected bounding box, or create a new one
    def on_drag(self, event):
        zoom_factor = self.owner.ZOOMER.zoom_factor
        self.owner.dragging = True
        if self.owner.selected_box is not None:
            dx = event.x - self.owner.start_x
            dy = event.y - self.owner.start_y
            dx = dx / zoom_factor
            dy = dy / zoom_factor

            # Handle resizing
            if self.owner.resizing:
                label, x1, y1, x2, y2 = self.owner.ANNOTATION_HANDLER.annotations[self.owner.selected_box]
                if self.owner.resize_corner == 'top_left':
                    self.owner.ANNOTATION_HANDLER.annotations[self.owner.selected_box] = [label, x1 + dx, y1 + dy, x2, y2]
                elif self.owner.resize_corner == 'top_right':
                    self.owner.ANNOTATION_HANDLER.annotations[self.owner.selected_box] = [label, x1, y1 + dy, x2 + dx, y2]
                elif self.owner.resize_corner == 'bottom_left':
                    self.owner.ANNOTATION_HANDLER.annotations[self.owner.selected_box] = [label, x1 + dx, y1, x2, y2 + dy]
                elif self.owner.resize_corner == 'bottom_right':
                    self.owner.ANNOTATION_HANDLER.annotations[self.owner.selected_box] = [label, x1, y1, x2 + dx, y2 + dy]
            
            # Handle moving
            elif self.owner.dragging:
                label, x1, y1, x2, y2 = self.owner.ANNOTATION_HANDLER.annotations[self.owner.selected_box]
                self.owner.ANNOTATION_HANDLER.annotations[self.owner.selected_box] = [label, x1 + dx, y1 + dy, x2 + dx, y2 + dy]

            self.owner.start_x, self.owner.start_y = event.x, event.y
            self.owner.update_display()

        # Handle creating a new box
        if self.owner.adding_new_box and self.owner.new_box_start:
            x1, y1 = self.owner.new_box_start
            x2, y2 = event.x, event.y
            self.owner.update_display()  # Redraw everything, including the new box outline
            self.owner.canvas.create_rectangle(x1, y1, x2, y2, outline="green", width=2)
        
        if self.owner.selected_box is None:
            self.owner.start_x, self.owner.start_y = event.x, event.y
            self.owner.ZOOM_WINDOW.update_zoom_window()
            
    # Mouse release event to stop dragging or resizing or finalize the new box
    def on_release(self, event):
        self.owner.dragging = False
        self.owner.resizing = False
        self.owner.resize_corner = ""
        zoom_factor = self.owner.ZOOMER.zoom_factor
        view_offset_x = self.owner.ZOOMER.view_offset_x
        view_offset_y = self.owner.ZOOMER.view_offset_y
        # If adding a new box, finalize it
        if self.owner.adding_new_box and self.owner.new_box_start:
            x1, y1 = self.owner.ZOOMER.convert_to_original(self.owner.new_box_start[0], self.owner.new_box_start[1])
            x2, y2 = self.owner.ZOOMER.convert_to_original(event.x, event.y)
            if x1 > x2:
                x1, x2 = x2, x1
                
            if y1 > y2:
                y1, y2 = y2, y1
                
            if abs(x2 - x1) > 10 and abs(y2 - y1) > 10:  # Ensure the box is large enough
                # Add the new box with a default class (0)
                new_class = int(self.owner.class_names.index(self.owner.class_dropdown.get()))
                if not self.owner.ANNOTATION_HANDLER.are_coordinates_valid(x1,y1,x2, y2):
                    print("The coordinates are out of bounds.")
                    x1, y1 = self.owner.ANNOTATION_HANDLER.clamp_coordinates(x1, y1)
                    x2, y2 = self.owner.ANNOTATION_HANDLER.clamp_coordinates(x2, y2)
                    print(f"Clamped Coordinates: x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}")
                self.owner.ANNOTATION_HANDLER.annotations.append([new_class, x1, y1, x2, y2])
                
            self.owner.new_box_start = None
            self.owner.adding_new_box = False
            self.owner.update_display()  # Redraw the image with the new box
            
        elif self.owner.selected_box is not None:
            curr_box = self.owner.ANNOTATION_HANDLER.annotations[self.owner.selected_box]
            x1 = curr_box[1]
            y1 = curr_box[2]
            x2 = curr_box[3]
            y2 = curr_box[4]
            
            x1,x2 = min(x1,x2), max(x1,x2)
            y1,y2 = min(y1,y2), max(y1,y2)
            
            self.owner.ANNOTATION_HANDLER.annotations[self.owner.selected_box][1:] = [x1, y1, x2, y2]
            
            if not self.owner.ANNOTATION_HANDLER.are_coordinates_valid(x1,y1,x2, y2):
                print("The coordinates are out of bounds.")
                x1, y1 = self.owner.ANNOTATION_HANDLER.clamp_coordinates(x1, y1)
                x2, y2 = self.owner.ANNOTATION_HANDLER.clamp_coordinates(x2, y2)
                print(f"Clamped Coordinates: x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}")
                
                if x1 > x2:
                    x1, x2 = x2, x1
                    
                if y1 > y2:
                    y1, y2 = y2, y1
                
                self.owner.ANNOTATION_HANDLER.annotations[self.owner.selected_box][1] = x1
                self.owner.ANNOTATION_HANDLER.annotations[self.owner.selected_box][2] = y1
                self.owner.ANNOTATION_HANDLER.annotations[self.owner.selected_box][3] = x2
                self.owner.ANNOTATION_HANDLER.annotations[self.owner.selected_box][4] = y2
            
            self.owner.update_display()  # Redraw the image with the new box

    # Function to handle saving the modified annotations
    def on_save(self):
        try:
            self.owner.last_save = copy.deepcopy(self.owner.ANNOTATION_HANDLER.annotations)
            self.owner.ANNOTATION_HANDLER.save_yolo_annotations(self.owner.annotations_path, self.owner.ANNOTATION_HANDLER.annotations, self.owner.image.shape[0], self.owner.image.shape[1])

            messagebox.showinfo("Success", f"Annotations saved to {self.owner.annotations_path}")
            print(f"Annotations saved to {self.owner.annotations_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save annotations: {e}")
            print(f"Error saving annotations: {e}")

    def on_copy(self):        
        if self.owner.multiselect_on and len(self.owner.multiselect_idx) > 0:
            self.owner.copying_box = []
            for idx in self.owner.multiselect_idx:
                self.owner.copying_box.append(self.owner.ANNOTATION_HANDLER.annotations[idx])
            return
        
        if self.owner.selected_box is not None:
            self.owner.copying_box = self.owner.ANNOTATION_HANDLER.annotations[self.owner.selected_box]
            print("Copying")
        else:
            print("No Box Selected")

    def on_paste(self):        
        if isinstance(self.owner.copying_box, list) and all(isinstance(item, list) for item in self.owner.copying_box):
            # Do something if copying_box is a list of lists
            print("copying_box is a list of lists")
            for box in self.owner.copying_box:
                self.owner.ANNOTATION_HANDLER.annotations.append(box)
            self.owner.selected_box = None
            self.owner.update_display()
            return
        
        if self.owner.copying_box is not None:
            self.owner.ANNOTATION_HANDLER.annotations.append(self.owner.copying_box)
            self.owner.selected_box = len(self.owner.ANNOTATION_HANDLER.annotations)-1
            print("Pasted")
            self.owner.update_display()
        else:
            print("Nothing to Paste")

    # Key press event handler to add new bounding annotations or delete the selected box
    def on_key_press(self, event):
        if event.char == 'n':
            self.owner.adding_new_box = True
            print("Adding new bounding box... Click and drag to create a box.")
        elif event.keysym == 'Delete':  # Handle delete key
            self.delete_selected_box(event)

    def take_screenshot(self, event=None):
        fileName = self.owner.title_label.cget("text")+"_viewport.png"
        self.owner.image_pil.save(fileName)   
        print("Screenshot Saved!")

    def validate_numeric_input(self, new_value):
        return new_value.isdigit() or new_value == ""

    def multiselect(self, event):
        self.owner.multiselect_on = True
        self.on_click(event)
        
    def stop_multiselect(self, event=None):
        self.owner.multiselect_idx = []
        self.owner.multiselect_on = False

    # Function to delete the selected bounding box
    def delete_selected_box(self, event=None):        
        if self.owner.multiselect_on:
            for idx in sorted(self.owner.multiselect_idx, reverse=True):
                if 0 <= idx < len(self.owner.confidences):
                    del self.owner.confidences[idx]
                del self.owner.ANNOTATION_HANDLER.annotations[idx]
            self.stop_multiselect()
            self.owner.selected_box = None
            self.owner.update_display()
            return
        
        if self.owner.selected_box is not None:
            if 0 <= self.owner.selected_box < len(self.owner.confidences):
                del self.owner.confidences[self.owner.selected_box]
            del self.owner.ANNOTATION_HANDLER.annotations[self.owner.selected_box]  # Remove the selected box from the list
            self.owner.selected_box = None  # Deselect after deletion
            self.owner.update_display()  # Redraw the image without the deleted box

    def delete_selected_box_menu(self):           
        if 0 <= self.owner.selected_box < len(self.owner.confidences):
            del self.owner.confidences[self.owner.selected_box]
        
        del self.owner.ANNOTATION_HANDLER.annotations[self.owner.selected_box]  # Remove the selected box from the list
        
        self.owner.selected_box = None  # Deselect after deletion
        self.owner.update_display()  # Redraw the image without the deleted box

    def jump_to_image(self, event=None):
        try:
            jump_index = int(self.owner.number.get())
        except:
            print("Selected Image index needs to be between 0 and "+str(len(self.owner.image_paths)-1))
            return
                
        # Check if current number is different from desired jump number, only jump if different
        if jump_index is self.owner.current_image_index:
            print("Already at that image")
            return
        
        if jump_index < len(self.owner.image_paths) and jump_index >= 0 :
            self.owner.number.set(jump_index)
            self.owner.IMAGE_HANDLER.load_image(jump_index)
        else:
            print("Selected Image index needs to be between 0 and "+str(len(self.owner.image_paths)-1))


    # Function to update the class of the selected bounding box
    def update_class(self, event):
        if self.owner.selected_box is not None:
            new_class = int(self.owner.class_names.index(self.owner.class_dropdown.get()))
            self.owner.ANNOTATION_HANDLER.annotations[self.owner.selected_box][0] = new_class        
            self.owner.update_display()
            if self.owner.buttons:
                self.owner.buttons[self.owner.selected_box].config(text="Box "+str(self.owner.selected_box)+" "+self.owner.class_names[new_class])

    def set_save_flag(self, event=None):
        self.owner.save_flag = not self.owner.save_flag
        tk.messagebox.showinfo("Notification", f"Save Image Change set to: {self.owner.save_flag}")

    def prompt_saving(self):
        if not self.owner.last_save == self.owner.ANNOTATION_HANDLER.annotations and self.owner.save_flag:
            print("maybe Save")
            result = messagebox.askyesno("Changes Detected", "Do you want to save your changes?")
            if result:
                self.on_save()

    def new_BB_from_context_menu(self):
        self.owner.adding_new_box = True
        print("Adding new bounding box... Click and drag to create a box.")

    def show_context_menu(self,event):
        if self.owner.selected_box is not None or self.owner.multiselect_on:
            self.owner.context_menu_mask_selected.post(event.x_root, event.y_root)
        else:
            self.owner.context_menu_mask_not_selected.post(event.x_root, event.y_root)

    def change_class_from_context_menu(self,index):        
        if self.owner.multiselect_on == False:
            self.owner.ANNOTATION_HANDLER.annotations[self.owner.selected_box][0] = index
            if self.owner.buttons:
                self.owner.buttons[self.owner.selected_box].config(text="Box "+str(self.owner.selected_box)+" "+self.owner.class_names[index])
            
            self.owner.class_dropdown.set(str(self.owner.class_names[self.owner.ANNOTATION_HANDLER.annotations[self.owner.selected_box][0]]))
        else:
            for idx in self.owner.multiselect_idx:
                self.owner.ANNOTATION_HANDLER.annotations[idx][0] = index
                if self.owner.buttons:
                    self.owner.buttons[idx].config(text="Box "+str(idx)+" "+self.owner.class_names[index])
                
                self.owner.class_dropdown.set(str(self.owner.class_names[self.owner.ANNOTATION_HANDLER.annotations[idx][0]]))
                
        self.owner.update_display()

class Helper:
    def __init__(self, owner, help_path="files_bbox/help.txt", url="https://docs.ultralytics.com/models/fast-sam/"):
        """
        Initialize Helper with paths to help file and URL.
        """
        self.help_path = help_path
        self.url = url
        self.owner = owner

    def show_help(self, event=None):
        """
        Display help content from the help file. If missing, show fallback message.
        """
        if os.path.exists(self.help_path):
            try:
                with open(self.help_path, "r") as file:
                    help_content = file.read()
            except Exception as e:
                help_content = f"Error reading help file: {e}"
        else:
            help_content = "Help file not found. Please check the files folder for help.txt."

        messagebox.showinfo("Help", help_content)

    def open_ultralytics_webpage(self):
        """
        Open the configured Ultralytics documentation URL in a web browser.
        """
        try:
            webbrowser.open(self.url)
        except Exception:
            # Fallback to Google if something goes wrong
            webbrowser.open("https://www.google.com")

class Zoomer:
    def __init__(self, owner):
        self.owner = owner
        self.root = self.owner.root
                       
        # Zooming
        self.owner.root.bind("<MouseWheel>", self.zoom)
        self.zoom_factor = 1.0
        self.last_zoom_factor = -1.0
        self.view_offset_x = 0
        self.view_offset_y = 0
        self.do_zoom = False
                        
        # Panning
        self.owner.root.bind("<Button-2>", self.start_pan)
        self.owner.root.bind("<ButtonRelease-2>", self.stop_pan)
        self.owner.root.bind("<B2-Motion>", self.do_pan)  # While moving with button 2 pressed
        self.start_pan_x = 0
        self.start_pan_y = 0
        self.image_dragging = False
        
        
    def zoom(self, event):
        scale_factor = 1.1 if event.delta > 0 else 0.9
        self.zoom_factor *= scale_factor
        
        cursor_x, cursor_y = event.x, event.y
        
        self.view_offset_x = (self.view_offset_x - cursor_x) * scale_factor + cursor_x
        self.view_offset_y = (self.view_offset_y - cursor_y) * scale_factor + cursor_y
        self.do_zoom = True
        
        print(self.zoom_factor)
        if self.zoom_factor < 1:
            self.reset_zoom()
        print(self.zoom_factor)
        
        self.owner.update_display()
    
    def convert_coordinates(self, event):
        x, y = (event.x - self.view_offset_x) / self.zoom_factor, (event.y - self.view_offset_y) / self.zoom_factor
        return x,y
    
    def convert_to_original(self, x,y):
        x_orig, y_orig = (x - self.view_offset_x) / self.zoom_factor, (y - self.view_offset_y) / self.zoom_factor
        return x_orig, y_orig
    
    def start_pan(self, event):
        # Save starting point
        self.start_pan_x, self.start_pan_y = event.x, event.y
        self.image_dragging = True
    
    def stop_pan(self, event):
        # Stop dragging
        self.image_dragging = False
    
    def do_pan(self, event):
        if self.image_dragging:
            dx, dy = event.x - self.start_pan_x, event.y - self.start_pan_y
            self.view_offset_x += dx
            self.view_offset_y += dy
            self.start_pan_x, self.start_pan_y = event.x, event.y
    
            # Calculate image size after zoom
            img_width = 640 * self.zoom_factor
            img_height = 640 * self.zoom_factor
    
            canvas_width = 640   # You should have this stored somewhere
            canvas_height = 640
    
            # Clamp the offsets
            max_offset_x = 0
            max_offset_y = 0
    
            min_offset_x = min(0, canvas_width - img_width)
            min_offset_y = min(0, canvas_height - img_height)
    
            if self.view_offset_x > max_offset_x:
                self.view_offset_x = max_offset_x
            elif self.view_offset_x < min_offset_x:
                self.view_offset_x = min_offset_x
    
            if self.view_offset_y > max_offset_y:
                self.view_offset_y = max_offset_y
            elif self.view_offset_y < min_offset_y:
                self.view_offset_y = min_offset_y
    
            self.owner.update_display()
              
    
    def reset_zoom(self):
        self.zoom_factor = 1
        self.last_zoom_factor = -1
        self.view_offset_x = 0
        self.view_offset_y = 0
        self.owner.update_display()

class Zoomer_Old:
    def __init__(self, owner):
        self.owner = owner
        self.zoom_factor = 1.0
        self.root = self.owner.root
        self.set_keybinds()
        self.scale_factor = 1
        
        # Zoom center in original image coordinates
        self.zoom_center_x = 0
        self.zoom_center_y = 0

        # Current crop offsets
        self.crop_left = 0
        self.crop_top = 0

        self.enlarged_image_np = None
        self.cropped_image_pil = None
        
        self.view_offset_x = 0
        self.view_offset_y = 0
        self.cursor_x = 0
        self.cursor_y = 0

    def set_keybinds(self):
        self.owner.root.bind("<MouseWheel>", self.on_mousewheel)

    def on_mousewheel(self, event):
        # 1) Convert cursor (canvas coords) → original coords
        orig_x, orig_y = self.convert_to_original(event.x, event.y)
        
        # 2) Adjust zoom factor
        self.scale_factor = 1.1 if event.delta > 0 else 0.9
        self.zoom_factor = max(1.0, round(self.scale_factor * self.zoom_factor, 2))

        # 3) Update zoom center in original coords
        self.zoom_center_x = orig_x
        self.zoom_center_y = orig_y

        # 4) Redraw
        self.enlarge_image()
        self.print_on_enlarged_image()
        self.crop_image()
        self.overwrite_image_in_owner()

    def enlarge_image(self):
        np_image_to_enlarge = self.owner.image
        np_image_to_enlarge = cv2.cvtColor(np_image_to_enlarge, cv2.COLOR_RGB2BGR)
        # Original dimensions
        h, w = np_image_to_enlarge.shape[:2]

        # New dimensions
        new_w = round(w * self.zoom_factor)
        new_h = round(h * self.zoom_factor)

        # Resize with OpenCV
        self.enlarged_image_np = cv2.resize(
            np_image_to_enlarge,
            (new_w, new_h),
            interpolation=cv2.INTER_NEAREST
        )

    def print_on_enlarged_image(self):
        zoomed_annotations = [
            [coord * self.zoom_factor for coord in ann[1:]]
            for ann in self.owner.ANNOTATION_HANDLER.annotations
        ]
        for box in zoomed_annotations:
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(self.enlarged_image_np, (x1, y1), (x2, y2), (0, 255, 0), 1)

    def crop_image(self):
        crop_w, crop_h = 640, 640

        # Convert zoom center to enlarged image coords
        center_x = self.zoom_center_x * self.zoom_factor
        center_y = self.zoom_center_y * self.zoom_factor

        img_w = self.enlarged_image_np.shape[1]
        img_h = self.enlarged_image_np.shape[0]

        # Initial crop box
        left = int(center_x - crop_w // 2)
        top = int(center_y - crop_h // 2)
        right = left + crop_w
        bottom = top + crop_h

        # Clamp to bounds
        if left < 0:
            right -= left
            left = 0
        if top < 0:
            bottom -= top
            top = 0
        if right > img_w:
            left -= (right - img_w)
            right = img_w
        if bottom > img_h:
            top -= (bottom - img_h)
            bottom = img_h

        # Ensure no negatives after shifting
        left = max(0, left)
        top = max(0, top)

        # Save crop offsets for coordinate conversions
        self.crop_left = left
        self.crop_top = top

        # Crop and store
        cropped = self.enlarged_image_np[top:bottom, left:right]
        self.cropped_image_pil = Image.fromarray(cropped)

    def overwrite_image_in_owner(self):     
        
        self.owner.image_tk = ImageTk.PhotoImage(self.cropped_image_pil)
        self.owner.image_id = self.owner.canvas.create_image(
            self.view_offset_x, self.view_offset_y, anchor=tk.NW, image=self.owner.image_tk
        )

    def convert_to_original(self, canvas_x, canvas_y):
        """
        Convert canvas coords → original image coords
        considering current zoom and crop offsets.
        """
        # Translate canvas to enlarged coords
        enlarged_x = canvas_x + self.crop_left
        enlarged_y = canvas_y + self.crop_top

        # Convert to original coords
        orig_x = enlarged_x / self.zoom_factor
        orig_y = enlarged_y / self.zoom_factor
        
        orig_x = min(max(orig_x, 0), self.owner.image.shape[1] - 1)
        orig_y = min(max(orig_y, 0), self.owner.image.shape[0] - 1)

        return orig_x, orig_y
    
    def convert(self, canvas_x, canvas_y):
        """
        Convert canvas click to original image coordinates.
        """
        # Account for crop offset (from last crop)
        abs_x = canvas_x + self.view_offset_x
        abs_y = canvas_y + self.view_offset_y

        # Convert to original size by removing zoom factor
        orig_x = abs_x / self.zoom_factor
        orig_y = abs_y / self.zoom_factor

        return orig_x, orig_y


class BBOX_App:
    def __init__(self,caller_root=None):        
        # Instance variables for tracking interactions
        self.class_dropdown = None
        self.selected_box = None
        self.dragging = False
        self.resizing = False
        self.resize_corner = None
        self.start_x, self.start_y = 0, 0
        self.current_image_index = 0
        self.image_paths = []
        self.annotation_folder = "annotations_bbox"  # Folder containing images and annotations
        self.files_folder = "files_bbox"  # Folder containing setup files
        self.canvas = None  # Initialize canvas variable
        self.adding_new_box = False  # Flag to indicate if we're adding a new bounding box
        self.new_box_start = None  # Starting point for new box creation
        self.class_names = []
        self.context_menu = None
        self.copying_box = None
        self.archive = []

        self.view_offset_x, self.view_offset_y = 0, 0
        self.image_id = None  # Stores the canvas ID of the displayed image
        self.boxlist = None
        self.buttons = []
        self.scrollable_frame = None
        self.multiselect_on = False
        self.multiselect_idx = []
        self.selected_box_idx = None
        self.image_pil = None
        self.last_save = None
        self.confidences = []
        self.show_conf = True
        self.a = []
        # Variables for translating annotations
        self.last_annotations = []
        self.last_translate_value_x, self.last_translate_value_y = None, None
        self.w1, self.w2 = None, None
        self.annotation_backup_before_translation = None

        self.save_flag = True
        self.class_colors = []
        # Variables for inference
        self.set_conf, self.set_iou = 0.7, 0.8
        
        # Initialize handlers (store as instance attributes!)
        self.USER_INPUT_HANDLER = UserInputHandler(self)        
        self.DATA_AUGMENTOR = DataAugmentor(self)        
        self.IMAGE_HANDLER = ImageHandler(self)        
        self.PREDICTION_MODEL_HANDLER = PredictionModelHandler(self)        
        self.ANNOTATION_HANDLER = AnnotationHandler(self)        
        self.ARCHIVE = Archive(self)        
        self.HELPER = Helper(self)
        self.ZOOM_WINDOW = None        
        self.BOX_LIST = None        
        self.IMAGE_LIST_WINDOW = None        
        self.MODEL_SETTINGS_WINDOW = None        
        self.TRANSLATE_ANNOTATIONS_WINDOW = None        
        self.COLOUR_SELECT_WINDOW = None
        self.CHANGE_CLASS_NAMES_WINDOW = None
        
        
        self.class_names_path = os.path.join(os.getcwd(),self.files_folder,"class_names.txt")        
        if os.path.exists(self.class_names_path):
            with open(self.class_names_path, 'r') as file:
                self.class_names[:1]=(file.read().strip().split(','))  # Read the entire file content      
            
            self.generate_colors(len(self.class_names))
        else: 
            print('Could not find class_names.txt in files Folder!')
        
        # Generate class colors
        self.class_colors = self.generate_colors(10)

        # Initialize the Tkinter window
        if caller_root == None:
            self.root = tk.Tk()
        else:
            self.root = tk.Toplevel(caller_root)
        self.root.title("Image with YOLO Annotations")
        
        # Set window icon
        p1 = tk.PhotoImage(file='files_bbox/logo.png') 
        self.root.iconphoto(False, p1)
        
        # Create instance of Zoomer Class to handle Zoom function
        self.ZOOMER = Zoomer(self)
        
        # Get the list of image files
        image_extensions = ['.png', '.jpg', '.jpeg']
        self.image_paths = [os.path.join(self.annotation_folder, f) 
                            for f in os.listdir(self.annotation_folder) 
                            if os.path.splitext(f)[1].lower() in image_extensions]
        if not self.image_paths:
            print("No images found in the folder!")
            return

        # Create a canvas to display the image
        self.image = cv2.imread(self.image_paths[0])
        self.image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)  # Convert to RGB for displaying
        self.image_pil = Image.fromarray(self.image_rgb)
        self.image_tk = ImageTk.PhotoImage(self.image_pil)
        
        title = Path(self.image_paths[0]).stem
        self.title_label = tk.Label(self.root, text=title, font=("Helvetica", 16))
        self.title_label.pack(pady=10)  # Add vertical padding
        
        self.canvas = Canvas(self.root, width=self.image_pil.width, height=self.image_pil.height)
        self.canvas.pack()

        # Load the first image
        self.IMAGE_HANDLER.load_image(0) 
        
        # Initialize windows
        self.ZOOM_WINDOW = ZoomWindow(self)
        self.BOX_LIST = BoxList(self)
        self.IMAGE_LIST_WINDOW = ImageListWindow(self)
        self.MODEL_SETTINGS_WINDOW = ModelSettingsWindow(self)
        self.TRANSLATE_ANNOTATIONS_WINDOW = TranslateAnnotationsWindow(self)
        self.COLOUR_SELECT_WINDOW = ColourSelectWindow(self)
        try:
            self.CHANGE_CLASS_NAMES_WINDOW = ChangeClassNamesWindow(self)
        except Exception as e:
            print(e)
        # Setup User Controls   
        self.USERINTERFACE = UserInterface(self)
        
        # Add a counter to show the current image index
        self.number = tk.StringVar(value="0")
        validate_command = self.root.register(self.USER_INPUT_HANDLER.validate_numeric_input)
        index_counter = tk.Entry(self.root, textvariable=self.number, justify="center", 
                                 validate="key", validatecommand=(validate_command, "%P"))
        index_counter.pack(side=tk.BOTTOM)
        
        
        
        # Run the Tkinter main loop
        self.root.mainloop()

    def generate_colors(self, n=None):
        if n is None:
            n = self.yolo_model.model.nc
        
        self.class_colors = []           
        for i in range(n):
            # Generate hue value evenly spaced around the color wheel
            hue = i / n
            # Convert HSV (hue, saturation, value) to RGB, full saturation and brightness for vivid colors
            rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            # Scale RGB from 0-1 to 0-255
            self.class_colors.append([int(c * 255) for c in rgb])

    def update_display(self):
        # Clear canvas
        self.canvas.delete("all")
        
        # Zoom
        zoom_factor = self.ZOOMER.zoom_factor
        if zoom_factor is not self.ZOOMER.last_zoom_factor:
            self.image_pil = Image.fromarray(self.image)
            image_resized = self.image_pil.resize((int(self.image_pil.width * zoom_factor), int(self.image_pil.height * zoom_factor)), Image.NEAREST)
            image_np_orig = np.array(image_resized)   
        
        
        # Convert image to RGB for display
        self.image_rgb = cv2.cvtColor(image_np_orig, cv2.COLOR_BGR2RGB)
    
        # Generate colors if not initialized
        if self.class_colors is None:
            self.generate_colors(len(self.class_names))
            self.generate_colors(20)
    
        # Draw annotations
        for i, box in enumerate(self.ANNOTATION_HANDLER.annotations):
            label, x1, y1, x2, y2 = box
            x1 = int(x1 * self.ZOOMER.zoom_factor)
            x2 = int(x2 * self.ZOOMER.zoom_factor)
            y1 = int(y1 * self.ZOOMER.zoom_factor)
            y2 = int(y2 * self.ZOOMER.zoom_factor)
            color = self.class_colors[label]
    
            # Highlight selected box
            if i == self.selected_box:
                vertices = [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]
                corners = {
                    "top_left": vertices[0],
                    "top_right": vertices[1],
                    "bottom_left": vertices[2],
                    "bottom_right": vertices[3]
                }
                cv2.rectangle(self.image_rgb, (x1, y1), (x2, y2), (255, 255, 0), 1)
                for corner, coords in corners.items():
                    corner_color = [255, 255, 0] if corner == self.resize_corner else [128, 0, 128]
                    cv2.circle(self.image_rgb, coords, 5, corner_color, 1)
    
            if i in self.multiselect_idx and self.multiselect_on:
                cv2.rectangle(self.image_rgb, (x1, y1), (x2, y2), (255, 255, 0), 1)
    
            if i != self.selected_box and i not in self.multiselect_idx:
                cv2.rectangle(self.image_rgb, (x1, y1), (x2, y2), color, 1)
    
            fontSize = 0.6
            try:
                cv2.putText(self.image_rgb, str(self.class_names[label]), (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, fontSize, color, 1)
            except:
                cv2.putText(self.image_rgb, "N.A.", (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, fontSize, color, 1)
    
            if self.show_conf:
                try:
                    conf = str(self.confidences[i])
                    cv2.rectangle(self.image_rgb, (x1 + 2, y2 - 2),
                                  (int(x1 + 30 * fontSize / 0.4), int(y2 - 16 * fontSize / 0.4)), (0, 0, 0), -1)
                    cv2.putText(self.image_rgb, conf, (x1 + 2, y2 - 5), cv2.FONT_HERSHEY_SIMPLEX, fontSize, color, 1)
                except:
                    cv2.rectangle(self.image_rgb, (x1 + 2, y2 - 2),
                                  (int(x1 + 12 * fontSize / 0.4), int(y2 - 16 * fontSize / 0.4)), (0, 0, 0), -1)
                    cv2.putText(self.image_rgb, "M", (x1 + 2, y2 - 5), cv2.FONT_HERSHEY_SIMPLEX, fontSize, color, 1)
    
        # Convert to PIL and then to Tkinter format
        self.image_pil = Image.fromarray(self.image_rgb)
        self.image_tk = ImageTk.PhotoImage(self.image_pil)
        #self.image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)
        
        vx = self.ZOOMER.view_offset_x
        vy = self.ZOOMER.view_offset_y
        self.image_id = self.canvas.create_image(vx, vy, anchor=tk.NW, image=self.image_tk)
    
        # Update archive and UI elements
        self.ARCHIVE.fill_archive()
    
        if self.BOX_LIST is not None:
            self.BOX_LIST.refresh_boxlist()
    
        if self.ZOOM_WINDOW is not None:
            self.ZOOM_WINDOW.update_zoom_window()
    
        
    def exit_app(self):
        self.root.destroy()  

# Main function to browse and annotate images
def initialize_bbox_app():
    BBOX_APP = BBOX_App()

if __name__ == "__main__":
    initialize_bbox_app()


        