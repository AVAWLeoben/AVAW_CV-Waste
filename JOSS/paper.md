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

`AVAW_CV-Waste` is a free and open-source offline desktop application for creating and correcting image annotations used to train object detection models. The software allows users to draw, edit, move, resize, copy, and manage bounding boxes around objects in images, with outputs compatible with YOLO-based artificial intelligence workflows, specifically the YOLO PyTorch TXT annotation format commonly used by YOLO11, YOLOv8, YOLOv5, and related computer vision models.

The software also supports the integration of existing YOLO models for semi-automatic annotation generation, reducing the amount of manual labelling required during dataset preparation. The application was designed specifically for waste management, recycling, and material sorting research, where datasets often contain highly domain-specific object classes and cannot easily be processed using generic or cloud-based annotation platforms.

Because the software operates entirely offline, it can be deployed directly at industrial facilities or research sites where internet access may be limited or unavailable. Local processing additionally guarantees data sovereignty, an important requirement for industrial research collaborations involving sensitive operational data.

The primary goal of `AVAW_CV-Waste` is to simplify and accelerate dataset creation for non-specialist users, including students, laboratory staff, recycling operators, and industrial research partners. By reducing the technical complexity of annotation workflows, the software supports the development of custom machine learning models for applications such as waste classification, contaminant detection, scrap sorting, and sensor-based recycling research.

# Statement of need

The development of machine learning systems for waste management and recycling research strongly depends on the availability of annotated image datasets. However, publicly available waste datasets are scarce and often unsuitable for highly specialized industrial research applications. Waste management datasets frequently require custom object classes representing plastics, paper fractions, scrap metal categories, hazardous materials, contaminated objects, or mixed waste streams under realistic industrial conditions.

Existing annotation tools frequently rely on cloud-based infrastructures that require uploading datasets and annotations to external services. This introduces significant challenges regarding data sovereignty and confidentiality when collaborating with industrial partners. Although self-hosted solutions exist, they typically require advanced technical expertise, additional infrastructure, and substantial setup effort.

Furthermore, many existing annotation platforms restrict the use of custom-trained object detection models for automated annotation support. In waste management research, domain-specific pre-trained models are often essential to accelerate annotation tasks involving highly heterogeneous materials.

`AVAW_CV-Waste` was therefore developed as a free and open-source alternative that enables researchers to:

- define custom annotation classes,
- use their own pre-trained object detection models,
- work completely offline without cloud services,
- maintain flexible dataset folder structures, and
- rapidly review and correct annotations.

The software primarily targets researchers and industrial practitioners working in waste management, recycling, circular economy technologies, and sensor-based sorting applications.

# State of the field

Several commercial and open-source annotation tools are available for object detection dataset generation. Popular platforms provide browser-based interfaces and collaborative workflows but commonly rely on cloud-hosted infrastructures. While these tools are suitable for general computer vision tasks, they are often less appropriate for industrial recycling research where strict requirements regarding data confidentiality and offline usability exist.

In principle, self-hosted deployments of cloud annotation systems are possible through containerized infrastructures. However, these approaches typically require advanced technical expertise and dedicated computing resources that may not be available in smaller research groups or industrial pilot environments.

Additionally, many existing solutions limit the integration of custom pre-trained object detection models or provide automated annotation features only through commercial subscription models. This restriction is problematic for waste management applications where highly specialized, domain-specific models are required.

`AVAW_CV-Waste` was developed to address these limitations by providing a lightweight, fully offline, and freely available annotation environment specifically suited for recycling and waste management research. The software emphasizes:

- offline usability,
- support for custom YOLO models,
- modular extensibility,
- low hardware requirements, and
- straightforward workflows for non-specialist users.

The tool therefore fills a niche between generic cloud annotation platforms and highly customized in-house software solutions used in industrial recycling research.

# Software design

The software architecture of `AVAW_CV-Waste` prioritizes accessibility, adaptability, and low hardware requirements. The application was implemented in Python using the `tkinter` graphical user interface framework to ensure compatibility with a wide range of systems commonly encountered in research laboratories and industrial environments.

A central design goal was to support users with varying levels of technical expertise. The graphical user interface and user experience were iteratively improved through extensive testing with students, researchers, and industrial users performing large-scale annotation tasks under realistic working conditions.

The application supports both manual and semi-automatic annotation workflows. Users can manually create and modify bounding boxes or accelerate dataset creation through automatic predictions generated using externally trained YOLO object detection models.

Several design trade-offs were made to ensure broad hardware compatibility and stable operation on lower-performance research machines. Lightweight rendering and simplified interaction workflows were prioritized over computationally expensive visualization features.

The use of Python additionally enables straightforward customization and extension by other researchers working in waste management and recycling domains. Since Python is widely adopted in machine learning and computer vision research, the software integrates naturally into existing scientific workflows.

# Research impact statement

`AVAW_CV-Waste` has already been successfully applied in the development of scientific datasets and research workflows involving waste detection, classification, and recycling automation.

The software addresses a major bottleneck in waste management machine learning applications: the creation of high-quality annotated training datasets. The tool has been used in projects involving post-consumer textiles, lightweight packaging waste, and post-shredder scrap recycling, where large quantities of annotated images are required for training object detection models.

Datasets created using `AVAW_CV-Waste` have contributed to scientific publications and research activities focused on sensor-based sorting and automated classification of heterogeneous waste streams. These applications support the development of intelligent recycling systems capable of reducing manual sorting requirements and improving material recovery efficiency.

The software is currently being used within multiple recycling and circular economy research projects, including:

- KiRAMET: AI-based recycling of metal composite wastes,
- StraTex: Sorting and processing strategies for used textiles,
- greenPLAST-food: Green plastic recycling for food contact materials, and
- Scarpa: Strategic recycling of footwear.

# AI usage disclosure

Generative artificial intelligence tools were not used for the architectural design or core software implementation of `AVAW_CV-Waste`.

ChatGPT (OpenAI) was used during software development for documentation support, generation of docstrings, bug-fixing assistance, and minor inline code modifications. For this manuscript, generative AI tools were used only for grammatical improvements and formatting support, including conversion of manuscript content from `.docx` to Markdown syntax.

All generated content and code modifications were manually reviewed and validated by the authors.

# Acknowledgements

This work was created as part of the research projects `KiRAMET` and `greenPLAST-food`.

The projects "KiRAMET KI-based Recycling of Metal Compound Waste" (project number FO999899661) and "greenPLAST-food - Green Plastic Recycling Factory for Food Contact Materials" (project number 5135363) are funded by the Austrian Research Promotion Agency (FFG) and the Federal Ministry for Climate Action, Environment, Energy, Mobility, Innovation, and Technology.

# References

