# AVAW CVAT BBox Tool

## 📦 Installation

### Option A — Using pip 

```bash
git clone https://github.com/<your-org>/<repo-name>.git
cd <repo-name>

python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

---

### Option B — Using Conda (recommended)

```bash
conda env create -f environment.yml
conda activate <env-name>
```

---

## 🚀 Usage

Run the application:

```bash
python AVAW_CVAT_BBOX_v4.py
```

or (if packaged with entry point):

```bash
avaw-cvat-bbox
```

---

## 📋 Requirements

Core dependencies:

* Python ≥ 3.12
* numpy
* pillow
* opencv-python
* natsort
* ultralytics

Install with:

```bash
pip install -r requirements.txt
```

---

## 🛠️ Development

Recommended setup:

```bash
conda env create -f environment.yml
conda activate <env-name>
```

---

```bash
python -m venv .venv
pip install -U pip
pip install -r requirements.txt
```

---

## ⚠️ Notes

* Tkinter must be available in your Python installation.
* Large images may require additional RAM.
* GPU acceleration depends on your PyTorch installation.

