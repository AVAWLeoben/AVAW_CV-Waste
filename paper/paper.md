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

date: 15 May 2026
bibliography: paper.bib
---

# Summary

`AVAW_CV-Waste` is a free and open-source offline desktop application for creating and correcting image annotations used to train object detection models. The software allows users to draw, edit, move, resize, copy, and manage bounding boxes around objects in images. It creates outputs compatible with YOLO-based artificial intelligence workflows, specifically the YOLO PyTorch TXT annotation format commonly used by YOLO11, YOLOv8, YOLOv5, and related computer vision models.

`AVAW_CV-Waste` supports the integration of existing YOLO models for semi-automatic annotation generation, reducing the amount of manual labelling required during dataset preparation. This assistance can be used to annotate complete images or follow a one-click annotation process in which the user clicks on an object and the currently loaded models tries to fit a bounding box around the selected object. The application was designed specifically for waste management, recycling, and material sorting research, where datasets often contain highly domain-specific object classes and cannot easily be processed using generic or cloud-based annotation platforms.

Because the software operates entirely offline, it can be deployed directly at industrial facilities or research sites where internet access may be limited or unavailable. Local processing additionally guarantees data sovereignty, an important requirement for industrial research collaborations involving sensitive operational data.

The primary goal of `AVAW_CV-Waste` is to simplify and accelerate dataset creation for non-specialist users, including students, laboratory staff, recycling operators, and industrial research partners. By reducing the technical complexity of annotation workflows, the software supports the development of custom machine learning models for applications such as waste classification, contaminant detection, scrap sorting, and sensor-based recycling research.

<img src="https://raw.githubusercontent.com/AVAWLeoben/AVAW_CV-Waste/JOSS-short-lived-branch/DEMO/Screenshot_UI.png" alt="UI Screenshot" width="300" />

# Statement of need

`CV-Waste` was developed as a free and open-source alternative that can be adapted to specific scientific workflows, especially in waste management and recycling research.

The Waste Management domain needs images of particles with contamination, deformation and on conveyor belts, specific to the actual research question regarding the sorting and classification of waste particles are necessary.
Thus, waste datasets often require highly specific object classes, such as plastics, paper, scrap-types, hazardous waste, or mixed waste fractions in environments relevant to the waste management domain.
Publicly available datasets that fit all these requirements are scarce to non-existent and thus need to be created for each research project individually. 

Existing annotation tools for this purpuse may not easily support these specialized categories or the frequent changes that occur during research projects and often prohibit or disincentivise the use of custom pre-trained models, which may impede up the annotation process. However, these tools´ reliance on online annotation with the requirement to upload the dataset and related annotations into a cloud service often clashes with industrial partners need for data sovereignty. Additionally, existing annotation tools may not easily integrate with the specialized categories or the frequent changes that occur during research projects.

In addition, many annotation tools restrict or disincentivise the integration of custom pre-trained models, thereby limiting opportunities to accelerate the annotation process through domain-specific automation.
While some cloud-based services provide server-side automated annotation using existing pre-trained models, such functionality is often confined to paid subscription tiers and restricted to the models supported by the respective platform, or simply limited to set number of uses if using free subscription tiers. 

Consequently, researchers are frequently unable to leverage their own waste-management-specific pre-trained models to support and aid annotation.

Lastly, as many existing tools are cloud based, and thus data sovereignty may not always be guaranteed. This is an increasingly precarious issue when working with industrial partners in general and patners in waste management in particular due to research projects requiring data to be recorded directly in respective material recovery facilites. 

This tool allows users to define their own custom annotation classes, load and use their own models for automatic predictions and to work entirely offline without requiring cloud services.  

While there exist solutions that provide a framework for building annotation tools [@Epifânio2022], `CV-Waste` addresses a different practical need. Its purpose is not to replace a programmable annotation framework, but to provide an immediately usable, domain-focused desktop GUI for YOLO-style waste annotation workflows. `CV-Waste` is designed for research assistants, students, laboratory staff, and industrial partners who may not have programming experience, but still need to create, review, and correct high-quality annotations efficiently. In this sense, [@Epifânio2022] serves developers and users who want to build or customize annotation tools, whereas AVAW_CV-Waste serves non-programming users who need a polished, accessible, and research-ready annotation environment.

Although several related tools exist, `CV-Waste` fills a distinct gap. AddaxAI is primarily a no-code platform for training and deploying YOLOv5 object detection models, whereas `CV-Waste` focuses specifically on creating, reviewing, and correcting YOLO-style bounding-box annotations for waste and recycling datasets which can then be used to train most object classification networks including YOLO26 and RT-DETR models. SAMBA targets semantic segmentation rather than bounding-box object detection, while LaMa and occupationMeasurement are aimed at labelling or coding text-based qualitative and survey data. `CV-Waste` is therefore necessary because it provides a dedicated, lightweight, offline, and research-oriented GUI for bounding-box annotation in waste-management applications. Bounding Box annotation is itself suited to Waste Management application as it is faster than segmentation annotation and requires less computational hardware when deployed. Additionally usiual ejection mechanisms like high pressure nozzle bars or flippers do not have the spatioal resolution to leverage the additional localisation detail provided by segmentation masks.

Its interface is designed for research assistants, students, laboratory staff, and industrial partners without programming experience, while still supporting custom classes, custom YOLO models, and assisted annotation workflows. This makes it better suited to practical dataset creation in waste and recycling research than more general, segmentation-focused, YOLOv5-specific, or text-labelling tools.

This software thus primarily targets researchers and industrial practitioners working in waste management, recycling, circular economy technologies, and related sensor-based sorting applications enabling them to
quickly create, review, edit, and correct annotations at no cost.

# State of the field

The field of annotation software allows for several pre-build alternatives. 



In principle, many of these limitations can be circumvented by deploying self-hosted instances of existing annotation platforms on offline systems. 
However, accomplishing this typically requires advanced technical expertise, and, most importantly, a considerable time investment.

Consequently,  the emerging research field of employing machine learning models for waste classification tasks requires an open source, free of cost, offline and adaptable tool that allows for modular expansions and use of domain specific detection models that also ensures data-sovereignty and is not reliant on online services once installed.



`AVAW_CV-Waste` addresses this gap by occupying a niche between generic cloud-based annotation platforms and highly specialized in-house software solutions commonly employed in industrial recycling research.

# Software design

While generative AI can now accelerate the initial development of software like this, extensive testing in real research environments is still required. In particular, evaluating the tool with researchers of different technical backgrounds cannot be meaningfully outsourced or offloaded to generative AI systems.

Thus, the UI and UIX of this tool were subject to constant iteration and improvement, spanning multiple years of research projects in this emerging field in waste management research. It could therefore incorporate criticism and feedback from students during lectures, as well as from researchers and workers that annotated thousands of images using this tool. Ongoing use and the evolving requirements of research projects, particularly in waste-management-related sorting tasks, will inevitably uncover further opportunities for optimisation and adaptation. The use of Python, the widely adopted UI framework Tkinter, and an object-oriented software architecture is intended to support straightforward customisation and extension by researchers in waste management and recycling domains.

To maintain simplicity and accessibility, the software intentionally avoids implementation complexity, such as multithreading or multitasking even though these approaches could have potentially improved application responsiveness by offloading annotation tasks to separate processes.

Since Python is already widely used in machine learning and computer vision research, the tool integrates naturally into existing scientific workflows.

Several design trade-offs were made to ensure broad hardware compatibility and stable operation on lower-performance research machines while still providing the quality-of-life features expected from such a tool. Lightweight rendering and simplified interaction workflows were prioritized over computationally expensive visualization features. Although the default Python environment is primarily designed for CPU-based inference, the underlying inference modules also enable advanced users to leverage available GPU hardware resources with only minor changes to the installation workflow.

Overall, Python and its ecosystem of modules were selected as the underlying architecture due to the broad support available for Python applications, the ease with which other waste management researchers can adapt the tool to their own requirements, and the widespread adoption of Python for the rapid development of machine learning applications.

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

