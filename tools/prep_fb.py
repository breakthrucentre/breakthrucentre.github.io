"""Add photos saved from the Breakthrough Centre Facebook page (and Jessica Nair's posts about the centre).

The photos were exported from Facebook on 28 Oct 2026 and decoded into FB below (tag-NN.jpg).
Makes WebP 800/1600 + JPEG 800 and merges sizes into tools/sizes.json, like prep_recent.py.
"""
import json, os
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "docs", "images")
FB = "/tmp/claude-0/-home-claude/bbefee32-b007-5e8f-8388-b57898708902/scratchpad/fb2/"

SRC = {
    # Community: child protection
    "child-protection-day-2026": "cp-1-04",
    "child-protection-heroes-2026": "cp-2-00",
    "child-protection-captains-2026": "cp-2-11",
    "child-protection-team-2026": "cp-3-04",
    "child-protection-march": "alb-childprot-march-09",
    "child-protection-march-placards": "alb-childprot-march-03",
    "child-protection-march-crowd": "alb-childprot-march-08",
    # Community: relief and outreach
    "blanket-outreach": "alb-isaiah58-outreach-09",
    "food-parcel-outreach": "alb-isaiah58-outreach-04",
    "outreach-in-the-rain": "alb-isaiah58-outreach-01",
    "gift-box-distribution-2014": "alb-gift-boxes-2014-07",
    "gift-box-hall-2014": "alb-gift-boxes-2014-02",
    "feeding-scheme-2013": "alb-feeding-robena-03",
    "feeding-scheme-children": "alb-feeding-discipleship-04",
    "school-shoes-lotus-fm": "alb-school-shoes-02",
    "christmas-carols-alberlito": "carols-hospital-01",
    "christmas-gifts-etete": "kc-christmas-01",
    "community-meal-bethel": "kc-bethel-00",
    "netball-hoops-sasko": "sasko-00",
    "library-books-donation": "bookclub-01",
    "big5-award-2012": "alb-big5-awards-03",
    "kidz-club-crowd-2006": "anniv-34-06",
    # Training and talks
    "boys-talk-2026": "jn-school-talk-05",
    "school-talk-learners-2026": "jn-school-talk-10",
    # Kidz Club
    "kidz-club-contest-prizes": "kc-contest-04",
    "kidz-club-contest-winners": "kc-contest-00",
    "kidz-club-soccer": "kc-alumni-02",
    "kidz-club-easter-meal": "kc-easter-02",
    "kidz-club-worship": "kc-34yrs-06",
    "kidz-club-mothers-day-2023": "alb-kc-mothersday-2023-01",
    "kidz-club-early-days": "alb-kc-development-08",
    "kidz-club-cupcakes": "kc-fathersday-03",
    "kidz-club-play": "kc-friendship-00",
}
ROTATE = {"big5-award-2012": 90}  # stored sideways on Facebook

sizes_path = os.path.join(HERE, "sizes.json")
sizes = json.load(open(sizes_path))
for name, src in SRC.items():
    im = ImageOps.exif_transpose(Image.open(FB + src + ".jpg")).convert("RGB")
    if name in ROTATE:
        im = im.rotate(ROTATE[name], expand=True)
    sizes[name] = list(im.size)
    for w in (800, 1600):
        if w == 1600 and im.width <= 900:
            continue
        r = im if im.width <= w else im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        r.save(os.path.join(OUT, f"{name}-{w}.webp"), quality=78, method=6)
        if w == 800:
            r.save(os.path.join(OUT, f"{name}-{w}.jpg"), quality=80, optimize=True, progressive=True)
json.dump(sizes, open(sizes_path, "w"), indent=0)
print(len(SRC), "Facebook photos added")
