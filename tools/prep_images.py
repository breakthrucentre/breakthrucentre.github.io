"""Make web images (WebP + JPEG, 800w and 1600w) with descriptive file names."""
import os
from PIL import Image, ImageOps

USB = "/mnt/user-data/uploads/d/Website photos/"
FB = "/tmp/claude-0/-home-claude/bbefee32-b007-5e8f-8388-b57898708902/scratchpad/fb/"
OUT = "/home/claude/bc-website/docs/images/"
os.makedirs(OUT, exist_ok=True)

SRC = {
  # USB photos
  "heritage-day-flag-wide": USB+"breakthrough-centre-groutville-home-header.jpg",
  "heritage-day-circle": USB+"bca-heritage-day-celebration-preschool.jpg",
  "heritage-day-flag": USB+"bca-heritage-day-learners-sa-flag.jpg",
  "graduation-class": USB+"bca-graduation-class-ecd-kwadukuza.jpg",
  "graduate-certificate": USB+"bca-graduate-certificate-trophy-groutville.jpg",
  "end-of-year-function": USB+"bca-learner-end-of-year-function.jpg",
  "back-to-school": USB+"bca-back-to-school-learner.jpg",
  "valentines-boy": USB+"bca-valentines-day-2026-boy.jpg",
  "valentines-girl": USB+"bca-valentines-day-2026-girl.jpg",
  "valentines-red-dress": USB+"bca-valentines-day-2026-red-dress.jpg",
  "valentines-smile": USB+"bca-valentines-day-2026-smile.jpg",
  "valentines-learner": USB+"bca-valentines-day-2026-learner.jpg",
  "valentines-balloon": USB+"bca-valentines-day-i-love-you-balloon.jpg",
  "valentines-2024": USB+"bca-valentines-day-learner-2024.jpg",
  # Facebook photos already on the site
  "community-outreach-crowd": FB+"home-03.jpg",
  "preschool-classroom": FB+"home-05.jpg",
  "kidz-club-costumes": FB+"home-06.jpg",
  "community-gathering": FB+"home-07.jpg",
  "beach-wedding-wagon": FB+"home-08.jpg",
  "computer-class": FB+"home-09.jpg",
  "children-praying": FB+"home-10.jpg",
  "kidz-club-sunday": FB+"kidz-01.jpg",
  "kidz-club-meal": FB+"kidz-02.jpg",
  "kidz-club-juice": FB+"kidz-03.jpg",
  "wedding-beach-setup": FB+"wedding-01.jpg",
  "wedding-canopy": FB+"wedding-02.jpg",
  "wedding-beach-guests": FB+"wedding-03.jpg",
  "wedding-reception-table": FB+"wedding-04.jpg",
  "wedding-vows": FB+"wedding-05.jpg",
  "wedding-family": FB+"wedding-06.jpg",
  "wedding-bride-vows": FB+"wedding-07.jpg",
  "wedding-reception-hall": FB+"wedding-08.jpg",
  "wedding-napkin": FB+"wedding-09.jpg",
  "wedding-cake": FB+"wedding-10.jpg",
  "wedding-cake-family": FB+"wedding-11.jpg",
  "wedding-coastal-path": FB+"wedding-12.jpg",
}

CROP_BOTTOM = {"graduation-class": 0.84}  # trims the phone-screen inset in the original photo
sizes = {}
for name, path in SRC.items():
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    if name in CROP_BOTTOM:
        im = im.crop((0, 0, im.width, int(im.height * CROP_BOTTOM[name])))
    sizes[name] = im.size
    for w in (800, 1600):
        if w == 1600 and im.width <= 900:
            continue  # don't upscale small originals
        r = im if im.width <= w else im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        r.save(f"{OUT}{name}-{w}.webp", quality=78, method=6)
        if w == 800:
            r.save(f"{OUT}{name}-{w}.jpg", quality=80, optimize=True, progressive=True)

logo = Image.open("/mnt/user-data/uploads/Downloads/bc-logo.png").convert("RGBA")
bbox = logo.getbbox()
logo = logo.crop(bbox)
logo.save(OUT + "logo.png", optimize=True)
s = logo.copy(); s.thumbnail((256, 256)); s.save(OUT + "logo-256.png", optimize=True)
fav = Image.new("RGBA", (max(logo.size),)*2, (0, 0, 0, 0))
fav.paste(logo, ((fav.width-logo.width)//2, (fav.height-logo.height)//2))
fav.resize((180, 180), Image.LANCZOS).save(OUT + "apple-touch-icon.png")
fav.resize((48, 48), Image.LANCZOS).save(OUT + "favicon.png")
import json; json.dump({k: list(v) for k, v in sizes.items()}, open(OUT + "../../tools/sizes.json", "w"), indent=0)
print(len(SRC), "photos;", "logo", logo.size)
