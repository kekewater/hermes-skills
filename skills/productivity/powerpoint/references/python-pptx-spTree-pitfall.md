# python-pptx Slide Shape Deletion Pitfall

## Problem

Deleting shapes from an existing slide then adding new shapes via `slide.shapes.add_shape()` **often breaks the PPTX file**.

```python
# DON'T DO THIS — breaks spTree
for sh in slide.shapes:
    sp = sh._element
    sp.getparent().remove(sp)

# After this, slide.shapes raises InvalidXmlError:
# "required <p:spTree> child element not present"
```

## Root Cause

When you remove all shapes via XML, python-pptx's shape enumerator (`slide.shapes`) can lose track of the `spTree` element. The shapes attribute depends on `spTree` being present and having children. If you clear it too aggressively or remove structural elements (`nvGrpSpPr`, `grpSpPr`), the slide becomes unreadable.

## Correct Approach: Zip-Level Slide Replacement

Instead of modifying slides in-place with python-pptx, **extract → edit XML → repack** at the zip level:

```python
import zipfile, shutil, tempfile, os
from lxml import etree

workdir = tempfile.mkdtemp()

# 1. Unpack
with zipfile.ZipFile('input.pptx', 'r') as zf:
    zf.extractall(workdir)

# 2. Replace slide XML files directly
slides_dir = os.path.join(workdir, 'ppt', 'slides')
new_slide_xml = b'...'  # your new slide content
with open(os.path.join(slides_dir, 'slide7.xml'), 'wb') as f:
    f.write(new_slide_xml)

# 3. Update presentation.xml if adding/removing slides
pres_path = os.path.join(workdir, 'ppt', 'presentation.xml')
tree = etree.parse(pres_path)
sldIdLst = tree.find('...')
# Add/remove <p:sldId> elements as needed
tree.write(pres_path)

# 4. Update _rels/presentation.xml.rels
rels_path = os.path.join(workdir, 'ppt', '_rels', 'presentation.xml.rels')
# Add/remove <Relationship> elements for slide count
tree.write(rels_path)

# 5. Repack
os.chdir(workdir)
with zipfile.ZipFile('output.pptx', 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(workdir):
        for file in files:
            zf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), workdir))

shutil.rmtree(workdir)
```

## Better Yet: Use the Skill's Built-in Tools

The `powerpoint` skill provides:

- `scripts/office/unpack.py presentation.pptx unpacked/` — extract to XML directory
- `scripts/add_slide.py unpacked/ slide2.xml` — duplicate a slide with proper rId tracking
- Edit slide XML files directly in `unpacked/ppt/slides/`
- Then repack (see `scripts/clean.py`)

## When python-pptx IS Safe

python-pptx works fine for:

- **Creating new presentations from scratch** (new `Presentation()`)
- **Adding shapes to a new slide** (one created by `add_slide()`)
- **Reading/analyzing content** (just reading `.shapes` and `.text`)
- **Minor text edits** on existing shapes (changing paragraph text)

It fails when you try to **delete** existing shapes from a pre-existing slide and add replacements.

## Creating New Slides for Insertion

Create slides in a separate temp PPTX, then extract their XML:

```python
from pptx import Presentation
from pptx.util import Emu

temp = Presentation()
temp.slide_width = Emu(9144000)   # match target
temp.slide_height = Emu(5143500)

slide = temp.slides.add_slide(temp.slide_layouts[6])  # blank
# ... add shapes here ...

temp.save('/tmp/new_slide.pptx')

# Then extract slide1.xml from this temp file:
with zipfile.ZipFile('/tmp/new_slide.pptx', 'r') as zf:
    zf.extract('ppt/slides/slide1.xml', workdir)
# Copy to target PPTX's slides dir
shutil.copy2(os.path.join(workdir, 'ppt/slides/slide1.xml'),
             os.path.join(slides_dir, 'slide7.xml'))
```

This gives you full control while bypassing python-pptx's fragile in-place editing.
