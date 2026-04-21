# AVAW CVAT BBox Tool

A lightweight desktop GUI tool for creating, editing, and managing YOLO-style bounding box annotations.
Built with Tkinter, OpenCV, and Ultralytics for fast manual labeling and assisted annotation workflows.

---

## ✨ Features

* 🖼️ Interactive bounding box annotation GUI
* 🔍 Smooth zoom and pan support
* 🧠 Optional YOLO inference for assisted labeling
* 🏷️ Class-based color visualization
* 📂 Image list navigation
* ✏️ Resize, move, copy, and multi-select boxes
* 💾 Auto-save support
* 📊 Confidence display toggle
* 🎨 Custom class names and colors
* 🔄 Annotation translation utilities

---

## 🖥️ Screenshots

![UI Screenshot](DEMO/Screenshot_UI.png)

---

## Aim of this Tool´s development

Quality annotations are essential for training reliable YOLO object detection models.

Many existing annotation tools are commercial, cloud-based, difficult to customize, or too complex for smaller research groups and industrial partners.

The AVAW CVAT BBox Tool was developed as a free and open-source alternative that can be adapted to specific scientific workflows, especially in waste management and recycling research, where open source data is scarce to non-existent. Especially because in this domain, images of particles with contamination, deformation and on conveyor belts, specific to the actual research question are necessary.

Thus, waste datasets often require highly specific object classes, such as plastics, paper, metals, hazardous waste, or mixed waste fractions. Existing tools may not easily support these specialized categories or the frequent changes that occur during research projects.

This tool allows users to:

Define their own custom annotation classes
Load and use their own YOLO models for automatic predictions
Work entirely offline without requiring cloud services
Organize datasets according to their own folder structures and workflows
Quickly review, edit, and correct annotations

A major design goal was ease of use.

The interface was developed iteratively to be simple and intuitive, even for users without a technical background.

Many annotation projects involve operators, students, laboratory staff, or industrial personnel who may not have experience with machine learning tools. The AVAW CVAT BBox Tool focuses on clear controls, minimal setup effort, and a straightforward workflow to make annotation accessible to a wider range of users.

The tool is intended to support both research and real-world applications.

By making annotation faster, easier, and more flexible, it can help improve:

Waste sorting and recycling systems
Material recognition and classification
Detection of contaminants and hazardous waste
Dataset creation for custom AI models
Scientific studies involving object detection and computer vision in waste management

Because the software is free, open-source, and fully customizable, users can adapt it to their own research questions, industrial environments, and annotation needs without being restricted by licensing costs or proprietary systems.

---
## References

This tool has already been successfully used in the development of scientific datasets and in the publication of research related to waste detection, classification, and recycling workflows.

- [AI Pipeline for sensor based sorting of shredder scrap towards green steel production. in 11th Sensor-Based Sorting & Control 2026](https://pure.unileoben.ac.at/de/publications/ai-pipeline-for-sensor-based-sorting-of-shredder-scrap-towards-gr/)

- [GreenPLAST-food: Grüne Kunststoffrecyclingfabrik für Lebensmittelkontaktmaterialien](https://pure.unileoben.ac.at/de/publications/greenplast-food-gr%C3%BCne-kunststoffrecyclingfabrik-f%C3%BCr-lebensmittelk-2/)

- [Kiramet: KI-basierte Konditionierung von Schredderschrott – für grüneren Stahl](https://pure.unileoben.ac.at/de/publications/kiramet-ki-basierte-konditionierung-von-schredderschrott-f%C3%BCr-gr%C3%BCn/)

- [KiRAMET: KI Basiertes Recycling von Metallverbund-Abfällen](https://pure.unileoben.ac.at/de/publications/kiramet-ki-basiertes-recycling-von-metallverbund-abf%C3%A4llen-2/)

- [Robust YOLO-Based Ejection of Copper-Containing Particles in Heavily Corroded Scrap Towards Green-Steel Production](https://doi.org/10.3390/pr14050746)

- [Detection of copper-containing scrap in a post-shredder fraction with machine vision and artificial intelligence towards green-steel production](https://pure.unileoben.ac.at/de/publications/detection-of-copper-containing-scrap-in-a-post-shredder-fraction-/)

- [Deep learning approaches for classification of copper-containing metal scrap in recycling processes](https://pure.unileoben.ac.at/de/publications/deep-learning-approaches-for-classification-of-copper-containing-/)


Further publication details and citations will be added here as they become available.

---
## 🚀 Installation

To get started, download the latest version of the software from the [Releases](https://github.com/AVAWLeoben/AVAW_CVAT/releases) page.

After downloading and extracting the release files, open the [INSTALL](https://github.com/AVAWLeoben/AVAW_CVAT/tree/AVAW_BBOX_DEVELOPMENT/INSTALL) folder for detailed setup instructions.

The INSTALL folder contains step-by-step guides for both Conda-based and Pip-based installations, as well as optional instructions for enabling GPU acceleration with PyTorch.

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

| Action                    | Binding                                         | Description                                          |
| ------------------------- | ----------------------------------------------- | ---------------------------------------------------- |
| Click (canvas)            | **Left Click**                                  | Select / interact with a box (`on_click`)            |
| Draw / drag               | **Left Click + Drag**                           | Draw or move/resize depending on context (`on_drag`) |
| Finish drag               | **Left Button Release**                         | Finish creation/edit (`on_release`)                  |
| Multi-drag                | **Ctrl + Left Drag**                            | Drag multiple selected boxes (`on_multi_drag`)       |
| Multi-select start        | **Ctrl + Left Click**                           | Start multiselect / add selection (`on_multiselect`) |
| Multi-select stop         | **Ctrl + Right Click**                          | Stop multiselect (`stop_multiselect`)                |
| Context menu              | **Right Click** *(or App/Menu key)*             | Open context menu (`show_context_menu`)              |
| Single-click prediction   | **Alt + Left Click** *(or Ctrl+Alt+Left Click)* | Run prediction at click (`single_click_prediction`)  |
| Add box                   | **n** *(or ↓ Down Arrow)*                       | Add a new box (`add_box`)                            |
| Delete selected box       | **Delete**                                      | Delete selected box (`delete_box`)                   |
| Save                      | **s** *(or ↑ Up Arrow)*                         | Save annotations (`on_save`)                         |
| Force save flag           | **p**                                           | Set save flag (`set_save_flag`)                      |
| Toggle confidences        | **h**                                           | Show/hide confidences (`show_confidences`)           |
| YOLO inference            | **y**                                           | Run YOLO inference (`run_yolo_inference`)            |
| Select all                | **Ctrl + A**                                    | Select all boxes (`select_all`)                      |
| Copy / paste boxes        | **Ctrl + C / Ctrl + V**                         | Copy / paste selection (`on_copy`, `on_paste`)       |
| Next image                | **e / d / → Right Arrow**                       | Next image (`next_image`)                            |
| Previous image            | **q / a / ← Left Arrow**                        | Previous image (`previous_image`)                    |
| Jump to image             | **Enter / Return**                              | Jump to image index (`jump_to_image`)                |
| Translate annotations     | **8 / 2 / 4 / 6**                               | Move all annotations up/down/left/right              |
| Help                      | **F1**                                          | Open help menu                                       |
| Toggle box list           | **F2**                                          | Show/hide box list                                   |
| Toggle image list         | **F3**                                          | Show/hide image list window                          |
| Toggle color selector     | **F4**                                          | Show/hide color selector                             |
| Toggle class names editor | **F5**                                          | Show/hide class names window                         |
| Toggle autosave           | **F6**                                          | Enable/disable autosave                              |
| Screenshot                | **F12**                                         | Take screenshot                                      |


*(TODO KEEP UP TO DATE AND Adjust as actual bindings change during DEV)*

---

## 📋 Requirements

Core dependencies:

* Python ≥ 3.12
* numpy
* pillow
* opencv-python
* natsort
* ultralytics

---

## ⚠️ Notes

* Tkinter must be available in your Python installation.
* Large Images may require additional RAM.
* Zooming of Large Images may lead to significant performance drops and RAM usage
* GPU acceleration depends on your PyTorch installation and Hardware Setup.

---

## 🐛 Known Limitations

* Limited undo history
* Designed primarily for YOLO bbox workflows

---

## 🤝 Contributing

If you want to contribute, feel free to contact Bojan Lorber via bojan.lorber@unileoben.ac.at.  
Additionally, you can do so by reporting bugs and/or suggesting new feautures.

---

## 📄 License

MIT License

---

## 👤 Author

Gerald Koinig

Technical University of Leoben

Bojan Lorber

Technical University of Leoben

---

## ⭐ Acknowledgements

* OpenCV
* Ultralytics
* Tkinter
* Pillow

---












