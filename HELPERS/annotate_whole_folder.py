import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from ultralytics import YOLO
from pathlib import Path
import json
import time

IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".bmp", ".tif")
SETTINGS_FILE = Path(__file__).parent / "yolo_annotator_settings.json"

DARK_BG = "#2E2E2E"
DARK_FRAME = "#3C3F41"
BTN_COLOR = "#4CAF50"
BTN_HOVER = "#45A049"
TEXT_COLOR = "#FFFFFF"
ACCENT_COLOR = "#FF9800"

class YoloAnnotatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YOLO Auto Annotator")
        self.root.geometry("520x500")
        self.root.configure(bg=DARK_BG)

        self.image_folder = None
        self.output_folder = None
        self.model_path = None
        self.conf = 0.8
        self.iou = 0.2

        self._build_ui()
        self.load_settings()

    def _build_ui(self):
        pad = 10

        def style_button(btn):
            btn.configure(bg=BTN_COLOR, fg=TEXT_COLOR, activebackground=BTN_HOVER,
                          font=("Arial", 10, "bold"), relief="flat", padx=10, pady=5)

        # Frame for folder selection
        frame_paths = tk.Frame(self.root, bg=DARK_BG)
        frame_paths.pack(pady=pad, fill="x")

        self.lbl_images = tk.Label(frame_paths, text="No folder selected", bg=DARK_BG, fg=TEXT_COLOR)
        self.lbl_output = tk.Label(frame_paths, text="No folder selected", bg=DARK_BG, fg=TEXT_COLOR)
        self.lbl_model = tk.Label(frame_paths, text="No model selected", bg=DARK_BG, fg=TEXT_COLOR)

        btn_images = tk.Button(frame_paths, text="Select Image Folder", command=self.select_images)
        style_button(btn_images)
        btn_images.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.lbl_images.grid(row=0, column=1, sticky="w", padx=5)

        btn_output = tk.Button(frame_paths, text="Select Output Folder", command=self.select_output)
        style_button(btn_output)
        btn_output.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.lbl_output.grid(row=1, column=1, sticky="w", padx=5)

        btn_model = tk.Button(frame_paths, text="Select YOLO Model", command=self.select_model)
        style_button(btn_model)
        btn_model.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.lbl_model.grid(row=2, column=1, sticky="w", padx=5)

        # Frame for sliders
        frame_sliders = tk.LabelFrame(self.root, text="Settings", bg=DARK_FRAME, fg=ACCENT_COLOR, padx=10, pady=10, font=("Arial", 10, "bold"))
        frame_sliders.pack(pady=pad, fill="x", padx=10)

        # Confidence slider
        self.conf_label = tk.Label(frame_sliders, text=f"Confidence: {self.conf:.2f}", bg=DARK_FRAME, fg=TEXT_COLOR)
        self.conf_label.pack(anchor="w")
        self.conf_slider = tk.Scale(frame_sliders, from_=10, to=100, orient=tk.HORIZONTAL,
                                    command=self.update_conf_label, bg=DARK_FRAME, fg=TEXT_COLOR,
                                    troughcolor="#555555", highlightthickness=0)
        self.conf_slider.set(int(self.conf * 100))
        self.conf_slider.pack(fill="x")

        # IoU slider
        self.iou_label = tk.Label(frame_sliders, text=f"IoU: {self.iou:.2f}", bg=DARK_FRAME, fg=TEXT_COLOR)
        self.iou_label.pack(anchor="w")
        self.iou_slider = tk.Scale(frame_sliders, from_=5, to=100, orient=tk.HORIZONTAL,
                                   command=self.update_iou_label, bg=DARK_FRAME, fg=TEXT_COLOR,
                                   troughcolor="#555555", highlightthickness=0)
        self.iou_slider.set(int(self.iou * 100))
        self.iou_slider.pack(fill="x")

        # Frame for start button and progress
        frame_run = tk.Frame(self.root, bg=DARK_BG)
        frame_run.pack(pady=pad)

        self.start_btn = tk.Button(frame_run, text="Start Annotation", command=self.run_yolo)
        style_button(self.start_btn)
        self.start_btn.pack(pady=5)

        style = ttk.Style()
        style.theme_use('default')
        style.configure("TProgressbar", troughcolor="#555555", background=ACCENT_COLOR, thickness=20)

        self.progress = ttk.Progressbar(frame_run, length=450, mode="determinate", style="TProgressbar")
        self.progress.pack(pady=5)

        self.status = tk.Label(frame_run, text="Idle", bg=DARK_BG, fg=TEXT_COLOR, font=("Arial", 10, "bold"))
        self.status.pack()

    # Slider callbacks
    def update_conf_label(self, val):
        self.conf = int(val) / 100
        self.conf_label.config(text=f"Confidence: {self.conf:.2f}")
        self.save_settings()

    def update_iou_label(self, val):
        self.iou = int(val) / 100
        self.iou_label.config(text=f"IoU: {self.iou:.2f}")
        self.save_settings()

    # Folder and model selection
    def select_images(self):
        path = filedialog.askdirectory(title="Select Image Folder")
        if path:
            self.image_folder = Path(path)
            self.lbl_images.config(text=str(self.image_folder))
            self.save_settings()

    def select_output(self):
        path = filedialog.askdirectory(title="Select Output Folder")
        if path:
            self.output_folder = Path(path)
            self.lbl_output.config(text=str(self.output_folder))
            self.save_settings()

    def select_model(self):
        path = filedialog.askopenfilename(title="Select YOLO Model", filetypes=[("YOLO Model", "*.pt")])
        if path:
            self.model_path = path
            self.lbl_model.config(text=str(self.model_path))
            self.save_settings()

    # Run YOLO
    def run_yolo(self):
        if not self.image_folder or not self.model_path:
            messagebox.showwarning("Missing input", "Please select images and YOLO model first")
            return

        if not self.output_folder:
            self.output_folder = self.image_folder

        images = [p for p in self.image_folder.iterdir() if p.suffix.lower() in IMAGE_EXTS]
        total = len(images)
        if total == 0:
            messagebox.showinfo("No images", "No images found in folder")
            return

        self.progress["maximum"] = total
        self.progress["value"] = 0
        self.start_btn.config(state="disabled")

        model = YOLO(self.model_path)
        start_time = time.time()

        for i, img in enumerate(images, start=1):
            elapsed = time.time() - start_time
            images_left = total - i + 1
            eta = images_left * (elapsed / i) if i > 0 else 0
            self.status.config(text=f"Processing {i}/{total}: {img.name} | ETA: {int(eta)}s")
            self.progress["value"] = i
            self.root.update_idletasks()
            self.root.update()

            model(
                str(img),
                augment=True,
                agnostic_nms=True,
                conf=self.conf,
                iou=self.iou,
                save_txt=True,
                project=str(self.output_folder),
                exist_ok=True,
                verbose=False
            )

        self.status.config(text="Finished ✔")
        self.start_btn.config(state="normal")

    # Save / load settings
    def save_settings(self):
        data = {
            "image_folder": str(self.image_folder) if self.image_folder else "",
            "output_folder": str(self.output_folder) if self.output_folder else "",
            "model_path": str(self.model_path) if self.model_path else "",
            "conf": self.conf,
            "iou": self.iou
        }
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def load_settings(self):
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                if data.get("image_folder"):
                    self.image_folder = Path(data["image_folder"])
                    self.lbl_images.config(text=str(self.image_folder))
                if data.get("output_folder"):
                    self.output_folder = Path(data["output_folder"])
                    self.lbl_output.config(text=str(self.output_folder))
                if data.get("model_path"):
                    self.model_path = data["model_path"]
                    self.lbl_model.config(text=str(self.model_path))
                if data.get("conf"):
                    self.conf = data["conf"]
                    self.conf_slider.set(int(self.conf*100))
                if data.get("iou"):
                    self.iou = data["iou"]
                    self.iou_slider.set(int(self.iou*100))
            except Exception as e:
                print(f"Error loading settings: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = YoloAnnotatorApp(root)
    root.mainloop()
