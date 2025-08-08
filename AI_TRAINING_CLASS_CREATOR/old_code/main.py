# -*- coding: utf-8 -*-
"""
Created on Wed Aug  6 13:58:56 2025

@author: GKoinig
"""

import pygame
import os
###
#%% Button Callbacks
import easygui

def add_new_class():
    new_class_name = easygui.enterbox("Enter new class name:")
    if new_class_name:  # If user didn't cancel
        new_class_path = os.path.join(MAIN_FOLDER_PATH, new_class_name)
        if not os.path.exists(new_class_path):
            os.makedirs(new_class_path)
            print(f"Class '{new_class_name}' created at {new_class_path}")
        else:
            easygui.msgbox(f"Class '{new_class_name}' already exists!")

def select_main_folder(caller=None):
    global MAIN_FOLDER_PATH
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
        CLASS_IMAGE_MENU = Class_Image_Menu(10, 10, 980, 880, caller.name)

#%% Classes
class Class:
    def __init__(self, class_name, image_paths):
        self.class_name = class_name
        self.image_paths = image_paths

class Class_Image_Menu:
    class_image_menu_shown = False  
    def __init__(self, x, y, w, h, class_name):        
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.class_name = class_name
        self.class_path = CLASS_PATHS.get(self.class_name)

        self.image_paths = [os.path.join(self.class_path, img) for img in os.listdir(self.class_path)]
        self.images = []
        for image_path in self.image_paths:
            img = pygame.image.load(image_path)
            img = pygame.transform.scale(img, (100, 100))
            self.images.append(img)

        # layout config
        self.padding = 10
        self.border_thickness = 5
        self.bg_color = pygame.Color('black')
        self.border_color = pygame.Color('gray')
        
        Class_Image_Menu.class_image_menu_shown = True
        self.buttons = []
        #def __init__(self,x,y,w,h,callback,image,name="",class_path=None):
        self.close_button = Button(self.x+self.w-100,10,80,80,self.close,IMAGES.get("close"))
        self.buttons.append(self.close_button)
        BUTTONS.remove(self.close_button)
        MENUS.append(self)
        self.start_y = self.y
    
    def update(self):
        for b in self.buttons:
            b.update()
        for event in EVENTS:
            if event.type == pygame.MOUSEWHEEL:
                if event.y < 0:
                    self.start_y -= 5
                elif event.y > 0:
                    self.start_y += 5
    
    def close(self,caller=None):
        Class_Image_Menu.class_image_menu_shown = False
        MENUS.remove(self)
    
    def draw(self):
        # Draw background
        menu_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(SCREEN, self.bg_color, menu_rect)

        # Draw border around menu
        pygame.draw.rect(SCREEN, self.border_color, menu_rect, self.border_thickness)

        # Calculate grid positions
        images_per_row = max(1, (self.w - 2 * self.border_thickness) // (100 + self.padding))
        
        for i, img in enumerate(self.images):
            row = i // images_per_row
            col = i % images_per_row

            img_x = self.x + self.border_thickness + col * (100 + self.padding)
            img_y = self.start_y + self.border_thickness + row * (100 + self.padding)

            # Stop drawing if image goes outside the menu height
            if img_y + 100 > self.y + self.h - self.border_thickness:
                break

            SCREEN.blit(img, (img_x, img_y))
        
        for b in self.buttons:
            b.draw()
 
class Button:
    SELECTED_BUTTON = None
    def __init__(self,x,y,w,h,callback,image,name="",class_path=None):
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
        self.class_path = None
        
        BUTTONS.append(self)
        
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_1_clicked = pygame.mouse.get_pressed()[0]
        mouse_2_clicked = pygame.mouse.get_pressed()[2]
        if self.rect.collidepoint(mouse_pos):
            self.hovered = True
        else:
            self.hovered = False
            
        if self.hovered and mouse_1_clicked:
            self.callback(self)
            
        if self.hovered and mouse_2_clicked:
            if Button.SELECTED_BUTTON == None:
                self.getting_dragged = True
                Button.SELECTED_BUTTON = self
        else:
            self.getting_dragged = False
            if Button.SELECTED_BUTTON == self:
                Button.SELECTED_BUTTON = None
        
        
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
        blit_text(self.name,self.rect.centerx,self.rect.centery,color=pygame.Color("black"))

#%% Helper Functions         
def get_class_names_from_main_folder():
    global CLASS_NAMES, CLASS_PATHS, CLASS_CONTENTS

    CLASS_NAMES = []
    CLASS_PATHS = {}
    CLASS_CONTENTS = {}

    for name in os.listdir(MAIN_FOLDER_PATH):
        folder_path = os.path.join(MAIN_FOLDER_PATH, name)
        if os.path.isdir(folder_path):
            CLASS_NAMES.append(name)
            CLASS_PATHS[name] = folder_path
            CLASS_CONTENTS[name] = os.listdir(folder_path)
            CLASSES[name] = Class(name,os.listdir(folder_path))
            
            
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

def draw_class_folders():
    pass

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
              "add":pygame.image.load("add.png").convert_alpha()}

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
    add_new_class_button = Button(890,10,100,100,add_new_class,IMAGES.get("add"))
    BUTTONS.append(select_main_folder_button)
    BUTTONS.append(add_new_class_button)
        
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
    if len(MENUS) == 0:
        update_buttons()
    update_menus()
    
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