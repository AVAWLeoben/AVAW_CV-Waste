# AVAW CV-Waste Bounding Box Tool

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

<img src="https://raw.githubusercontent.com/AVAWLeoben/AVAW_CV-Waste/JOSS-short-lived-branch/DEMO/Screenshot_UI.png" alt="UI Screenshot" width="400" />

---

## Aim of this Tool´s development

Quality annotations are essential for training reliable YOLO object detection models.

Many existing annotation tools are commercial, cloud-based, difficult to customize, or too complex for smaller research groups and industrial partners.

The AVAW CVAT BBox Tool was developed as a free and open-source alternative that can be adapted to specific scientific workflows, especially in waste management and recycling research, where open source data is scarce to non-existent. Especially because in this domain, images of particles with contamination, deformation and on conveyor belts, specific to the actual research question are necessary.

Thus, waste datasets often require highly specific object classes, such as plastics, paper, metals, hazardous waste, or mixed waste fractions. Existing tools may not easily support these specialized categories or the frequent changes that occur during research projects. Existing tools also often prohibit or complicate the use of custom pre-trained models, which may speed up the annotation process. Lastly, since many existing tools are cloud based, data sovereignty may not always be guaranteed - an increasingly precarious issue when working with industrial partners in research projects.

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

After downloading and extracting the release files, open the [INSTALL](https://github.com/AVAWLeoben/AVAW_CV-Waste/tree/JOSS-short-lived-branch/INSTALL) folder in the repository for detailed setup instructions.

The INSTALL folder contains step-by-step guides for both Conda-based and Pip-based installations, as well as optional instructions for enabling GPU acceleration with PyTorch.

---

## 📚 Demo

Visit the [DEMO](https://github.com/AVAWLeoben/AVAW_CV-Waste/tree/DEMO) page for a detailed walkthrough of the application.

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
## 🌍 Community Guidelines
: Are there clear guidelines for third parties wishing to 1) Contribute to the software 2) Report issues or problems with the software 3) Seek support

### 🤝 Contributing

If you want to contribute, feel free to contact Bojan Lorber via bojan.lorber@unileoben.ac.at.  
Additionally, you can do so by reporting bugs and/or suggesting new feautures.

### 🐞 Reporting Issues

If you encounter bugs, unexpected behaviour, crashes, or compatibility issues, please open a GitHub issue or contact Bojan Lorber via bojan.lorber@unileoben.ac.at.

When reporting an issue, please include:
- Operating system and Python version
- A short description of the problem
- Steps required to reproduce the issue
- Error messages or screenshots, if available
- Information about the used model or dataset, if relevant (e.g. Images of uncommon dimensions)

Clear and reproducible bug reports greatly help improving the software and maintaining compatibility across different research environments.

Thank you very much!

### 🛟 Seeking Support
If you are in need of additional support or look for establishing a colaboratory event to further the efforts in using Computer Vision methods in waste management, feel free to contact Bojan Lorber via bojan.lorber@unileoben.ac.at.  

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












