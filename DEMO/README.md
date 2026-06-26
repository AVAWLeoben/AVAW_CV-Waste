# AVAW CVAT BBox Tool

A lightweight desktop GUI tool for creating, editing, and managing YOLO-style bounding box annotations.
Built with Tkinter, OpenCV, and Ultralytics for fast manual labeling and assisted annotation workflows.

---

## 📚 Demo

The DEMO section contains example datasets, usage instructions, and a step-by-step tutorial covering the main features of the tool, including:

- loading images and label folders
- creating and editing bounding boxes
- managing annotation classes
- loading YOLO models
- generating automatic predictions
- reviewing and correcting annotations
- exporting YOLO-compatible label files

The demo is intended to help new users get familiar with the interface and typical annotation workflow as quickly as possible.

---

## Installation Guide

Get started with **AVAW CV-Waste** using the visual installation guide below. It walks through the manual installation process step by step.

👉 [Open the visual installation guide](https://avawleoben.github.io/AVAW_CV-Waste/AVAW_CV-Waste_Install.html)

For Git- or Conda-based installation options, please refer to the repository installation instructions:

📦 [Open INSTALL instructions](https://github.com/AVAWLeoben/AVAW_CV-Waste/tree/JOSS-short-lived-branch/INSTALL)


## First Steps

Once the software is installed, the following guides introduce the basic workflow.


### Load a Model

This guide explains how to load an existing model into the application.

👉 [Open the Load Model guide](https://avawleoben.github.io/AVAW_CV-Waste/AVAW_CV-Waste_Load_Model.html)


### Load a Model and Perform a First Automatic Annotation

This guide shows how to load a model and use it to perform the first automatic annotation step.

👉 [Open the First Automatic Annotation guide](https://avawleoben.github.io/AVAW_CV-Waste/AVAW_CV-Waste_First_Automatic_Annotation.html)

---

## ⚙️ Configuration

The application can be customized to match your annotation workflow and project setup.

### 🏷️ Class Names

The available object classes are defined in:

```text
files_bbox/class_names.txt
```

Edit this file to specify the classes you want to use for annotation.

Use a comma-separated format such as:

```text
person,car,bicycle,dog
```

Each class will automatically appear in the application and can be selected while creating or editing bounding boxes.

You can customize this list at any time to match your dataset or project requirements.

---

### 💾 Settings

User-specific settings are stored in:

```text
settings.json
```

The application automatically saves important information between sessions, including:

- the last opened image index
- selected image and label folders
- the currently selected YOLO model path
- user interface preferences and window settings

This allows you to close and reopen the application without losing your workflow progress.

---

## 🧠 YOLO Model Support

The application supports loading YOLO models for automatic object detection and assisted annotation.

Currently supported:

- Ultralytics YOLO

YOLO model settings can be configured in the **Model Settings** window inside the application.

Typical model files use the `.pt` format and can be selected through the graphical interface.

Once a model is loaded, the application can generate bounding box predictions automatically, making it much faster to annotate large datasets.

## 🖱️ Basic Controls

| Action | Binding | Description |
|---|---|---|
| Select / interact with box | **Left Click** | Select an existing box or start interaction |
| Draw / drag | **Left Click + Drag** | Draw a new box, move a box, or resize a box depending on context |
| Finish drag/edit | **Left Button Release** | Finalize box creation, movement, or resizing |
| Multi-select | **Ctrl + Left Click** | Add boxes to the current multi-selection |
| Multi-drag | **Ctrl + Left Drag** | Move all currently selected boxes |
| Stop multi-select | **Ctrl + Right Click** | Clear/stop multi-selection |
| Context menu | **Right Click** | Open the context-sensitive menu |
| Context menu key | **Menu** on Linux/macOS, **App** on Windows | Open the context-sensitive menu via keyboard |
| Single-click prediction | **Alt + Left Click** or **Ctrl + Alt + Left Click** | Run prediction at the clicked position |
| Add new box | **n** or **↓ Down Arrow** | Enable creation of a new bounding box |
| Delete selected box | **Delete** | Delete the currently selected box |
| Save annotations | **s** or **↑ Up Arrow** | Save current annotations |
| Force save flag | **p** | Mark current annotations as needing save |
| Toggle confidences | **h** | Show or hide confidence values |
| Run YOLO inference | **y** | Run model inference on the current image |
| Single-click prediction shortcut | **j** | Run single-click prediction mode/action |
| Select all boxes | **Ctrl + A** | Select all annotations in the current image |
| Copy boxes | **Ctrl + C** | Copy selected box or selected boxes |
| Paste boxes | **Ctrl + V** | Paste copied box or boxes |
| Next image | **e**, **d**, or **→ Right Arrow** | Load next image |
| Previous image | **q**, **a**, or **← Left Arrow** | Load previous image |
| Jump to image | **Enter / Return** | Jump to selected image index |
| Move annotations up | **8** | Translate all annotations upward |
| Move annotations down | **2** | Translate all annotations downward |
| Move annotations left | **4** | Translate all annotations left |
| Move annotations right | **6** | Translate all annotations right |
| Help | **F1** | Open help window |
| Toggle box list | **F2** | Show or hide annotation/box list |
| Toggle image list | **F3** | Show or hide image list window |
| Toggle color selector | **F4** | Show or hide class color selector |
| Toggle class name editor | **F5** | Show or hide class name editor |
| Toggle autosave | **F6** | Enable or disable autosave |
| Screenshot | **F12** | Take screenshot |


*(TODO KEEP UP TO DATE AND Adjust as actual bindings change during DEV)*

---














