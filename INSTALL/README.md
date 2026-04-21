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













