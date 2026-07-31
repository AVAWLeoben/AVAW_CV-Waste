# AVAW_CV-Waste

A lightweight desktop GUI tool for creating, editing, and managing YOLO-style bounding box annotations.

Built with Tkinter, OpenCV, and Ultralytics for fast manual labeling and assisted annotation workflows.

---

## ⌨️ Prerequisites

We recommend using Miniconda as the environment manager.

If Miniconda is not already installed, follow this guide:

[Install Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install/overview)

---

If there is no pre-trained ultralytics model available for testing on the local PC, we recommend downloading YOLOv11n for initial tests.

[Download YOLOv11n](https://github.com/AVAWLeoben/AVAW_CV-Waste/blob/JOSS-short-lived-branch/AVAW_BBOX/sample_model/yolo11n.pt)

---

## 📦 Installation

### Option A – Install from PyPI (Recommended)

To create a new Environment in Conda for the application use:

```bash
conda create -n CV-Waste python=3.12
conda activate CV-Waste
```

'CV-Waste' can be installed directly from PyPI:

```bash
python -m pip install avaw-cv-waste
```

After installation, you can launch the application from the command line with:

```bash
avaw-cv-waste
```

#### 📚 Demo

Visit the [DEMO](https://github.com/AVAWLeoben/AVAW_CVAT/tree/AVAW_BBOX_DEVELOPMENT/DEMO) page for a detailed walkthrough of the application.

The DEMO section contains example datasets, usage instructions, and a step-by-step tutorial covering the main features of the tool, including:

- loading images and label folders
- creating and editing bounding boxes
- managing annotation classes
- loading YOLO models
- generating automatic predictions
- reviewing and correcting annotations
- exporting YOLO-compatible label files

The demo is intended to help new users get familiar with the interface and typical annotation workflow as quickly as possible.


### Option B — Using Conda

In Anaconda Prompt:
Clone the repository:
```bash
git clone -b JOSS-short-lived-branch https://github.com/AVAWLeoben/AVAW_CV-Waste.git
cd AVAW_CV-Waste
```

Create the Conda environment from the INSTALL folder:
```bash
cd INSTALL
conda env create -f environment.yml 
conda activate AVAW_BBOX
```

Run the application:
```bash
cd ..\AVAW_BBOX
python AVAW_CVAT_BBOX.py
```

### Option C — Using Pip (native)

```bash
git clone -b JOSS-short-lived-branch https://github.com/AVAWLeoben/AVAW_CV-Waste.git
cd AVAW_CV-Waste

python -m venv avaw_bbox_env

# Windows PowerShell:
.\avaw_bbox_env\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r INSTALL\requirements.txt

# Windows CMD:
avaw_bbox_env\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r INSTALL\requirements.txt

# Linux / macOS
source avaw_bbox_env/bin/activate
python -m pip install --upgrade pip
python -m pip install -r INSTALL/requirements.txt

# Then run the app:
cd AVAW_BBOX
python AVAW_CVAT_BBOX.py

```

This will install the CPU only version of without CUDA support.
For CUDA support please follow along the GPU instructions further above.

---


### 🚧 Optional: Install Spyder IDE
The default environment does not contain an IDE. A preliminary installation to further adapt the application could be Spyder.

To install spyder run the following command after activating the new environment.
```bash
conda install spyder
```

### 🔥 Advanced: Enable GPU Support

The default environment is CPU-only and should work on most machines.

If you have a compatible NVIDIA GPU and want faster inference, follow these additional steps.

First, update Ultralytics:

```bash
pip install -U ultralytics
```

Uninstall any existing PyTorch packages that may have been installed automatically as Ultralytics dependencies:

```bash
pip uninstall torch torchvision torchaudio
```
To check your installed CUDA version, run the following command in the Command Prompt (cmd):

```bash
nvidia-smi
```

This will show output similar to the following:

<img width="862" height="210" alt="image" src="https://github.com/user-attachments/assets/0b475fe1-4334-46a4-9d6c-b52e247c2ecb" />

Next, visit the PyTorch installation page:

[PyTorch Installation Guide](https://pytorch.org/get-started/locally/)

<img width="535" alt="image" src="https://github.com/user-attachments/assets/b2c3863a-ca30-4bf8-ba2d-0a890f879468" />

Choose the correct operating system, package manager, Python version, and CUDA version.

This will generate an install command similar to:

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu130
```

In this example, `cu130` refers to CUDA 13.0.

Run this in Anaconda Prompt.

---



## 🚀 Usage

Run the application from your IDE of choice, or from the command line after a cd into the AVAW_BBOX folder:

An example with placeholder path is shown below:

```bash
cd C:\Path\To\AVAW_CV-Waste\AVAW_BBOX
python AVAW_CVAT_BBOX.py
```

## 📚 Demo

Visit the [DEMO](https://github.com/AVAWLeoben/AVAW_CVAT/tree/AVAW_BBOX_DEVELOPMENT/DEMO) page for a detailed walkthrough of the application.

The DEMO section contains example datasets, usage instructions, and a step-by-step tutorial covering the main features of the tool, including:

- loading images and label folders
- creating and editing bounding boxes
- managing annotation classes
- loading YOLO models
- generating automatic predictions
- reviewing and correcting annotations
- exporting YOLO-compatible label files

The demo is intended to help new users get familiar with the interface and typical annotation workflow as quickly as possible.
