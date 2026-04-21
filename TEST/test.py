from cv2 import imread, resize, cvtColor, COLOR_BGR2RGB, rectangle, putText, LINE_AA
from pathlib import Path
from ultralytics import YOLO
import matplotlib.pyplot as plt
import shutil

# ----------------------------
# Configuration
# ----------------------------
yolo_model = YOLO("test_model.pt")

set_conf, set_iou = 0.7, 0.8
num_images = 3
display_size = (640, 640)  # width, height
tol = 1e-6

current_dir = Path.cwd()
labels_dir = current_dir / "labels"
labels_dir.mkdir(exist_ok=True)

# If your APP exports files as test (1)_APP.txt, keep this True.
# If your APP exports as test (1).txt, set this to False.
use_app_suffix = False

# Class names for plotting
class_names = yolo_model.names

# BGR colors per class
class_colors = {
    0: (0, 255, 0),      # green
    1: (255, 0, 0),      # blue
    2: (0, 0, 255),      # red
    3: (0, 255, 255),    # yellow
    4: (255, 0, 255),    # magenta
    5: (255, 255, 0),    # cyan
}


# ----------------------------
# Helpers
# ----------------------------
def parse_yolo_file(txt_path):
    """Read YOLO txt file into list of tuples: (cls, xc, yc, w, h)."""
    boxes = []
    if not txt_path.exists():
        return boxes

    with open(txt_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if not parts:
                continue
            cls = int(parts[0])
            vals = [float(x) for x in parts[1:]]
            boxes.append((cls, *vals))
    return boxes


def lines_match(a, b, tol=1e-5):
    """Compare two YOLO boxes with numeric tolerance."""
    if a[0] != b[0]:
        return False
    return all(abs(x - y) <= tol for x, y in zip(a[1:], b[1:]))


def compare_box_lists(generated_lines, reference_lines, tol=1e-5):
    """Greedy matching of generated/reference boxes using numeric tolerance."""
    matched = 0
    used_reference = set()

    for g in generated_lines:
        for j, r in enumerate(reference_lines):
            if j in used_reference:
                continue
            if lines_match(g, r, tol=tol):
                matched += 1
                used_reference.add(j)
                break

    total = max(len(generated_lines), len(reference_lines))
    similarity = matched / total * 100 if total else 100.0
    return matched, total, similarity


def yolo_to_xyxy(box, image_width, image_height):
    """Convert YOLO normalized box (cls, xc, yc, w, h) to pixel xyxy."""
    cls, xc, yc, bw, bh = box
    x1 = int((xc - bw / 2) * image_width)
    y1 = int((yc - bh / 2) * image_height)
    x2 = int((xc + bw / 2) * image_width)
    y2 = int((yc + bh / 2) * image_height)
    return cls, x1, y1, x2, y2


def draw_boxes(image_bgr, boxes, source_prefix="", class_names=None, class_colors=None):
    """Draw YOLO boxes onto a BGR image with class names and class colors."""
    h, w = image_bgr.shape[:2]
    out = image_bgr.copy()

    for box in boxes:
        cls, x1, y1, x2, y2 = yolo_to_xyxy(box, w, h)

        color = class_colors.get(cls, (255, 255, 255)) if class_colors else (255, 255, 255)
        class_label = class_names.get(cls, f"class_{cls}") if class_names else str(cls)
        text = f"{source_prefix}{class_label} ({cls})"

        rectangle(out, (x1, y1), (x2, y2), color, 2)
        putText(
            out,
            text,
            (x1, max(15, y1 - 5)),
            0,
            0.5,
            color,
            1,
            LINE_AA,
        )

    return out


# ----------------------------
# Clear previous Ultralytics labels
# ----------------------------
for txt_file in labels_dir.glob("*.txt"):
    txt_file.unlink()


# ----------------------------
# Run inference and save Ultralytics labels
# ----------------------------
for i in range(num_images):
    image_name = f"test ({i+1}).png"
    image_path = current_dir / image_name

    image = imread(str(image_path))
    if image is None:
        print(f"Could not read image: {image_path}")
        continue

    image = resize(image, display_size)

    yolo_model(
        image,
        agnostic_nms=True,
        conf=set_conf,
        iou=set_iou,
        augment=True,
        save_txt=True,
        save=False,
        project=current_dir,
        name=".",
        exist_ok=True
    )

    temp_txt = labels_dir / "image0.txt"
    final_txt = labels_dir / f"test ({i+1}).txt"

    if temp_txt.exists():
        if final_txt.exists():
            final_txt.unlink()
        shutil.move(str(temp_txt), str(final_txt))
    else:
        print(f"Missing generated label file for {image_name}")


# ----------------------------
# Compare all images
# ----------------------------
total_matching = 0
total_generated = 0
total_reference = 0
total_total = 0

per_image_results = []

for i in range(num_images):
    generated_txt = labels_dir / f"test ({i+1}).txt"

    if use_app_suffix:
        reference_txt = current_dir / f"test ({i+1})_APP.txt"
    else:
        reference_txt = current_dir / f"test ({i+1}).txt"

    if not generated_txt.exists() or not reference_txt.exists():
        print(f"Missing comparison files for test ({i+1})")
        continue

    generated_lines = parse_yolo_file(generated_txt)
    reference_lines = parse_yolo_file(reference_txt)

    matched, total, similarity = compare_box_lists(
        generated_lines,
        reference_lines,
        tol=tol
    )

    total_matching += matched
    total_generated += len(generated_lines)
    total_reference += len(reference_lines)
    total_total += total

    per_image_results.append(
        {
            "index": i + 1,
            "generated_txt": generated_txt,
            "reference_txt": reference_txt,
            "generated_lines": generated_lines,
            "reference_lines": reference_lines,
            "matched": matched,
            "total": total,
            "similarity": similarity,
        }
    )

    print(f"test ({i+1}) similarity: {similarity:.2f}%")
    print(f"  Matching boxes: {matched}")
    print(f"  Generated boxes: {len(generated_lines)}")
    print(f"  Reference boxes: {len(reference_lines)}")
    print()

overall_similarity = total_matching / total_total * 100 if total_total else 100.0

print("=== Overall Results ===")
print(f"Total matching boxes: {total_matching}")
print(f"Total generated boxes: {total_generated}")
print(f"Total reference boxes: {total_reference}")
print(f"Overall similarity: {overall_similarity:.2f}%")


# ----------------------------
# Plot APP vs ULTRALYTICS annotations
# ----------------------------
if per_image_results:
    fig, axes = plt.subplots(len(per_image_results), 2, figsize=(14, 5 * len(per_image_results)))
    fig.suptitle(f"Ultralytics vs APP Annotation Comparison\nTolerance = {tol}", fontsize=16)
    if len(per_image_results) == 1:
        axes = [axes]

    for row, result in enumerate(per_image_results):
        idx = result["index"]
        image_path = current_dir / f"test ({idx}).png"

        image = imread(str(image_path))
        if image is None:
            continue

        image = resize(image, display_size)

        ultralytics_img = draw_boxes(
            image,
            result["generated_lines"],
            source_prefix="U: ",
            class_names=class_names,
            class_colors=class_colors,
        )

        app_img = draw_boxes(
            image,
            result["reference_lines"],
            source_prefix="A: ",
            class_names=class_names,
            class_colors=class_colors,
        )

        ultralytics_img = cvtColor(ultralytics_img, COLOR_BGR2RGB)
        app_img = cvtColor(app_img, COLOR_BGR2RGB)

        axes[row][0].imshow(ultralytics_img)
        axes[row][0].set_title(
            f"Ultralytics - test ({idx})\n{result['generated_txt'].name}"
        )
        axes[row][0].axis("off")

        axes[row][1].imshow(app_img)
        axes[row][1].set_title(
            f"APP - test ({idx})\n"
            f"{result['reference_txt'].name}\n"
            f"Similarity: {result['similarity']:.2f}%"
        )
        axes[row][1].axis("off")
    plt.tight_layout()
    plt.show()