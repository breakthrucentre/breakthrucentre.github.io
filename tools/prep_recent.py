"""Add recent photos to the site (WebP 800/1600 + JPEG 800) and merge their sizes into tools/sizes.json.

Photos come from the laptop's Pictures folder (BCA 2026, 2025 GRAD, 35 Anninversary),
copied into /mnt/user-data/uploads/Pictures/ by Claude. EXIF (including GPS) is stripped on save.
"""
import json, os
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "docs", "images")
P = "/mnt/user-data/uploads/Pictures/"
B = P + "BCA 2026/WhatsApp Image "

SRC = {
    "academy-graduate-2026": P + "BCA 2026/20260916_080055.jpg",
    "academy-graduate-2026-red": P + "BCA 2026/20260916_080512.jpg",
    "back-to-school-2026": B + "2026-04-08 at 20.35.34 (1).jpeg",
    "back-to-school-learner-2026": B + "2026-04-08 at 20.26.52.jpeg",
    "sunshine-craft": B + "2026-04-17 at 17.29.06.jpeg",
    "water-play": B + "2026-04-17 at 17.51.27.jpeg",
    "parachute-play": B + "2026-04-17 at 18.51.35.jpeg",
    "outdoor-learning-circle": B + "2026-03-27 at 16.04.42.jpeg",
    "ball-play": B + "2026-03-27 at 16.51.40.jpeg",
    "finger-painting": B + "2026-03-27 at 16.57.24.jpeg",
    "shape-sorting": B + "2026-04-10 at 18.36.45.jpeg",
    "garden-planting": B + "2026-04-17 at 17.30.50.jpeg",
    "leaf-art": B + "2026-04-24 at 16.38.31.jpeg",
    "space-art": B + "2026-07-31 at 17.26.37.jpeg",
    "rocket-counting": B + "2026-07-31 at 17.35.46.jpeg",
    "building-blocks": B + "2026-07-31 at 17.40.45.jpeg",
    "solar-system-project": B + "2026-07-31 at 17.45.42.jpeg",
    "maths-worksheets": B + "2026-07-31 at 16.21.58.jpeg",
    "graduation-2025": P + "2025 GRAD/WhatsApp Image 2025-11-30 at 21.02.31.jpeg",
    "anniversary-cake-35": P + "35 Anninversary/IMG_0199.JPG",
    "anniversary-cake-cutting": P + "35 Anninversary/IMG_0181.JPG",
}

sizes_path = os.path.join(HERE, "sizes.json")
sizes = json.load(open(sizes_path))
for name, path in SRC.items():
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    sizes[name] = list(im.size)
    for w in (800, 1600):
        if w == 1600 and im.width <= 900:
            continue  # don't upscale small originals
        r = im if im.width <= w else im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        r.save(os.path.join(OUT, f"{name}-{w}.webp"), quality=78, method=6)
        if w == 800:
            r.save(os.path.join(OUT, f"{name}-{w}.jpg"), quality=80, optimize=True, progressive=True)
json.dump(sizes, open(sizes_path, "w"), indent=0)
print(len(SRC), "photos added")
