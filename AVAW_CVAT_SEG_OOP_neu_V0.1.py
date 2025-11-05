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


class GUI:
    def __init__(self, root):
        self.root = root
        self.img = None  # Wird das Pillow-Image halten
        self.tk_img = None
        self.create_gui()
        
    def create_gui(self):
        
       # Canvas erstellen
        canvas = tk.Canvas(self.root, width=640, height=640, bg="white") #Dinamisch an Bildgröße anpassen
        canvas.pack()

        # Bild mit Pillow laden und anzeigen
        try:
            # 1. Bild mit Pillow laden
            self.image = Image.open("MUL-logo.png")
            # 2. Optional skalieren
            self.image = self.image.resize((640, 500), Image.Resampling.LANCZOS)
            # 3. In Tkinter-Format konvertieren
            self.tk_image = ImageTk.PhotoImage(self.image)
            # 4. Im Canvas anzeigen
            canvas.create_image(320, 320, image=self.tk_image, anchor="center")
            
        except Exception as e:
            print(f"Fehler beim Laden des Bildes: {e}")
            canvas.create_text(200, 150, text="Kein Bild geladen", fill="black")
        
        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(side=tk.BOTTOM, anchor='center', pady=10)
        
        class_names = ["Option 1", "Option 2", "Option 3"]
        selected = tk.StringVar()
        dropdown = ttk.Combobox(buttons_frame, textvariable=selected, values=class_names, state="readonly")
        dropdown.current(0)  # Setzt die Standardauswahl
        dropdown.grid(row=0, column=1, padx=5, pady=5)
        
        anno_button = tk.Button(buttons_frame, text="Annotate Image (space)")# command=lambda: start_seg_app(bu_root))
        anno_button.grid(row=1, column=0, padx=5, pady=5)
        
        simply_button = tk.Button(buttons_frame, text="Simplify Image (B)")# command=lambda: start_seg_app(bu_root))
        simply_button.grid(row=1, column=1, padx=5, pady=5)
        
        save_button = tk.Button(buttons_frame, text="Save Annotation (S)")# command=lambda: start_seg_app(bu_root))
        save_button.grid(row=1, column=2, padx=5, pady=5)
        
        slider_value = tk.DoubleVar(value=0.5)
        slider = tk.Scale(buttons_frame,
                          from_=0.0,
                          to=1.0,
                          resolution=0.1,         # Schrittweite (z. B. 0.1)
                          orient='horizontal',    # horizontale Ausrichtung
                          variable=slider_value,  # Bindung an Variable
                          #command=print_value,    # Callback bei Veränderung
                          length=150)
        slider.grid(row=2, column=1, padx=5, pady=5)
        
        prev_button = tk.Button(buttons_frame, text="Previous Image (<-)")# command=lambda: start_seg_app(bu_root))
        prev_button.grid(row=3, column=0, padx=5, pady=5)
        
        
        jump_button = tk.Button(buttons_frame, text="Jump to Image")# command=lambda: start_seg_app(bu_root))
        jump_button.grid(row=3, column=1, padx=5, pady=5)
        
        next_button = tk.Button(buttons_frame, text="Next Image (->)")# command=lambda: start_seg_app(bu_root))
        next_button.grid(row=3, column=2, padx=5, pady=5)
        
        number = tk.StringVar(value="0")
        img_number = tk.Entry(buttons_frame, textvariable=number, justify="center")
        img_number.grid(row=4, column=1, padx=5, pady=5)
        
        undo_button = tk.Button(buttons_frame, text="Undo (Z)")# command=lambda: start_seg_app(bu_root))
        undo_button.grid(row=5, column=1, padx=5, pady=5)
        
        

class SEG_App:
    def __init__(self,caller_root=None):        
        
        if caller_root == None:
            self.root = tk.Tk()
        else:
            self.root = tk.Toplevel(caller_root)
        
        self.root.title("Segmentation Application")
        self.root.geometry("1000x1000")
        self.root.minsize(750, 900)
        self.root.iconbitmap('MUL-logo.ico')
        
        self.GUI = GUI(self.root)
        
    
    
        self.root.mainloop()
        
    def exit_app(self):
        self.root.destroy()

    
# Main function to browse and annotate images
def initialize_seg_app():
    SEG_APP = SEG_App()

if __name__ == "__main__":
    initialize_seg_app()
