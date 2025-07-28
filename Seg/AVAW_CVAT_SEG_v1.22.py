# updates:
    # -implementation of context_menu:  with right click and y-button pressed
    #       context_menu_mask_not_selected:
    #               -undo
    #               -reset_zoom
    #               -save_annotations
    #       context_menu_mask_selectedf:
    #               -delete_mask
    #               -change classnames

import tkinter as tk
from tkinter import ttk
from tkinter import ALL  # Import ALL for scaling
from tkinter import messagebox, Message, filedialog, Checkbutton, Scale
import tkinter.messagebox as messagebox  # Make sure this is imported
from PIL import Image, ImageTk
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

# Global variables
annotations = []  # Each entry is [class_id, x1, y1, x2, y2, ..., xn, yn]
annotations_folder = None
last_annotations = None
archive = []
selected_mask_idx = None
selected_point_idx = None
selected_class = 0
manual_mode = False
manual_polygon = []
new_mask_mode = False
zoom_factor = 1.0
view_offset_x = 0
view_offset_y = 0
start_pan_x = 0
start_pan_y = 0
start_x, start_y = 0, 0
image_paths = []
curr_image_index = 0
threshold = 0.000
files_folder = "files"
class_names = []
colors = []
nUndoes = 100
mask_dragging = False
image_dragging = False
undoing = False
number = None
do_zoom = False
is_y_pressed = False
curr_viewport = []

copied_annotation = None

selected_indices = []
multiselect_on = False

# Submenu for listing all segannotations
boxlist = None
buttons = []
entry_counter = None

w1 = None
w3, w4 = None, None
set_iou = 0.1
set_conf = 0.7
translate_step_size = 0.0025

last_zoom_factor = 1
image_resized = None
image_np_orig = None

def initialize_app(image_path, model_path):
    global root, canvas, tk_image, original_image, image, model, class_dropdown, colors, number, title_label, w1, is_y_pressed, context_menu_mask_not_selected, context_menu_mask_selected

    root = tk.Tk()
    root.title("FastSAM Segmentation App")    
    root.geometry("900x900")
    # Add MUL Logo to title bar
    try:
        p1 = tk.PhotoImage(file = 'files/logo.png') 
        root.iconphoto(False,p1)
    except:
        print("No Custom Logo Found - Using TKinter Standard")
    
    # Create Menu Bar on Window    
    add_menu_bar(root)
    
    # Retrieve image paths and load the first image
    getImagePaths()
    title = Path(image_paths[0]).stem
    title_label = tk.Label(root, text=title, font=("Helvetica", 16))
    
    load_image()
      
    
    title_label.pack(pady=10)  # Add some vertical padding
        
    # Load the model
    model = load_model(model_path)
    
    # Set up canvas
    canvas = tk.Canvas(root, width=image.width, height=image.height)  
    canvas.create_image(0, 0, anchor=tk.N, image=tk_image)
    canvas.pack(side="top")
    
    # Load Class Names
    load_class_names()        
    
   
    
    # Define the colors used in the app
    generate_colors(len(class_names))

    # ===== BOTTOM CONTROLS LAYOUT =====
    
    # Master bottom frame
    bottom_frame = tk.Frame(root)
    bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
    
    # ===== SOUTHWEST FRAME: Undo Button Only =====
    undo_frame = tk.Frame(bottom_frame)
    undo_frame.pack(side=tk.BOTTOM, anchor="sw", padx=10, pady=5)
    
    undo_button = tk.Button(undo_frame, text="Undo", command=undo)
    undo_button.pack()
    
    # --- Left Section: Undo + Previous ---
    left_frame = tk.Frame(bottom_frame)
    left_frame.pack(side=tk.LEFT, padx=10)
        
    prev_button = tk.Button(left_frame, text="Previous", command=previous_image)
    prev_button.pack(side=tk.LEFT, padx=5)
    
    # --- Center Section: Dropdown + Action Buttons ---
    center_frame = tk.Frame(bottom_frame)
    center_frame.pack(side=tk.LEFT, expand=True)
    
    # Dropdown to select class
    class_dropdown = ttk.Combobox(center_frame, values=[str(i) for i in class_names], state="readonly", justify="center")
    class_dropdown.current(0)
    class_dropdown.bind("<<ComboboxSelected>>", update_class)
    class_dropdown.pack(pady=2)
    
    # Segment Whole Image Button
    segment_button = tk.Button(center_frame, text="Segment Image", command=segment_whole_image)
    segment_button.pack(pady=2)
    
    # Simplify Whole Image Button
    simplify_button = tk.Button(center_frame, text="Simplify Annotations Image", command=simplify_annotations)
    simplify_button.pack(pady=2)
    
    # Save Button
    save_button = tk.Button(center_frame, text="Save Annotations of current Image", command=save_annotations)
    save_button.pack(pady=2)
    
    # Jump To Image Button + numeric input
    jump_button = tk.Button(center_frame, text="Jump To Image", command=jump_to_image)
    jump_button.pack(pady=2)
    
    number = tk.StringVar(value="0")
    index_counter = tk.Entry(center_frame, textvariable=number, justify="center")
    index_counter.pack(pady=2)
    
    # --- Right Section: Next Button ---
    right_frame = tk.Frame(bottom_frame)
    right_frame.pack(side=tk.RIGHT, padx=10)
    
    next_button = tk.Button(right_frame, text="Next", command=next_image)
    next_button.pack()
    
    # ===== END BOTTOM CONTROLS =====

           
    
    
    
    
    
    # Bindings for user actions
    canvas.bind("<Button-1>", on_click)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    canvas.bind("<MouseWheel>", on_mousewheel)
    
    canvas.bind("<Control-Button-1>", multiselect)
    canvas.bind("<Control-Button-3>", stop_multiselect)
    
    # canvas.bind("<ButtonRelease-3>", stop_image_drag)  # Middle button release (Windows/macOS)
    
    canvas.bind("<Button-2>", on_click)  # Middle button to start panning
    canvas.bind("<B2-Motion>", drag_mask)
    canvas.bind("<ButtonRelease-2>", on_release)
    
    #bind right click for paning
    canvas.bind("<Button-3>", start_pan)  # Middle button to start panning
    canvas.bind("<B3-Motion>", do_pan)
    canvas.bind("<ButtonRelease-3>", release_pan)
    
    root.bind("<Right>", next_image)
    root.bind("<Left>", previous_image)
    root.bind("<n>", toggle_new_mask_mode)
    root.bind("<m>", toggle_manual_mode)
    root.bind("<Delete>", delete_mask)
    root.bind("<BackSpace>", delete_vertex)
    root.bind("<d>",simplify_mask)
    root.bind("<Insert>", add_vertex)
    root.bind("<i>", add_vertex)
    root.bind("<s>", save_annotations)
    root.bind("<Up>", save_annotations)
    root.bind("c", copy_annotation)
    root.bind("v", paste_annotation)
    root.bind("u",save_current_view)
    root.bind("<Return>",jump_to_image)
    root.bind("q",merge_annotations)
    root.bind("a",select_all)
    
    # Translate Annotations
    root.bind("2",translate_down)
    root.bind("8",translate_up)
    root.bind("6",translate_right)
    root.bind("4",translate_left)
    
    #Bind the Y key press and release events to the root window
    root.bind("<KeyPress-y>", y_key_press)
    root.bind("<KeyRelease-y>", y_key_release)
    
    root.bind("<F1>",show_help)
    root.bind("<F2>",show_boxlist)
    
    # Create Drop Down Menu at Cursor when box is not selected
    context_menu_mask_not_selected = tk.Menu(root, tearoff=0)
    context_menu_mask_not_selected.add_command(label="Undo", command=undo)
    context_menu_mask_not_selected.add_command(label="Save Annotations", command=save_annotations)  
    context_menu_mask_not_selected.add_command(label="Reset zoom", command=reset_zoom)
    
    # Add a "File" menu to the main menu
    global_menu = tk.Menu(context_menu_mask_not_selected, tearoff=0)
    
    # Create a "change_all_classes_menu" submenu under "global_menu"
    change_all_classes_menu = tk.Menu(global_menu, tearoff=0)
    for idx, class_name in enumerate(class_names):
        change_all_classes_menu.add_command(label=class_name, command=lambda i=idx: change_all_classes_from_context_menu(i))
    
    # Add "change_all_classes_menu" submenu to the "global_menu" menu
    global_menu.add_cascade(label="Change All Classes To:", menu=change_all_classes_menu)
    global_menu.add_command(label="Clear Annotations", command=clear_annotations)
    global_menu.add_command(label="Copy Annotations", command=copy_annotations)
    global_menu.add_command(label="Paste Annotations", command=paste_annotations)
    global_menu.add_command(label="Add Annotations", command=add_annotations)
    
    # Add "Global" menu to the main menu
    context_menu_mask_not_selected.add_cascade(label="Global", menu=global_menu)
    
    # Create Drop Down Menu at Cursor when box is selected
    context_menu_mask_selected = tk.Menu(root, tearoff=0)
    context_menu_mask_selected.add_command(label="Delete Mask", command=delete_mask)
    for idx, class_name in enumerate(class_names):
        context_menu_mask_selected.add_command(label=class_name, command=lambda i=idx: change_class_from_context_menu(i))

    update_display()
    
    root.mainloop()

def select_all(event=None):
    global selected_indices, multiselect_on
    multiselect_on = True
    selected_indices = []
    for idx,_ in enumerate(annotations):
        selected_indices.append(idx)
    update_display()     

def add_annotations(event=None):
    global annotations, last_annotations
    if last_annotations is None:
        tk.messagebox.showinfo("showinfo", "Nothing To Paste") 
        return
    annotations.extend(last_annotations)
    update_display()    
    
def copy_annotations(event=None):
    global annotations, last_annotations
    last_annotations = copy.deepcopy(annotations)
    update_display()

def paste_annotations(event=None):
    global annotations, last_annotations
    if last_annotations is None:
        tk.messagebox.showinfo("showinfo", "Nothing To Paste") 
        return
    annotations = copy.deepcopy(last_annotations)
    update_display()

def clear_annotations(event=None):
    global annotations
    annotations = []
    update_display()

def copy_annotation(event=None):
    global annotations, copied_annotation, selected_mask_idx, multiselect_on
    copied_annotation = []
    if multiselect_on:      
        for idx in selected_indices:
            copied_annotation.append(annotations[idx])        
    else:
        copied_annotation.append(annotations[selected_mask_idx])

def merge_annotations(event=None):
    global annotations, copied_annotation, selected_mask_idx, multiselect_on
    
    if len(selected_indices) < 2:
        print("Select at least two masks")
        return
    
    class_id = annotations[selected_indices[0]][0]
    polygons = []
    to_merge = []
    for idx in selected_indices:
        to_merge.append(annotations[idx])
    for ann in to_merge:
        coords = list(zip(ann[1::2], ann[2::2]))
        poly = Polygon(coords)
        if not poly.is_valid or poly.area == 0:
            continue
        polygons.append(poly)
        
    if not polygons:
        return []
    
    merged = unary_union(polygons)
    # If result is MultiPolygon, take outer boundary of union
    if merged.geom_type == 'MultiPolygon':
        merged = merged.convex_hull  # alternative: merged = merged.buffer(0)
    elif merged.geom_type == 'Polygon':
        merged = merged.exterior
    merged_coords = list(merged.coords)
    flat = [class_id] + [coord for point in merged_coords for coord in point]
    annotations.append(flat)    
    
    for idx in sorted(selected_indices,reverse=True):
        del annotations[idx]
    
    update_display(None)

def paste_annotation(event=None):
    global annotations, copied_annotation, selected_point_idx
    for entry in copied_annotation:
        annotations.append(copy.deepcopy(entry))
    
    if len(copied_annotation) == 1:
        selected_point_idx = 0
        update_display(len(annotations)-1)
    else:
        selected_point_idx = None
        update_display(None)
        

def translate_down(event=None):
    global annotations, translate_step_size, multiselect_on, selected_indices
    
    if multiselect_on:
        for idx in selected_indices:
            annotation = annotations[idx]
            for i in range(2, len(annotation), 2):
                annotation[i] += translate_step_size
                if annotation[i] > 1:
                    annotation[i] = 1
            if np.mean(annotation[2::2]) == 1:
                del annotations[idx]
    
    if not multiselect_on and selected_mask_idx is None:
        for idx, annotation in enumerate(annotations):                 
            for i in range(2, len(annotation), 2):
                annotation[i] += translate_step_size
                if annotation[i] > 1:
                    annotation[i] = 1
            if np.mean(annotation[2::2]) == 1:
                del annotations[idx]
        
    if not multiselect_on and selected_mask_idx is not None:
        annotation = annotations[selected_mask_idx]
        for i in range(2, len(annotation), 2):
            annotation[i] += translate_step_size
            if annotation[i] > 1:
                annotation[i] = 1
        if np.mean(annotation[2::2]) == 1:
            del annotations[idx]
        
    update_display(selected_mask_idx)

def translate_up(event=None):
    global annotations, translate_step_size, multiselect_on, selected_indices, selected_mask_idx
    
    if multiselect_on:
        for idx in selected_indices:
            annotation = annotations[idx]
            for i in range(2, len(annotation), 2):
                annotation[i] -= translate_step_size
                if annotation[i] <= 0:
                    annotation[i] = 0
            if np.mean(annotation[2::2]) == 0:
                del annotations[idx]
    
    if not multiselect_on and selected_mask_idx is None:
        for idx, annotation in enumerate(annotations):                 
            for i in range(2, len(annotation), 2):
                annotation[i] -= translate_step_size
                if annotation[i] <= 0:
                    annotation[i] = 0
            if np.mean(annotation[2::2]) == 0:
                del annotations[idx]
                
    if not multiselect_on and selected_mask_idx is not None:
        annotation = annotations[selected_mask_idx]
        for i in range(2, len(annotation), 2):
            annotation[i] -= translate_step_size
            if annotation[i] <= 0:
                annotation[i] = 0
        if np.mean(annotation[2::2]) == 0:
            del annotations[idx]
        
    update_display(selected_mask_idx)

def translate_right(event=None):
    global annotations, translate_step_size, multiselect_on, selected_indices
    
    if multiselect_on:
        for idx in selected_indices:
            annotation = annotations[idx]
            for i in range(1, len(annotation), 2):
                annotation[i] += translate_step_size
                if annotation[i] > 1:
                    annotation[i] = 1
            if np.mean(annotation[1::2]) == 1:
                del annotations[idx]
    
    if not multiselect_on and selected_mask_idx is None:
        for idx, annotation in enumerate(annotations):                 
            for i in range(1, len(annotation), 2):
                annotation[i] += translate_step_size
                if annotation[i] > 1:
                    annotation[i] = 1
            if np.mean(annotation[1::2]) == 1:
                del annotations[idx]
    
    if not multiselect_on and selected_mask_idx is not None:
        annotation = annotations[selected_mask_idx]
        for i in range(1, len(annotation), 2):
            annotation[i] += translate_step_size
            if annotation[i] > 1:
                annotation[i] = 1
        if np.mean(annotation[1::2]) == 1:
            del annotations[idx]
        
    update_display(selected_mask_idx)    
    
    
def translate_left(event=None):
    global annotations, translate_step_size, multiselect_on, selected_indices, selected_mask_idx
    
    if multiselect_on:
        for idx in selected_indices:
            annotation = annotations[idx]
            for i in range(1, len(annotation), 2):
                annotation[i] -= translate_step_size
                if annotation[i] <= 0:
                    annotation[i] = 0
            if np.mean(annotation[1::2]) == 0:
                del annotations[idx]
    
    if not multiselect_on and selected_mask_idx is None:
        for idx, annotation in enumerate(annotations):                 
            for i in range(1, len(annotation), 2):
                annotation[i] -= translate_step_size
                if annotation[i] <= 0:
                    annotation[i] = 0
            if np.mean(annotation[1::2]) == 0:
                del annotations[idx]
                
    if not multiselect_on and selected_mask_idx is not None:
        annotation = annotations[selected_mask_idx]
        for i in range(1, len(annotation), 2):
            annotation[i] -= translate_step_size
            if annotation[i] <= 0:
                annotation[i] = 0
        if np.mean(annotation[1::2]) == 0:
            del annotations[idx]
        
    update_display(selected_mask_idx) 
        
        
def change_all_classes_from_context_menu(index):
    global annotations
    for annotation in annotations:
        annotation[0] = index
        update_display()
    
def change_class_from_context_menu(index):
    global selected_mask_idx, buttons, multiselect_on, selected_indices
    
    if multiselect_on:
        for idx in selected_indices:
            annotations[idx][0] = index
        if buttons:
            buttons[selected_mask_idx].config(text="Box "+str(selected_mask_idx)+" "+class_names[index])
        stop_multiselect()
        update_display()
        return 
    
    annotations[selected_mask_idx][0] = index
    if buttons:
        buttons[selected_mask_idx].config(text="Box "+str(selected_mask_idx)+" "+class_names[index])
    #is_y_pressed.set(False)
    update_display()    
    
# Function to update the class of the selected bounding box
def update_class(event):    
    global selected_mask_idx, annotations, class_dropdown, selected_class, buttons, multiselect_on  
    new_class = int(class_names.index(class_dropdown.get()))
    selected_class = new_class
    
    if multiselect_on:
        for idx in selected_indices:
            annotations[idx][0] = new_class
        update_display()
        stop_multiselect()
        return
    
    if selected_mask_idx is not None:      
        annotations[selected_mask_idx][0] = new_class 
        update_display(selected_mask_idx)
        buttons[selected_mask_idx].config(text="Box "+str(selected_mask_idx)+" "+class_names[new_class])



def is_valid_model(model):
    """Try a dummy forward pass to validate model."""
    try:
        # Dummy input: a black image (640x640)
        dummy = np.zeros((640, 640, 3), dtype=np.uint8)
        _ = model(dummy)
        return True
    except Exception:
        return False

def load_model(model_path):
    """Try loading the model using YOLO, FastSAM, or SAM."""
    error_messages = []

    try:
        model = YOLO(model_path)
        if is_valid_model(model):
            messagebox.showinfo("Model Loaded", f"Loaded model from:\n{model_path}")
            generate_colors(len(model.names))
            return model
        else:
            error_messages.append("YOLO loaded, but forward pass failed.")
    except Exception as e:
        error_messages.append(f"YOLO failed: {e}")

    try:
        model = FastSAM(model_path)
        if is_valid_model(model):
            messagebox.showinfo("Model Loaded", f"Loaded model from:\n{model_path}")
            return model
        else:
            error_messages.append("FastSAM loaded, but forward pass failed.")
    except Exception as e:
        error_messages.append(f"FastSAM failed: {e}")

    try:
        model = SAM(model_path)
        if is_valid_model(model):
            messagebox.showinfo("Model Loaded", f"Loaded model from:\n{model_path}")
            return model
        else:
            error_messages.append("SAM loaded, but forward pass failed.")
    except Exception as e:
        error_messages.append(f"SAM failed: {e}")

    messagebox.showerror("Model Load Failed", f"Could not load a valid model.\n\n" + "\n".join(error_messages))
    return None

def load_class_names():
    global class_names
    class_names_path = os.path.join(os.getcwd(),files_folder,"class_names.txt")
    
    if os.path.exists(class_names_path):
        with open(class_names_path, 'r') as file:
            class_names[:1]=(file.read().strip().split(','))  # Read the entire file content      
        generate_colors(len(class_names))
    else: 
        print('Could not find class_names.txt in files Folder! Using Default Class Names')
        class_names = ["Class 1", "Class 2"]

def getImagePaths(folder_dir = "Images"):
    global image_paths    
    image_extensions = ['.png', '.jpg', '.jpeg']
    image_paths = [os.path.join(folder_dir, f) for f in os.listdir(folder_dir) 
                   if os.path.splitext(f)[1].lower() in image_extensions]
    if not image_paths:
        print("No images found in the folder!")



def generate_colors(n):
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
    n = 80
    # Repeat colors if more are needed, but preserve order
    colors = [base_colors[i % len(base_colors)] for i in range(n)]



def edit_class_names_window():
    def save_changes():
        global class_names, class_dropdown  # if needed
        input_text = text_input.get("1.0", tk.END).strip()
        if input_text:
            class_names[:] = [name.strip() for name in input_text.split(',') if name.strip()]
            messagebox.showinfo("Success", "Class names updated!")
            if class_dropdown:
                class_dropdown.configure(values=class_names)
                class_dropdown.current(0)
            window.destroy()
            generate_colors(len(class_names))
        else:
            messagebox.showwarning("Empty Input", "Class names cannot be empty.")

    window = tk.Toplevel()
    window.title("Edit Class Names")
    window.geometry("400x200")
    window.grab_set()  # make window modal

    label = tk.Label(window, text="Edit class names (comma-separated):")
    label.pack(pady=10)

    text_input = tk.Text(window, height=4, width=40)
    text_input.pack(padx=10)
    text_input.insert(tk.END, ", ".join(class_names))  # Show current class names

    save_button = tk.Button(window, text="Save", command=save_changes)
    save_button.pack(pady=10)

def load_new_class_name_list():
    global class_names, class_dropdown
    filepath = filedialog.askopenfilename()
    print(filepath)
    if os.path.exists(filepath):
        class_names = []
        with open(filepath, 'r') as file:
            class_names[:1]=(file.read().strip().split(','))  # Read the entire file content      
        print("Class Names Changed")
        
        # Update Class Dropdown Menu
        class_dropdown.configure(values=[str(i) for i in class_names])
        class_dropdown.current(0)
    else: 
        print('Could not find class_names.txt in files Folder! Using Default Class Names')
        class_names = ["Class 1", "Class 2"]


def set_annotations_folder():
    global annotations_folder
    annotations_folder = filedialog.askdirectory(title="Select Annotations Directory")
    load_yolo_segmentation()
    
    load_image()
    reset_zoom()
    update_display()

def add_menu_bar(root):    
    # Adding a 'File' menu to the menu bar
    menu_bar = tk.Menu(root)
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Load Images", command=select_image_dir)
    file_menu.add_command(label="Load Model", command=load_new_model)
    file_menu.add_command(label="Load Class Name List", command=load_new_class_name_list)
    file_menu.add_command(label="Load Annotations from different Folder", command=set_annotations_folder)
    file_menu.add_command(label="Save Annotation", command=save_annotations)
    file_menu.add_separator()  # Adds a separator line
    file_menu.add_command(label="Exit", command=exit_app)
    # Add the File menu to the menu bar
    menu_bar.add_cascade(label="File", menu=file_menu)
    
    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(label="Controls", command=show_help)
    help_menu.add_command(label="Ultralytics", command=open_ultralytics_webpage)
    menu_bar.add_cascade(label="Help",menu=help_menu)
    
    view_menu = tk.Menu(menu_bar, tearoff=0)
    view_menu.add_command(label="Annotations List", command=show_boxlist)
    view_menu.add_command(label="Reset Zoom", command=reset_zoom)
    menu_bar.add_cascade(label="View",menu=view_menu)
    
    global_menu = tk.Menu(menu_bar, tearoff=0)
    global_menu.add_command(label="Set Vertex Threshold", command=set_vertex_threshold)
    global_menu.add_command(label="Delete Duplicaties", command=delete_duplicates)
    global_menu.add_command(label="Delete Contained Polygons", command=delete_contained_polygons)
    global_menu.add_command(label="Define Translation Stepsize", command=define_translation_speed)
    global_menu.add_command(label="Alter Class Names", command=edit_class_names_window)
    menu_bar.add_cascade(label="Global",menu=global_menu)
    
    model_menu = tk.Menu(menu_bar, tearoff=0)
    model_menu.add_command(label="Change Model Setting", command=show_model_settings)
    #view_menu.add_command(label="Reset Zoom", command=reset_zoom)
    menu_bar.add_cascade(label="Model",menu=model_menu)
    
    # Display the menu bar
    root.config(menu=menu_bar)

def define_translation_speed():
    global translate_step_size
    
    def update_translation_speed(value):
        global translate_step_size
        translate_step_size = float(value)
        translation_label.config(text=f"Translation Step Size: {translate_step_size:.2f}")
    
    # Create a new tkinter window
    translation_window = tk.Toplevel()
    translation_window.title("Translation Step Size")
        
    # Create a scale widget
    scale = tk.Scale(translation_window, from_=0.001, to=0.01, resolution=0.001, orient=tk.HORIZONTAL, 
                     length=400, command=update_translation_speed)
    scale.pack(pady=20)
    
    # Create a label to display the current threshold value
    translation_label = tk.Label(translation_window, text=f"Translation Step Size: {translate_step_size:.2f}")
    translation_label.pack()
    
    # Set the initial threshold value
    scale.set(translate_step_size)
    translation_label.config(text=f"Translation Step Size: {translate_step_size:.2f}")

def show_model_settings():
    global w3, w4
    model_window = tk.Toplevel(root)
    model_window.title("Model Setting")
    model_window.geometry("400x400")      
    
    p1 = tk.PhotoImage(file = 'files/logo.png') 
    model_window.iconphoto(False,p1)
    
    w3 = Scale(model_window, from_=0, to=1, tickinterval=0.1, resolution = 0.1, orient=tk.HORIZONTAL, command=change_conf, length = 300, label="Set Min Confidence", font=("TkDefaultFont", 10))
    w3.set(set_conf)
    w3.pack()
    
    w4 = Scale(model_window, from_=0, to=1,tickinterval=0.1, resolution = 0.1, orient=tk.HORIZONTAL, command=change_IoU, length = 300, label="Set IoU",font=("TkDefaultFont", 10))
    w4.set(set_iou)
    w4.pack()

def change_conf(event=None):
    global w3, set_conf
    set_conf = w3.get()

def change_IoU(event=None):
    global w4, set_iou
    set_iou = w4.get()

def delete_duplicates(event=None):
    global annotations
    len_old = len(annotations)
    annotations = list(map(list, set(map(tuple, annotations))))
    len_new = len(annotations)
    diff = len_old - len_new
    refresh_boxlist()
    messagebox.showinfo("Information", "Found and Deleted "+str(diff)+" duplicates")
    
def set_vertex_threshold(event=None):
    global threshold
    
    def update_threshold(value):
        global threshold
        threshold = float(value)
        threshold_label.config(text=f"Threshold: {threshold:.2f}")
    
    # Create a new tkinter window
    threshold_window = tk.Toplevel()
    threshold_window.title("Vertex Distance Threshold")
    threshold_window.bind("<d>",simplify_mask)
    
    # Create a scale widget
    scale = tk.Scale(threshold_window, from_=0, to=0.01, resolution=0.001, orient=tk.HORIZONTAL, 
                     length=400, command=update_threshold)
    scale.pack(pady=20)
    
    # Create a label to display the current threshold value
    threshold_label = tk.Label(threshold_window, text="Threshold: 0.00")
    threshold_label.pack()
    
    # Set the initial threshold value
    scale.set(threshold)
    threshold_label.config(text=f"Threshold: {threshold:.2f}")
    

def open_ultralytics_webpage():
    #webbrowser.open("www.gidf.at")
    try:
        webbrowser.open("https://docs.ultralytics.com/models/fast-sam/")
    except:
        webbrowser.open("www.google.com")
    else:
        print("No Webbrowser Found")

def select_image_dir():
    global curr_image_index, annotations_folder
    annotations_folder = None
    directory = filedialog.askdirectory(title="Select Directory")
    getImagePaths(directory)
    curr_image_index = 0
    load_image()
    reset_zoom()
    update_display()    

def load_new_model():
    global model
    model_path = filedialog.askopenfilename(title="Select Model")
    model = load_model(model_path)    

def exit_app():
    global root
    root.destroy()      

def show_help(event=None):
    # Display a message box with a help message
    help_path = "files/help.txt"
    
    if os.path.exists(help_path):
        with open(help_path, "r") as file:
            help_content = file.read()
    else:
        help_content = "Help file not found. Please check the files folder for help.txt."                  
    
    messagebox.showinfo("Help", help_content)

def show_boxlist(event=None):
    global annotations, buttons, scrollable_frame, boxlist, entry_counter
    buttons = []
    # Create a new Toplevel window for the box list
    boxlist = tk.Toplevel(root)
    boxlist.title("Boxlist")
    boxlist.geometry("200x600")
    
    p1 = tk.PhotoImage(file = 'files/logo.png') 
    boxlist.iconphoto(False,p1)
        
    # Show how many Segments there are in the image
    #
    
    # Bind Buttons
    boxlist.bind("<Delete>", delete_mask)
    boxlist.bind("<c>", copy_annotation)
    boxlist.bind("<v>", paste_annotation)
    
    # Create a canvas and scrollbar
    canvas = tk.Canvas(boxlist, width=180, height=600, borderwidth=0)
    scrollbar = tk.Scrollbar(boxlist, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    # Configure the scrollbar with the canvas
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack the canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    entry_counter = Message(scrollable_frame, text="Objects in Image: "+str(len(annotations)),width=600)
    entry_counter.pack()

    # Add buttons to the scrollable frame    
    for i in range(len(annotations)):
        color_hex = rgb2hex(colors[annotations[i][0]])
        box_class = annotations[i][0]
        if i == selected_mask_idx:
            color_hex = "yellow"
        box_class_name = class_names[box_class]
        btn = tk.Button(scrollable_frame, text=f"Box {i} "+box_class_name, bg=color_hex, command=lambda i=i: set_selectedBox(i))
        buttons.append(btn)
        btn.pack(pady=2, padx=10, fill="x")        

def close_boxlist():
    global boxlist
    try:
        boxlist.destroy()
    except:
        pass
            

def set_selectedBox(index):
    global selected_mask_idx, buttons
    selected_mask_idx = index;
    refresh_boxlist()
    update_display(selected_mask_idx)

def refresh_boxlist():
    global selected_mask_idx, buttons, scrollable_frame, annotations
    
    if len(annotations) != len(buttons):
        buttons = []
        for widget in scrollable_frame.winfo_children():
            widget.destroy()  # deleting widget
        entry_counter = Message(scrollable_frame, text="Objects in Image: "+str(len(annotations)),width=600)
        entry_counter.pack()
        for i in range(len(annotations)):
            color_hex = rgb2hex(colors[annotations[i][0]])
            box_class = annotations[i][0]
            box_class_name = class_names[box_class]
            btn = tk.Button(scrollable_frame, text=f"Box {i} "+box_class_name, bg=color_hex, command=lambda i=i: set_selectedBox(i))
            btn.pack(pady=2, padx=10, fill="x")   
            buttons.append(btn)      
    
    
    for idx, button in enumerate(buttons):
        if idx == selected_mask_idx:
            button.config(bg="yellow")
        else:
            color_hex = rgb2hex(colors[annotations[idx][0]])
            button.config(bg=color_hex)   
        

def rgb2hex(rgb):
      return "#%02x%02x%02x" % (rgb[0], rgb[1], rgb[2])

    
def jump_to_image(event=None):
    global number, curr_image_index
    print(int(number.get()))
    jump_index = int(number.get())
    if jump_index < len(image_paths) and jump_index >= 0:
        number.set(jump_index)
        curr_image_index = jump_index
        load_image()
        reset_zoom()
        #update_display()
    else:
        print("Selected Image index needs to be between 0 and "+str(len(image_paths)-1))

def undo(event=None):
    global annotations, archive, selected_mask_idx, undoing
    
    if len(archive) > 1:
        # Remove the current state and revert to the previous one
        archive.pop()
        annotations = copy.deepcopy(archive[-1])  # Revert to the previous state
        update_display()
    else:
        print("Nothing to undo")

def drag_mask(event):
    global start_x, start_y, annotations, selected_mask_idx, dx, dy, mask_dragging, image_dragging, zoom_factor, selected_indices, multiselect_on
    if selected_mask_idx is not None and mask_dragging:
        mask_dragging = True
        dx = (event.x - start_x)/image.width/zoom_factor
        dy = (event.y - start_y)/image.height/zoom_factor
        
        if not multiselect_on:
            curr_mask = annotations[selected_mask_idx]
            curr_mask[1::2] = [xValues + dx for xValues in curr_mask[1::2]]
            curr_mask[2::2] = [yValues + dy for yValues in curr_mask[2::2]]
            annotations[selected_mask_idx] = curr_mask
            update_display()
            start_x, start_y = event.x, event.y
        
        if multiselect_on:
            cleaned_list = [item for item in selected_indices if item is not None]
            for idx in cleaned_list:
                curr_mask = annotations[idx]
                curr_mask[1::2] = [xValues + dx for xValues in curr_mask[1::2]]
                curr_mask[2::2] = [yValues + dy for yValues in curr_mask[2::2]]
                annotations[idx] = curr_mask
                update_display()
            start_x, start_y = event.x, event.y


def add_vertex(event):
    global selected_mask_idx, selected_point_idx
    
    if selected_mask_idx is not None and selected_point_idx is not None:
        new_mask = annotations[selected_mask_idx]
        x1 = new_mask[1 + selected_point_idx * 2]
        y1 = new_mask[2 + selected_point_idx * 2]
        if 3 + selected_point_idx * 2 < len(new_mask):
            x2 = new_mask[3 + selected_point_idx * 2]  
            y2 = new_mask[4 + selected_point_idx * 2]
        else:
            x2 = new_mask[1]
            y2 = new_mask[2]
            
        xNew = x1 + (x2-x1)/2
        yNew = y1 + (y2-y1)/2
        new_mask.insert(3 + selected_point_idx * 2, xNew)
        new_mask.insert(4 + selected_point_idx * 2, yNew)
        annotations[selected_mask_idx] = new_mask
        update_display(highlight_idx=selected_mask_idx)

def toggle_new_mask_mode(event=None):
    global new_mask_mode
    new_mask_mode = True
    print("New mask creation mode activated.")

def toggle_manual_mode(event=None):
    global manual_mode, manual_polygon
    manual_mode = not manual_mode
    manual_polygon = []
    print("Manual polygon "+str(manual_mode))

def on_click(event):
    global a,selected_mask_idx, selected_point_idx, new_mask_mode, manual_polygon, manual_mode, selected_class, start_x, start_y, image_dragging, mask_dragging
    
    
    # Adjust for zoom and pan offsets
    x, y = (event.x - view_offset_x) / zoom_factor, (event.y - view_offset_y) / zoom_factor
    
    start_x, start_y = event.x, event.y
    
    print(f"Clicked at: ({x}, {y})")
    
    if event.num == 2:
        start_x, start_y = event.x, event.y
        if selected_mask_idx is not None:
            mask_dragging = True
    
        
    elif new_mask_mode:
        stop_multiselect()
        print("new_mask_mode")
        polygon_class, polygon = perform_segmentation(x, y)
        if polygon_class is not None:
            a = polygon_class
            class_label = polygon_class
            annotations.append([class_label] + polygon)
            update_display()
        new_mask_mode = False

    elif manual_mode:
        stop_multiselect()
        print("manual_mode")
        manual_polygon.append([x / image.width, y / image.height])
        update_display()

    else:
        stop_multiselect()
        print("select_mode")
        # Select the closest polygon vertex within a threshold
        selected_mask_idx, selected_point_idx = get_polygon_at_click(x, y)
        print(selected_mask_idx)
        update_display(highlight_idx=selected_mask_idx)
        
def multiselect(event):
    global selected_indices, multiselect_on, selected_mask_idx
    multiselect_on = True
    #selected_mask_idx = None
    x, y = (event.x - view_offset_x) / zoom_factor, (event.y - view_offset_y) / zoom_factor
    
    start_x, start_y = event.x, event.y
    selected_mask_idx, selected_point_idx = get_polygon_at_click(x, y)
    if selected_mask_idx not in selected_indices:
        selected_indices.append(selected_mask_idx)
        
    update_display(None)

def stop_multiselect(event=None):
    global selected_indices, multiselect_on
    selected_indices = []
    multiselect_on = False
    update_display()
        
def delete_vertex(event):
    global selected_mask_idx, selected_point_idx, annotations
    
    if selected_mask_idx is not None and selected_point_idx is not None:
        # Create a copy of the selected annotation
        annotation_copy = copy.deepcopy(annotations[selected_mask_idx][:])
        
        # Delete the selected vertex from the copy
        del annotation_copy[1 + selected_point_idx * 2]
        del annotation_copy[1 + selected_point_idx * 2]
        
        # Replace the original annotation with the modified copy
        annotations[selected_mask_idx] = annotation_copy
        
        # Adjust the selected point index
        try:
            selected_point_idx = 0
        except:
            selected_point_idx = None
        
        # Update the display
        update_display(highlight_idx=selected_mask_idx)

def on_drag(event):
    global selected_mask_idx, selected_point_idx, manual_polygon, mask_dragging, zoom_factor, manual_mode
    #mask_dragging = True
    
    if selected_mask_idx is not None and selected_point_idx is not None:
        # Adjust cursor position with zoom and pan to update vertex accurately
        x, y = (event.x - view_offset_x) / zoom_factor, (event.y - view_offset_y) / zoom_factor
           
        annotations[selected_mask_idx][1 + selected_point_idx * 2] = x / image.width
        annotations[selected_mask_idx][2 + selected_point_idx * 2] = y / image.height
        
        update_display(highlight_idx=selected_mask_idx)
        
    elif manual_mode:
        x, y = (event.x - view_offset_x) / zoom_factor, (event.y - view_offset_y) / zoom_factor
        print(x,y)
        manual_polygon.append([x / image.width, y / image.height])
        update_display()

def on_release(event):
    global selected_point_idx, manual_polygon, selected_class, mask_dragging, image_dragging
    mask_dragging = False
    
    if selected_mask_idx is not None:
        a = 1
        update_display(selected_mask_idx)
        #selected_point_idx = None  # Clear the selected vertex after dragging
    if manual_mode:           
        class_label = selected_class
        manual_polygon = [coord for point in manual_polygon for coord in point]
        #manual_polygon = remove_close_points(manual_polygon)
        annotations.append([class_label] + manual_polygon)
        toggle_manual_mode()
        update_display()
        
def simplify_annotations(event=None):
    global annotations
    for idx, mask in enumerate(annotations):
        new_mask = [mask[0]]
        coords = mask[1:]
        filtered_coords = remove_close_points(coords)
        new_mask[1:] = filtered_coords
        annotations[idx] = new_mask;
    update_display(selected_mask_idx) 
    

def simplify_mask(event):
    global selected_mask_idx, annotations
    
    if selected_mask_idx is not None:
        mask = annotations[selected_mask_idx]
        new_mask = [mask[0]]
        coords = mask[1:]
        filtered_coords = remove_close_points(coords)
        new_mask[1:] = filtered_coords
        annotations[selected_mask_idx] = new_mask;
        update_display(selected_mask_idx)    
        
def remove_close_points(coords):
    global threshold
    # If fewer than two points, nothing to filter out
    if len(coords) < 4:
        return coords

    # Start with the first point in the result list
    filtered_coords = [coords[0], coords[1]]

    for i in range(2, len(coords), 2):
        # Calculate the distance between last added point and current point
        x1, y1 = filtered_coords[-2], filtered_coords[-1]
        x2, y2 = coords[i], coords[i + 1]
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        # Only add the current point if it's beyond the threshold distance
        if distance >= threshold:
            filtered_coords.extend([x2, y2])

    return filtered_coords


def on_mousewheel(event):
    global zoom_factor, view_offset_x, view_offset_y, do_zoom, mask_dragging
    
    scale_factor = 1.1 if event.delta > 0 else 0.9
    zoom_factor *= scale_factor
    
    cursor_x, cursor_y = event.x, event.y
    
    view_offset_x = (view_offset_x - cursor_x) * scale_factor + cursor_x
    view_offset_y = (view_offset_y - cursor_y) * scale_factor + cursor_y
    do_zoom = True
    
    print(zoom_factor)
    if zoom_factor < 1:
        reset_zoom()
    print(zoom_factor)
    
    if selected_mask_idx is not None and selected_point_idx is not None:
        update_display(highlight_idx=selected_mask_idx)
    else:
        update_display()

def reset_zoom():
    global zoom_factor, view_offset_x, view_offset_y, last_zoom_factor
    zoom_factor = 1
    last_zoom_factor = -1
    view_offset_x = 0
    view_offset_y = 0
    update_display()

def start_pan(event):
    global start_pan_x, start_pan_y, image_dragging, is_y_pressed
    start_pan_x, start_pan_y = event.x, event.y
    if is_y_pressed:
        show_context_menu(event.x_root,event.y_root)
    else:
        image_dragging = True

def do_pan(event):
    global view_offset_x, view_offset_y, start_pan_x, start_pan_y, image_dragging 
    if image_dragging and view_offset_x <=0 and view_offset_y<=0:
        dx, dy = event.x - start_pan_x, event.y - start_pan_y
        view_offset_x += dx
        view_offset_y += dy
        start_pan_x, start_pan_y = event.x, event.y
        update_display()
    
    if view_offset_x > 0:
        view_offset_x = 0
    if view_offset_y > 0:
        view_offset_y = 0
   
def release_pan(event):
    global image_dragging
    image_dragging = False
    
def show_context_menu(x_context,y_context):
    global selected_mask_idx, is_y_pressed
    if selected_mask_idx is not None:
        context_menu_mask_selected.post(x_context, y_context)
        is_y_pressed = False
    else:
        context_menu_mask_not_selected.post(x_context, y_context)
        is_y_pressed = False

def segment_whole_image(event=None):
    global annotations, set_conf, set_iou
    
    image_np = np.array(original_image)
    image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    results = model(image_bgr, conf=set_conf, iou=set_iou)    
            
    if len(results[0]) == 0:
        print("No objects found.")
        return None, None
    
    annotations = []
    for idx, mask in enumerate(results[0].masks):
        polygon = mask.xyn[0].tolist()            
        new_polygon = [coord for point in polygon for coord in point]  # Flattened coordinates
        new_polygon.insert(0,np.uint8(results[0].boxes[idx].cls).item())
        annotations.append(new_polygon)
        delete_contained_polygons()
    update_display()

def delete_contained_polygons():
    global annotations
    new_annotations = annotations
    indices_to_delete = set()

    # Convert each mask's coordinates to a Polygon once and store
    polygons = [Polygon(list(zip(mask[1::2], mask[2::2]))) for mask in annotations]

    # Compare each outer_polygon with inner_polygon
    for outer_idx, outer_polygon in enumerate(polygons):
        for inner_idx, inner_polygon in enumerate(polygons):
            if outer_idx != inner_idx and outer_polygon.contains(inner_polygon):
                indices_to_delete.add(inner_idx)

    # Sort and delete from new_annotations in reverse order
    for index in sorted(indices_to_delete, reverse=True):
        del new_annotations[index]

    annotations = new_annotations
    update_display()
            
def perform_segmentation(x, y): 
    global set_conf, set_iou
    image_np = np.array(original_image)
    image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)  
    try:      
        results = model(image_bgr, points=[[x, y]], conf=set_conf, iou=set_iou)
    except:
        print("No object found at the click location.")
        return None, None
            
       
    if len(results[0]) == 0:
        print("No object found at the click location.")
        return None, None
    
    polygon = results[0].masks.xyn[0].tolist()
    return np.uint8(results[0].boxes[0].cls).item(), [coord for point in polygon for coord in point]  # Flattened coordinates
    
def get_polygon_at_click(x, y, threshold=10):
    """Returns the index of the mask and polygon point closest to the click coordinates."""
    closest_idx = None
    closest_point_idx = None
    min_distance = float("inf")

    for idx, mask_data in enumerate(annotations):
        class_id, *coordinates = mask_data
        for point_idx in range(0, len(coordinates), 2):
            px = coordinates[point_idx] * image.width
            py = coordinates[point_idx + 1] * image.height
            dist = np.sqrt((px - x) ** 2 + (py - y) ** 2)
            if dist < threshold and dist < min_distance:
                min_distance = dist
                closest_idx = idx
                closest_point_idx = point_idx // 2

    return closest_idx, closest_point_idx

def delete_mask(event=None):
    global selected_mask_idx, selected_point_idx, multiselect_on, selected_indices
    if multiselect_on:
        for idx in sorted(selected_indices, reverse=True):            
            del annotations[idx]
        selected_indices = []
        multiselect_on = False
        update_display()
        return
        
    if selected_mask_idx is not None:
        del annotations[selected_mask_idx]
        selected_mask_idx = None
        selected_point_idx = None
        update_display()
        return

def save_annotations(event=None):
    global annotations_folder, title_label
    if annotations_folder is None:
        text_name = os.path.splitext(image_paths[curr_image_index])[0] + ".txt"
    else:
        text_name = annotations_folder + "/" + title_label.cget("text") + ".txt"
    
    try:
        with open(text_name, 'w') as f:
            for mask_data in annotations:
                class_id, *coordinates = mask_data
                f.write(f"{class_id} " + " ".join(map(str, coordinates)) + "\n")
        print("Saved annotations to", text_name)
        messagebox.showinfo("Success", f"Annotations saved to:\n{text_name}")
    except Exception as e:
        print("Failed to save annotations:", e)
        messagebox.showerror("Error", f"Failed to save annotations:\n{e}")
    

def update_display(highlight_idx=selected_mask_idx):
    global tk_image, image, last_zoom_factor, image_resized, image_np_orig, multiselect_on, selected_indices, zoom_factor, view_offset_x, view_offset_y, coordinates, manual_polygon, colors, do_zoom, points_array,points, manual_mode, curr_viewport
    start_time = time.time() 
    if zoom_factor is not last_zoom_factor:
        image_resized = image.resize((int(image.width * zoom_factor), int(image.height * zoom_factor)), Image.NEAREST)
        image_np_orig = np.array(image_resized)    
    
    image_np = copy.deepcopy(image_np_orig)
    #   
    #
    
    for idx, mask_data in enumerate(annotations):
        mask_class, *coordinates = mask_data
        color = (255, 255, 0) if idx == highlight_idx else colors[mask_class]
        if idx in selected_indices:
            color = (255, 255, 0) 
        points = np.array(
            [(int(coordinates[i] * image.width * zoom_factor),
              int(coordinates[i + 1] * image.height * zoom_factor))
             for i in range(0, len(coordinates), 2)], dtype=np.int32)
        cv2.polylines(image_np, [points], isClosed=True, color=color, thickness=1)
        
        if idx == highlight_idx and not multiselect_on:
            for idx, point in enumerate(points):
                if idx is selected_point_idx:
                    cv2.circle(image_np, tuple(point), 5, [255, 0, 0], 1)
                else:
                    cv2.circle(image_np, tuple(point), 5, [0, 0, 0], 1)
    
                    
    if manual_mode:    
        modified_points = [(x * image.width * zoom_factor, y * image.height * zoom_factor) for (x, y) in manual_polygon]
        points_array = np.array(modified_points, np.int32)  # Ensure the points are integers
        cv2.polylines(image_np, [points_array], isClosed=False, color=[255, 255, 0], thickness=1)
    

    
    
    # Extract the visible region from image_np
    viewport_x, viewport_y = int(abs(view_offset_x)), int(abs(view_offset_y))  # Example offsets
    viewport_width, viewport_height = 640, 640  # Example viewport size
    visible_region = image_np[viewport_y:viewport_y + viewport_height, viewport_x:viewport_x + viewport_width]               
    image_np = visible_region.astype('uint8')  # Ensure dtype is uint8       
    
    blended_pil = Image.fromarray(image_np)  
    curr_viewport = blended_pil
    
    tk_image = ImageTk.PhotoImage(blended_pil)
    vx = 0
    vy = 0
    if view_offset_x > 0:
        vx = view_offset_x
    if view_offset_y > 0:
        vy = view_offset_y
    
    canvas.config(width=640, height=640)
    canvas.create_image(vx, vy, anchor=tk.NW, image=tk_image)
    #canvas.create_image(view_offset_x, view_offset_y, anchor=tk.NW, image=tk_image)
    #do_zoom = False
    
    canvas.image = tk_image
    fill_archive()
    
    try:
        refresh_boxlist()
    except:
        pass
    
    last_zoom_factor = zoom_factor
    #print("Time:", time.time() - start_time)

def save_current_view(event = None):
    global curr_viewport
    fileName = title_label.cget("text")+"_viewport.png"
    curr_viewport.save(fileName)    
    
def fill_archive():
    global archive, nUndoes, annotations, mask_dragging, undoing

    # Avoid archiving if dragging or undoing
    if not mask_dragging and not undoing:
        # Only add to archive if the new state is different
        if not archive or annotations != archive[-1]:
            if len(archive) >= nUndoes:
                archive.pop(0)  # Maintain a fixed number of undos by removing the oldest
            archive.append(copy.deepcopy(annotations))  # Archive a deep copy of annotations

def load_image():
    global curr_image_index, image, original_image, tk_image, annotations, title_label, archive, selected_mask_idx, multiselect_on, selected_indices
    
    selected_mask_idx = None
    selected_indices = []
    original_image = Image.open(image_paths[curr_image_index])
    image = original_image.copy()
    
    max_height = 640

    # Get the original dimensions of the image
    original_width, original_height = image.size
    if original_height > max_height:
        aspect_ratio = original_width / original_height
        new_height = max_height
        new_width = int(max_height * aspect_ratio)
        # Resize the image
        image = image.resize((new_width,new_height))
   
    #image.resize((int(image.width * zoom_factor), int(image.height * zoom_factor)), Image.LANCZOS)
    tk_image = ImageTk.PhotoImage(image)    
    image_name = Path(image_paths[curr_image_index]).stem
    title_label.config(text=image_name)
    annotations = load_yolo_segmentation()
    multiselect_on = False
    archive = []

def load_yolo_segmentation():
    global annotations_folder, title_label
    if annotations_folder is not None:
        text_path = annotations_folder+"/"+title_label.cget("text")+".txt"
        
        #text_path = os.path.splitext(image_paths[curr_image_index])[0] + ".txt"
        if not os.path.exists(text_path):
            return []
    else:
        text_path = os.path.splitext(image_paths[curr_image_index])[0] + ".txt"
        if not os.path.exists(text_path):
            return []
    print(text_path)    
    annotations = []
    with open(text_path, 'r') as file:
        for line in file:
            try:
                parts = line.strip().split()
                class_id = int(parts[0])
                coordinates = list(map(float, parts[1:]))
                annotations.append([class_id] + coordinates)
            except Exception as e:
                print(e)
                return []
    return annotations

def next_image(event=None):
    global curr_image_index, number
    if curr_image_index + 1 < len(image_paths):
        curr_image_index += 1
        number.set(curr_image_index)
        load_image()
        try:
            refresh_boxlist()
        except:
            pass
        reset_zoom()
        #update_display()

def previous_image(event=None):
    global curr_image_index, number
    if curr_image_index - 1 >= 0:
        curr_image_index -= 1
        number.set(curr_image_index)
        load_image()
        try:
            refresh_boxlist()
        except:
            pass
        reset_zoom()
        #update_display()
        
# Function to set the Y key as  pressed
def y_key_press(event):
    global is_y_pressed
    is_y_pressed = True

# Function to set the Y key as released
def y_key_release(event):
    global is_y_pressed
    is_y_pressed = False

# Run the application
initialize_app("155.png", "model.pt")
