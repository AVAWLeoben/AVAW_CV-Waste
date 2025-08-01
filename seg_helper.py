import cv2
import numpy as np
import os

class MorphologicSegHelper:
    def __init__(self,owner=None):
        self.owner = owner
        self.annotations = []
        self.image_path = None
        self.yolo_segments = None
    
    def segment_image(self,image_path):
        # Load image
        self.annotations = []
        self.yolo_segments = []
        self.image_path = image_path
        image = cv2.imread(image_path)
        h, w = image.shape[:2]

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Edge detection
        edged = cv2.Canny(gray, 30, 200)

        # Morphological closing
        kernel = np.ones((5, 5), np.uint8)
        closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)

        # Get only external contours
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Convert contours to YOLO segmentation format
        for contour in contours:
            # Flatten points and normalize to [0,1]
            poly = contour.reshape(-1, 2)
            poly_norm = poly / np.array([w, h])  # normalize
            poly_list = poly_norm.flatten().tolist()
            self.yolo_segments.append(poly_list)

        # Example YOLO annotation line (class_id=0)
        # Format: class_id x1 y1 x2 y2 x3 y3 ...
        for poly in self.yolo_segments:
            ann = [0] + [float(f"{p:.6f}") for p in poly]
            self.annotations.append(ann)
        return self.annotations
    
    def save_annotations(self):
        # annotations list now contains YOLO-seg compatible lines
        txt_path = os.path.splitext(self.image_path)[0] + ".txt"

        with open(txt_path, "w") as f:
            for poly in self.yolo_segments:
                # Class ID 0 (change if needed)
                line = "0 " + " ".join([f"{p:.6f}" for p in poly])
                f.write(line + "\n")
        print(f"YOLO annotation saved to {txt_path}")



if __name__ == "__main__":
    morph_helper = MorphologicSegHelper()
    morph_helper.segment_image("frame_2025-02-07_11-20-51.png")
    morph_helper.save_annotations()
