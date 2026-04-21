# YOLO Annotation Similarity Test

Currently, there is no automated test to verify that YOLO predictions generated directly through the model match the annotations that are created, stored, and exported inside the application.

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

1. Run inference on a fixed set of test images using a known YOLO model
2. Save the raw YOLO txt outputs
3. Load the same images and predictions into the application
4. Export the annotations again from the application
5. Compare the original and exported annotation files line-by-line
6. Use a numeric tolerance (for example `1e-5`) instead of strict string matching

The test should report:

* total number of matching boxes
* mismatching boxes
* similarity percentage
* coordinate differences
