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
    "graduation-2025": P + "2025 GRAD/WhatsApp Image 2025-11-30 at 21.02.31.jpeg",
    "anniversary-cake-35": P + "35 Anninversary/IMG_0199.JPG",
    "anniversary-cake-cutting": P + "35 Anninversary/IMG_0181.JPG",
    # sent by the owner in chat, 28 Oct 2026
    "anniversary-family-35": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/66157780-image.jpg",
    "founders-kidz-club-party": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/41a02ea9-image.png",  # sent 7 Nov 2026
    "child-protection-march-flag-wave": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/36ac3586-image.png",  # sent 7 Nov 2026
    "dr-jonathan-and-helen-david": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/9589a77b-image.png",  # sent 7 Nov 2026
    "big5-award-2012-presentation": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/48e4b8a4-image.jpg",  # sent 7 Nov 2026 (rotate 90)
    "child-protection-little-marcher": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/0b17b5ac-image.jpg",  # sent 7 Nov 2026
    "child-protection-superhero-dance": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/0caf81bf-image.jpg",  # sent 7 Nov 2026
    "child-protection-saps": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/21a34afd-image.jpg",  # sent 7 Nov 2026
    "child-protection-paramedics": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/1fbf5a98-image.jpg",  # sent 7 Nov 2026
    "lotus-fm-jessica": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/2b7132a6-image.jpg",  # sent 7 Nov 2026
    "lotus-fm-trevor": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/609d3782-image.jpg",  # sent 7 Nov 2026
    "partners-gift-bags-academy": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/29f5dc39-image.jpg",  # sent 7 Nov 2026
    "partners-kidz-club-balls": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/5e7bbb41-image.jpg",  # sent 7 Nov 2026
    "kidz-club-1990s": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/78bfd992-image.jpg",  # sent 7 Nov 2026
    "pam-mills-kidz-club": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/bd0e779e-image.jpg",  # sent 7 Nov 2026
    "distribution-trevor-parcels": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/af151cba-image.jpg",  # sent 7 Nov 2026
    "national-planning-ps-raj": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/67c141ec-image.jpg",  # sent 7 Nov 2026
    "schools-event-folders": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/2761dc44-image.jpg",  # sent 7 Nov 2026
    "inter-school-competition-winners": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/519db333-image.jpg",  # sent 7 Nov 2026
    "partners-speak-out-school": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/07041157-image.jpg",  # sent 7 Nov 2026
    "kidz-club-ballet-2009": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/53c0f6d8-image.jpg",  # sent 7 Nov 2026
    "bca-concert-2019-fairies": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/0f530ea8-image.jpg",  # sent 7 Nov 2026
    "meeting-community-leaders": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/0a8ceaef-image.jpg",  # sent 7 Nov 2026
    "academy-pretend-kitchen": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/b15de8bd-image.jpg",  # BCA activities, sent 7 Nov 2026
    "academy-colouring-worksheets": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/d614021f-image.jpg",  # BCA activities, sent 7 Nov 2026
    "academy-shop-role-play": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/66d45a70-image.jpg",  # BCA activities, sent 7 Nov 2026
    "academy-nature-binoculars": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/ecaa92b0-image.jpg",  # BCA activities, sent 7 Nov 2026
    "academy-pattern-building": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/d21427a4-image.jpg",  # BCA activities, sent 7 Nov 2026
    "academy-coding-grids": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/e0717732-image.jpg",  # BCA activities, sent 7 Nov 2026
    "academy-leaf-magnifier": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/c9cb0944-image.jpg",  # BCA activities, sent 7 Nov 2026
    "i-can-read-parent-workshop": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/5c8820d9-image.png",  # sent 7 Nov 2026
    "bca-grade-r-graduates-2022": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/d88803cb-image.png",  # sent 7 Nov 2026 (white strip at top trimmed)
    "founders-and-exco": "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/cf834791-image.jpg",
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
