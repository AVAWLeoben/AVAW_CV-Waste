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

# 1 Summary

`AVAW_CV-Waste` is a free and open-source offline desktop application for creating and correcting image annotations used to train object detection models. The software allows users to draw, edit, move, resize, copy, and manage bounding boxes around objects in images, with outputs compatible with YOLO-based artificial intelligence workflows, specifically the YOLO PyTorch TXT annotation format commonly used by YOLO11, YOLOv8, YOLOv5, and related computer vision models.

The software also supports the integration of existing YOLO models for semi-automatic annotation generation, reducing the amount of manual labelling required during dataset preparation. The application was designed specifically for waste management, recycling, and material sorting research, where datasets often contain highly domain-specific object classes and cannot easily be processed using generic or cloud-based annotation platforms.

Because the software operates entirely offline, it can be deployed directly at industrial facilities or research sites where internet access may be limited or unavailable. Local processing additionally guarantees data sovereignty, an important requirement for industrial research collaborations involving sensitive operational data.

The primary goal of `AVAW_CV-Waste` is to simplify and accelerate dataset creation for non-specialist users, including students, laboratory staff, recycling operators, and industrial research partners. By reducing the technical complexity of annotation workflows, the software supports the development of custom machine learning models for applications such as waste classification, contaminant detection, scrap sorting, and sensor-based recycling research.

# 2 Statement of need

The AVAW_CV-Waste Tool was developed as a free and open-source alternative that can be adapted to specific scientific workflows, especially in waste management and recy-cling research, where open-source data is scarce to non-existent. 

In this domain, images of particles with contamination, deformation and on conveyor belts, specific to the actual re-search question regarding the sorting and classification of waste particles are necessary. 

Thus, waste datasets often require highly specific object classes, such as plastics, paper, scrap-types, hazardous waste, or mixed waste fractions in environments relevant to the waste management domain.

Existing tools may not easily support these specialized categories or the frequent changes that occur during research projects and often prohibit or disincentivise the use of custom pre-trained models, which may speed up the annotation process. 

Lastly, since many existing tools are cloud based, data sovereignty may not always be guaranteed - an increasingly precarious issue when working with industrial partners in waste management research projects heeding to data often being recorded directly in respective material recovery facilites. 

This tool allows users to define their own custom annotation classes, load and use their own models for automatic predictions, work entirely offline without requiring cloud services organize datasets according to their own folder structures and workflows and quickly review, edit, and correct annotations at no cost.

The software primarily targets researchers and industrial practitioners working in waste management, recycling, circular economy technologies, and sensor-based sorting applications.

# 3 State of the field

The field of annotation software allows for several pre-build alternatives. 

However, as we noticed in many of our research projects, these tools´ reliance on online annotation with the requirement to upload the dataset and related annotations into a cloud service often clashes with industrial partners need for data sovereignty. 

In theory one can build a self-hosted version and move docker images to offline machines. 

But one would need advanced technical skills and additional resource and time for that. 

Further, this approach would eliminate the application of pre-trained models to semi-automatically segment and annotate objects in one’s dataset. 

However, this automated annotation is oftentimes limited paid plans to alleviate usage limits and the available models provided by cloud service in question, prohibiting using one’s own pre-trained waste management domain specific models for aiding the annotation process. 

In conclusion, the emerging research field of using machine learning models for waste management classification tasks needed an open source, free of cost, offline and adaptable tool that allows for modular expansions and use of domain specific detection models that also ensures data-sovereignty and is not reliant on online services once installed.

The tool therefore fills a niche between generic cloud annotation platforms and highly customized in-house software solutions used in industrial recycling research.

# Software design

While we are aware that basic code for software like this can rapidly be developed using generative ai, extensive testing under real research scenarios with researchers of varying degrees of technical prowess can’t be offloaded to GenAI. 

Thus, the UI and UIX of this tool were subject to constant iteration and improvement, spanning multiple years of research projects in this emerging field in waste management research. It could therefore incorporate criticism and feedback from students during lectures, researchers and workers that annotated thousands of images using this tool. Ongoing usage and the everchanging nature of research projects in general and Waste Managment related sorting tasks in particular will inevitably uncover further optimisations and adaptations. The use of Python itself and the common UI framework tkinter as well and an object oriented approach to the tools makeup is aimed at enabling customisation and extension by other researchers working in waste management and recycling domains. Since Python is widely adopted in machine learning and computer vision research, the software integrates naturally into existing scientific workflows.

Several design trade-offs were made to ensure broad hardware compatibility and stable operation on lower-performance research machines, while still allowing for quality of life features expected from a tool like this. Lightweight rendering and simplified interaction workflows were prioritized over computationally expensive visualization features.

Overall, we chose Python and tkinter as the underlying architecture to leverage both the wide support for Python applications, its ease of use for other waste management researchers to adapt the tool for their purposes and of course the widespread adoption of Python as the programming language for rapid development of machine learning tools.

# Research impact statement

`AVAW_CV-Waste` has already been successfully used in the development of scientific datasets and in the publication of research related to waste detection, classification, and recycling workflows.

`AVAW_CV-Waste` addresses a major bottleneck in the development of computer vision systems for waste management and recycling research, namely the creation of annotated training datasets.

The software is currently being used within multiple recycling and circular economy lighthouse research projects, including:

- KiRAMET: AI-based recycling of metal composite wastes,
- StraTex: Sorting and processing strategies for used textiles,
- greenPLAST-food: Green plastic recycling for food contact materials, and
- Scarpa: Strategic recycling of footwear.

Within these projects, the software has already been applied in research workflows involving post-consumer textiles, lightweight packaging waste, and post-shredder scrap, where large quantities of annotated image data are required for training and evaluating object detection models.

The created datasets formed the basis for scientific publications showcasing the applicability of machine learning methods for sorting heterogeneous waste streams and reducing manual sorting requirements
[@yolo_scrap_2026; @greenplast_food; @kiramet_green_steel;
@kiramet_recycling; @robust_yolo_2026; @copper_detection;
@deep_learning_scrap].

# AI usage disclosure

Generative artificial intelligence tools were not used for the architectural design or core software implementation of `AVAW_CV-Waste`.

ChatGPT (OpenAI) was used during software development for documentation support, generation of docstrings, bug-fixing assistance, and minor inline code modifications. For this manuscript, generative AI tools were used only for grammatical improvements and formatting support, including conversion of manuscript content from `.docx` to Markdown syntax.

All generated content and code modifications were manually reviewed and validated by the authors.

# Acknowledgements

This work was created as part of the research projects `KiRAMET` and `greenPLAST-food`.

The projects "KiRAMET KI-based Recycling of Metal Compound Waste" (project number FO999899661) and "greenPLAST-food - Green Plastic Recycling Factory for Food Contact Materials" (project number 5135363) are funded by the Austrian Research Promotion Agency (FFG) and the Federal Ministry for Climate Action, Environment, Energy, Mobility, Innovation, and Technology.

# References

