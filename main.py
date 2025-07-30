# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 12:59:52 2025

@author: BLorber

Bachelorarbeit Lorber
"""

import tkinter as tk
from tkinter import ttk
from tkinter import ALL  # Import ALL for scaling
from tkinter import messagebox, Message, filedialog, Checkbutton, Scale
import tkinter.messagebox as messagebox  # Make sure this is imported
from tkinter import PhotoImage
import tkinter.font as tkFont
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
import AVAW_CVAT_BBOX_OOP
from AVAW_CVAT_BBOX_OOP import BBOX_App



#%% -------------------- Space for variables --------------------


# ---------------------------------------------------------------

#%% -------------------- Class for Interface/Buttons/GUI ----------------
class GUI:
    #Seg App = 1, BBox APP = 2

    def __init__(self, app, root):
        self.app = app 
        self.root = root
        self.image = None  # Hier wird das Bild gespeichert
        self.create_gui()
        
    def create_gui(self):
        canvas = tk.Canvas(self.root, width=400, height=300, bg="white")
        canvas.pack()

        try:
            self.image = tk.PhotoImage(file="MUL-logo.png")  # Als Instanzvariable speichern
            canvas.create_image(200, 150, image=self.image, anchor="center")
        except:
            canvas.create_text(200, 150, text="Kein Bild geladen", fill="black")
        
        # Rest des Codes bleibt gleich...
        
        
        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        
        class_names = ["Option 1", "Option 2", "Option 3"]
        selected = tk.StringVar()
        dropdown = ttk.Combobox(buttons_frame, textvariable=selected, values=class_names, state="readonly")
        dropdown.current(0)
        dropdown.grid(row=0, column=1, padx=5, pady=5)
        
        # Zweite Zeile - Buttons
        anno_button = tk.Button(buttons_frame, text="Annotate Image (space)")
        anno_button.grid(row=1, column=0, padx=5, pady=5)
        
        if self.app == 1:
            simply_button = tk.Button(buttons_frame, text="Simplify Image (B)")
            simply_button.grid(row=1, column=1, padx=5, pady=5)
        else:
            simply_button = tk.Label(buttons_frame)
            simply_button.grid(row=1, column=1, padx=5, pady=5)
        
        save_button = tk.Button(buttons_frame, text="Save Annotation (S)")
        save_button.grid(row=1, column=2, padx=5, pady=5)
        
        # Dritte Zeile - Slider
        slider_value = tk.DoubleVar(value=0.5)
        slider = tk.Scale(buttons_frame,
                          from_=0.0,
                          to=1.0,
                          resolution=0.1,
                          orient='horizontal',
                          variable=slider_value,
                          length=150)
        slider.grid(row=2, column=1, padx=5, pady=5)
        
        # Vierte Zeile - Navigation
        prev_button = tk.Button(buttons_frame, text="Previous Image (<-)")
        prev_button.grid(row=3, column=0, padx=5, pady=5)
        
        jump_button = tk.Button(buttons_frame, text="Jump to Image")
        jump_button.grid(row=3, column=1, padx=5, pady=5)
        
        next_button = tk.Button(buttons_frame, text="Next Image (->)")
        next_button.grid(row=3, column=2, padx=5, pady=5)
        
        # Fünfte Zeile - Eingabe
        number = tk.StringVar(value="0")
        img_number = tk.Entry(buttons_frame, textvariable=number, justify="center")
        img_number.grid(row=4, column=1, padx=5, pady=5)
        
        # Sechste Zeile - Undo
        undo_button = tk.Button(buttons_frame, text="Undo (Z)")
        undo_button.grid(row=5, column=1, padx=5, pady=5)
        
        # Grid-Konfiguration für gleichmäßige Spalten
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        buttons_frame.grid_columnconfigure(2, weight=1)
    

    def choose_class():
        return 0
    
    def annotate_img():
        return 0
    
    def simplify_annotation():
        return 0
        
    def save_annotation():
        return 0 
    
    def set_vertex_threshold():
        return 0
    
    def prev_img():
        return 0
    
    def jump_to_img():
        return 0
    
    def next_img():
        return 0
    
    def undo():
        return 0
    
        

#%% -------------------- Initialize app --------------------------
def initialize_app(image_path):
    global bu_root
    
    # Create Window for Boot-Up
    bu_root = tk.Tk()
    
    bu_root.title("Classification application for object recognition and annotation")    
    bu_root.geometry("600x300")
    bu_root.resizable(False, False)
    
    try:
        p1 = tk.PhotoImage(file = 'MUL-logo.png') 
        bu_root.iconphoto(False,p1)
    except:
        print("No Custom Logo Found - Using TKinter Standard")
    bu_root.iconbitmap('MUL-logo.ico')
    
    
    
    # Space for the MUL logo
    image_frame = tk.Frame(bu_root)
    image_frame.pack(side=tk.TOP, fill="both", expand=True)
    image_path = "MUL-logo.png"
    image = Image.open(image_path)
    image = image.resize((120, 80))
    photo = ImageTk.PhotoImage(image)
    label_img = tk.Label(image_frame, image=photo)
    label_img.image = photo  # Referenz behalten!
    label_img.pack(expand=True)

    # Create text for Boot-Up
    header_font = tkFont.Font(family="Arial", size=24)
    header = tk.Label(bu_root, text="Choose your application!",font=header_font)
    header.pack(pady=5)
    
    
    # Create Buttons for Boot-Up
    choose_app_frame = tk.Frame(bu_root)
    choose_app_frame.pack(fill=tk.X, pady=20)
    
    spacer_left = tk.Label(choose_app_frame)
    spacer_left.pack(side="left", expand=True)
    
    seg_button = tk.Button(choose_app_frame, text="Segmentation APP", width=25, height=2, command=start_old_seg)
    seg_button.pack(side="left", padx=20)
    
    spacer_middle = tk.Label(choose_app_frame)
    spacer_middle.pack(side="left", expand=True)
    
    spacer_right = tk.Label(choose_app_frame)
    spacer_right.pack(side="right", expand=True)
    
    bbox_button = tk.Button(choose_app_frame, text="Boundingbox APP", width=25, height=2,  command=start_old_bbox)
    bbox_button.pack(side="right", padx=20)
    
    
    
    
    # Start application and wait for user input
    bu_root.mainloop() 
    
def start_old_bbox():
    BBOX_App(bu_root)

def start_old_seg():
    from AVAW_CVAT_SEG_OOP import initialize_app
    initialize_app(None,None,bu_root)
    
def start_seg_app(bu_root):

    seg_root = tk.Toplevel(bu_root)
    seg_root.title("Segmentation Application")
    seg_root.geometry("1000x1000")
    seg_root.minsize(750, 900)
    
    label = tk.Label(seg_root, text="Ready for segmentation?")
    label.pack(pady=20)
    btn_schliessen = tk.Button(seg_root, text="Schließen", command=seg_root.destroy)
    btn_schliessen.pack(pady=10)
    buttons = GUI(1, seg_root)
    

def start_bbox_app(bu_root):

    bbox_root = tk.Toplevel(bu_root)
    bbox_root.title("Bounding Box Application")
    bbox_root.geometry("1000x1000")
    bbox_root.minsize(750, 900)
    
    label = tk.Label(bbox_root, text="Ready for the Boxes?")
    label.pack(pady=20)
    btn_schliessen = tk.Button(bbox_root, text="Schließen", command=bbox_root.destroy)
    btn_schliessen.pack(pady=10)
    buttons = GUI(2,bbox_root)
    
    
# Run the application
initialize_app("logo.png")



        
        
        
    
    