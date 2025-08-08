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
###
#%% Button Callbacks

def save_created_classes(caller=None):
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

    selected = easygui.multchoicebox(
        msg="Select one or more classes to delete:",
        title="Delete Classes",
        choices=entries
    )

    if selected:
        for class_name in selected:
            # Remove from CLASSES and related global structures
            CLASSES.pop(class_name, None)
            CLASS_NAMES.remove(class_name) if class_name in CLASS_NAMES else None
            CLASS_PATHS.pop(class_name, None)
            CLASS_CONTENTS.pop(class_name, None)
        create_class_folder_buttons()
        easygui.msgbox(f"Deleted: {', '.join(selected)}")


def save_class(caller):
    new_folder_name = caller.name
    new_folder_path = os.path.join(MAIN_FOLDER_PATH,new_folder_name)
    class_to_save = CLASSES.get(caller.name)
    images_to_save = class_to_save.image_paths
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
        easygui.msgbox(f"Folder Set to:\n{MAIN_FOLDER_PATH}")
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
        return [
            os.path.join(self.folder_path, f)
            for f in os.listdir(self.folder_path)
            if f.lower().endswith(valid_ext)
        ]

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
        Menu.ACTIVE_MENU = None
        Menu.LAST_MENU_CLOSE_TIME = time.time()
        MENUS.remove(self)
        
class Magnify_Image_Menu(Menu):
    ACTIVE_MENU = None
    def __init__(self,x,y,w,h,image_path,name=""):
        super().__init__(x,y,w,h,name)
        Menu.ACTIVE_MENU = self
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image,(self.w-100,self.h-100))
    def draw(self):        
        super().draw()
        SCREEN.blit(self.image,(self.x+self.border_thickness,self.y+self.border_thickness))
        
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
        
        for image_path in self.image_paths:
            try:
                print("Loading image:", image_path)
                img = pygame.image.load(image_path).convert_alpha()
                img = pygame.transform.scale(img, (100, 100))
                remove_button = Button(0,0,25,25,self.delete_image,IMAGES.get("remove"),image_path,show_name=False)
                self.remove_buttons.append(remove_button)
                self.images.append(img)
            except Exception as e:
                print(f"Error loading image: {image_path} -> {e}")

        self.archive = {
            "paths": [],
            "images": [],
            "remove_buttons": []
        }
        self.archive["paths"].append(self.image_paths.copy())
        self.archive["images"].append(self.images.copy())
        self.archive["remove_buttons"].append(self.remove_buttons.copy())
        


        # layout config
        self.padding = 10
        self.border_thickness = 5
        self.bg_color = pygame.Color('black')
        self.border_color = pygame.Color('gray')
        
        Class_Image_Menu.class_image_menu_shown = True
        self.buttons = []
        #def __init__(self,x,y,w,h,callback,image,name="",class_path=None):
        self.close_button = Button(self.x+self.w-100,20,80,80,self.close,IMAGES.get("close"))
        self.save_button = Button(self.x+self.w-100,130,80,80,save_class,IMAGES.get("save"),name=selected_class.class_name,show_name=False)
        self.undo_button = Button(self.x+self.w-100,240,80,80,self.undo,IMAGES.get("undo"),name="undo",show_name=False)
        self.buttons.append(self.close_button)
        self.buttons.append(self.save_button)
        self.buttons.append(self.undo_button)
        MENUS.append(self)
        self.start_y = self.y
        self.debounce = 0.5
        self.last_click = time.time()
        self.image_marker = None
        self.image_draw_rects = []
    
    def undo(self,caller):
        if self.last_click+self.debounce < time.time():
            if not self.archive["paths"]:
                print("Nothing to undo.")
                return
            self.image_paths = self.archive["paths"].pop()
            self.images = self.archive["images"].pop()
            self.remove_buttons = self.archive["remove_buttons"].pop()
            self.last_click = time.time()
    
    def fill_archive(self):
        self.archive["paths"].append(self.image_paths.copy())
        self.archive["images"].append(self.images.copy())
        self.archive["remove_buttons"].append(self.remove_buttons.copy())
    
    def delete_image(self,caller):
        if self.last_click+self.debounce < time.time():
            self.fill_archive()
            
            idx = self.image_paths.index(caller.name)
            self.images.remove(self.images[idx])
            self.image_paths.remove(caller.name)
            self.remove_buttons.remove(caller)
            self.last_click = time.time()
            self.image_marker = None
    
    def enlarge_image(self, x, y, w, h, image_path):
        if self.last_click + self.debounce < time.time():
            if Menu.ACTIVE_MENU is None and time.time() - Menu.LAST_MENU_CLOSE_TIME > 0.2:
                self.last_click = time.time()
                Magnify_Image_Menu(x, y, w, h, image_path, name="")
    
    def update(self):
        if Menu.ACTIVE_MENU == None:
            for b in self.buttons:
                b.update()
            for b in self.remove_buttons:
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
                    break
            if self.image_marker is not None:    
                if image_rect.collidepoint(mouse_pos):
                    if pygame.mouse.get_pressed()[0]:
                        img_path = self.image_paths[self.image_draw_rects.index(self.image_marker)]
                        self.enlarge_image(self.x+self.w//2-300, self.y+self.h//2-300, 600, 600, img_path)
    
    def close(self,caller=None):
        Class_Image_Menu.class_image_menu_shown = False
        if Menu.ACTIVE_MENU is not None:
            Menu.ACTIVE_MENU.close()
        MENUS.remove(self)
    
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
            self.remove_buttons[i].x,self.remove_buttons[i].y = img_x, img_y
            self.remove_buttons[i].rect.topleft = (img_x,img_y)
            # Stop drawing if image goes outside the menu height
            if img_y + 100 > self.y + self.h - self.border_thickness:
                break
            if img_y > self.y + self.border_thickness:
                image_draw_rect = img.get_rect()
                image_draw_rect.topleft = (img_x,img_y)
                SCREEN.blit(img, image_draw_rect)
                self.image_draw_rects.append(image_draw_rect)
                self.remove_buttons[i].draw()
        
        for b in self.buttons:
            b.draw()
        for b in self.remove_buttons:
            pass
            #b.draw()
        
        if self.image_marker is not None:
            pygame.draw.rect(SCREEN,pygame.Color("white"),self.image_marker,2)
            
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
        
        #BUTTONS.append(self)
        
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
                if b is not self and b.rect.collidepoint(self.rect.center):
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
        if self.hovered and not self.getting_dragged:
            pygame.draw.rect(SCREEN,self.color,self.rect,2)
        elif self.getting_dragged:
            pygame.draw.rect(SCREEN,self.color,self.rect,2)
        if self.show_name:
            blit_text(self.name,self.rect.centerx,self.rect.centery,color=pygame.Color("black"))

#%% Helper Functions         
def get_class_names_from_main_folder():
    global CLASS_NAMES, CLASS_PATHS, CLASS_CONTENTS, CLASSES

    CLASS_NAMES = []
    CLASS_PATHS = {}
    CLASS_CONTENTS = {}
    CLASSES = {}

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
    draw_area_y_max = 800

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


def blit_text(text, x, y, font=None, fontsize=16, color=pygame.Color("white")):
    if font is None:
        font = pygame.font.Font(None, fontsize)  # Default font with given size
    # Render the text
    font_surface = font.render(text, True, color)
    # Center the text at (x, y)
    font_rect = font_surface.get_rect(center=(x, y))
    font_rect.centerx = x
    font_rect.top = y
    # Blit to the screen
    SCREEN.blit(font_surface, font_rect)

def load_images():
    global IMAGES
    IMAGES = {"folder": pygame.image.load("folder.png").convert_alpha(),
              "close": pygame.image.load("close.png").convert_alpha(),
              "add":pygame.image.load("add.png").convert_alpha(),
              "save":pygame.image.load("save.png").convert_alpha(),
              "remove":pygame.image.load("remove.png").convert_alpha(),
              "undo":pygame.image.load("undo.png").convert_alpha(),
              "barplot":pygame.image.load("barplot.png").convert_alpha(),
              "sort_alphabetically":pygame.image.load("sort_alphabetically.png").convert_alpha(),
              "sort_numerically":pygame.image.load("sort_numerically.png").convert_alpha()
              }

#%% Setup Functions  
def setup():
    global SCREEN, RUNNING    
    pygame.init()
    SCREEN = pygame.display.set_mode((1000,800))
    RUNNING = True   
    
    load_images()
    
    global MAIN_FOLDER_PATH
    MAIN_FOLDER_PATH = ""
    
    global BUTTONS
    BUTTONS = []
    select_main_folder_button = Button(10,10,100,100,select_main_folder,IMAGES.get("folder"))
    add_new_class_button = Button(890,700,100,100,add_new_class,IMAGES.get("add"))
    show_class_distribution_button = Button(890,590,100,100,show_class_dist_menu,IMAGES.get("barplot"))
    remove_class_button = Button(890,480,100,100,remove_class,IMAGES.get("remove"))
    save_classes_button = Button(890,370,100,100,save_created_classes,IMAGES.get("save"))
    BUTTONS.append(select_main_folder_button)
    BUTTONS.append(add_new_class_button)
    BUTTONS.append(show_class_distribution_button)
    BUTTONS.append(remove_class_button)
    BUTTONS.append(save_classes_button)
        
    global CLASS_FOLDER_BUTTONS
    CLASS_FOLDER_BUTTONS = []
    
    global CLASSES
    CLASSES = {}
    
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

def update():
    global RUNNING, EVENTS
    EVENTS = pygame.event.get()
    for event in EVENTS:
        if event.type == pygame.QUIT:
            RUNNING = False
    
    update_menus()
    
    if len(MENUS) == 0:
        update_buttons()
    
    
    
#%% Draw Functions 
def draw_menus():
    for m in MENUS:
        m.draw()

def draw_buttons():
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
    pygame.display.flip()

#%% Main Function     
def main():
    setup()
    while RUNNING:
        update()
        draw()
    pygame.quit()
    
    
if __name__ == "__main__":
    main()