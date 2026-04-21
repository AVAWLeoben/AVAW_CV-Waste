# YOLO Annotation Similarity Test

Currently, there is no automated test to verify that YOLO predictions generated directly through the model match the annotations that are created, stored, and exported inside the application.
Therefore, we propose a manual approach to testing whether these two paths generate the same outcome as expected.

This is important because the application internally converts predictions into annotation objects, displays them in the GUI, and later saves them back into YOLO format.

During this process, differences can occur due to:

* conversion from float to integer coordinates
* resizing of images before inference
* saving annotations using display dimensions instead of original image dimensions
* rounding or truncation of coordinates before export
* conversion between pixel coordinates and normalized YOLO coordinates

These differences can lead to exported annotation files that do not exactly match the original YOLO model output.

---

## Expected Behavior

The application should preserve YOLO predictions as closely as possible when importing and exporting annotations.

The test should compare:

* direct YOLO predictions saved from a standalone script
* predictions loaded into the application
* annotations exported again from the application

The test should verify that all saved YOLO annotations remain numerically equivalent within a small tolerance.

---

## Suggested Test Procedure

Using the test.py in [TEST]([https://github.com/orgs/community/discussions/22534](https://github.com/AVAWLeoben/AVAW_CVAT/tree/AVAW_BBOX_DEVELOPMENT/TEST) and the application itself we can:

1. Load the same images and predictions into the application
2. Export the annotations again from the application
3. Run inference on a fixed set of test images using a known YOLO model
4. Save the raw YOLO txt outputs
5. Compare the original and exported annotation files line-by-line
6. Use a numeric tolerance (for example `1e-5`) instead of strict string matching

The test reports:
* total number of matching boxes
* mismatching boxes
* similarity percentage
* coordinate differences

# Test Results Reported on Images provided in TEST folder:
- yolo_model = YOLO("test_model.pt")
- set_conf, set_iou = 0.7, 0.8
- num_images = 3
- display_size = (640, 640)  # width, height
- `tol = 1e-5`

```bash
test (1) similarity: 100.00%
  Matching boxes: 36
  Generated boxes: 36
  Reference boxes: 36

test (2) similarity: 100.00%
  Matching boxes: 41
  Generated boxes: 41
  Reference boxes: 41

test (3) similarity: 100.00%
  Matching boxes: 33
  Generated boxes: 33
  Reference boxes: 33

=== Overall Results ===
Total matching boxes: 110
Total generated boxes: 110
Total reference boxes: 110
Overall similarity: 100.00%
```
<img width="1426" height="2145" alt="image" src="https://github.com/user-attachments/assets/30d9dd19-fe34-4837-8a0c-ceebbd238d4f" />

# Test Results Reported on Images provided in TEST folder:
- yolo_model = YOLO("test_model.pt")
- set_conf, set_iou = 0.7, 0.8
- num_images = 3
- display_size = (640, 640)  # width, height
- `tol = 1e-6`

```bash
test (1) similarity: 100.00%
  Matching boxes: 36
  Generated boxes: 36
  Reference boxes: 36

test (2) similarity: 100.00%
  Matching boxes: 41
  Generated boxes: 41
  Reference boxes: 41

test (3) similarity: 100.00%
  Matching boxes: 33
  Generated boxes: 33
  Reference boxes: 33

=== Overall Results ===
Total matching boxes: 110
Total generated boxes: 110
Total reference boxes: 110
Overall similarity: 100.00%
```

- `tol = 1e-6`

```bash
test (1) similarity: 100.00%
  Matching boxes: 36
  Generated boxes: 36
  Reference boxes: 36

test (2) similarity: 95.12%
  Matching boxes: 39
  Generated boxes: 41
  Reference boxes: 41

test (3) similarity: 96.97%
  Matching boxes: 32
  Generated boxes: 33
  Reference boxes: 33

=== Overall Results ===
Total matching boxes: 107
Total generated boxes: 110
Total reference boxes: 110
Overall similarity: 97.27%
```
