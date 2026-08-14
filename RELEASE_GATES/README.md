Below is the manual release acceptance test suite I would run before uploading 1.0.1 to PyPI. It is based on the functionality actually exposed by your current code: navigation, annotation editing, marquee/multiselect, zoom/pan, YOLO inference, class management, auxiliary windows, augmentation, saving, shortcuts, settings, and packaging. The keyboard bindings alone cover F1–F6, F12, navigation keys, copy/paste, saving, translation, YOLO inference, select-all, and others.

Use a simple result notation while testing:

PASS
FAIL - short description
N/A

0. Prepare a clean test environment

Use your clean Anaconda environment:

conda activate CV-Waste_1.0.1_test

Install the exact wheel:

pip install dist\avaw_cv_waste-1.0.1-py3-none-any.whl

Confirm installation:

pip show avaw-cv-waste

Expected:

Name: avaw-cv-waste
Version: 1.0.1

Create a temporary working directory with copies of several .png/.jpg images and their .txt annotation files. Do not use irreplaceable annotation files for these tests because we will intentionally overwrite/delete annotations.

1. Package/launcher smoke test — CRITICAL
1.1 Start through installed command

Run:

avaw-cv-waste

Expected:

GUI opens.
No traceback appears in Anaconda Prompt.
Main window has an image canvas.
Menus appear.
Controls below the image appear.
No missing logo.png, help.txt, or other resource error.

The PyPI launcher points to initialize_bbox_app(), which exists in the module.

1.2 Close and reopen

Close normally.

Run again:

avaw-cv-waste

Expected:

Starts normally a second time.
No stale-process issue.
No corrupted settings issue.
2. Initial UI and startup state — CRITICAL
2.1 Image display

Expected on startup:

Image is visible.
Bounding boxes from its .txt file appear.
Class colors appear.
Title contains the image name.
No boxes appear offset from their objects.
2.2 Progress indicator

If there are, for example, 100 images and saved index is 13:

Expected:

13/99

and progress bar should be approximately 13% filled.

This now works because the progress widgets are initialized before initial load_image(), while load_image() updates both the bar and label.

2.3 Current-image entry

Expected:

Numeric entry shows the current image index.
It agrees with progress label and displayed image.
2.4 Window resizing

Resize the window several times:

wider
narrower
taller
smaller

Expected:

Canvas resizes.
Controls remain usable.
Image stays sensibly positioned.
Boxes stay aligned with the image.
No exceptions.
3. Image navigation — CRITICAL

Your app supports buttons plus several keyboard alternatives.

3.1 Next button

Click Next.

Expected:

Next image appears.
Correct annotations load.
image counter increments by 1.
progress bar advances.
title changes.
3.2 Previous button

Click Previous.

Expected:

Previous image returns.
counter decrements.
annotations correspond to correct image.
3.3 Arrow keys

Test:

Right Arrow → next
Left Arrow  → previous
3.4 Alternative navigation keys

Test:

D → next
E → next

A → previous
Q → previous

Expected: same behavior as navigation buttons.

3.5 Boundary behavior

Navigate to image 0.

Press Previous / Left / A / Q.

Expected:

Remains at image 0.
No crash.

Navigate to final image.

Press Next / Right / D / E.

Expected:

Remains at last image.
No crash.
4. Jump-to-image — CRITICAL
4.1 Valid index

Enter, for example:

2

into the image index entry.

Press Jump To Image.

Expected:

Image 2 appears.
label becomes 2/max.
progress bar moves.
4.2 Enter shortcut

Enter another valid number and press:

Enter

Expected: jumps to that image.

4.3 Current index

Enter current index and press Enter.

Expected:

Nothing harmful happens.
Console may print Already at that image.
4.4 Invalid high index

Enter something larger than final image index.

Expected:

Image does not change.
No crash.
Console reports valid range.
4.5 Non-numeric input

Try typing letters.

Expected:

Numeric validation should reject them.
5. Image list window

Press:

F3

Expected:

Image List window opens.
all loaded image names appear.

Select a different image and click Load Image.

Expected:

selected image becomes current image.
annotations update.
index updates.

Press F3 again / close the window.

Expected:

window hides.
opening it again works.
6. Load a different image folder — CRITICAL

Use:

File → Load Images

This menu action is wired to folder selection.

Choose your disposable test folder.

Expected:

folder contents load.
natural sorting is sensible.
current image becomes image 0.
annotations are loaded from that folder.
image list window updates.
progress becomes 0/(N-1).
6.1 Folder with no supported images

Choose an empty folder.

Expected:

warning appears.
no crash.
application remains usable.
6.2 Update image list

While app is running, add a new .png to the directory.

Choose:

File → Update Image List

Expected:

new file appears in image list.
7. Single bounding-box selection — CRITICAL
7.1 Select box

Left-click inside an existing bounding box.

Expected:

box becomes selected.
selection highlight appears.
class dropdown changes to its class.

The click routine converts screen coordinates back into image coordinates before selecting.

7.2 Deselect

Left-click empty image space without meaningfully dragging.

Expected:

current selection clears.
no exception.

This specifically tests the self.stop_multiselect() fix.

7.3 Overlapping boxes

If you have nested/overlapping boxes, click an overlapping region.

Expected:

sensible box is selected.
no random crash.
8. Move bounding box — CRITICAL

Select a box in its center.

Hold left mouse button and drag it.

Expected:

entire box moves.
size stays unchanged.
release finalizes position.
box remains aligned with cursor.
8.1 Move against image boundary

Drag box partly beyond:

left edge
right edge
top
bottom

Expected:

coordinates are clamped.
annotation does not remain outside the image.
no negative-coordinate corruption.
9. Resize bounding boxes — CRITICAL

Test all four corners:

top-left
top-right
bottom-left
bottom-right

Expected:

correct corner follows mouse.
opposite corner stays fixed.
box updates live.
releasing finalizes new shape.

Your current corner hit-test deliberately uses a constant 8 screen-pixel sensitivity by dividing by zoom factor.

9.1 Repeat while zoomed

Zoom substantially in.

Repeat corner resize.

Expected:

corner remains approximately equally easy to grab.
hit area does not become huge.
resize movement remains proportional to mouse movement.

This is an important regression test for the recent zoom fix.

10. Marquee / rectangle selection — CRITICAL
10.1 Rectangle around several boxes

Start on empty canvas.

Hold left button.

Drag white dashed rectangle around 2–3 complete boxes.

Release.

Expected:

white dashed rectangle appears during drag.
boxes fully inside become multiselected.
boxes only partly inside should not be selected.

The implementation explicitly selects boxes completely contained by the rectangle.

10.2 Drag in opposite direction

Repeat:

bottom-right → top-left
top-right → bottom-left

Expected:

selection works regardless of drag direction.
10.3 Empty marquee

Draw a rectangle containing no boxes.

Expected:

nothing selected.
no crash.
10.4 Marquee while zoomed

Zoom to approximately 2× or more.

Pan image.

Draw marquee around several boxes.

Expected:

correct boxes are selected despite zoom and pan.

This is important because marquee release converts canvas coordinates back to original-image coordinates.

11. Ctrl multiselect — CRITICAL

Hold:

Ctrl

and left-click several boxes individually.

Expected:

boxes accumulate in selection.
previously selected boxes stay selected.

The binding is explicitly Ctrl + left mouse.

11.1 Clear multiselect

Use:

Ctrl + Right Click

Expected:

multiselection clears.
11.2 Select all

Press:

Ctrl+A

Expected:

all boxes become selected.
12. Move multiple boxes — CRITICAL

Select several boxes.

Hold:

Ctrl + Left Drag

Expected:

all selected boxes move together.
12.1 Repeat at high zoom

Zoom in significantly.

Ctrl-drag selected boxes approximately 50 screen pixels.

Expected:

boxes move by the visually expected amount.
movement does not become exaggerated according to zoom.

The current implementation divides drag delta by the zoom factor.

13. Create new manual bounding box — CRITICAL

Press:

N

Expected console message indicates new-box mode. N and Down Arrow are both bound to this function.

Click-drag a new box.

Expected:

green preview rectangle appears while dragging.
releasing creates the annotation.
resulting annotation stays within image bounds.

Repeat using:

Down Arrow
13.1 Context-menu creation

Right-click empty canvas:

New Box

Expected:

same new-box behavior.

The empty-selection context menu exposes New Box, Paste, Undo, Save, and Track Annotations.

14. Delete annotations — CRITICAL
14.1 Single box

Select a box.

Press:

Delete

Expected:

selected box disappears.
14.2 Context menu

Select a box.

Right-click → Delete Box.

Expected: same result.

14.3 Multiple boxes

Multiselect several boxes.

Press Delete.

Expected:

selected boxes are removed.
unrelated boxes remain.
15. Undo — CRITICAL

Modify a box.

Click:

Undo

Expected:

previous annotation state returns.

Repeat after:

moving
deleting
creating

Expected:

undo behaves consistently.

The main UI exposes a dedicated Undo button.

16. Copy/paste
16.1 Single box

Select a box.

Press:

Ctrl+C
Ctrl+V

Expected:

duplicate annotation appears.
16.2 Context menu

Select box → Right Click → Copy Box.

Click empty space → Right Click → Paste Box.

Expected: same result.

16.3 Multiple boxes

Select several boxes.

Press:

Ctrl+C
Ctrl+V

Expected:

all selected annotations are duplicated.
17. Class dropdown — CRITICAL

Select a box.

Choose a different class in dropdown.

Expected:

annotation changes to chosen class.
displayed color changes accordingly.
right-click menu/class state remains consistent.
18. Change class names — CRITICAL

Press:

F5

or:

Model → Change Class Names

Rename classes without changing class count.

Example:

Plastic, Metal, Paper

→

Plastic Waste, Metal Waste, Paper Waste

Expected:

names change.
class count remains the same.
existing class colors remain unchanged.
dropdown updates.
context menu updates.

This is precisely the behavior we fixed around class-count comparison.

18.1 Change number of classes

Add one class.

Expected:

no index errors.
color list is regenerated/adjusted according to current implementation.
dropdown and color window contain every class.

Remove a class again.

Expected:

no crash.
19. Class color window

Press:

F4

Expected:

Class Colours window opens.
19.1 Preset color

Choose a class.

Click a preset color.

Expected:

class button changes.
existing boxes of that class change color immediately.
19.2 Custom color

Click:

Choose custom colour...

Select a color.

Expected:

preview updates.
annotation color updates.
19.3 Many classes

If practical, create >9 classes.

Expected:

color window remains usable.
scrolling works.
no IndexError.
19.4 Restart behavior

At present your settings file stores class names but not class_colors, so custom colors are not clearly designed to persist across restart.

If you expect color persistence as a product requirement, treat reset-after-restart as a bug. Otherwise test only same-session behavior.

20. Right-click context menus
Box selected

Right-click selected box.

Verify:

Delete Box
Copy Box
each class name

are shown.

Change class using context menu.

Expected:

selected box class updates.
No box selected

Right-click empty canvas.

Verify:

Undo
Save Annotations
Paste Box
Track Annotations
New Box

appear.

Execute each once.

Expected: no errors.

21. Zoom — CRITICAL

Mouse wheel up.

Expected:

image zooms in around cursor.

Mouse wheel down.

Expected:

zooms out.
cannot zoom below minimum fit level.

The active Zoomer binds MouseWheel plus Linux Button-4/5.

21.1 Annotation alignment

At several zoom levels:

boxes remain aligned.
labels remain attached.
clicks select the correct underlying box.
21.2 Zoom around different points

Place cursor near:

top-left
center
bottom-right

Zoom in.

Expected:

image zooms around mouse position rather than jumping unpredictably.
22. Pan — CRITICAL

Zoom in until image exceeds canvas.

Hold middle mouse button:

Middle Mouse + Drag

Expected:

image pans.

Release middle button.

Expected:

panning stops.

Bindings are Button-2 / B2-Motion.

22.1 Pan limits

Attempt to drag image completely off-screen.

Expected:

panning is clamped.
image cannot disappear irretrievably.
22.2 Select after pan

Pan image, then:

select box
move box
resize box
marquee select

Expected:

all operate on correct annotations.
23. YOLO model loading — CRITICAL if inference is advertised

Use:

File → Load Model

or:

Model → Load Model

Choose your .pt test model.

Expected:

model loads.
no exception.
class names behave as expected.
model path is remembered.

The menu exposes Load Model in both File and Model menus.

24. Full YOLO inference — CRITICAL

With model loaded:

Click:

Run YOLO Inference

Expected:

existing annotation set is replaced by detections.
boxes appear.
class colors are correct.
no invalid class index.
confidence values are stored.

Repeat using shortcut:

Y

The button and keyboard shortcut both call YOLO inference.

25. Single-click YOLO annotation

With model loaded:

Hold:

Alt + Left Click

on an obvious detected object.

Expected:

YOLO runs.
highest-confidence prediction containing clicked point is added.
only one annotation is added.

The mouse binding invokes single_click_prediction() directly.

25.1 Empty location

Alt-click area with no detection.

Expected:

console reports no detected object.
nothing added.
no crash.
25.2 Zoom/pan

Zoom and pan.

Alt-click object again.

Expected:

correct object is detected, demonstrating coordinate conversion still works.
25.3 J shortcut

Press:

J

Your code binds J to the same prediction handler.

Verify carefully whether it acts at the intended mouse location. If it behaves unpredictably, log it as a shortcut bug.

26. Model settings

Open:

Model → Change Model Setting

Test:

confidence slider
IoU slider
class-agnostic NMS checkbox
inference-time augmentation checkbox

Expected:

status text updates.
next YOLO inference uses current values.
reopening window reflects current in-session values.
27. Confidence display

After YOLO inference press:

H

Expected:

confidence display toggles.
boxes remain.
annotations do not change.

Press H again.

Expected: returns to original display.

28. Annotation translation

Use a box well away from image edges.

Press:

4 → left
6 → right
8 → up
2 → down

Expected:

all annotations move exactly one image pixel in requested direction.
28.1 Boundary behavior

Translate boxes repeatedly into an image edge.

Expected:

values clamp.
boxes do not become invalid.
28.2 Translation window

Open:

Global → Translate Annotations

Move horizontal/vertical sliders.

Expected:

annotations translate interactively.
no desynchronization.
29. Delete duplicates

Create an exact duplicate using copy/paste.

Choose:

Global → Delete Duplicates

Expected:

reports at least one duplicate removed.
only one equivalent box remains.
30. Delete all annotations

Use disposable image.

Choose:

Global → Delete All Annotations

Expected:

every box disappears.
app remains usable.

Then use Undo if expected.

Do not save unless intentionally testing empty-label saving.

31. Flip augmentation

Use:

Augmentation → Flip Image Vertically

Expected:

image flips according to application's command semantics.
bounding boxes flip with image.
annotations remain aligned.

Then:

Augmentation → Flip Image Horizontally

Expected same alignment.

Because image and annotation flip operations are coupled, alignment is what matters most.

32. Save annotation — CRITICAL

Modify one box.

Use:

Save Annotations

Expected:

success dialog.
.txt file timestamp changes.
file contains normalized YOLO lines.

The save routine records current annotation state and writes the corresponding .txt.

Repeat using:

S

and:

Up Arrow

Expected: same save behavior.

32.1 Reload verification

After saving:

navigate away
navigate back

Expected:

edited annotation reloads exactly.

This validates the full cycle:

pixel coordinates
→ YOLO normalized text
→ reload
→ pixel coordinates
33. Unsaved-change prompt — CRITICAL

Turn Auto Save OFF.

Modify a box.

Navigate to next image.

Expected:

prompt asks whether to save.

Choose No.

Expected:

navigates without saving.

Return to image.

Expected:

old on-disk state is restored.

Repeat:

modify
navigate
choose Yes

Expected:

file is saved.
returning shows modification.

This also validates the last_save fix we discussed.

34. Auto Save — CRITICAL

Toggle using checkbox.

Expected:

checkbox state changes.

Modify box.

Navigate away.

Expected:

no save confirmation.
annotation file is automatically saved.

Return.

Expected:

modification persists.

Now press:

F6

Expected:

Auto Save toggles and checkbox follows it.
35. Save-change prompting toggle

Press:

P

Expected:

notification reports save-change setting toggled.

With prompting disabled:

modify box
navigate

Expected according to code:

save prompt is suppressed.

Toggle back on afterwards.

36. Save image

Choose:

Augmentation → Save Image

Select destination.

Expected:

PNG is created.
saved image opens normally.
app remains functional.
37. Save annotated image

Choose:

Augmentation → Save Annotated Image

Expected:

output image is created.
it visually contains expected annotation rendering.
temporary deselection during save does not permanently alter selected state.
38. Screenshot

Press:

F12

Expected console:

Screenshot Saved!

The code saves a file named from the title plus _viewport.png.

Verify file appears in the current working directory.

Open it.

Expected:

valid image.
39. Box List window

Press:

F2

Expected:

annotation list opens.
object count agrees with visible annotations.

Click an entry.

Expected:

corresponding annotation becomes selected.

Delete/add boxes.

Expected:

list refreshes appropriately.

Close/reopen several times.

Expected: no stale/destroyed-window error.

40. Help functionality

Press:

F1

Expected:

help opens.
help text loads from packaged files_bbox/help.txt.

Use:

Help → Ultralytics

Expected:

browser attempts to open correct external resource.
41. Show folders externally

Test:

File → Show Image Folder Externally
File → Show Annotations Folder Externally

Expected on Windows:

File Explorer opens correct directory.
no console exception.
42. Separate annotation folder

Prepare:

images\
    img1.png

labels\
    img1.txt

Load the image directory.

Then:

File → Load Annotations from different Folder

choose labels.

Expected:

annotation appears.
saving writes to label folder rather than image folder.

Navigate images and verify correct matching by filename.

43. Missing/empty annotation files

Prepare image with no matching .txt.

Load it.

Expected:

image loads with zero boxes.
no error.

Create an empty .txt.

Reload.

Expected:

zero boxes.
no error.

Create a box and save.

Expected:

.txt receives annotation line.
44. Settings persistence — CRITICAL

Set a recognizable state:

image folder = test folder
annotation folder = test folder
current image = e.g. 2
custom class names
Auto Save = chosen value
confidence visibility = chosen value
save-prompt flag = chosen value
model path = test model

Exit normally.

Restart:

avaw-cv-waste

Expected:

correct folder restored.
correct image index restored.
progress matches restored index.
class names restored.
Auto Save restored.
confidence setting restored.
save flag restored.
model path reloads if still valid.

Those are the values currently written into settings.json.

Pay particular attention to whether settings actually survive an installed PyPI launch, because your current settings path is inside the package directory.

45. Startup after folder deletion

Close app.

Rename/delete the previously saved image folder.

Start app again.

Expected:

app handles invalid saved path gracefully.
resets/falls back rather than crashing.
46. No-model behavior

Start without valid model loaded.

Click:

Run YOLO Inference

Expected:

informative No YOLO model loaded message.
no traceback.

Alt-click image.

Expected: same graceful warning.

47. UI window cycling

Open and close repeatedly:

F2 Box List
F3 Image List
F4 Class Colors
F5 Class Names
Model Settings
Translation
Help

Expected:

every window can be reopened.
no invalid command name, destroyed-widget, or stale-reference errors.
48. High-interaction regression test — CRITICAL

This is the one I would do last.

On one image:

Zoom to ~2×.
Pan.
Select a box.
Resize it.
Move it.
Create a new box.
Marquee-select several boxes.
Ctrl-drag them.
Change their class.
Copy/paste them.
Delete one.
Undo.
Save.
Move to next image.
Return.

Expected:

no crash.
saved geometry remains correct.
no boxes jump when changing zoom.
no selection state leaks into the next image.
progress and title remain correct.

This sequence exercises most of the code paths that have recently changed.

49. Final clean-install test — CRITICAL

After all development testing, uninstall:

pip uninstall avaw-cv-waste

Confirm removal.

Then reinstall only from the wheel:

pip install dist\avaw_cv_waste-1.0.1-py3-none-any.whl

Do not run the Python file from your source directory.

Prefer changing to another directory first:

cd %USERPROFILE%
avaw-cv-waste

This is important because it proves the installed wheel contains everything it needs instead of accidentally finding files from your source checkout.

Then repeat just this final smoke subset:

launch
load demo image
navigate
select/move/resize
marquee select
zoom/pan
load model
YOLO inference
save annotation
restart
settings restore

If those all pass from outside the source repository, I would consider the wheel ready for upload.

Release gate

I would classify these as must-pass before PyPI:

1   package launch
2   startup/progress
3   navigation
7   selection
8   move
9   resize
10  marquee selection
11  multiselect
12  multidrag at zoom
13  new box
14  delete
15  undo
17  class changes
18  class-name rename
21  zoom
22  pan
23  model load
24  inference
32  annotation saving
33  unsaved-change detection
34  autosave
44  settings persistence
48  mixed-interaction regression
49  clean installed-wheel test

If all of those pass and the remaining convenience/UI tests don't expose a crash, that is a strong release candidate for 1.0.1.
