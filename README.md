# AVAW CVAT BBox Tool

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

![Alt text](DEMO/Screenshot_UI.png)
*(Add screenshots here if desired)*

---

## 📦 Installation

### Option A — Using pip (recommended)

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

### Option B — Using Conda

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

## 📁 Project Structure

```
.
├── AVAW_CVAT_BBOX_v4.py
├── annotations_bbox/      # Images and YOLO labels
├── files_bbox/            # Config files, class names, logo
├── settings.json          # Persistent user settings
├── requirements.txt
└── README.md
```

---

## ⚙️ Configuration

### Class Names

Edit:

```
files_bbox/class_names.txt
```

Format:

```
person,car,bicycle,dog
```

---

### Settings

User settings are stored in:

```
settings.json
```

The app automatically saves:

* last image index
* folders
* model path
* UI preferences

---

## 🧠 YOLO Model Support

You can load a YOLO model for automatic predictions.

Supported via:

* Ultralytics YOLO

Adjust in the **Model Settings** window inside the app.

---

## 🖱️ Basic Controls

| Action       | Description         |
| ------------ | ------------------- |
| Left drag    | Create bounding box |
| Click box    | Select box          |
| Drag corners | Resize              |
| Drag box     | Move                |
| Multi-select | Enabled via UI      |
| Mouse wheel  | Zoom                |
| Middle drag  | Pan                 |

*(Adjust if your actual bindings differ)*

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
python -m venv .venv
pip install -U pip
pip install -r requirements.txt
```

---

## ⚠️ Notes

* Tkinter must be available in your Python installation.
* Large images may require additional RAM.
* GPU acceleration depends on your PyTorch installation.

---

## 🐛 Known Limitations

* Single-window architecture
* Limited undo history
* Designed primarily for YOLO bbox workflows

---

## 🤝 Contributing

Pull requests and issues are welcome.

Suggested workflow:

1. Fork the repo
2. Create a feature branch
3. Submit a PR

---

## 📄 License

MIT License (adjust if different).

---

## 👤 Author

Your Name
Your Organization

---

## ⭐ Acknowledgements

* OpenCV
* Ultralytics
* Tkinter
* Pillow

---
