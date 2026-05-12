# AVAW CVAT BBox Tool

A lightweight desktop GUI tool for creating, editing, and managing YOLO-style bounding box annotations.

Built with Tkinter, OpenCV, and Ultralytics for fast manual labeling and assisted annotation workflows.

---

## ⌨️ Prerequisites

We recommend using Miniconda as the environment manager.

If Miniconda is not already installed, follow this guide:

[Install Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install/overview)

---

## 📦 Download Software

1. Download the latest release source code
2. Extract the release into a folder
3. Install the environment using either Option A or Option B below

---

## 📦 Environment Installation

### Option A — Using Conda (Recommended)

Open an Anaconda Prompt and navigate to the installation folder.

```bash
cd path\to\AVAW_CV-Waste\INSTALL
```

Create and activate the Conda environment:

```bash
conda env create -f environment.yml -n AVAW_BBOX
conda activate AVAW_BBOX
```

### Optional: Enable GPU Support

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

### Option B — Using Pip

```bash
git clone https://github.com/AVAWLeoben/AVAW_CVAT.git
cd AVAW_CVAT

python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

This will install the CPU only version of without CUDA support.
For CUDA support please follow along the GPU instructions further above.

---

## 🚀 Usage

Run the application from your IDE of choice, or from the command line after a cd into the AVAW_BBOX folder:

```bash
python AVAW_CVAT_BBOX.py
```

On Windows, you can also run the executable directly:

```text
dist/AVAW_CVAT_BBOX.exe
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
