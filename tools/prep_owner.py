"""Add the photos the owner sent as website.zip (28 Oct 2026), named for the page they belong on.

Reads straight from the zip. Makes WebP 800/1600 + JPEG 800 and merges sizes into tools/sizes.json.
"""
import io, json, os, zipfile
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "docs", "images")
ZIP = "/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/cd8e9e91-website.zip"

SRC = {
    "christmas-shoebox-gifts": "56819132_10156964007318467_5193738715070988288_n.jpg",
    "academy-heritage-day": "ACADEMY - HERITAGE DAY.jpg",
    "academy-with-principal": "ACADEMY - WITH PRINCIPAL.jpg",
    "christmas-carols-alberlito-stairs": "CHRISTMAS CAROLS ALBERLITO HOSPITAL.jpg",
    "christmas-party-gifts": "CHRISTMAS PARTY (2).jpg",
    "christmas-party-stage": "CHRISTMAS PARTY.jpg",
    "community-children-field": "COMMUNITY (2).jpg",
    "hospital-visit-gifts": "COMMUNITY HOSPITAL.jpg",
    "hospital-visit-baby": "COMMUNITY _ HOSPITAL.jpg",
    "community-handout": "COMMUNITY.jpg",
    "child-protection-march-flags": "CPM (2).jpg",
    "child-protection-programme": "CPM PROGRAMME - ANNUAL CPM PROGRAMME.jpg",
    "child-protection-march-superhero": "CPM.jpg",
    "elderly-distribution": "ELDERLY DISTRIBUTION.jpg",
    "feeding-and-distribution": "FEEDING AND DISTRIBUTION.jpg",
    "feeding-cooldrinks": "FEEDING.jpg",
    "founders-cake": "FOUNDERS - HOME PAGE.jpg",
    "founders-child-protection": "FOUNDERS CPM.jpg",
    "founders-mums": "FOUNDERS MUMS.jpg",
    "girls-health-hygiene": "GIRLS HEALTH HYGIENNE PROGRAMME.jpg",
    "girls-health-hygiene-2": "GIRLS HEALTH HYGIENNE.jpg",
    "kidz-club-heritage-day": "HERITAGE DAY KIDZ CLUB.jpg",
    "welcoming-dr-jonathan-david": "HOME PAGE - WELCOMING DR JOHNATHAN DAVID AND MUM HELEN _LINK PREVIEW IMAGE.jpg",
    "kidz-club-madiba-day": "KIDZ CLKUB.jpg",
    "kidz-club-toys": "KIDZ CLUB (2).jpg",
    "kidz-club-line-up": "KIDZ CLUB (3).jpg",
    "kidz-club-smiles": "KIDZ CLUB (4).jpg",
    "kidz-club-gifts": "KIDZ CLUB (5).jpg",
    "kidz-club-hall": "KIDZ CLUB (6).jpg",
    "kidz-club-outdoor-lesson": "KIDZ CLUB (7).jpg",
    "kidz-club-foosball": "KIDZ CLUB.jpg",
    "kidz-club-vegetable-garden": "KIDZ CLUB12.jpg",
    "kidz-club-praise-outside": "KIDZ CLUB6.jpg",
    "kidz-club-group-outside": "KIDZ CLUB66.jpg",
    "kidz-club-story-on-steps": "KIDZ CLUB8.jpg",
    "kidz-club-games-room": "KIDZ CLUB9.jpg",
    "larry-puppet": "LARRY (2).jpg",
    "larry-with-children": "LARRY (3).jpg",
    "larry-stage": "LARRY.jpg",
    "kidz-club-reading-mat": "READING AT KIDZ CLUB 1.jpg",
    "kidz-club-reading-table": "READING AT KIDZ CLUB.jpg",
    "spin-da-flava-visit": "SPIN DA FLAVA VISITS KIDZ CLUB.jpg",
    "working-with-schools": "WORKING WITH SCHOOLS.jpg",
}

z = zipfile.ZipFile(ZIP)
sizes_path = os.path.join(HERE, "sizes.json")
sizes = json.load(open(sizes_path))
for name, fn in SRC.items():
    im = ImageOps.exif_transpose(Image.open(io.BytesIO(z.read("website/" + fn)))).convert("RGB")
    sizes[name] = list(im.size)
    for w in (800, 1600):
        if w == 1600 and im.width <= 900:
            continue
        r = im if im.width <= w else im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        r.save(os.path.join(OUT, f"{name}-{w}.webp"), quality=78, method=6)
        if w == 800:
            r.save(os.path.join(OUT, f"{name}-{w}.jpg"), quality=80, optimize=True, progressive=True)
json.dump(sizes, open(sizes_path, "w"), indent=0)

# link preview image (1200x630 is ideal; this photo is 720 wide, so 720x378)
im = ImageOps.exif_transpose(Image.open(io.BytesIO(z.read("website/" + SRC["welcoming-dr-jonathan-david"])))).convert("RGB")
W, H = im.size; th = round(W * 630 / 1200); top = (H - th) // 2
im.crop((0, top, W, top + th)).save(os.path.join(OUT, "og-welcome-dr-jonathan-david.jpg"), quality=86, optimize=True, progressive=True)
print(len(SRC), "owner photos added")
