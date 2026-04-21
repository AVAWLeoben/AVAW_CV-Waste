# AVAW CVAT BBox Tool

A lightweight desktop GUI tool for creating, editing, and managing YOLO-style bounding box annotations.
Built with Tkinter, OpenCV, and Ultralytics for fast manual labeling and assisted annotation workflows.

## ⌨️ Prerequisites
- We recommend using miniconda as environment manager. If not already installed, please follow the following link to miniconda.
- https://www.anaconda.com/docs/getting-started/miniconda/install/overview
---
## 📦 Download Software
- Download latest release source code
- Unpack latest release into folder
- Install Environment following either Option A or Option B

## 📦 Installation of Environment

### Option A — Using Conda (Recommended) 
Open Anaconda Prompt and cd into the INSTALL folder
In the INSTALL folder, use conda to recreate the saved environment containing all necessary dependencies for the CVAT Applet.
```bash
conda env create -f environment.yml -n AVAW_BBOX
conda activate AVAW_BBOX
```
#### Using GPU libraries
This Option so far will install the environment for CPU use only, which should run on most machines.
For faster inference, if a suitable GPU is available, please follow the following steps as well.

- Install or upgrade the ultralytics package from PyPI
```bash
pip install -U ultralytics
```

To find the current CUDA Version used, run in the command prompt
```bash
nvidia-smi
```
This will yield output like this, in which the current CUDA version is displayed.
<img width="862" height="210" alt="image" src="https://github.com/user-attachments/assets/0b475fe1-4334-46a4-9d6c-b52e247c2ecb" />

PyTorch requirements vary by operating system and CUDA requirements, so install PyTorch first by following the instructions at PyTorch.

https://pytorch.org/get-started/locally/

<img width="535" alt="image" src="https://github.com/user-attachments/assets/b2c3863a-ca30-4bf8-ba2d-0a890f879468" />

Selecting the correct combination of OS and CUDA Version will yield an install command like:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu130
```

With cu1xx representing the selected CUDA version.



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


---

## 🚀 Usage

Run the application:

Compile and run AVAW_CVAT_BBOX_v4.py in your IDE of choice  
or run the AVAW_CVAT_BBOX_v4.py from CLI:  


```bash
python AVAW_CVAT_BBOX_v4.py
```

or, if on Windows (TO DO PACK AS .exe!) run the:  
```
dist/AVAW_CVAT_BBOX_v4.exe  
```

---













