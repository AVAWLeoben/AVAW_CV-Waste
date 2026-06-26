---
title: 'AVAW_CV-Waste: An Offline Computer Vision Annotation Tool for Waste Management Research'
tags:
  - Python
  - computer vision
  - waste management
  - recycling
  - object detection
  - annotation tool
  - YOLO
authors:
  - name: Gerald Koinig
    corresponding: true
    affiliation: 1
  - name: Bojan Lorber
    affiliation: 1
affiliations:
  - name: Montanuniversität Leoben, Austria
    index: 1

date: 26 June 2026
bibliography: paper.bib
---

# Summary

`AVAW_CV-Waste` is a free and open-source offline desktop application for creating and correcting image annotations used to train object detection models. The software allows users to draw, edit, move, resize, copy, and manage bounding boxes around objects in images. It creates outputs compatible with YOLO-based artificial intelligence workflows, specifically the YOLO PyTorch TXT annotation format commonly used by YOLO11, YOLOv8, YOLOv5, and related computer vision models.

`CV-Waste` supports the integration of existing YOLO models for semi-automatic annotation generation, reducing the amount of manual labelling required during dataset preparation. This assistance can be used to annotate complete images or follow a one-click annotation process in which the user clicks on an object and the currently loaded model tries to fit a bounding box around the selected object. The application was designed specifically for waste management, recycling, and material sorting research, where datasets often contain highly domain-specific object classes and cannot easily be processed using generic or cloud-based annotation platforms.

Because the software operates entirely offline, it can be deployed directly at industrial facilities or research sites where internet access may be limited or unavailable. Local processing additionally guarantees data sovereignty, an important requirement for industrial research collaborations involving sensitive operational data.

The primary goal of `AVAW_CV-Waste` is to simplify and accelerate dataset creation for non-specialist users, including students, laboratory staff, recycling operators, and industrial research partners. By reducing the technical complexity of annotation workflows, the software supports the development of custom machine learning models for applications such as waste classification, contaminant detection, scrap sorting, and sensor-based recycling research.

[Screenshot of the AVAW CV-Waste graphical user interface.](https://github.com/AVAWLeoben/AVAW_CV-Waste/blob/JOSS-short-lived-branch/DEMO/Screenshot_UI.png){ width=50% }

# Statement of need

`CV-Waste` was developed as a free and open-source alternative that can be adapted to workflows in waste management and recycling research.

Currently cloud-based commercial services exist and provide server-side automated annotation using existing pre-trained models. However, such functionality is often confined to paid subscription fees and restricted to the models supported by the respective platform. 
Consequently, researchers are frequently unable to leverage their own waste management-specific pre-trained models to support and aid annotation.
Further, as many existing tools are cloud-based, data sovereignty may not always be guaranteed. This is an increasingly precarious issue when working with industrial partners in general and partners in waste management in particular. These data sovereignty issues may prohibit the use of these commercial, cloud-based alternatives outright.
`CV-Waste` allows users to define their own custom annotation classes, load and use their own models for automatic predictions and to work entirely offline without requiring cloud-services.  
Open source alternatives include frameworks for building annotation tools [@Epifânio2022], However, `CV-Waste` addresses a different practical need. Its purpose is not to be a programmable annotation framework, but to provide an immediately usable, domain-focused desktop GUI for YOLO-style waste annotation workflows in waste management research. `CV-Waste` is designed for research assistants, students, laboratory staff, and industrial partners who may not have programming experience, but still need to create, review, and correct high-quality annotations efficiently. In this sense, [@Epifânio2022] serves developers and users who want to build or customize annotation tools, whereas AVAW_CV-Waste serves non-programming users who need a polished, accessible, and research-ready annotation environment.
 `AddaxAI` is primarily a no-code platform for training and deploying YOLOv5 object detection models [@van_Lunteren2023]. `CV-Waste` focuses specifically on creating, reviewing, and correcting YOLO-style bounding-box annotations for waste and recycling datasets, which can then be used to train most object classification networks including YOLO26 and RT-DETR models. 

`SAMBA` targets semantic segmentation rather than bounding-box object detection, while `LaMa` and `occupationMeasurement` are aimed at labelling or coding text-based qualitative and survey data [@Docherty2024SAMBA; @lama2023; @Simson2023occupationMeasurement]. Therefore, `CV-Waste` provides a dedicated, lightweight, offline, and research-oriented GUI for bounding-box annotation in waste management applications and fills a distinct gap.

# State of the field

The field of leveraging object classification models like YOLO or RT-DETR for classifying waste particles is a recently emerging one. Low cost sensoric equipment, i.e. RGB cameras, have becoming of increasing interest with the advent of attainable post-consumer hardware capable of running these models in deployment scenarios. The systems are becoming increasingly adopted to pre-sort waste streams prior to more chemically astute systems like LIBS or XRF, XRT. 
However, as the training of waste classification models requires extensive, divers and well labelled datasets that represent the expected working environment i.e. deformed, heterogeneous, contaminated, particles on a conveyor belt, existing datasets often cannot be used to train these models. 
Albeit, object classification models are becoming increasingly adopted to sort highly specific object classes, such as plastics, paper, scrap, hazardous waste, or mixed waste fractions. Sorting tasks that were recently primarily performed manually.
This reliance on manual sorting of waste fractions is another driving factor in the adoption of object classification models in waste management, as finding and holding of staff is becoming increasingly difficult for MRF operators. Additionally, scaling up manual sorting operations to handle the increasing volume of waste streams is unfeasible. 
Consequently, large stakeholders are already investing in research projects regarding the application of object detectors for waste sorting. This includes lighthouse projects like `StraTex` and `Scarpa` whjich focus on Textiles and Footwear waste, `KiRAMET`, which researches scrap recovery for the carbon neutral transformation of steel production and `greenPLAST-food`, which aims at improving the circular economy of lightweight packaging waste, as it is currently polluting environment and wildlife. All these projects need extensive datasets to train their models and are using `CV-Waste` to create them.

# Software design
While generative AI can now accelerate the initial development of software like this, extensive testing in real research environments is still required. In particular, evaluating the tool with researchers of different technical backgrounds cannot be meaningfully outsourced or offloaded to generative AI systems.

Thus, the UI and UX of this tool were subject to constant iteration and improvement, spanning multiple years of research projects in this emerging field in waste management research. It could therefore incorporate criticism and feedback from students during lectures, as well as from researchers and workers that annotated tens of thousands of images using this tool. Ongoing use and the evolving requirements of research projects, particularly in waste-management-related sorting tasks, will inevitably uncover further opportunities for optimisation and adaptation. The use of Python, the widely adopted UI framework Tkinter, and an object-oriented software architecture is intended to support straightforward customisation and extension by researchers in waste management and recycling domains.

To maintain simplicity and accessibility, the software intentionally avoids implementation complexity, such as multithreading or multitasking even though these approaches could have potentially improved application responsiveness.

Since Python is already widely used in machine learning and computer vision research, the tool integrates naturally into existing scientific workflows.

Several design trade-offs were made to ensure broad hardware compatibility and stable operation on lower-performance research machines while still providing the quality-of-life features expected from such a tool. Lightweight rendering and simplified interaction workflows were prioritised over computationally expensive visualisation features. Although the default Python environment is primarily designed for CPU-based inference, the underlying inference modules also enable advanced users to leverage available GPU hardware resources with only minor changes to the installation workflow.

Lastly, `CV-Waste` was specifically tailored to bounding box annotation. Bounding Box annotation is itself tailored to waste management applications as it is faster than segmentation-based annotation and requires less computational hardware when deployed. Additionally usual ejection mechanisms like high pressure nozzle bars or flippers do not have the spatial resolution to leverage the additional localisation detail provided by segmentation masks.


# Research impact statement

`AVAW_CV-Waste` has already been successfully used in the development of scientific datasets and in research related to waste detection, classification, and recycling workflows.

`AVAW_CV-Waste` addresses a major bottleneck in the development of computer vision systems for waste management and recycling research, namely the creation of annotated training datasets.

`AVAW_CV-Waste` is currently being used within multiple recycling and circular economy lighthouse research projects, including KiRAMET, StraTex, greenPLAST-food, and Scarpa.

Within these projects, the software has been applied in research workflows involving post-consumer textiles, lightweight packaging waste, and post-shredder scrap, where large quantities of annotated image data are required for training and evaluating object detection models.

Datasets created using `AVAW_CV-Waste` contributed to research on sensor-based sorting of shredder scrap towards green steel production [@yolo_scrap_2026], AI-assisted recycling workflows for metal composite waste streams [@kiramet_green_steel; @kiramet_recycling], and plastic recycling systems for food-contact materials [@greenplast_food].

The generated datasets also supported research on robust YOLO-based ejection of copper-containing particles from heavily corroded scrap streams [@robust_yolo_2026], detection of copper-containing scrap in post-shredder fractions using machine vision and artificial intelligence [@copper_detection], and deep learning approaches for classification of copper-containing metal scrap in recycling processes [@deep_learning_scrap].

These applications demonstrate the utility of the software for reducing manual annotation effort and enabling machine learning methods for heterogeneous waste sorting tasks.

# AI usage disclosure

Generative artificial intelligence tools were not used for the architectural design or core software implementation of `AVAW_CV-Waste`.

ChatGPT (OpenAI) was used during software development for documentation support, generation of docstrings, bug-fixing assistance, and inline code modifications. For this manuscript, generative AI tools were used only for grammatical improvements and formatting support, including conversion of manuscript content from `.docx` to Markdown syntax.

All generated content and code modifications were manually reviewed and validated by the authors.

# Acknowledgements

This work was created as part of the research projects `KiRAMET` and `greenPLAST-food`.

The projects "KiRAMET KI-based Recycling of Metal Compound Waste" (project number FO999899661) and "greenPLAST-food - Green Plastic Recycling Factory for Food Contact Materials" (project number 5135363) are funded by the Austrian Research Promotion Agency (FFG) and the Federal Ministry for Climate Action, Environment, Energy, Mobility, Innovation, and Technology.

# References

