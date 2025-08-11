# -*- coding: utf-8 -*-
"""
Created on Wed Aug  6 13:58:56 2025

@author: GKoinig
"""

import pygame
import os
import time
import shutil
from natsort import natsorted
import easygui
import random
import multiprocessing
from ultralytics import YOLO
from PIL import Image
import sys

###
#%% Button Callbacks
    
def train_model(caller=None):   
    global TRAIN_PROCESS
    if TRAINING_FLAG.value == True:
        easygui.msgbox("Training already in progress...")
        return
    
    choices = ["Classifier","Detector","Segmentor"]
    model_of_choice = easygui.choicebox("Select a model type:", "Model Selection", choices)
    if not model_of_choice:
        return
    if model_of_choice == "Classifier":
        TRAIN_PROCESS = multiprocessing.Process(target=train_classifier,args=(Q,TRAINING_FLAG,))
        TRAIN_PROCESS.start()
        easygui.msgbox("Training Subprocess is being initialized, please stand by...")
    elif model_of_choice == "Detector":
        TRAIN_PROCESS = multiprocessing.Process(target=train_detector,args=(Q,TRAINING_FLAG,))
        TRAIN_PROCESS.start()
        easygui.msgbox("Training Subprocess is being initialized, please stand by...")
    else:
        easygui.msgbox(f"{model_of_choice} not yet implemented")

def get_training_parameters_from_user_input():
    # Field names
    fields = ["Number of training epochs", "Batch size", "Learning rate", "Box", "CLS", "Project", "Name"]
    
    # Default values for each field
    defaults = ["100", "16", "0.01", "7.5", "0.5", "Project", "train"]
    
    # Show dialog
    values = easygui.multenterbox("Enter training parameters:", "Training Settings", fields, defaults)
    
    # If user cancels, values will be None
    if values:
        try:
            n_epochs = int(values[0])
        except:
            n_epochs = 100
    
        try:
            batch_size = int(values[1])
        except:
            batch_size = 16
    
        try:
            learning_rate = float(values[2])
        except:
            learning_rate = 0.01
            
        try:
            box = float(values[3])
        except:
            box = 7.5
            
        try:
            class_weight = float(values[4])
        except:
            class_weight = 0.5
            
        try:
            project = values[5]
        except:
            project = "Project"
            
        try:
            name = values[6]
        except:
            name = "train"
    
        print(f"Epochs: {n_epochs}, Batch size: {batch_size}, Learning rate: {learning_rate}, Project: {project}, Name: {name}")
    else:
        print("Dialog cancelled.")
    
    return n_epochs, batch_size, learning_rate, box, class_weight, project, name

def train_classifier(Q,training_flag):    
    training_flag.value = False
    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

    train_folder = easygui.diropenbox("Select training folder")
    if not train_folder:
        training_flag.value = False
        return

    choices = ["yolo11n-cls.pt", "yolo11s-cls.pt", "yolo11m-cls.pt", "yolo11l-cls.pt", "yolo11x-cls.pt"]
    model_of_choice = easygui.choicebox("Select a YOLO classification model:", "Model Selection", choices)
    if not model_of_choice:
        training_flag.value = False
        return

    n_epochs, batch_size, learning_rate, box, class_weight, project, name = get_training_parameters_from_user_input()

    # Auto-detect image size from the first image in train folder
    imgsz = detect_imgsz_for_training(train_folder)

    model = YOLO(model_of_choice)
    training_flag.value = True
    
    sys.stdout = QueueWriter(Q)
    sys.stderr = QueueWriter(Q)    
    model.train(data=train_folder, epochs=n_epochs, imgsz=imgsz, batch=batch_size, lr0 = learning_rate, project=project, name=name, box=box,cls=class_weight)

    training_flag.value = False
    if TRAIN_PROCESS.is_alive():
        easygui.msgbox("Training Process Closed", "Done")
        TRAIN_PROCESS.terminate()  # sends SIGTERM on Unix / force-kill on Windows
        TRAIN_PROCESS.join()
        

def train_detector(Q,training_flag):    
    try:
        training_flag.value = False
        os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
    
        #train_folder = easygui.diropenbox("Select training folder")
        #if not train_folder:
            #training_flag.value = False
            #return
    
        choices = ["yolo11n.pt", "yolo11s.pt", "yolo11m.pt", "yolo11l.pt", "yolo11x.pt"]
        model_of_choice = easygui.choicebox("Select a YOLO classification model:", "Model Selection", choices)
        if not model_of_choice:
            training_flag.value = False
            return
        yaml_path = easygui.fileopenbox("Select_path_to_training_YAML")
        
        if not yaml_path:
            training_flag.value = False
            easygui.msgbox("YAML Path must be defined")
            return
        
        n_epochs, batch_size, learning_rate, box, class_weight, project, name = get_training_parameters_from_user_input()
    
        # Auto-detect image size from the first image in train folder
        #imgsz = detect_imgsz_for_training(train_folder)
    
        model = YOLO(model_of_choice)
        training_flag.value = True
        
        sys.stdout = QueueWriter(Q)
        sys.stderr = QueueWriter(Q)    
        model.train(data=yaml_path, epochs=n_epochs, batch=batch_size, lr0 = learning_rate, project=project, name=name, box=box,cls=class_weight)
    
        #TRAIN_PROCESS.join()
        #easygui.msgbox("Training Complete", "Done")
        
    finally:
        training_flag.value = False
        if TRAIN_PROCESS.is_alive():
            easygui.msgbox("Training Process Closed", "Done")
            TRAIN_PROCESS.terminate()  # sends SIGTERM on Unix / force-kill on Windows
            TRAIN_PROCESS.join()
            

def detect_imgsz_for_training(train_folder):
    # Auto-detect image size from the first image in train folder
    train_images_dir = os.path.join(train_folder, "train")
    imgsz = 224  # default fallback
    found_image = False
    for root, dirs, files in os.walk(train_images_dir):
        for file in files:
            if file.lower().endswith((".jpg", ".png", ".jpeg")):
                image_path = os.path.join(root, file)
                try:
                    with Image.open(image_path) as img:
                        width, height = img.size
                        imgsz = max(width, height)
                        found_image = True
                        break
                except Exception as e:
                    print(f"Could not read image size: {e}")
        if found_image:
            break
    return imgsz


def select_yolo_mode():
    choices = ["YOLO Classification", "YOLO Detection", "YOLO Segmentation"]
    selected = easygui.choicebox("Select the YOLO mode you want to use:", "YOLO Mode Selection", choices)
    
    if selected:
        print(f"You selected: {selected}")
        return selected
    else:
        print("No selection made.")
        return None

def create_yolo_detection_training_data_split(target_folder):
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # Create train and test folders
    train_folder_path = os.path.join(target_folder, "train")
    val_folder_path = os.path.join(target_folder, "val")
    os.makedirs(train_folder_path, exist_ok=True)
    os.makedirs(val_folder_path, exist_ok=True)
    
    progress_bar_background = pygame.Rect(80,70,840,120)
    progress_bar_background_rect = pygame.Rect(100,100,800,30)
    progress = 0
    progress_bar_progress_rect = pygame.Rect(100,100,800*progress,30)
    
    
    total_classes = len(CLASSES)
    image_paths = []
    for i, (class_name, class_obj) in enumerate(CLASSES.items()):
        image_paths.extend(class_obj.image_paths)
        if not image_paths:
            continue

    # Shuffle and split images 80/20
    random.shuffle(image_paths)
    split_idx = int(len(image_paths) * 0.8)
    image_paths_train = image_paths[:split_idx]
    image_paths_test = image_paths[split_idx:]

    # Create image and label subfolders
    train_image_folder = os.path.join(train_folder_path, "image")
    val_image_folder = os.path.join(val_folder_path, "image")
    os.makedirs(train_image_folder, exist_ok=True)
    os.makedirs(val_image_folder, exist_ok=True)
    
    train_label_folder = os.path.join(train_folder_path, "label")
    val_label_folder = os.path.join(val_folder_path, "label")
    os.makedirs(train_label_folder, exist_ok=True)
    os.makedirs(val_label_folder, exist_ok=True)
        
    
    # Copy images
    for path in image_paths_train:
        if os.path.isfile(path):
            shutil.copy(path, train_image_folder)
    # Copy YOLO annotation txt files for training images    
            # Replace file extension with .txt
            txt_path = os.path.splitext(path)[0] + ".txt"
            
            if os.path.isfile(txt_path):
                shutil.copy(txt_path, train_label_folder)
            else:
                print(f"Annotation file not found for {path}")

    for path in image_paths_test:
        if os.path.isfile(path):
            shutil.copy(path, val_image_folder)
        # Copy YOLO annotation txt files for training images      
            # Replace file extension with .txt
            txt_path = os.path.splitext(path)[0] + ".txt"
            
            if os.path.isfile(txt_path):
                shutil.copy(txt_path, val_label_folder)
            else:
                print(f"Annotation file not found for {path}")
        
        
    print("✅ YOLO detection training data split completed.")

def create_yolo_classification_training_data_split(target_folder):
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # Create train and test folders
    train_folder_path = os.path.join(target_folder, "train")
    test_folder_path = os.path.join(target_folder, "test")
    os.makedirs(train_folder_path, exist_ok=True)
    os.makedirs(test_folder_path, exist_ok=True)
    
    progress_bar_background = pygame.Rect(80,70,840,120)
    progress_bar_background_rect = pygame.Rect(100,100,800,30)
    progress = 0
    progress_bar_progress_rect = pygame.Rect(100,100,800*progress,30)
    
    
    total_classes = len(CLASSES)
    for i, (class_name, class_obj) in enumerate(CLASSES.items()):
        image_paths = class_obj.image_paths
        if not image_paths:
            continue

        # Shuffle and split images 80/20
        random.shuffle(image_paths)
        split_idx = int(len(image_paths) * 0.8)
        image_paths_train = image_paths[:split_idx]
        image_paths_test = image_paths[split_idx:]

        # Create class subfolders
        train_class_folder = os.path.join(train_folder_path, class_name)
        test_class_folder = os.path.join(test_folder_path, class_name)
        os.makedirs(train_class_folder, exist_ok=True)
        os.makedirs(test_class_folder, exist_ok=True)
        
        
        pygame.draw.rect(SCREEN,pygame.Color("white"),progress_bar_background)
        # Compute progress as a float between 0 and 1
        progress = (i + 1) / total_classes        
        pygame.draw.rect(SCREEN,pygame.Color("black"),progress_bar_background_rect)
        # Update the progress rect
        progress_bar_progress_rect = pygame.Rect(100, 100, int(800 * progress), 30)
        pygame.draw.rect(SCREEN,pygame.Color("green"),progress_bar_progress_rect)
        pygame.draw.rect(SCREEN,pygame.Color("gray"),progress_bar_background_rect,3)
        blit_text("Creating Training Split...",progress_bar_background.centerx,progress_bar_background.top+5,color=pygame.Color("black"),fontsize=32)
        
        # Update display
        pygame.display.flip()
        
        # Copy images
        for path in image_paths_train:
            if os.path.isfile(path):
                shutil.copy(path, train_class_folder)

        for path in image_paths_test:
            if os.path.isfile(path):
                shutil.copy(path, test_class_folder)
        
        
    print("✅ YOLO classification training data split completed.")
    

def export_dataset(caller=None):
    target_folder = easygui.diropenbox(title="Select Destination Folder to Export")
    if not target_folder:
        easygui.msgbox("No Target Folder Selected")
        return
    
    # Example usage
    yolo_mode = select_yolo_mode()
    
    if yolo_mode == "YOLO Classification":
        create_yolo_classification_training_data_split(target_folder)
    elif yolo_mode == "YOLO Detection" or yolo_mode == "YOLO Segmentation":
        create_yolo_detection_training_data_split(target_folder)

def load_folder(caller=None):
    source_folder = easygui.diropenbox(title="Select Destination Folder to Save Classes")
    if not source_folder:
        return
    new_class_name = os.path.basename(source_folder)

    CLASSES[new_class_name] = Class(new_class_name,source_folder)
    CLASS_NAMES.append(new_class_name)
    CLASS_PATHS[new_class_name] = source_folder
    CLASS_CONTENTS[new_class_name] = os.listdir(source_folder)
    
    
    create_class_folder_buttons()

def save_created_classes(caller=None):
    if 'CLASS_PATHS' not in globals() or not CLASS_PATHS:
        easygui.msgbox("No class data to save. Make sure classes are loaded or created first.")
        return

    dest_folder = easygui.diropenbox(title="Select Destination Folder to Save Classes")
    if not dest_folder:
        return

    # Prepare list of all files to copy
    tasks = []
    for class_name, class_path in CLASS_PATHS.items():
        for filename in os.listdir(class_path):
            src = os.path.join(class_path, filename)
            dst = os.path.join(dest_folder, class_name, filename)
            if os.path.isfile(src):
                tasks.append((src, dst))

    for class_name in CLASS_NAMES:
        if class_name not in CLASS_PATHS:
            class_obj = CLASSES.get(class_name)
            if class_obj:
                for image_path in class_obj.image_paths:
                    if os.path.isfile(image_path):
                        dst = os.path.join(dest_folder, class_name, os.path.basename(image_path))
                        tasks.append((image_path, dst))

    # Progress bar settings
    total = len(tasks)
    bar_x, bar_y, bar_w, bar_h = int(SCREEN.get_width()//2-200), int(SCREEN.get_height()//2-15), 400, 30  # Position & size
    font = pygame.font.Font(None, 24)

    # Loop through and copy with progress
    progress_text = font.render("Saving classes...", True, pygame.Color("white"))
    SCREEN.blit(progress_text, (bar_x, bar_y - 30))
    for i, (src, dst) in enumerate(tasks):
        # Ensure folder exists
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src, dst)

        # Update progress bar
        pygame.draw.rect(SCREEN, pygame.Color("black"), (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(SCREEN, pygame.Color("white"), (bar_x, bar_y, bar_w, bar_h), 2)
        progress = int((i + 1) / total * bar_w)
        pygame.draw.rect(SCREEN, pygame.Color("green"), (bar_x, bar_y, progress, bar_h))
        
        pygame.display.update()

    easygui.msgbox("All classes have been saved.", title="Save Complete")    

def save_created_classes_old(caller=None):
    if 'CLASS_PATHS' not in globals() or not CLASS_PATHS:
        easygui.msgbox("No class data to save. Make sure classes are loaded or created first.")
        return
    
    dest_folder = easygui.diropenbox(title="Select Destination Folder to Save Classes")
    if not dest_folder:
        return

    # Save classes that already have folder paths
    for class_name, class_path in CLASS_PATHS.items():
        target_path = os.path.join(dest_folder, class_name)
        if not os.path.exists(target_path):
            os.mkdir(target_path)
        for filename in os.listdir(class_path):
            src = os.path.join(class_path, filename)
            dst = os.path.join(target_path, filename)
            if os.path.isfile(src):
                shutil.copy(src, dst)

    # Save newly created classes (those not yet in CLASS_PATHS)
    for class_name in CLASS_NAMES:
        if class_name not in CLASS_PATHS:
            class_obj = CLASSES.get(class_name)
            if class_obj:
                target_path = os.path.join(dest_folder, class_name)
                if not os.path.exists(target_path):
                    os.mkdir(target_path)
                for image_path in class_obj.image_paths:
                    if os.path.isfile(image_path):
                        filename = os.path.basename(image_path)
                        dst = os.path.join(target_path, filename)
                        shutil.copy(image_path, dst)

    easygui.msgbox("All classes have been saved.", title="Save Complete")
    
def remove_class(caller=None):
    global CLASSES, CLASS_NAMES, CLASS_PATHS, CLASS_CONTENTS

    if not CLASSES:
        easygui.msgbox("No classes to delete.")
        return

    entries = list(CLASSES.keys())
    if len(entries) > 1:
        selected = easygui.multchoicebox(
            msg="Select one or more classes to delete:",
            title="Delete Classes",
            choices=entries
        )
    else:
        selected = entries

    if selected:
        for class_name in selected:
            # Remove from CLASSES and related global structures
            CLASSES.pop(class_name, None)
            CLASS_NAMES.remove(class_name) if class_name in CLASS_NAMES else None
            CLASS_PATHS.pop(class_name, None)
            CLASS_CONTENTS.pop(class_name, None)
        create_class_folder_buttons()
        easygui.msgbox(f"Deleted: {', '.join(selected)}")

def add_new_class(caller):
    new_class_name = easygui.enterbox("Enter new class name:")
    if new_class_name:  # If user didn't cancel
        CLASSES[new_class_name] = Class(new_class_name)
        CLASS_NAMES.append(new_class_name)
        create_class_folder_buttons()
        print(f"Class '{new_class_name}' created")
    else:
        easygui.msgbox(f"Class '{new_class_name}' already exists!")

def select_main_folder(caller=None):
    global MAIN_FOLDER_PATH
    global CLASS_FOLDER_BUTTONS
    
    CLASS_FOLDER_BUTTONS = []
    MAIN_FOLDER_PATH = easygui.diropenbox(title="Select Main Folder")
    if MAIN_FOLDER_PATH is not None:
        #easygui.msgbox(f"Folder Set to:\n{MAIN_FOLDER_PATH}")
        get_class_names_from_main_folder()
        create_class_folder_buttons()
    else:
        easygui.msgbox(f"No Folder Set. Remaining in:\n{MAIN_FOLDER_PATH}")
        
def test_callback(caller=None):
    print("clicked")
    
def open_class_image_window(caller=None):
    global CLASS_IMAGE_MENU
    if Class_Image_Menu.class_image_menu_shown == False:
        CLASS_IMAGE_MENU = Class_Image_Menu(10, 10, 980, 880, CLASSES.get(caller.name))
        
def show_class_dist_menu(caller=None) :
    Class_Dist_Menu(10, 10, 980, 780, name="")

#%% Classes

class QueueWriter:
        def __init__(self, q):
            self.q = q
        def write(self, msg):
            if msg.strip():
                self.q.put(msg)
        def flush(self):
            pass

class ProgressBar:
    def __init__(self, x, y, w, h, title="Progress"):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.progress = 0.0
        self.title = title
        self.font = pygame.font.SysFont(None, 30)
        self.active = True

    def update(self, progress):
        """Update progress: value between 0.0 and 1.0"""
        self.progress = max(0.0, min(1.0, progress))

    def draw(self, surface):
        if not self.active:
            return

        # Draw background box
        pygame.draw.rect(surface, (50, 50, 50), (self.x, self.y, self.w, self.h))
        # Draw progress bar
        inner_width = int(self.progress * (self.w - 4))
        pygame.draw.rect(surface, (0, 200, 0), (self.x + 2, self.y + 2, inner_width, self.h - 4))
        # Draw border
        pygame.draw.rect(surface, (255, 255, 255), (self.x, self.y, self.w, self.h), 2)

        # Draw text
        text = self.font.render(f"{self.title}: {int(self.progress * 100)}%", True, (255, 255, 255))
        surface.blit(text, (self.x, self.y - 30))

    def close(self):
        self.active = False


class Class:
    def __init__(self, class_name, folder_path=None):
        self.class_name = class_name
        if folder_path is not None:
            self.folder_path = folder_path  # rename to clarify
            self.image_paths = self._get_image_paths()            
        else:
            self.image_paths = []

    def _get_image_paths(self):
        # Allowed extensions
        valid_ext = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')

        # Build full paths and filter
        return natsorted([
            os.path.join(self.folder_path, f)
            for f in os.listdir(self.folder_path)
            if f.lower().endswith(valid_ext)
        ])
    

    def save(self,caller=None):
        new_folder_name = self.class_name
        new_folder_path = os.path.join(MAIN_FOLDER_PATH,new_folder_name)
        class_to_save = self
        images_to_save = self.image_paths
        if not os.path.exists(new_folder_path):
            os.mkdir(new_folder_path)
        # Copy all images from images_to_save into the new folder
        # Copy images
        for image_path in images_to_save:
            filename = os.path.basename(image_path)
            dest_path = os.path.join(new_folder_path, filename)
        
            # Avoid overwriting existing files (optional)
            if not os.path.exists(dest_path):
                shutil.copy2(image_path, dest_path)
            else:
                print(f"Skipped: {filename} (already exists)")
        # List files currently in the destination folder
        target_file_list = os.listdir(new_folder_path)
    
        # Build a set of filenames that *should* be there
        valid_filenames = set(os.path.basename(p) for p in images_to_save)
    
        # Delete any files in the folder that are NOT in images_to_save
        for file in target_file_list:
            if file not in valid_filenames:
                try:
                    os.remove(os.path.join(new_folder_path, file))
                    print(f"Deleted: {file} (not in source list)")
                except Exception as e:
                    print(f"Error deleting {file}: {e}")
        
        self._get_image_paths()

class Menu:
    ACTIVE_MENU = None
    LAST_MENU_CLOSE_TIME = 0
    def __init__(self, x, y, w, h, name="Menu"):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.name = name
        
        
        # layout config
        self.bg_color = pygame.Color('black')
        self.border_color = pygame.Color('gray')
        self.border_thickness = 5
        
        self.buttons = []
        self.close_button = Button(self.x+self.w-80-self.border_thickness,self.y+self.border_thickness,80,80,self.close,IMAGES.get("close"))
        self.buttons.append(self.close_button)
        
        MENUS.append(self)
        self.debounce = 0.5
        self.last_click = time.time()
        
    def update(self):
        for b in self.buttons:
            b.update()
    
    def draw_buttons(self):
        for b in self.buttons:
            b.draw()
    
    def draw(self):
        # Draw background
        menu_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(SCREEN, self.bg_color, menu_rect)

        # Draw border around menu
        pygame.draw.rect(SCREEN, self.border_color, menu_rect, self.border_thickness)

        self.draw_buttons()
            
        blit_text(self.name, self.w//2, self.y+10,fontsize=32)
    
    
    def close(self, caller=None):
        global TIME_LAST_MENU_CLOSED
        TIME_LAST_MENU_CLOSED = time.time()
        Menu.ACTIVE_MENU = None
        Menu.LAST_MENU_CLOSE_TIME = time.time()
        MENUS.remove(self)
        
        
class Magnify_Image_Menu(Menu):
    ACTIVE_MENU = None
    def __init__(self,x,y,w,h,image_path,name=""):
        super().__init__(x,y,w,h,name)
        Menu.ACTIVE_MENU = self
        self.image_path = image_path
        self.image = pygame.image.load(self.image_path)
        self.image = pygame.transform.scale(self.image,(self.w-100,self.h-100))
        self.image_index = CLASSES.get(self.name).image_paths.index(self.image_path)
        self.left_button = Button(
          self.x + 10, self.y + self.h - 90, 80, 80,
          self.previous_image, IMAGES.get("previous"), show_name=False
      )
        self.right_button = Button(
            self.x + self.w - 90, self.y +self.h - 90, 80, 80,
            self.next_image, IMAGES.get("next"), show_name=False
        )
        self.mark_button = Button(
            self.x + self.w//2 - 40, self.y +self.h - 90, 80, 80,
            self.mark_image, IMAGES.get("unchecked"), show_name=False
        )
        self.show_BBOXES_Button = Button(
            self.x + self.w - 90, self.y + self.h//2-40, 80, 80,
            self.toggle_annotations, IMAGES.get("eye"), show_name=False
        )
        self.buttons.append(self.left_button)
        self.buttons.append(self.right_button)
        self.buttons.append(self.mark_button)
        self.buttons.append(self.show_BBOXES_Button)
        #self.close_button = Button(self.x+self.w-80-self.border_thickness,self.y+self.border_thickness,80,80,self.close,IMAGES.get("close"))
        self.color_list = list(pygame.color.THECOLORS.keys())
        self.show_annotations = True
    
    def toggle_annotations(self, caller=None):
        self.show_annotations = not self.show_annotations
    
    def next_image(self,caller=None):
        self.image_index += 1
        self.image_index = min(self.image_index,len(CLASSES.get(self.name).image_paths)-1)
        self.image_path = CLASSES.get(self.name).image_paths[self.image_index]
        self.image = pygame.image.load(self.image_path)
        self.image = pygame.transform.scale(self.image,(self.w-100,self.h-100))
    def previous_image(self,caller=None):
        self.image_index -= 1
        self.image_index = max(self.image_index,0)
        self.image_path = CLASSES.get(self.name).image_paths[self.image_index]
        self.image = pygame.image.load(self.image_path)
        self.image = pygame.transform.scale(self.image,(self.w-100,self.h-100))
    
    def mark_image(self,caller=None):
        if self.image_index in CLASS_IMAGE_MENU.marked_image_indices:
            CLASS_IMAGE_MENU.marked_image_indices.remove(self.image_index)
        else:
            CLASS_IMAGE_MENU.marked_image_indices.append(self.image_index)
            
    def update(self):
        super().update()
        
        for e in EVENTS:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RIGHT:
                    self.next_image()
                elif e.key == pygame.K_LEFT:
                    self.previous_image()
                elif e.key == pygame.K_SPACE:
                    self.mark_image()
        
        if self.image_index in CLASS_IMAGE_MENU.marked_image_indices:
            self.mark_button.image = pygame.transform.scale(IMAGES.get("checked"),(80,80))
        else:
            self.mark_button.image = pygame.transform.scale(IMAGES.get("unchecked"),(80,80))
        
        for b in self.buttons:
            b.update()
    
    def draw_annotations(self,target):        
        if self.show_annotations:
            annotations_path =  os.path.splitext(self.image_path)[0] + ".txt"
            annotations = []
            if os.path.isfile(annotations_path):
                with open(annotations_path,'r') as txt:
                    for line in txt:
                        parts = line.strip().split()
                        if len(parts) == 5:  # YOLO format: class x_center y_center width height
                            cls_id = int(parts[0])
                            x_center = float(parts[1])*self.image.get_width()
                            y_center = float(parts[2])*self.image.get_height()
                            width = float(parts[3])*self.image.get_width()
                            height = float(parts[4])*self.image.get_height()
                            annotations.append((cls_id, x_center, y_center, width, height))
                            x = x_center - width//2
                            y = y_center - height//2
                            w = width
                            h = height
                            annotation_rect = pygame.Rect(x,y,w,h)
                            try:
                                color = pygame.Color(self.color_list[cls_id*10])
                            except: # Might go OOB in Color List, revert to white
                                color = pygame.Color("white")
                            pygame.draw.rect(target,color,annotation_rect,1)
                            blit_text(parts[0], x+6, y+6,fontsize=20,target=target)
    
    def draw(self):        
        super().draw()
        draw_image = self.image.copy()
        self.draw_annotations(draw_image)
        SCREEN.blit(draw_image,(self.x+self.border_thickness,self.y+self.border_thickness))
        
        for b in self.buttons:
            b.draw()
        
class Class_Dist_Menu(Menu):
    ACTIVE_MENU = None
    def __init__(self, x, y, w, h, name=""):
        super().__init__(x, y, w, h, name)
        Menu.ACTIVE_MENU = self
    
        # Get (name, size) pairs
        name_size_pairs = [(name, len(c.image_paths)) for name, c in CLASSES.items()]
    
        # Sort by size descending
        name_size_pairs.sort(key=lambda x: x[1], reverse=True)
    
        # Unzip sorted data
        self.class_names, self.class_sizes = zip(*name_size_pairs) if name_size_pairs else ([], [])
        
        self.buttons = []
        sort_alpha_button = Button(self.x+self.w-80-self.border_thickness, self.y+self.border_thickness+110,80,80,self.sort_alphabetically,IMAGES.get("sort_alphabetically"))
        sort_numer_button = Button(self.x+self.w-80-self.border_thickness, self.y+self.border_thickness+220,80,80,self.sort_numerically,IMAGES.get("sort_numerically"))
        self.buttons.append(sort_alpha_button)
        self.buttons.append(sort_numer_button)
        
    def sort_numerically(self,caller=None):
        # Get (name, size) pairs
        name_size_pairs = [(name, len(c.image_paths)) for name, c in CLASSES.items()]
    
        # Sort by size descending
        name_size_pairs.sort(key=lambda x: x[1], reverse=True)
    
        # Unzip sorted data
        self.class_names, self.class_sizes = zip(*name_size_pairs) if name_size_pairs else ([], [])
        
    def sort_alphabetically(self,caller=None):
        # Zip the names and sizes
        paired = list(zip(self.class_names, self.class_sizes))
        
        # Sort using natsorted by the class name
        sorted_paired = natsorted(paired, key=lambda x: x[0])
        
        # Unzip back into names and sizes
        self.class_names, self.class_sizes = zip(*sorted_paired) if sorted_paired else ([], [])

    def update(self):
        super().update()
        self.close_button.update()
    
    def draw_plot(self):    
        chart_margin = 40           # More space for labels
        label_space = 80            # Space at bottom for rotated labels
        top_margin = 40             # Space at top for bar values
        max_bar_height = self.h - label_space - top_margin - chart_margin
    
        if not self.class_sizes or not self.class_names:
            return
    
        # Background & border
        chart_area = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(SCREEN, pygame.Color("black"), chart_area)
        pygame.draw.rect(SCREEN, pygame.Color("gray"), chart_area, 2)
    
        max_value = max(self.class_sizes)
        if max_value == 0:
            return
    
        # Font sizing
        font_size = max(32, min(20, self.w // max(20, len(self.class_names))))  # adapt font size
        font = pygame.font.Font(None, font_size)
    
        num_classes = len(self.class_sizes)
        total_space = self.w - 2 * chart_margin
        space_per_bar = total_space // num_classes
        bar_width = max(6, min(space_per_bar - 10, 30))
        padding = max(4, space_per_bar - bar_width)
    
        start_x = self.x + chart_margin
        base_y = self.y + top_margin + max_bar_height
    
        for i, (name, size) in enumerate(zip(self.class_names, self.class_sizes)):
            x = start_x + i * (bar_width + padding)
            bar_height = int((size / max_value) * max_bar_height)
            y = base_y - bar_height
    
            # Draw bar
            bar_rect = pygame.Rect(x, y, bar_width, bar_height)
            pygame.draw.rect(SCREEN, pygame.Color("dodgerblue"), bar_rect)
    
            # Value above bar (ensure it doesn't go off screen)
            value_text = font.render(str(size), True, pygame.Color("white"))
            value_y = max(self.y + 5, y - value_text.get_height() - 2)
            SCREEN.blit(value_text, (
                x + bar_width // 2 - value_text.get_width() // 2, 
                value_y
            ))
    
            # Draw rotated class label below bar
            label = name if len(name) <= 12 else name[:10] + "…"
            label_surf = font.render(label, True, pygame.Color("white"))
            label_rotated = pygame.transform.rotate(label_surf, 60)
            label_rect = label_rotated.get_rect()
            label_rect.center = (x + bar_width // 2, base_y + label_rect.height // 2 + 10)
            SCREEN.blit(label_rotated, label_rect.topleft)

    
    def draw(self):
        
        super().draw()
        self.draw_plot()        
        
        blit_text("Class Distribution Chart",self.x+self.w//2,self.y+self.border_thickness+5,fontsize=32)
        
        self.draw_buttons()
        self.close_button.draw()
        

class Class_Image_Menu:
    class_image_menu_shown = False  
    def __init__(self, x, y, w, h, selected_class):        
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.name = selected_class.class_name
        self.image_paths = selected_class.image_paths
        self.images = []
        self.remove_buttons = []
        self.marked_image_indices = []
        self.mark_buttons = []
        self.image_paths = natsorted(self.image_paths)
        for image_path in self.image_paths:
            try:
                img = pygame.image.load(image_path)
                img = pygame.transform.scale(img, (100, 100))
                remove_button = Button(0,0,25,25,self.delete_image,IMAGES.get("remove"),image_path,show_name=False)
                mark_button = Button(0,0,25,25,self.mark_image,IMAGES.get("checked"),image_path,show_name=False)
                self.remove_buttons.append(remove_button)
                self.images.append(img)
            except Exception as e:
                print(f"Error loading image: {image_path} -> {e}")
                
        
        self.mark_buttons = []
        for image_path in self.image_paths:
            mark_button = Button(0, 0, 25, 25, self.mark_image, IMAGES.get("checked"), image_path, show_name=False)
            self.mark_buttons.append(mark_button)
        
        self.archive = {
            "paths": [],
            "images": [],
            "remove_buttons": [],
            "mark_buttons": []
        }
        self.archive["paths"].append(self.image_paths.copy())
        self.archive["images"].append(self.images.copy())
        self.archive["remove_buttons"].append(self.remove_buttons.copy())
        self.archive["mark_buttons"].append(self.mark_buttons.copy())
        
        self.archive_length_at_last_save = len(self.archive["paths"])


        # layout config
        self.padding = 10
        self.border_thickness = 5
        self.bg_color = pygame.Color('black')
        self.border_color = pygame.Color('gray')
        
        Class_Image_Menu.class_image_menu_shown = True
        self.buttons = []
        #def __init__(self,x,y,w,h,callback,image,name="",class_path=None):
        self.close_button = Button(self.x+self.w-100,20,80,80,self.close,IMAGES.get("close"))
        self.save_button = Button(self.x+self.w-100,130,80,80,self.save_class,IMAGES.get("save"),name=selected_class.class_name,show_name=False)
        self.undo_button = Button(self.x+self.w-100,240,80,80,self.undo,IMAGES.get("undo"),name="undo",show_name=False)
        self.move_button = Button(self.x+self.w-100,350,80,80,self.move_images,IMAGES.get("move"),name="move",show_name=False)
        self.copy_button = Button(self.x+self.w-100,460,80,80,self.copy_images,IMAGES.get("copy"),name="copy",show_name=False)
        self.buttons.append(self.close_button)
        self.buttons.append(self.save_button)
        self.buttons.append(self.undo_button)
        self.buttons.append(self.move_button)
        self.buttons.append(self.copy_button)
        MENUS.append(self)
        self.start_y = self.y
        self.debounce = 0.5
        self.last_click = time.time()
        self.image_marker = None
        self.image_draw_rects = []
    
    def remove_from_list(self, indices, a_list):
        curr_list = a_list.copy()
        for i in sorted(indices, reverse=True):
            del curr_list[i]
        return curr_list
    
    def copy_images(self,caller=None):
        paths_to_copy = [self.image_paths[i] for i in self.marked_image_indices]
        
        choices = list(CLASSES.keys())
        target_class_name = easygui.choicebox("Select a target class:", "Class Selection", choices)
        if target_class_name == None:
            return
        
        target_class = CLASSES.get(target_class_name)
        target_class.image_paths.extend(paths_to_copy)        
        
        self.marked_image_indices = []
    
    def move_images(self,caller=None):
        indices_to_move = self.marked_image_indices
        #images_to_move = [self.images[i] for i in self.marked_image_indices]
        paths_to_move = [self.image_paths[i] for i in self.marked_image_indices]
        
        choices = list(CLASSES.keys())
        target_class_name = easygui.choicebox("Select a target class:", "Class Selection", choices)
        if target_class_name == None:
            return
        
        target_class = CLASSES.get(target_class_name)
        source_class = CLASSES.get(self.name)
        #target_class.images.extend(images_to_move)
        target_class.image_paths.extend(paths_to_move)
        source_class.image_paths = self.remove_from_list(indices_to_move,source_class.image_paths)
        
        self.image_paths = self.remove_from_list(indices_to_move,self.image_paths)
        self.images = self.remove_from_list(indices_to_move,self.images)
        self.remove_buttons = self.remove_from_list(indices_to_move,self.remove_buttons)
        self.mark_buttons = self.remove_from_list(indices_to_move,self.mark_buttons)
        
        
        self.marked_image_indices = []
        target_class.save()
        target_class.image_paths = target_class._get_image_paths()
    
    def mark_image(self,caller=None):
        idx = self.image_paths.index(caller.name)
        if idx in self.marked_image_indices:
            self.marked_image_indices.remove(idx)
        else:
            self.marked_image_indices.append(idx)
    
    def save_class(self,caller=None):
        new_folder_name = self.name
        new_folder_path = os.path.join(MAIN_FOLDER_PATH,new_folder_name)
        class_to_save = CLASSES.get(self.name)
        images_to_save = class_to_save.image_paths
        images_to_save = self.image_paths
        if not os.path.exists(new_folder_path):
            os.mkdir(new_folder_path)
        # Copy all images from images_to_save into the new folder
        # Copy images
        for image_path in images_to_save:
            filename = os.path.basename(image_path)
            dest_path = os.path.join(new_folder_path, filename)
        
            # Avoid overwriting existing files (optional)
            if not os.path.exists(dest_path):
                shutil.copy2(image_path, dest_path)
            else:
                print(f"Skipped: {filename} (already exists)")
        # List files currently in the destination folder
        target_file_list = os.listdir(new_folder_path)
    
        # Build a set of filenames that *should* be there
        valid_filenames = set(os.path.basename(p) for p in images_to_save)
    
        # Delete any files in the folder that are NOT in images_to_save
        for file in target_file_list:
            if file not in valid_filenames:
                try:
                    os.remove(os.path.join(new_folder_path, file))
                    print(f"Deleted: {file} (not in source list)")
                except Exception as e:
                    print(f"Error deleting {file}: {e}")
        
            ####
        self.archive_length_at_last_save = len(self.archive["paths"])
        easygui.msgbox(f"Class: {self.name} saved under {new_folder_path}")
    
    def undo(self,caller):
        if self.last_click+self.debounce < time.time():
            if not self.archive["paths"]:
                print("Nothing to undo.")
                return
            self.image_paths = self.archive["paths"].pop()
            self.images = self.archive["images"].pop()
            self.remove_buttons = self.archive["remove_buttons"].pop()
            self.mark_buttons = self.archive["mark_buttons"].pop()
            self.last_click = time.time()
    
    def fill_archive(self):
        self.archive["paths"].append(self.image_paths.copy())
        self.archive["images"].append(self.images.copy())
        self.archive["remove_buttons"].append(self.remove_buttons.copy())
        self.archive["mark_buttons"].append(self.mark_buttons.copy())
    
    def delete_image(self,caller):
        if self.last_click+self.debounce < time.time():
            self.fill_archive()
            
            idx = self.image_paths.index(caller.name)
            self.images.remove(self.images[idx])
            self.image_paths.remove(caller.name)
            
            self.remove_buttons.remove(caller)
            self.mark_buttons.remove(self.mark_buttons[idx])
            self.image_draw_rects.remove(self.image_draw_rects[idx])
            self.last_click = time.time()
            self.image_marker = None
            if idx in self.marked_image_indices:
                self.marked_image_indices.remove(idx)
                
            # Move Marked Indices that are smaller than the deleted one -1
            for i in range(len(self.marked_image_indices)):
                if self.marked_image_indices[i] > idx:
                    self.marked_image_indices[i] -= 1
    
    def enlarge_image(self, x, y, w, h, image_path):
        if self.last_click + self.debounce < time.time():
            if Menu.ACTIVE_MENU is None and time.time() - Menu.LAST_MENU_CLOSE_TIME > 0.2:
                self.last_click = time.time()
                Magnify_Image_Menu(x, y, w, h, image_path, name=self.name)
    
    def update(self):
        if Menu.ACTIVE_MENU == None:
            for b in self.buttons:
                b.update()
            for b in self.remove_buttons:
                b.update()
            for b in self.mark_buttons:
                b.update()
                
            for event in EVENTS:
                if event.type == pygame.MOUSEWHEEL:
                    if event.y < 0:
                        self.start_y -= 15
                    elif event.y > 0:
                        self.start_y += 15
        
            self.image_marker = None
            mouse_pos = pygame.mouse.get_pos()
            for image_rect in  self.image_draw_rects:
                if image_rect.collidepoint(mouse_pos):
                    self.image_marker = image_rect
                    
            if self.image_marker is not None:    
                curr_idx = self.image_draw_rects.index(self.image_marker)
                if self.image_marker.collidepoint(mouse_pos) and not self.mark_buttons[curr_idx].rect.collidepoint(mouse_pos):
                    if pygame.mouse.get_pressed()[0]:
                        img_path = self.image_paths[self.image_draw_rects.index(self.image_marker)]
                        self.enlarge_image(self.x+self.w//2-300, self.y+self.h//2-300, 600, 600, img_path)
    
    def close(self,caller=None):
        Class_Image_Menu.class_image_menu_shown = False
        if Menu.ACTIVE_MENU is not None:
            Menu.ACTIVE_MENU.close()
        MENUS.remove(self)
        global TIME_LAST_MENU_CLOSED
        TIME_LAST_MENU_CLOSED = time.time()
    
    def draw(self):
        # Draw background
        menu_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(SCREEN, self.bg_color, menu_rect)

        # Draw border around menu
        pygame.draw.rect(SCREEN, self.border_color, menu_rect, self.border_thickness)

        # Calculate grid positions
        self.image_draw_rects = []
        images_per_row = max(1, (self.w - 2 * self.border_thickness) // (100 + self.padding))
        
        for i, img in enumerate(self.images):
            row = i // images_per_row
            col = i % images_per_row

            img_x = self.x + self.border_thickness + col * (100 + self.padding)
            img_y = self.start_y + self.border_thickness + row * (100 + self.padding) +100
            image_draw_rect = img.get_rect()
            image_draw_rect.topleft = (img_x,img_y)
            self.image_draw_rects.append(image_draw_rect)
            
            self.remove_buttons[i].x,self.remove_buttons[i].y = img_x, img_y
            self.remove_buttons[i].rect.topleft = (img_x,img_y)
            
            self.mark_buttons[i].x,self.remove_buttons[i].y = img_x, img_y
            self.mark_buttons[i].rect.topright = (img_x+100,img_y)
            # Stop drawing if image goes outside the menu height
            #if img_y + 100 > self.y + self.h - self.border_thickness:
                #break
            if img_y > self.y + self.border_thickness and img_y + 100 < self.y + self.h - self.border_thickness:                
                SCREEN.blit(img, image_draw_rect)                
                self.remove_buttons[i].draw()
                self.mark_buttons[i].draw()
            
            
            
        
        for b in self.buttons:
            b.draw()
        for b in self.remove_buttons:
            pass
            #b.draw()
        
        if self.image_marker is not None:
            pygame.draw.rect(SCREEN,pygame.Color("white"),self.image_marker,2)
        
        for idx in self.marked_image_indices:
            rect = self.image_draw_rects[idx]
            pygame.draw.rect(SCREEN,pygame.Color("green"),rect,2)
        
        blit_text(self.name, self.w//2, self.y+10,fontsize=32)
 
class Button:
    SELECTED_BUTTON = None
    def __init__(self,x,y,w,h,callback,image,name="",class_path=None,show_name=True):
        self.x = x
        self.y = y        
        self.w = w
        self.h = h
        self.image = image
        self.image = pygame.transform.scale(self.image,(self.w,self.h))
        self.rect = self.image.get_rect(topleft = (self.x,self.y))
        self.color = pygame.Color("white")
        self.callback = callback
        self.hovered = False
        self.clicked = False
        self.getting_dragged = False
        self.name = name
        self.show_name = show_name
        self.class_path = None
        self.debounce = 0.500 #s
        self.last_click = time.time()
        self.start_drag_x = None
        self.start_drag_y = None
        self.angle = 0
        
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_1_clicked = pygame.mouse.get_pressed()[0]
        mouse_2_clicked = pygame.mouse.get_pressed()[2]
        if self.rect.collidepoint(mouse_pos):
            self.hovered = True
        else:
            self.hovered = False
            
        if self.hovered and mouse_1_clicked and self.last_click + self.debounce < time.time():
            self.last_click = time.time()
            self.callback(self)
            
        if self.hovered and mouse_2_clicked:
            if Button.SELECTED_BUTTON == None:
                self.getting_dragged = True
                Button.SELECTED_BUTTON = self
                self.start_drag_x = mouse_pos[0]
                self.start_drag_y = mouse_pos[1]
        # Right-click released: perform drop check once
        if not mouse_2_clicked and self.getting_dragged:
            self.getting_dragged = False
            if Button.SELECTED_BUTTON == self:
                Button.SELECTED_BUTTON = None
    
            # Only check collision ONCE here
            for b in CLASS_FOLDER_BUTTONS:
                if b is not self and b.rect.collidepoint(self.rect.center) and self in CLASS_FOLDER_BUTTONS:
                    easygui.msgbox(f"Copying Images into class: {b.name}")
                    self.x = self.start_drag_x
                    self.y = self.start_drag_y
                    self.rect.center = (self.x,self.y)
                    source_class = CLASSES.get(self.name)
                    target_class = CLASSES.get(b.name)
                    target_class.image_paths.extend(source_class.image_paths)
                    break
        
                
        
        
        if self.getting_dragged:
            self.x = mouse_pos[0]
            self.y = mouse_pos[1]
            self.rect.center = (self.x,self.y)
            self.color = pygame.Color("red")
        else:
            self.color = pygame.Color("white")
            
    def draw(self):
        SCREEN.blit(self.image,self.rect)
        hover_rect = pygame.Rect(self.x,self.y,self.w,self.h)
        hover_rect.center = self.rect.center
        if self.hovered and not self.getting_dragged:                        
            pygame.draw.rect(SCREEN,self.color,hover_rect,2)
        elif self.getting_dragged:
            pygame.draw.rect(SCREEN,self.color,hover_rect,2)
        if self.show_name:
            blit_text(self.name,self.rect.centerx,self.rect.centery,color=pygame.Color("black"))

#%% Helper Functions         
def get_class_names_from_main_folder():
    

    for name in os.listdir(MAIN_FOLDER_PATH):
        folder_path = os.path.join(MAIN_FOLDER_PATH, name)
        if os.path.isdir(folder_path):
            CLASS_NAMES.append(name)
            CLASS_PATHS[name] = folder_path
            CLASS_CONTENTS[name] = os.listdir(folder_path)
            CLASSES[name] = Class(name,folder_path)
            
            
def create_class_folder_buttons():
    global CLASS_FOLDER_BUTTONS
    CLASS_FOLDER_BUTTONS = []
    draw_area_x_min = 100
    draw_area_x_max = 900
    draw_area_y_min = 100
    draw_area_y_max = 30000

    area_width = draw_area_x_max - draw_area_x_min
    area_height = draw_area_y_max - draw_area_y_min

    button_width = 100
    button_height = 100
    padding = 20  # space between buttons

    # Calculate how many buttons fit per row
    buttons_per_row = max(1, area_width // (button_width + padding))
    CLASS_NAMES = CLASSES.keys()
    for i, name in enumerate(CLASS_NAMES):
        row = i // buttons_per_row
        col = i % buttons_per_row

        x = draw_area_x_min + col * (button_width + padding)
        y = draw_area_y_min + row * (button_height + padding)

        # Ensure we don't exceed area height
        if y + button_height > draw_area_y_max:
            break  # stop creating buttons if no more vertical space

        b = Button(
            x, y, button_width, button_height,
            open_class_image_window, IMAGES.get("folder"),name=name
        )
        CLASS_FOLDER_BUTTONS.append(b)


def blit_text(text, x, y, font=None, fontsize=16, color=pygame.Color("white"),target=None):
    if target is None:
        target = SCREEN
    if font is None:
        font = pygame.font.Font(None, fontsize)  # Default font with given size
    # Render the text
    font_surface = font.render(text, True, color)
    # Center the text at (x, y)
    font_rect = font_surface.get_rect(center=(x, y))
    font_rect.centerx = x
    font_rect.top = y
    # Blit to the screen
    target.blit(font_surface, font_rect)

def load_images():
    global IMAGES
    IMAGES = {"folder": pygame.image.load("assets/folder.png").convert_alpha(),
              "close": pygame.image.load("assets/close.png").convert_alpha(),
              "add":pygame.image.load("assets/add.png").convert_alpha(),
              "save":pygame.image.load("assets/save.png").convert_alpha(),
              "remove":pygame.image.load("assets/remove.png").convert_alpha(),
              "undo":pygame.image.load("assets/undo.png").convert_alpha(),
              "barplot":pygame.image.load("assets/barplot.png").convert_alpha(),
              "sort_alphabetically":pygame.image.load("assets/sort_alphabetically.png").convert_alpha(),
              "sort_numerically":pygame.image.load("assets/sort_numerically.png").convert_alpha(),
              "load":pygame.image.load("assets/load.png").convert_alpha(),
              "export":pygame.image.load("assets/export.png").convert_alpha(),
              "next":pygame.image.load("assets/next.png").convert_alpha(),
              "previous":pygame.image.load("assets/previous.png").convert_alpha(),
              "checked":pygame.image.load("assets/checked.png").convert_alpha(),
              "unchecked":pygame.image.load("assets/unchecked.png").convert_alpha(),
              "move":pygame.image.load("assets/move.png").convert_alpha(),
              "copy":pygame.image.load("assets/copy.png").convert_alpha(),
              "train":pygame.image.load("assets/train.png").convert_alpha(),
              "eye":pygame.image.load("assets/eye.png").convert_alpha()
              }

#%% Setup Functions  
def setup():    
    global MAIN_FOLDER_PATH
    MAIN_FOLDER_PATH = ""
    
    global TRAIN_PROCESS
    TRAIN_PROCESS = None
    
    global TRAIN_MESSAGE
    TRAIN_MESSAGE = None
    
    global Q
    Q = multiprocessing.Queue()
    
    global TIME_LAST_MENU_CLOSED, COOLDOWN_AFTER_MENU_CLOSE
    TIME_LAST_MENU_CLOSED = time.time()
    COOLDOWN_AFTER_MENU_CLOSE = 0.5
    
    global TRAINING_FLAG
    TRAINING_FLAG = multiprocessing.Value('b',False)
    
    global SCREEN, RUNNING    
    pygame.init()
    SCREEN = pygame.display.set_mode((1000,800))
    RUNNING = True   
    
    global CLOCK
    CLOCK = pygame.time.Clock()
    
    load_images()
            
    global CLASS_NAMES, CLASS_PATHS, CLASS_CONTENTS, CLASSES
    CLASS_NAMES = []
    CLASS_PATHS = {}
    CLASS_CONTENTS = {}
    CLASSES = {}
    
    global BUTTONS
    BUTTONS = []
    select_main_folder_button = Button(10,10,100,100,select_main_folder,IMAGES.get("folder"),name="Load")
    add_new_class_button = Button(890,700,100,100,add_new_class,IMAGES.get("add"))
    show_class_distribution_button = Button(890,590,100,100,show_class_dist_menu,IMAGES.get("barplot"))
    remove_class_button = Button(890,480,100,100,remove_class,IMAGES.get("remove"))
    save_classes_button = Button(890,370,100,100,save_created_classes,IMAGES.get("save"))
    load_folder_button = Button(890,260,100,100,load_folder,IMAGES.get("load"))
    export_button = Button(890,150,100,100,export_dataset,IMAGES.get("export"))
    train_button = Button(890,40,100,100,train_model,IMAGES.get("train"))
    BUTTONS.append(select_main_folder_button)
    BUTTONS.append(add_new_class_button)
    BUTTONS.append(show_class_distribution_button)
    BUTTONS.append(remove_class_button)
    BUTTONS.append(save_classes_button)
    BUTTONS.append(load_folder_button)
    BUTTONS.append(export_button)
    BUTTONS.append(train_button)
        
    global CLASS_FOLDER_BUTTONS
    CLASS_FOLDER_BUTTONS = []
        
    global MENUS
    MENUS = []
    
#%% Update Functions 

def update_menus():
    for m in MENUS:
        m.update()

def update_buttons():    
    for b in BUTTONS:
        b.update()
        
    for b in CLASS_FOLDER_BUTTONS:
        b.update()
        
    for e in EVENTS:
        if e.type == pygame.MOUSEWHEEL:
            if e.y < 0:
                for b in CLASS_FOLDER_BUTTONS:
                    b.rect.top -= 15
            elif e.y > 0:
                for b in CLASS_FOLDER_BUTTONS:
                    b.rect.top += 15
         

def update():
    global RUNNING, EVENTS, TRAIN_MESSAGE
    EVENTS = pygame.event.get()
    for event in EVENTS:
        if event.type == pygame.QUIT:
            RUNNING = False
    
    update_menus()
    
    if len(MENUS) == 0 and TIME_LAST_MENU_CLOSED+COOLDOWN_AFTER_MENU_CLOSE < time.time():
        update_buttons()
        
    # Print logs as they come in
    if TRAIN_PROCESS is not None:
        if TRAIN_PROCESS.is_alive() or not Q.empty():
            try:
                TRAIN_MESSAGE = Q.get(timeout=0.01)                
                print(TRAIN_MESSAGE, end="")
            except:
                pass
    
    
    
#%% Draw Functions 
def draw_menus():
    for m in MENUS:
        m.draw()

def draw_buttons():
    if TRAINING_FLAG.value == True:
        train_button = BUTTONS[7]
        train_button.angle -= 7
        img = pygame.transform.scale(IMAGES.get("train"),(100,100))
        img = pygame.transform.rotate(img,train_button.angle)
        old_center = train_button.rect.center
        train_button.image = img
        train_button.rect = train_button.image.get_rect()
        train_button.rect.center = old_center
    else:
        train_button = BUTTONS[7]
        train_button.angle = 0
        img = pygame.transform.scale(IMAGES.get("train"),(100,100))
        img = pygame.transform.rotate(img,train_button.angle)  
        old_center = train_button.rect.center
        train_button.image = img
        train_button.rect = train_button.image.get_rect()
        train_button.rect.center = old_center
        
    for b in BUTTONS:
        b.draw()
    for b in CLASS_FOLDER_BUTTONS:
        b.draw()
        

def draw():
    SCREEN.fill(pygame.Color("black"))
    blit_text("AI Class Creator",SCREEN.get_width()//2,0,fontsize=32)
    if len(MENUS) == 0:
        draw_buttons()
    draw_menus()
    if TRAIN_MESSAGE and TRAINING_FLAG.value:
        blit_text(TRAIN_MESSAGE, SCREEN.get_width()//2, SCREEN.get_height()-10,fontsize=16)
    pygame.display.flip()
    CLOCK.tick(60)
    

#%% Main Function     
def main():
    setup()
    while RUNNING:
        update()
        draw()
    pygame.quit()
    
    
if __name__ == "__main__":
    main()