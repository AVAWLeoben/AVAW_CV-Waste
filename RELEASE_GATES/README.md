# AVAW CV-Waste — Manual Release Acceptance Test Suite

Use this checklist before publishing a new release to PyPI.

Recommended result notation:

```text
PASS
FAIL - short description
N/A
```

> **Important:** Run destructive tests against a throwaway copy of your demo images and labels. Several tests intentionally save, delete, flip, or overwrite annotations.

---

## 0. Prepare a clean test environment

Activate the clean Anaconda environment:

```cmd
conda activate CV-Waste_1.0.1_test
```

Install the exact wheel:

```cmd
pip install dist\avaw_cv_waste-1.0.1-py3-none-any.whl
```

Confirm installation:

```cmd
pip show avaw-cv-waste
```

Expected:

```text
Name: avaw-cv-waste
Version: 1.0.1
```

Create a temporary working directory with copies of several `.png` / `.jpg` images and their `.txt` annotation files.

---

# 1. Package / launcher smoke test — CRITICAL

## 1.1 Start through installed command

Run:

```cmd
avaw-cv-waste
```

Expected:

- GUI opens.
- No traceback appears in Anaconda Prompt.
- Main window has an image canvas.
- Menus appear.
- Controls below the image appear.
- No missing `logo.png`, `help.txt`, or other resource error.

## 1.2 Close and reopen

Close normally.

Run again:

```cmd
avaw-cv-waste
```

Expected:

- Starts normally a second time.
- No stale-process issue.
- No corrupted settings issue.

---

# 2. Initial UI and startup state — CRITICAL

## 2.1 Image display

Expected on startup:

- Image is visible.
- Bounding boxes from its `.txt` file appear.
- Class colors appear.
- Title contains the image name.
- No boxes appear offset from their objects.

## 2.2 Progress indicator

If there are, for example, 100 images and the saved index is 13:

Expected:

```text
13/99
```

The progress bar should be approximately 13% filled.

## 2.3 Current-image entry

Expected:

- Numeric entry shows the current image index.
- It agrees with the progress label and displayed image.

## 2.4 Window resizing

Resize the window several times:

- wider
- narrower
- taller
- smaller

Expected:

- Canvas resizes.
- Controls remain usable.
- Image stays sensibly positioned.
- Boxes stay aligned with the image.
- No exceptions.

---

# 3. Image navigation — CRITICAL

## 3.1 Next button

Click **Next**.

Expected:

- Next image appears.
- Correct annotations load.
- Image counter increments by 1.
- Progress bar advances.
- Title changes.

## 3.2 Previous button

Click **Previous**.

Expected:

- Previous image returns.
- Counter decrements.
- Annotations correspond to the correct image.

## 3.3 Arrow keys

Test:

```text
Right Arrow -> next
Left Arrow  -> previous
```

## 3.4 Alternative navigation keys

Test:

```text
D -> next
E -> next

A -> previous
Q -> previous
```

Expected: same behavior as navigation buttons.

## 3.5 Boundary behavior

Navigate to image 0.

Press Previous / Left / A / Q.

Expected:

- Remains at image 0.
- No crash.

Navigate to final image.

Press Next / Right / D / E.

Expected:

- Remains at last image.
- No crash.

---

# 4. Jump-to-image — CRITICAL

## 4.1 Valid index

Enter, for example:

```text
2
```

into the image index entry.

Press **Jump To Image**.

Expected:

- Image 2 appears.
- Label becomes `2/max`.
- Progress bar moves.

## 4.2 Enter shortcut

Enter another valid number and press:

```text
Enter
```

Expected: jumps to that image.

## 4.3 Current index

Enter the current index and press Enter.

Expected:

- Nothing harmful happens.
- Console may print `Already at that image`.

## 4.4 Invalid high index

Enter something larger than the final image index.

Expected:

- Image does not change.
- No crash.
- Console reports valid range.

## 4.5 Non-numeric input

Try typing letters.

Expected:

- Numeric validation rejects them.

---

# 5. Image list window

Press:

```text
F3
```

Expected:

- Image List window opens.
- All loaded image names appear.

Select a different image and click **Load Image**.

Expected:

- Selected image becomes current image.
- Annotations update.
- Index updates.

Press `F3` again / close the window.

Expected:

- Window hides.
- Opening it again works.

---

# 6. Load a different image folder — CRITICAL

Use:

```text
File -> Load Images
```

Choose your disposable test folder.

Expected:

- Folder contents load.
- Natural sorting is sensible.
- Current image becomes image 0.
- Annotations are loaded from that folder.
- Image list window updates.
- Progress becomes `0/(N-1)`.

## 6.1 Folder with no supported images

Choose an empty folder.

Expected:

- Warning appears.
- No crash.
- Application remains usable.

## 6.2 Update image list

While app is running, add a new `.png` to the directory.

Choose:

```text
File -> Update Image List
```

Expected:

- New file appears in image list.

---

# 7. Single bounding-box selection — CRITICAL

## 7.1 Select box

Left-click inside an existing bounding box.

Expected:

- Box becomes selected.
- Selection highlight appears.
- Class dropdown changes to its class.

## 7.2 Deselect

Left-click empty image space without meaningfully dragging.

Expected:

- Current selection clears.
- No exception.

## 7.3 Overlapping boxes

If you have nested / overlapping boxes, click an overlapping region.

Expected:

- Sensible box is selected.
- No random crash.

---

# 8. Move bounding box — CRITICAL

Select a box in its center.

Hold left mouse button and drag it.

Expected:

- Entire box moves.
- Size stays unchanged.
- Release finalizes position.
- Box remains aligned with cursor.

## 8.1 Move against image boundary

Drag box partly beyond:

- left edge
- right edge
- top
- bottom

Expected:

- Coordinates are clamped.
- Annotation does not remain outside the image.
- No negative-coordinate corruption.

---

# 9. Resize bounding boxes — CRITICAL

Test all four corners:

```text
top-left
top-right
bottom-left
bottom-right
```

Expected:

- Correct corner follows mouse.
- Opposite corner stays fixed.
- Box updates live.
- Releasing finalizes new shape.

## 9.1 Repeat while zoomed

Zoom substantially in.

Repeat corner resize.

Expected:

- Corner remains approximately equally easy to grab.
- Hit area does not become huge.
- Resize movement remains proportional to mouse movement.

---

# 10. Marquee / rectangle selection — CRITICAL

## 10.1 Rectangle around several boxes

Start on empty canvas.

Hold left button.

Drag a white dashed rectangle around 2–3 complete boxes.

Release.

Expected:

- White dashed rectangle appears during drag.
- Boxes fully inside become multiselected.
- Boxes only partly inside should **not** be selected.

## 10.2 Drag in opposite direction

Repeat:

- bottom-right -> top-left
- top-right -> bottom-left

Expected:

- Selection works regardless of drag direction.

## 10.3 Empty marquee

Draw a rectangle containing no boxes.

Expected:

- Nothing selected.
- No crash.

## 10.4 Marquee while zoomed

Zoom to approximately 2x or more.

Pan image.

Draw marquee around several boxes.

Expected:

- Correct boxes are selected despite zoom and pan.

---

# 11. Ctrl multiselect — CRITICAL

Hold:

```text
Ctrl
```

and left-click several boxes individually.

Expected:

- Boxes accumulate in selection.
- Previously selected boxes stay selected.

## 11.1 Clear multiselect

Use:

```text
Ctrl + Right Click
```

Expected:

- Multiselection clears.

## 11.2 Select all

Press:

```text
Ctrl+A
```

Expected:

- All boxes become selected.

---

# 12. Move multiple boxes — CRITICAL

Select several boxes.

Hold:

```text
Ctrl + Left Drag
```

Expected:

- All selected boxes move together.

## 12.1 Repeat at high zoom

Zoom in significantly.

Ctrl-drag selected boxes approximately 50 screen pixels.

Expected:

- Boxes move by the visually expected amount.
- Movement does **not** become exaggerated according to zoom.

---

# 13. Create new manual bounding box — CRITICAL

Press:

```text
N
```

Expected console message indicates new-box mode.

Click-drag a new box.

Expected:

- Green preview rectangle appears while dragging.
- Releasing creates the annotation.
- Resulting annotation stays within image bounds.

Repeat using:

```text
Down Arrow
```

## 13.1 Context-menu creation

Right-click empty canvas:

```text
New Box
```

Expected:

- Same new-box behavior.

---

# 14. Delete annotations — CRITICAL

## 14.1 Single box

Select a box.

Press:

```text
Delete
```

Expected:

- Selected box disappears.

## 14.2 Context menu

Select a box.

Right-click -> **Delete Box**.

Expected: same result.

## 14.3 Multiple boxes

Multiselect several boxes.

Press Delete.

Expected:

- Selected boxes are removed.
- Unrelated boxes remain.

---

# 15. Undo — CRITICAL

Modify a box.

Click:

```text
Undo
```

Expected:

- Previous annotation state returns.

Repeat after:

- moving
- deleting
- creating

Expected:

- Undo behaves consistently.

---

# 16. Copy / paste

## 16.1 Single box

Select a box.

Press:

```text
Ctrl+C
Ctrl+V
```

Expected:

- Duplicate annotation appears.

## 16.2 Context menu

Select box -> Right Click -> **Copy Box**.

Click empty space -> Right Click -> **Paste Box**.

Expected: same result.

## 16.3 Multiple boxes

Select several boxes.

Press:

```text
Ctrl+C
Ctrl+V
```

Expected:

- All selected annotations are duplicated.

---

# 17. Class dropdown — CRITICAL

Select a box.

Choose a different class in dropdown.

Expected:

- Annotation changes to chosen class.
- Displayed color changes accordingly.
- Right-click menu / class state remains consistent.

---

# 18. Change class names — CRITICAL

Press:

```text
F5
```

or:

```text
Model -> Change Class Names
```

Rename classes **without changing class count**.

Example:

```text
Plastic, Metal, Paper
```

to:

```text
Plastic Waste, Metal Waste, Paper Waste
```

Expected:

- Names change.
- Class count remains the same.
- Existing class colors remain unchanged.
- Dropdown updates.
- Context menu updates.

## 18.1 Change number of classes

Add one class.

Expected:

- No index errors.
- Color list is regenerated / adjusted according to current implementation.
- Dropdown and color window contain every class.

Remove a class again.

Expected:

- No crash.

---

# 19. Class color window

Press:

```text
F4
```

Expected:

- Class Colours window opens.

## 19.1 Preset color

Choose a class.

Click a preset color.

Expected:

- Class button changes.
- Existing boxes of that class change color immediately.

## 19.2 Custom color

Click:

```text
Choose custom colour...
```

Select a color.

Expected:

- Preview updates.
- Annotation color updates.

## 19.3 Many classes

If practical, create more than 9 classes.

Expected:

- Color window remains usable.
- Scrolling works.
- No `IndexError`.

## 19.4 Restart behavior

If color persistence is expected as a product requirement, verify that custom colors survive restart.

Otherwise test only same-session behavior.

---

# 20. Right-click context menus

## Box selected

Right-click selected box.

Verify:

- Delete Box
- Copy Box
- each class name

Change class using context menu.

Expected:

- Selected box class updates.

## No box selected

Right-click empty canvas.

Verify:

- Undo
- Save Annotations
- Paste Box
- Track Annotations
- New Box

Execute each once.

Expected:

- No errors.

---

# 21. Zoom — CRITICAL

Mouse wheel up.

Expected:

- Image zooms in around cursor.

Mouse wheel down.

Expected:

- Zooms out.
- Cannot zoom below minimum fit level.

## 21.1 Annotation alignment

At several zoom levels:

- Boxes remain aligned.
- Labels remain attached.
- Clicks select the correct underlying box.

## 21.2 Zoom around different points

Place cursor near:

- top-left
- center
- bottom-right

Zoom in.

Expected:

- Image zooms around mouse position rather than jumping unpredictably.

---

# 22. Pan — CRITICAL

Zoom in until image exceeds canvas.

Hold middle mouse button:

```text
Middle Mouse + Drag
```

Expected:

- Image pans.

Release middle button.

Expected:

- Panning stops.

## 22.1 Pan limits

Attempt to drag image completely off-screen.

Expected:

- Panning is clamped.
- Image cannot disappear irretrievably.

## 22.2 Select after pan

Pan image, then:

- select box
- move box
- resize box
- marquee select

Expected:

- All operate on correct annotations.

---

# 23. YOLO model loading — CRITICAL if inference is advertised

Use:

```text
File -> Load Model
```

or:

```text
Model -> Load Model
```

Choose your `.pt` test model.

Expected:

- Model loads.
- No exception.
- Class names behave as expected.
- Model path is remembered.

---

# 24. Full YOLO inference — CRITICAL

With model loaded:

Click:

```text
Run YOLO Inference
```

Expected:

- Existing annotation set is replaced by detections.
- Boxes appear.
- Class colors are correct.
- No invalid class index.
- Confidence values are stored.

Repeat using shortcut:

```text
Y
```

Expected: same result.

---

# 25. Single-click YOLO annotation

With model loaded:

Hold on Windows:

```text
Alt + Left Click
```

J shortcut For Linux:

Press:

```text
J
```

on an obvious detected object.

Expected:

- YOLO runs.
- Highest-confidence prediction containing clicked point is added.
- Only one annotation is added.

---

## 25.1 Empty location

Alt-click area with no detection.

Expected:

- Console reports no detected object.
- Nothing added.
- No crash.

## 25.2 Zoom / pan

Zoom and pan.

Alt-click object again.

Expected:

- Correct object is detected.


# 26. Model settings

Open:

```text
Model -> Change Model Setting
```

Test:

- confidence slider
- IoU slider
- class-agnostic NMS checkbox
- inference-time augmentation checkbox

Expected:

- Status text updates.
- Next YOLO inference uses current values.
- Reopening window reflects current in-session values.

---

# 27. Confidence display

After YOLO inference press:

```text
H
```

Expected:

- Confidence display toggles.
- Boxes remain.
- Annotations do not change.

Press `H` again.

Expected:

- Returns to original display.

---

# 28. Annotation translation

Use a box well away from image edges.

Press:

```text
4 -> left
6 -> right
8 -> up
2 -> down
```

Expected:

- All annotations move exactly one image pixel in requested direction.

## 28.1 Boundary behavior

Translate boxes repeatedly into an image edge.

Expected:

- Values clamp.
- Boxes do not become invalid.

## 28.2 Translation window

Open:

```text
Global -> Translate Annotations
```

Move horizontal / vertical sliders.

Expected:

- Annotations translate interactively.
- No desynchronization.

---

# 29. Delete duplicates

Create an exact duplicate using copy / paste.

Choose:

```text
Global -> Delete Duplicates
```

Expected:

- Reports at least one duplicate removed.
- Only one equivalent box remains.

---

# 30. Delete all annotations

Use a disposable image.

Choose:

```text
Global -> Delete All Annotations
```

Expected:

- Every box disappears.
- App remains usable.

Then use Undo if expected.

Do not save unless intentionally testing empty-label saving.

---

# 31. Flip augmentation

Use:

```text
Augmentation -> Flip Image Vertically
```

Expected:

- Image flips according to application's command semantics.
- Bounding boxes flip with image.
- Annotations remain aligned.

Then:

```text
Augmentation -> Flip Image Horizontally
```

Expected same alignment.

---

# 32. Save annotation — CRITICAL

Modify one box.

Use:

```text
Save Annotations
```

Expected:

- Success dialog.
- `.txt` file timestamp changes.
- File contains normalized YOLO lines.

Repeat using:

```text
S
```

and:

```text
Up Arrow
```

Expected: same save behavior.

## 32.1 Reload verification

After saving:

1. Navigate away.
2. Navigate back.

Expected:

- Edited annotation reloads exactly.

This validates the full cycle:

```text
pixel coordinates
-> YOLO normalized text
-> reload
-> pixel coordinates
```

---

# 33. Unsaved-change prompt — CRITICAL

Turn **Auto Save OFF**.

Modify a box.

Navigate to next image.

Expected:

- Prompt asks whether to save.

Choose **No**.

Expected:

- Navigates without saving.

Return to image.

Expected:

- Old on-disk state is restored.

Repeat:

- modify
- navigate
- choose **Yes**

Expected:

- File is saved.
- Returning shows modification.

---

# 34. Auto Save — CRITICAL

Toggle using checkbox.

Expected:

- Checkbox state changes.

Modify box.

Navigate away.

Expected:

- No save confirmation.
- Annotation file is automatically saved.

Return.

Expected:

- Modification persists.

Now press:

```text
F6
```

Expected:

- Auto Save toggles and checkbox follows it.

---

# 35. Save-change prompting toggle

Press:

```text
P
```

Expected:

- Notification reports save-change setting toggled.

With prompting disabled:

- modify box
- navigate

Expected:

- Save prompt is suppressed.

Toggle back on afterwards.

---

# 36. Save image

Choose:

```text
Augmentation -> Save Image
```

Select destination.

Expected:

- PNG is created.
- Saved image opens normally.
- App remains functional.

---

# 37. Save annotated image

Choose:

```text
Augmentation -> Save Annotated Image
```

Expected:

- Output image is created.
- It visually contains expected annotation rendering.
- Temporary deselection during save does not permanently alter selected state.

---

# 38. Screenshot

Press:

```text
F12
```

Expected console:

```text
Screenshot Saved!
```

Verify file appears in the current working directory.

Open it.

Expected:

- Valid image.

---

# 39. Box List window

Press:

```text
F2
```

Expected:

- Annotation list opens.
- Object count agrees with visible annotations.

Click an entry.

Expected:

- Corresponding annotation becomes selected.

Delete / add boxes.

Expected:

- List refreshes appropriately.

Close / reopen several times.

Expected:

- No stale or destroyed-window error.

---

# 40. Help functionality

Press:

```text
F1
```

Expected:

- Help opens.
- Help text loads.

Use:

```text
Help -> Ultralytics
```

Expected:

- Browser attempts to open the correct external resource.

---

# 41. Show folders externally

Test:

```text
File -> Show Image Folder Externally
File -> Show Annotations Folder Externally
```

Expected on Windows:

- File Explorer opens the correct directory.
- No console exception.

---

# 42. Separate annotation folder

Prepare:

```text
images\
    img1.png

labels\
    img1.txt
```

Load the image directory.

Then:

```text
File -> Load Annotations from different Folder
```

Choose `labels`.

Expected:

- Annotation appears.
- Saving writes to label folder rather than image folder.

Navigate images and verify correct matching by filename.

---

# 43. Missing / empty annotation files

Prepare image with **no matching `.txt`**.

Load it.

Expected:

- Image loads with zero boxes.
- No error.

Create an empty `.txt`.

Reload.

Expected:

- Zero boxes.
- No error.

Create a box and save.

Expected:

- `.txt` receives annotation line.

---

# 44. Settings persistence — CRITICAL

Set a recognizable state:

- image folder = test folder
- annotation folder = test folder
- current image = e.g. 2
- custom class names
- Auto Save = chosen value
- confidence visibility = chosen value
- save-prompt flag = chosen value
- model path = test model

Exit normally.

Restart:

```cmd
avaw-cv-waste
```

Expected:

- Correct folder restored.
- Correct image index restored.
- Progress matches restored index.
- Class names restored.
- Auto Save restored.
- Confidence setting restored.
- Save flag restored.
- Model path reloads if still valid.

Pay particular attention to whether settings survive an installed PyPI launch.

---

# 45. Startup after folder deletion

Close app.

Rename or delete the previously saved image folder.

Start app again.

Expected:

- App handles invalid saved path gracefully.
- Resets / falls back rather than crashing.

---

# 46. No-model behavior

Start without a valid model loaded.

Click:

```text
Run YOLO Inference
```

Expected:

- Informative `No YOLO model loaded` message.
- No traceback.

Alt-click image.

Expected:

- Same graceful warning.

---

# 47. UI window cycling

Open and close repeatedly:

```text
F2 Box List
F3 Image List
F4 Class Colors
F5 Class Names
Model Settings
Translation
Help
```

Expected:

- Every window can be reopened.
- No `invalid command name`, destroyed-widget, or stale-reference errors.

---

# 48. High-interaction regression test — CRITICAL

On one image:

1. Zoom to approximately 2x.
2. Pan.
3. Select a box.
4. Resize it.
5. Move it.
6. Create a new box.
7. Marquee-select several boxes.
8. Ctrl-drag them.
9. Change their class.
10. Copy / paste them.
11. Delete one.
12. Undo.
13. Save.
14. Move to next image.
15. Return.

Expected:

- No crash.
- Saved geometry remains correct.
- No boxes jump when changing zoom.
- No selection state leaks into the next image.
- Progress and title remain correct.

---

# 49. Final clean-install test — CRITICAL

After all development testing, uninstall:

```cmd
pip uninstall avaw-cv-waste
```

Confirm removal.

Then reinstall **only from the wheel**:

```cmd
pip install dist\avaw_cv_waste-1.0.1-py3-none-any.whl
```

Do **not** run the Python file from your source directory.

Prefer changing to another directory first:

```cmd
cd %USERPROFILE%
avaw-cv-waste
```

This proves the installed wheel contains everything it needs instead of accidentally finding files from your source checkout.

Repeat this final smoke subset:

```text
launch
load demo image
navigate
select / move / resize
marquee select
zoom / pan
load model
YOLO inference
save annotation
restart
settings restore
```

---

# Release gate

These are the **must-pass before PyPI** tests:

- [ ] 1 — Package launch
- [ ] 2 — Startup / progress
- [ ] 3 — Navigation
- [ ] 7 — Selection
- [ ] 8 — Move
- [ ] 9 — Resize
- [ ] 10 — Marquee selection
- [ ] 11 — Multiselect
- [ ] 12 — Multidrag at zoom
- [ ] 13 — New box
- [ ] 14 — Delete
- [ ] 15 — Undo
- [ ] 17 — Class changes
- [ ] 18 — Class-name rename
- [ ] 21 — Zoom
- [ ] 22 — Pan
- [ ] 23 — Model load
- [ ] 24 — Inference
- [ ] 32 — Annotation saving
- [ ] 33 — Unsaved-change detection
- [ ] 34 — Auto Save
- [ ] 44 — Settings persistence
- [ ] 48 — Mixed-interaction regression
- [ ] 49 — Clean installed-wheel test

If all of those pass and the remaining convenience / UI tests do not expose a crash, the build is a strong release candidate.
