# -*- coding: utf-8 -*-
"""
Created on Mon Sep 29 13:26:42 2025

@author: bojan
"""

import os
import tkinter as tk
from tkinter import ttk
from tkinter import ALL  # Import ALL for scaling
from tkinter import messagebox, Message, filedialog, Checkbutton, Scale
import tkinter.messagebox as messagebox  # Make sure this is imported
from PIL import Image, ImageTk
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
import ultralytics
from ultralytics import YOLO, SAM
import os
import math
from shapely.geometry import Polygon
from shapely.ops import unary_union
import colorsys
import copy
from pathlib import Path
import webbrowser
import time
import pygame.color

#from seg_helper import MorphologicSegHelper

#%% ----------- Space for Helper funktcions -----------


#%% ----------- GUI - Buttons and Canvas -----------
class UserInterface:
    def __init__(self, owner):
        self.owner = owner
        self.root = self.owner.root
        self.img = None  # Wird das Pillow-Image halten
        self.tk_img = None
        self.create_gui()
        
    def create_gui(self):
        title = "AVAW CVAT" #* Path(image_paths[0]).stem
        self.owner.title_label = tk.Label(self.root, text=title, font=("Helvetica", 16))
        self.owner.title_label.pack(pady=10)
        
       # Canvas erstellen
        self.owner.canvas = tk.Canvas(self.root, width=640, height=640, bg="white") # Auf dinamisch an Bildgröße anpassen ändern
        self.owner.canvas.pack()

        # Bild mit Pillow laden und anzeigen
        try:
            # 1. Bild mit Pillow laden
            self.image = Image.open("MUL-logo.png")
            # 2. Optional skalieren
            self.image = self.image.resize((640, 500), Image.Resampling.LANCZOS)
            # 3. In Tkinter-Format konvertieren
            self.tk_image = ImageTk.PhotoImage(self.image)
            # 4. Im Canvas anzeigen
            self.owner.canvas.create_image(320, 320, image=self.tk_image, anchor="center")
            
        except Exception as e:
            print(f"Fehler beim Laden des Bildes: {e}")
            self.owner.canvas.create_text(200, 150, text="Kein Bild geladen", fill="black")
        
        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(side=tk.BOTTOM, anchor='center', pady=10)
        
        slider_title = tk.Label(buttons_frame, text="Vertex Threshold:")
        slider_title.grid(row=0, column=0, padx=5, pady=5, sticky="se")
        
        slider_value = tk.DoubleVar(value=0.5)
        slider = tk.Scale(buttons_frame,
                          from_=0.0,
                          to=1.0,
                          resolution=0.1,         # Schrittweite (z. B. 0.1)
                          orient='horizontal',  # horizontale Ausrichtung
                          variable=slider_value,  # Bindung an Variable
                          #* command=print_value,    # Callback bei Veränderung
                          length=150)
        slider.set(0.0)
        slider.grid(row=0, column=1, padx=5, pady=5)
        
        anno_button = tk.Button(buttons_frame, text="Annotate Image (space)")#* command=lambda: start_seg_app(bu_root))
        anno_button.grid(row=1, column=0, padx=5, pady=5)
        
        simply_button = tk.Button(buttons_frame, text="Simplify Image (B)")#* command=lambda: start_seg_app(bu_root))
        simply_button.grid(row=1, column=1, padx=5, pady=5)
        
        save_button = tk.Button(buttons_frame, text="Save Annotation (S)")#* command=lambda: start_seg_app(bu_root))
        save_button.grid(row=1, column=2, padx=5, pady=5)
        
        selected = tk.StringVar()
        print(self.owner.class_names)
        self.owner.class_dropdown = ttk.Combobox(buttons_frame, textvariable=selected, values=self.owner.class_names, state="readonly")
        self.owner.class_dropdown.grid(row=2, column=1, padx=5, pady=5)
        # Delay setting the current selection to ensure Combobox is fully loaded
        self.owner.class_dropdown.after(100, lambda: self.owner.class_dropdown.set("Select your Class..."))
        
        prev_button = tk.Button(buttons_frame, text="Previous Image (<-)", command=self.owner.IMG_HANDLER.previous_image)
        prev_button.grid(row=3, column=0, padx=5, pady=5)
        
        
        jump_button = tk.Button(buttons_frame, text="Jump to Image", command=self.owner.IMG_HANDLER.jump_to_image)
        jump_button.grid(row=3, column=1, padx=5, pady=5)
        
        next_button = tk.Button(buttons_frame, text="Next Image (->)", command=self.owner.IMG_HANDLER.next_image)
        next_button.grid(row=3, column=2, padx=5, pady=5)
        
        img_number = tk.Entry(buttons_frame, textvariable=self.owner.number, justify="center")
        img_number.grid(row=4, column=1, padx=5, pady=5)
        
        undo_button = tk.Button(buttons_frame, text="Undo (Z)")#* command=lambda: start_seg_app(bu_root))
        undo_button.grid(row=5, column=1, padx=5, pady=5)
        
#%% ----------- Menubar -----------
class MenuBar:
    def __init__(self, owner):
        self.owner = owner
        self.root = self.owner.root
        self.creat_menu()
        
    def creat_menu(self):
        
        menu_bar = tk.Menu(self.root)
        
        # Adding a 'File' menu to the menu bar
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Load Images", command=self.owner.IMG_HANDLER.select_image_dir)
        # file_menu.add_command(label="Load Model", command=load_new_model)
        file_menu.add_command(label="Load Class Name List", command=self.owner.CLASS_HANDLER.load_new_class_name_list)
        # file_menu.add_command(label="Load Annotations from different Folder", command=set_annotations_folder)
        # file_menu.add_command(label="Save Annotation", command=save_annotations)
        file_menu.add_separator()  # Adds a separator line
        file_menu.add_command(label="Exit", command=self.owner.exit_app)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Controls", command=self.show_help)
        help_menu.add_command(label="Ultralytics", command=self.open_ultralytics_webpage)
        menu_bar.add_cascade(label="Help",menu=help_menu)
        
        # view_menu = tk.Menu(menu_bar, tearoff=0)
        # view_menu.add_command(label="Annotations List", command=show_boxlist)
        # view_menu.add_command(label="Reset Zoom", command=reset_zoom)
        # menu_bar.add_cascade(label="View",menu=view_menu)
        
        # global_menu = tk.Menu(menu_bar, tearoff=0)
        # global_menu.add_command(label="Set Vertex Threshold", command=set_vertex_threshold)
        # global_menu.add_command(label="Delete Duplicaties", command=delete_duplicates)
        # global_menu.add_command(label="Delete Contained Polygons", command=delete_contained_polygons)
        # global_menu.add_command(label="Define Translation Stepsize", command=define_translation_speed)
        # global_menu.add_command(label="Alter Class Names", command=edit_class_names_window)
        # menu_bar.add_cascade(label="Global",menu=global_menu)
        
        #model_menu = tk.Menu(menu_bar, tearoff=0)
        #model_menu.add_command(label="Change Model Setting", command=show_model_settings)
        #view_menu.add_command(label="Reset Zoom", command=reset_zoom)
        #menu_bar.add_cascade(label="Model",menu=model_menu)
        
        # Display the menu bar
        self.root.config(menu=menu_bar)

    def show_help(self, event=None):
        # Display a message box with a help message
        help_path = os.path.join(self.owner.files_folder, "help.txt")
        
        if os.path.exists(help_path):
            with open(help_path, "r") as file:
                help_content = file.read()
        else:
            help_content = "Help file not found. Please check the files folder for help.txt."                  
        
        messagebox.showinfo("Help", help_content)
    
    def open_ultralytics_webpage(self):
        #webbrowser.open("www.gidf.at")
        try:
            webbrowser.open("https://docs.ultralytics.com/models/fast-sam/")
        except:
            webbrowser.open("www.google.com")
        else:
            print("No Webbrowser Found")
            
            
#%% ----------- Image Handler-----------
class ImageHandler:
    def __init__(self, owner):
        self.owner = owner
        self.root = self.owner.root

    def select_image_dir(self):
        self.owner.annotations_folder = None
        self.directory = filedialog.askdirectory(title="Select Directory")
        self.getImagePaths(self.directory)
        self.owner.curr_image_index = 0
        self.load_image()
        #* reset_zoom()
        self.owner.update_display()  
        
        
    def getImagePaths(self, folder_dir="Images"):
        image_extensions = ['.png', '.jpg', '.jpeg']

        # Check if the provided folder exists
        if not os.path.exists(folder_dir):
            print(f"Folder '{folder_dir}' not found. Creating fallback folder 'annotations_seg'.")

            # Create fallback folder
            fallback_dir = "annotations_seg"
            os.makedirs(fallback_dir, exist_ok=True)

            # Create a placeholder image
            placeholder_path = os.path.join(fallback_dir, "no_images_found.png")

            if not os.path.exists(placeholder_path):
                # Create a blank image
                img = Image.new('RGB', (400, 200), color=(200, 200, 200))
                draw = ImageDraw.Draw(img)

                # Try using a default font (system dependent)
                try:
                    font = ImageFont.truetype("arial.ttf", 24)
                except IOError:
                    font = ImageFont.load_default()

                # Add text
                text = "No images Found"
                text_width, text_height = draw.textsize(text, font=font)
                position = ((400 - text_width) // 2, (200 - text_height) // 2)
                draw.text(position, text, fill=(0, 0, 0), font=font)

                # Save placeholder image
                img.save(placeholder_path)

            self.owner.image_paths = [placeholder_path]
            return self.image_paths

        # If folder exists, gather images
        self.owner.image_paths = [os.path.join(folder_dir, f) for f in os.listdir(folder_dir)
                       if os.path.splitext(f)[1].lower() in image_extensions]

        if not self.owner.image_paths:
            print("No images found in the folder!")

        return self.owner.image_paths
        
    def load_image(self):
        #global curr_image_index, image, original_image, tk_image, annotations, title_label, archive, selected_mask_idx, multiselect_on, selected_indices
    
        self.owner.selected_mask_idx = None
        self.owner.selected_indices = []
        self.owner.original_image = Image.open(self.owner.image_paths[self.owner.curr_image_index])
        self.owner.image = self.owner.original_image.copy()
        
        max_height = 640
    
        # Get the original dimensions of the image
        original_width, original_height = self.owner.image.size
        if original_height > max_height:
            aspect_ratio = original_width / original_height
            new_height = max_height
            new_width = int(max_height * aspect_ratio)
            # Resize the image
            self.owner.image = self.owner.image.resize((new_width,new_height))
       
        #image.resize((int(image.width * zoom_factor), int(image.height * zoom_factor)), Image.LANCZOS)
        self.owner.tk_image = ImageTk.PhotoImage(self.owner.image)  
        
        self.owner.zoom_factor = 1
        self.owner.image_resized = self.owner.image.resize((int(self.owner.image.width * self.owner.zoom_factor), int(self.owner.image.height * self.owner.zoom_factor)), Image.NEAREST)
        self.owner.image_np_orig = np.array(self.owner.image_resized)   
        
        image_name = Path(self.owner.image_paths[self.owner.curr_image_index]).stem
        self.owner.title_label.config(text=image_name)
        #* self.owner.annotations = load_yolo_segmentation()
        self.owner.multiselect_on = False
        self.owner.archive = []

    def next_image(self, event=None):
        #global curr_image_index, number
        if self.owner.curr_image_index + 1 < len(self.owner.image_paths):
            self.owner.curr_image_index += 1
            self.owner.number.set(self.owner.curr_image_index)
            self.load_image()
            #* try:
            #     self.owner.refresh_boxlist()
            # except:
            #     pass
            # reset_zoom()
            
            self.owner.update_display()

    def previous_image(self, event=None):
        #global curr_image_index, number
        if self.owner.curr_image_index - 1 >= 0:
            self.owner.curr_image_index -= 1
            self.owner.number.set(self.owner.curr_image_index)
            self.load_image()
            #* try:
            #     refresh_boxlist()
            # except:
            #     pass
            # reset_zoom()
            
            self.owner.update_display()
            
    def jump_to_image(self, event=None):
        global number, curr_image_index
        print(int(self.owner.number.get()))
        jump_index = int(self.owner.number.get())
        if jump_index < len(self.owner.image_paths) and jump_index >= 0:
            self.owner.number.set(jump_index)
            self.owner.curr_image_index = jump_index
            self.load_image()
            #* reset_zoom()
            self.owner.update_display()
        else:
            print("Selected Image index needs to be between 0 and "+str(len(self.owner.image_paths)-1))

#%% ----------- Class Handler -----------
class ClassHandler:
    def __init__(self, owner):
        self.owner = owner
        self.root = self.owner.root
        
    
    def load_class_names(self):
        #global class_names
        class_names_path = os.path.join(os.getcwd(), self.owner.files_folder,"class_names.txt")
        
        if os.path.exists(class_names_path):
            with open(class_names_path, 'r') as file:
                self.owner.class_names[:1]=(file.read().strip().split(','))  # Read the entire file content      
            #* generate_colors(len(self.owner.class_names))
        else: 
            print('Could not find class_names.txt in files Folder! Using Default Class Names')
            self.owner.class_names = ["Class 1", "Class 2", "Edit Classes"]
            
    def load_new_class_name_list(self):
        #global class_names, class_dropdown
        filepath = filedialog.askopenfilename()
        print(filepath)
        if os.path.exists(filepath):
            self.owner.class_names = []
            with open(filepath, 'r') as file:
                self.owner.class_names[:1]=(file.read().strip().split(','))  # Read the entire file content      
            print("Class Names Changed")
            
            # Update Class Dropdown Menu
            self.owner.class_dropdown.configure(values=[str(i) for i in self.owner.class_names])
            self.owner.class_dropdown.current(0)
        else: 
            print('Could not find class_names.txt in files Folder! Using Default Class Names')
            self.owner.class_names = ["Class 1", "Class 2"]
    

    # def change_all_classes_from_context_menu(self, index):
    #     global annotations
    #     for annotation in annotations:
    #         annotation[0] = index
    #         update_display()
        
    # def change_class_from_context_menu(self, index):
    #     global selected_mask_idx, buttons, multiselect_on, selected_indices
        
    #     if multiselect_on:
    #         for idx in selected_indices:
    #             annotations[idx][0] = index
    #         if buttons:
    #             buttons[selected_mask_idx].config(text="Box "+str(selected_mask_idx)+" "+class_names[index])
    #         stop_multiselect()
    #         update_display()
    #         return 
        
    #     annotations[selected_mask_idx][0] = index
    #     if buttons:
    #         buttons[selected_mask_idx].config(text="Box "+str(selected_mask_idx)+" "+class_names[index])
    #     #is_y_pressed.set(False)
    #     update_display()    
        
    # # Function to update the class of the selected bounding box
    # def update_class(self, event):    
    #     global selected_mask_idx, annotations, class_dropdown, selected_class, buttons, multiselect_on  
    #     new_class = int(class_names.index(class_dropdown.get()))
    #     selected_class = new_class
        
    #     if multiselect_on:
    #         for idx in selected_indices:
    #             annotations[idx][0] = new_class
    #         update_display()
    #         stop_multiselect()
    #         return
        
    #     if selected_mask_idx is not None:      
    #         annotations[selected_mask_idx][0] = new_class 
    #         update_display(selected_mask_idx)
    #         buttons[selected_mask_idx].config(text="Box "+str(selected_mask_idx)+" "+class_names[new_class])
            
    # def edit_class_names_window(self):
    #     def save_changes(self):
    #         global class_names, class_dropdown  # if needed
    #         input_text = text_input.get("1.0", tk.END).strip()
    #         if input_text:
    #             class_names[:] = [name.strip() for name in input_text.split(',') if name.strip()]
    #             messagebox.showinfo("Success", "Class names updated!")
    #             if class_dropdown:
    #                 class_dropdown.configure(values=class_names)
    #                 class_dropdown.current(0)
    #             window.destroy()
    #             generate_colors(len(class_names))
    #         else:
    #             messagebox.showwarning("Empty Input", "Class names cannot be empty.")

    #     window = tk.Toplevel()
    #     window.title("Edit Class Names")
    #     window.geometry("400x200")
    #     window.grab_set()  # make window modal

    #     label = tk.Label(window, text="Edit class names (comma-separated):")
    #     label.pack(pady=10)

    #     text_input = tk.Text(window, height=4, width=40)
    #     text_input.pack(padx=10)
    #     text_input.insert(tk.END, ", ".join(class_names))  # Show current class names

    #     save_button = tk.Button(window, text="Save", command=save_changes)
    #     save_button.pack(pady=10)
        
#%% ----------- Seg APP Initalization -----------
class SEG_App:
    def __init__(self,caller_root=None):        
        
        # ---------- Space for Attributes ----------
        
        # gloabale Veriablen hinzugefügt. Werden die benötigt?
        self.original_image = None
        self.image = None
        self.tk_image = None
        self.title_label = None
        self.coordinates = None
        self.points_array = []
        self.points = []
        self.class_dropdown = None
        # -----------------------------------------------------
        
        self.canvas = None
        self.annotations = []  # Each entry is [class_id, x1, y1, x2, y2, ..., xn, yn]
        self.annotations_folder = None
        # self.last_annotations = None
        self.archive = []
        self.selected_mask_idx = None
        self.selected_point_idx = None
        # self.selected_class = 0
        self.manual_mode = False
        self.manual_polygon = []
        # self.new_mask_mode = False
        self.zoom_factor = 1.0
        self.last_zoom_factor = 1
        self.view_offset_x = 0
        self.view_offset_y = 0
        # self.start_pan_x = 0
        # self.start_pan_y = 0
        # self.start_x, start_y = 0, 0
        self.image_paths = []
        self.curr_image_index = 0
        # self.threshold = 0.000
        self.files_folder = "files_seg"
        self.class_names = []
        self.colors = []
        # self.nUndoes = 100
        # self.mask_dragging = False
        # self.image_dragging = False
        # self.undoing = False
        self.number = None
        self.do_zoom = False
        # self.is_y_pressed = False
        self.curr_viewport = []
        
        # self.copied_annotation = None
        
        self.selected_indices = []
        self.multiselect_on = False
        
        # # Submenu for listing all segannotations
        # self.boxlist = None
        # self.buttons = []
        # self.entry_counter = None
        
        # self.w1 = None
        # self.w3, w4 = None, None
        # self.set_iou = 0.1
        # self.set_conf = 0.7
        # self.translate_step_size = 0.0025
        
        self.image_resized = None
        self.image_np_orig = None
        
        # ---------- Initial Main Window ----------
        if caller_root == None:
            self.root = tk.Tk()
        else:
            self.root = tk.Toplevel(caller_root)
        
        self.root.title("Segmentation Application")
        self.root.geometry("1000x1000")
        self.root.minsize(750, 900)
        self.root.iconbitmap('MUL-logo.ico')
        
        self.number = tk.StringVar(value="0")  
        self.CLASS_HANDLER = ClassHandler(self)
        self.CLASS_HANDLER.load_class_names()
        
        self.IMG_HANDLER = ImageHandler(self)
        self.GUI = UserInterface(self)
        self.MENU_BAR = MenuBar(self)
        
    
    
        self.root.mainloop()
        
    def exit_app(self):
        self.root.destroy()

    # ---------- Space for Functions  ----------
    
    def update_display(self, highlight_idx = None):
        highlight_idx = self.selected_mask_idx
        
        #global tk_image, image, last_zoom_factor, image_resized, image_np_orig, multiselect_on, selected_indices, zoom_factor, view_offset_x, view_offset_y, coordinates, manual_polygon, colors, do_zoom, points_array,points, manual_mode, curr_viewport
        
        #* Unterer Block kommt in die Zoom funktion
        #* if self.zoom_factor is not self.last_zoom_factor:
        #     self.image_resized = self.image.resize((int(self.image.width * self.zoom_factor), int(self.image.height * self.zoom_factor)), Image.NEAREST)
        #     self.image_np_orig = np.array(self.image_resized)    
        
        image_np = copy.deepcopy(self.image_np_orig)
        
        
        for idx, mask_data in enumerate(self.annotations):
            mask_class, *self.coordinates = mask_data
            color = (255, 255, 0) if idx == highlight_idx else self.colors[mask_class]
            if idx in self.selected_indices:
                color = (255, 255, 0) 
            self.points = np.array(
                [(int(self.coordinates[i] * self.image.width * self.zoom_factor),
                  int(self.coordinates[i + 1] * self.image.height * self.zoom_factor))
                 for i in range(0, len(self.coordinates), 2)], dtype=np.int32)
            cv2.polylines(image_np, [self.points], isClosed=True, color=color, thickness=1)
            
            if idx == highlight_idx and not self.multiselect_on:
                for idx, point in enumerate(self.points):
                    if idx is self.selected_point_idx:
                        cv2.circle(image_np, tuple(point), 5, [255, 0, 0], 1)
                    else:
                        cv2.circle(image_np, tuple(point), 5, [0, 0, 0], 1)
        
                        
        if self.manual_mode:    
            modified_points = [(x * self.image.width * self.zoom_factor, y * self.image.height * self.zoom_factor) for (x, y) in self.manual_polygon]
            self.points_array = np.array(modified_points, np.int32)  # Ensure the points are integers
            cv2.polylines(image_np, [self.points_array], isClosed=False, color=[255, 255, 0], thickness=1)
        
    
        
        
        # Extract the visible region from image_np
        viewport_x, viewport_y = int(abs(self.view_offset_x)), int(abs(self.view_offset_y))  # Example offsets
        viewport_width, viewport_height = 640, 640  # Example viewport size
        visible_region = image_np[viewport_y:viewport_y + viewport_height, viewport_x:viewport_x + viewport_width]               
        image_np = visible_region.astype('uint8')  # Ensure dtype is uint8       
        
        blended_pil = Image.fromarray(image_np)  
        self.curr_viewport = blended_pil
        
        self.tk_image = ImageTk.PhotoImage(blended_pil)
        vx = 0
        vy = 0
        if self.view_offset_x > 0:
            vx = self.view_offset_x
        if self.view_offset_y > 0:
            vy = self.view_offset_y
        
        img_width, img_height = blended_pil.size   # size of the current PIL image
        self.canvas.config(width=img_width, height=img_height)
        self.canvas.delete("all")
        self.canvas.create_image(vx, vy, anchor=tk.NW, image=self.tk_image)
        #canvas.create_image(view_offset_x, view_offset_y, anchor=tk.NW, image=tk_image)
        #self.do_zoom = False
        
        self.canvas.image = self.tk_image
        #* fill_archive()
        
        #* try:
        #     refresh_boxlist()
        # except:
        #     pass
        
        self.last_zoom_factor = self.zoom_factor
        #print("Time:", time.time() - start_time)

    
    
# Main function to browse and annotate images
def initialize_seg_app():
    SEG_APP = SEG_App()

if __name__ == "__main__":
    initialize_seg_app()
