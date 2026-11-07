"""Build the Breakthrough Centre static website into ../site.

Plain Python, no dependencies beyond the standard library. Edit the page
content below and run:  python3 tools/build.py
"""
import json, math, os, html
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "docs")
BASE_URL = "https://breakthrucentre.github.io/"   # change if you use another address
SIZES = json.load(open(os.path.join(ROOT, "tools", "sizes.json")))

PHONE_DISPLAY = "081 775 1488"
PHONE_INTL = "+27817751488"
EMAIL = ""  # the Academy email was removed from Breakthrough Centre pages (owner, 7 Nov 2026)
ADDRESS = "170 Old Main Road, Etete, Groutville, Dolphin Coast, KwaZulu-Natal"
FB_CENTRE = "https://www.facebook.com/profile.php?id=100064851574467"
FB_ACADEMY = "https://www.facebook.com/profile.php?id=100063705845998"
MAPS = "https://www.google.com/maps/search/?api=1&query=170+Old+Main+Road+Etete+Groutville+KwaZulu-Natal"
MAP_EMBED = "https://www.google.com/maps?q=170+Old+Main+Road,+Etete,+Groutville,+KwaZulu-Natal&output=embed"


def wa(text="Hi Breakthrough Centre, I found you on your website."):
    from urllib.parse import quote
    return "https://wa.me/27817751488?text=" + quote(text)


e = html.escape

WA_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.1l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.7a2.7 2.7 0 0 0 1.8-1.3 2.2 2.2 0 0 0 .2-1.3c-.1-.1-.3-.2-.5-.3Z"/></svg>')


# ---------------------------------------------------------------- images
def pic(name, alt, cls="", sizes="(max-width: 820px) 100vw, 50vw", eager=False):
    w0, h0 = SIZES[name]
    w = min(800, w0)
    h = round(h0 * w / w0)
    srcset = f"images/{name}-800.webp 800w"
    if os.path.exists(os.path.join(SITE, "images", f"{name}-1600.webp")):
        srcset += f", images/{name}-1600.webp 1600w"
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ""
    return (f'<picture{c}><source type="image/webp" srcset="{srcset}" sizes="{sizes}">'
            f'<img src="images/{name}-800.jpg" alt="{e(alt)}" width="{w}" height="{h}" {load} decoding="async"></picture>')


def photo(name, alt, shape="wide", caption=None):
    cap = f"<figcaption>{e(caption)}</figcaption>" if caption else ""
    return f'<figure><div class="photo {shape}">{pic(name, alt)}</div>{cap}</figure>'


# ---------------------------------------------------------------- sunburst (the signature device)
def pt(cx, cy, r, a):
    t = math.radians(a)
    return cx + r * math.cos(t), cy - r * math.sin(t)


def ray_path(cx, cy, a, hw, r1, r2):
    p1, p2 = pt(cx, cy, r1, a - hw), pt(cx, cy, r2, a - hw)
    p3, p4 = pt(cx, cy, r2, a + hw), pt(cx, cy, r1, a + hw)
    d = (f"M{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} "
         f"A{r2},{r2} 0 0 0 {p3[0]:.1f},{p3[1]:.1f} L{p4[0]:.1f},{p4[1]:.1f} Z")
    xs, ys = [], []
    for k in range(0, 21):
        for r in (r1, r2):
            x, y = pt(cx, cy, r, a - hw + 2 * hw * k / 20)
            xs.append(x); ys.append(y)
    return d, (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))


def burst_svg(rays, cx, cy, sun_r, r1, hw, vb, sun_html="", cls="burst", label=True, uid="b"):
    out = [f'<svg class="{cls}" viewBox="{vb}" role="group" aria-label="What we do">', "<defs>"]
    shapes = []
    for i, ray in enumerate(rays):
        d, bb = ray_path(cx, cy, ray["a"], hw, r1, ray["r"])
        out.append(f'<clipPath id="{uid}{i}"><path d="{d}"/></clipPath>')
        shapes.append((d, bb, ray))
    out.append("</defs>")
    for i, (d, (x, y, w, h), ray) in enumerate(shapes):
        img = (f'<image href="images/{ray["img"]}-800.jpg" x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" '
               f'preserveAspectRatio="xMidYMid slice" clip-path="url(#{uid}{i})"/>')
        body = (f'<g class="ray-group" style="transform-origin:{cx}px {cy}px">'
                f'<path class="ray-shape" d="{d}"/>{img}<path class="ray-outline" d="{d}"/>')
        if label and ray.get("label"):
            lx, ly = pt(cx, cy, ray["r"] + 34, ray["a"])
            anchor = "middle" if ray["a"] > 75 else "start"
            body += f'<text class="ray-label" x="{lx:.0f}" y="{ly + 8:.0f}" text-anchor="{anchor}">{e(ray["label"])}</text>'
        body += "</g>"
        if ray.get("href"):
            out.append(f'<a class="ray-link" href="{ray["href"]}" aria-label="{e(ray["label"])}: {e(ray["alt"])}">'
                       f'<title>{e(ray["label"])}</title>{body}</a>')
        else:
            out.append(body)
    out.append(f'<g class="sun-group"><circle class="sun" cx="{cx}" cy="{cy}" r="{sun_r}"/>{sun_html}</g>')
    out.append("</svg>")
    return "".join(out)


HOME_RAYS = [
    dict(a=104, r=690, img="academy-graduate-2026", label="Academy", href="academy.html",
         alt="one of our Class of 2026 Academy graduates in her cap"),
    dict(a=88, r=760, img="kidz-club-costumes", label="Kidz Club", href="kidz-club.html",
         alt="our children dressed up at Kidz Club"),
    dict(a=72, r=790, img="child-protection-heroes-2026", label="Community", href="community.html",
         alt="our young superheroes at the Child Protection event"),
    dict(a=56, r=770, img="wedding-vows", label="Weddings", href="weddings.html",
         alt="a couple saying their vows before our marriage officer"),
    dict(a=40, r=720, img="computer-class", label="Training", href="training.html",
         alt="our young people learning computer skills"),
    dict(a=24, r=650, img="children-praying", label="Prayer", href="prayer.html",
         alt="our children praying together"),
]


def home_burst():
    sun = ('<text class="sun-text" x="215" y="745" text-anchor="middle">36 years</text>'
           '<text class="sun-small" x="215" y="782" text-anchor="middle">rising since 1990</text>')
    return burst_svg(HOME_RAYS, 215, 840, 200, 225, 7.4, "-60 20 1080 820", sun, uid="h")


def mini_burst(imgs):
    rays = [dict(a=a, r=r, img=i) for (a, r), i in zip([(78, 360), (52, 390), (26, 350)], imgs)]
    return burst_svg(rays, 70, 430, 82, 100, 9.5, "0 0 500 430", "", cls="mini-burst", label=False,
                     uid="m" + imgs[0][:6].replace("-", ""))


# ---------------------------------------------------------------- page chrome
NAV = [("about.html", "About"), ("academy.html", "Academy"), ("kidz-club.html", "Kidz Club"),
       ("community.html", "Community"), ("weddings.html", "Weddings"), ("events.html", "Events"),
       ("contact.html", "Contact")]


def header(current):
    items = "".join(
        f'<li><a href="{h}"{" aria-current=\"page\"" if h == current else ""}>{t}</a></li>' for h, t in NAV)
    cta_cur = ' aria-current="page"' if current == "get-involved.html" else ""
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="wrap">
<a class="brand" href="index.html"><img src="images/logo-256.png" alt="" width="60" height="51"><span>Breakthrough Centre<small>Etete, Groutville, since 1990</small></span></a>
<button class="menu-btn" aria-expanded="false" aria-controls="site-nav">Menu</button>
<nav class="nav" id="site-nav" aria-label="Main"><ul>{items}<li><a class="nav-cta" href="get-involved.html"{cta_cur}>Get involved</a></li></ul></nav>
</div></header>"""


def footer():
    year = date.today().year
    return f"""<footer class="site-footer"><div class="wrap">
<div class="footer-grid">
<div class="footer-brand"><img src="images/logo-256.png" alt="Breakthrough Centre logo" width="64" height="54">
<div><h2>Breakthrough Centre</h2><p>A registered non-profit organisation, 081-061-NPO, serving Etete, Groutville and the iLembe District since 10 October 1990.</p>
<p>{ADDRESS}<br>Call or WhatsApp <a href="tel:{PHONE_INTL}">{PHONE_DISPLAY}</a></p></div></div>
<div><h2>Our work</h2><ul>
<li><a href="academy.html">Breakthrough Centre Academy</a></li><li><a href="kidz-club.html">Kidz Club</a></li>
<li><a href="community.html">Social development</a></li><li><a href="weddings.html">Marriage officer</a></li>
<li><a href="training.html">Training and development</a></li><li><a href="prayer.html">Prayer and counselling</a></li></ul></div>
<div><h2>Find us</h2><ul>
<li><a href="{FB_CENTRE}" rel="noopener">Breakthrough Centre on Facebook</a></li>
<li><a href="{FB_ACADEMY}" rel="noopener">Breakthrough Centre Academy on Facebook</a></li>
<li><a href="news.html">Our story in the news</a></li><li><a href="events.html">What's on</a></li><li><a href="get-involved.html">Get involved</a></li><li><a href="contact.html">Contact and directions</a></li></ul></div>
</div>
<p class="footer-note">© {year} Breakthrough Centre. Touching one little life at a time.</p>
</div></footer>
<a class="wa-float" href="{wa()}" rel="noopener">{WA_ICON}<span>WhatsApp us</span></a>
<script src="assets/site.js" defer></script>"""


ORG_LD = {
    "@context": "https://schema.org",
    "@type": "NGO",
    "@id": BASE_URL + "#organization",
    "name": "Breakthrough Centre",
    "alternateName": "Breakthrough Centre Etete",
    "url": BASE_URL,
    "logo": BASE_URL + "images/logo.png",
    "image": BASE_URL + "images/og-founders-kidz-club-party.jpg",
    "description": "Community centre and early childhood development centre in Etete, Groutville, near KwaDukuza and Ballito, KwaZulu-Natal. Registered NPO 081-061-NPO.",
    "foundingDate": "1990-10-10",
    "telephone": PHONE_INTL,
    "address": {"@type": "PostalAddress", "streetAddress": "170 Old Main Road, Etete", "addressLocality": "Groutville",
                "addressRegion": "KwaZulu-Natal", "addressCountry": "ZA"},
    "areaServed": ["Groutville", "KwaDukuza", "Shakaskraal", "Ballito", "iLembe District"],
    "sameAs": [FB_CENTRE, FB_ACADEMY],
}


def page(path, title, desc, body, og_image="og-founders-kidz-club-party.jpg", extra_ld=None, body_class=""):
    url = BASE_URL + ("" if path == "index.html" else path)
    ld = [ORG_LD] + (extra_ld if isinstance(extra_ld, list) else [extra_ld] if extra_ld else [])
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    bc = f' class="{body_class}"' if body_class else ""
    doc = f"""<!doctype html>
<html lang="en-ZA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Breakthrough Centre">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE_URL}images/{og_image if og_image.endswith('.jpg') else og_image + '-800.jpg'}">
<meta property="og:image:alt" content="{'Ps Trevor and Jessica Nair with children at a Breakthrough Centre Kidz Club party' if og_image == 'og-founders-kidz-club-party.jpg' else 'Breakthrough Centre in Groutville'}">
<meta property="og:locale" content="en_ZA">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#f6d21f">
<link rel="icon" type="image/png" href="images/favicon.png">
<link rel="apple-touch-icon" href="images/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Baloo+2:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">
{ld_html}
</head>
<body{bc}>
{header(path)}
<main id="main">
{body}
</main>
{footer()}
</body>
</html>
"""
    with open(os.path.join(SITE, path), "w", encoding="utf-8") as f:
        f.write(doc)
    return url


def page_head(h1, lead, imgs, extra=""):
    return f"""<section class="page-head"><div class="wrap">
<div><h1>{e(h1)}</h1><p class="lead">{lead}</p>{extra}</div>
{mini_burst(imgs)}
</div></section>"""


def faq(title, items):
    """Questions people actually type into Google, answered plainly. Returns (html, schema)."""
    qs = "".join(f"<details><summary>{e(q)}</summary><p>{a}</p></details>" for q, a in items)
    import re as _re
    schema = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": _re.sub("<[^>]+>", "", a)}}
        for q, a in items]}
    return (f'<section class="section"><div class="wrap faq-wrap"><h2>{e(title)}</h2>'
            f'<div class="faq">{qs}</div></div></section>'), schema


def cta(title, text, label="WhatsApp {p}", msg=None):
    label = label.format(p=PHONE_DISPLAY)
    return f"""<section class="cta-band"><div class="wrap">
<div><h2>{e(title)}</h2><p>{text}</p></div>
<a class="btn" href="{wa(msg) if msg else wa()}" rel="noopener">{WA_ICON}{e(label)}</a>
</div></section>"""


# ================================================================ pages
pages = []

# ---------- Home
HOME_FAQ = faq("Questions people ask us", [
    ("Where is Breakthrough Centre?", f"We're at {ADDRESS}, in Groutville between KwaDukuza (Stanger) and Ballito on the KwaZulu-Natal North Coast. <a href=\"contact.html\">Get directions</a>."),
    ("From what age does the Academy take children?", "Breakthrough Centre Academy welcomes children from the age of two. <a href=\"academy.html\">See what they learn</a>."),
    ("How do I find out about a place for my child?", f"Send a WhatsApp to {PHONE_DISPLAY} and we'll tell you about places and registration."),
    ("When does Kidz Club meet?", "Every Sunday from 8 to 10am at the centre. All children in the community are welcome."),
    ("Is Breakthrough Centre a registered non-profit?", "Yes. We're a registered non-profit organisation, number 081-061-NPO, and we've served Etete since 1990."),
])
home = f"""
<section class="hero"><div class="wrap">
<div class="hero-text">
<h1>Breakthrough Centre</h1>
<p class="kicker">NPO, Community Centre and ECD site in Groutville, KwaDukuza</p>
<p class="lead">On 10 October 1990 children of the community began to gather at the Kidz Club in front of a little blue house on a hill in a place called Groutville. The club grew significantly, making a dynamic difference in the lives of people of every age.</p>
<div class="btn-row"><a class="btn btn-whatsapp" href="{wa()}" rel="noopener">{WA_ICON}WhatsApp {PHONE_DISPLAY}</a><a class="btn btn-ghost" href="about.html">Our story</a></div>
</div>
<div class="burst-wrap">{home_burst()}</div>
</div></section>

<section class="section tint"><div class="wrap split">
<div>
<h2>It started with a children's club</h2>
<p>It began with children gathering in front of a little blue house on a hill in Etete. That club never stopped, and today Breakthrough Centre is a full community centre with its own preschool, Breakthrough Centre Academy, where children from the age of two learn to read, count and speak up with confidence.</p>
<p>Breakthrough Centre makes its impact on an ongoing basis, from poverty alleviation programmes to education and empowerment. We see a need and, where possible, we address the need.</p>
<p>We're a registered non-profit organisation (081-061-NPO) in Groutville, between KwaDukuza (Stanger) and Ballito, and we serve families right across the iLembe District. What drives us hasn't changed in 36 years: helping people of every age reach their God-given potential.</p>
<p><a href="about.html">Read our story</a></p>
</div>
{photo("anniversary-family-35", "Our Breakthrough Centre family, all dressed up to celebrate 35 years together in 2025", "wide", "Celebrating 35 years of Breakthrough Centre, 2025")}
</div></section>

<section class="section"><div class="wrap split top">
<div class="measure letter"><h2>A message from our founders</h2>
<p>On 10 October 1990, the Lord caused a seed to be planted on the grounds of Etete, Groutville that was destined to germinate, flourish and change the region significantly. The Kidz Club emerged as a powerful children's ministry touching and changing the lives of a rising generation, unveiling the purpose and God-given destiny of precious, tender lives.</p>
<p>Today this ministry has blossomed into a formidable, unstoppable force making an eternal difference in the lives of many.</p>
<p>Our hearts are filled with gratitude as we celebrate 36 incredible years, honouring Abba Father for where He has brought us today. The struggles may have been great, but the impact has surely been greater.</p>
<p>We are thankful to our parents, both physical and spiritual, siblings, our supportive family, our schools, businesses, organisations, covenant partners and friends for your continued support, prayers and generosity. To our Breakthrough Centre Family, Members of the Executive Committee, BCA Staff and our two precious jewels Taldon and Tamsyn: you have sown faithfully, and may your harvest be bountiful. We are reminded of the words of our spiritual father, "Small beginnings of an accurate move will bring you into greater significance."</p>
<p>We celebrate the Lord's awesome favour, goodness and greatness. Surely His hands have been over our lives. In pursuing our dreams, may we be able to carry the capacity to bring light, love and life to the ones we meet.</p>
<p class="signoff">With much love,<br><strong>Ps. Trevor and Jessica Nair</strong></p>
<p><a href="about.html">Meet the Executive Committee</a></p></div>
<div class="stack">
{photo("founders-cake", "Ps Trevor and Jessica cutting the cake at our 35th anniversary, 35 years after Kidz Club began", "wide", "Our founders, Ps Trevor and Jessica Nair")}
{photo("founders-mums", "Ps Trevor and Jessica's mums, who stood with them from the very beginning", "wide", "The mothers of our founders")}
</div>
</div></section>

<section class="section tint"><div class="wrap split">
<div class="measure"><h2>A welcome seen in 42 countries</h2>
<p>When our spiritual parents, Dr Jonathan and Helen David, arrived in South Africa, Breakthrough Centre Academy learners were waiting at the airport in traditional dress, waving the South African flag. The welcome was screened in Malaysia to delegates from 42 countries.</p></div>
{photo("welcoming-dr-jonathan-david", "Our Academy learners in traditional dress, waving flags as they welcome Dr Jonathan and Mum Helen at the airport", "wide")}
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><h2>Highlights of our year</h2></div>
<div class="split top">
<div>{photo("christmas-party-stage", "Our Kidz Club children on stage with their Christmas gifts and Santa hats", "wide")}
<h3>The annual Kidz Club Christmas party</h3>
<p>The highlight of the Breakthrough Centre calendar. There is nothing more rewarding than putting a smile on the face of a child, and our annual Kidz Club party ensures that every child receives a gift for Christmas and a sumptuous treat.</p></div>
<div>{photo("child-protection-march-flags", "Hundreds of our children and their families marching together at the annual Child Protection Event", "wide")}
<h3>The annual Child Protection Event</h3>
<p>The town comes to a standstill as little ones join together with strategic people to make a clarion call declaring an end to child abuse, upholding child protection as one community. The theme "Every child a superhero" sees every child dress up as their favourite superhero, march through the town and speak out against child abuse.</p>
<p>Would you like to partner with us in this exciting event? <a href="{wa('Hi, I would like to partner with Breakthrough Centre on the Child Protection Event.')}" rel="noopener">Contact us for more information</a>.</p></div>
</div></div></section>

<section class="section tint"><div class="wrap">
<div class="pillars">
<div><div class="pillar-photo">{pic("child-protection-march-flag-wave", "Waving our flag at the Child Protection March: building a transformed city, one little life at a time", sizes="(max-width: 820px) 100vw, 33vw")}</div>
<h2>Our vision</h2><ul>
<li>A transformed city, empowered communities and an educated next generation.</li>
<li>Young people trained, nurtured and developed to be responsible in their schools, communities and workplaces.</li>
<li>"A new breed without greed": a generation living with righteousness and integrity.</li>
<li>A strategic response to poverty, crime, social ills and challenges.</li></ul></div>
<div><div class="pillar-photo">{pic("founders-kidz-club-party", "Ps Trevor and Jessica in matching yellow, surrounded by hundreds of our Kidz Club children at a party", sizes="(max-width: 820px) 100vw, 33vw")}</div>
<h2>Our mission</h2><ul>
<li>Reduce the effects of crime and poverty through empowerment, social development and life skills.</li>
<li>Provide a caring, supportive and safe environment for children and youth.</li>
<li>Run awareness and support programmes that meet present-day challenges.</li>
<li>Effect lasting change in lifestyles through ongoing training and mentoring.</li></ul></div>
<div><div class="pillar-photo">{pic("dr-jonathan-and-helen-david", "Our spiritual parents, Dr Jonathan David and Mum Helen, in prayer", sizes="(max-width: 820px) 100vw, 33vw")}</div>
<h2>Our values</h2><p>Everyone who serves at Breakthrough Centre commits to:</p>
<ul class="values"><li>Honesty</li><li>Integrity</li><li>Respect</li><li>Dedication</li><li>Excellence</li><li>Accountability</li><li>Non-discrimination</li></ul></div>
</div></div></section>

<section class="section olive"><div class="wrap">
<div class="section-head"><h2>How we can help you</h2><p class="lead">A preschool, a Sunday club, community projects, weddings, training and a listening ear, all at one address in Etete.</p></div>
<div class="services">
<article class="service"><div class="photo">{pic("back-to-school-2026", "Our Academy learners, school bags on and ready for the first day back in 2026", sizes="(max-width: 560px) 100vw, 33vw")}</div>
<h3><a href="academy.html">Preschool: Breakthrough Centre Academy</a></h3><p>In raising a company of young men and women who would develop into outstanding leaders, the concept of Breakthrough Centre Academy came into being. We also saw the need to keep our little ones in a safe environment where they would thrive, receiving quality education.</p></article>
<article class="service"><div class="photo">{pic("kidz-club-foosball", "The all-time favourite: our children crowded around the soccer machine at Kidz Club", sizes="(max-width: 560px) 100vw, 33vw")}</div>
<h3><a href="kidz-club.html">Sunday Kidz Club</a></h3><p>The most exciting place to be on a Sunday morning, from 8 to 10am. Arts and crafts, sport, Monopoly, Scrabble, the all-time favourite soccer machine and plenty of other games, with Larry the puppet popping in.</p></article>
<article class="service"><div class="photo">{pic("blanket-outreach", "Wrapping a warm blanket around one of our neighbours in Etete", sizes="(max-width: 560px) 100vw, 33vw")}</div>
<h3><a href="community.html">Community projects</a></h3><p>From poverty alleviation programmes to education and empowerment: the annual Child Protection Event, feeding, blankets and food parcels, hygiene packs and Christmas outreach.</p></article>
<article class="service"><div class="photo">{pic("wedding-beach-setup", "A beach wedding ready and waiting on the Dolphin Coast", sizes="(max-width: 560px) 100vw, 33vw")}</div>
<h3><a href="weddings.html">Weddings and marriage officer</a></h3><p>A personal ceremony on the beach, in a hall or wherever you choose, and we register your marriage with Home Affairs.</p></article>
<article class="service"><div class="photo">{pic("computer-class", "Our young people learning computer skills at the centre", sizes="(max-width: 560px) 100vw, 33vw")}</div>
<h3><a href="training.html">Workshops and training</a></h3><p>Practical workshops, leadership and mentoring for parents, teachers, young people and community groups.</p></article>
<article class="service"><div class="photo">{pic("children-praying", "Our children with their heads bowed, praying together", sizes="(max-width: 560px) 100vw, 33vw")}</div>
<h3><a href="prayer.html">Prayer and counselling</a></h3><p>Going through something hard? Talk to someone who will listen, pray with you and walk with you.</p></article>
</div></div></section>

<section class="section night"><div class="wrap split">
<div><p class="motto">How do you change the world?</p>
<p>By touching one little life at a time. Give an hour, share a skill, partner with us or simply come and visit. There's a place for you here.</p>
<div class="btn-row"><a class="btn btn-whatsapp" href="{wa('Hi Breakthrough Centre, I would like to get involved.')}" rel="noopener">{WA_ICON}WhatsApp us</a><a class="btn btn-ghost" style="color:#fff;border-color:#fff" href="get-involved.html">Ways to help</a></div></div>
{photo("heritage-day-flag", "Our Academy learners proudly wearing traditional dress around the flag on Heritage Day", "wide")}
</div></section>
"""
pages.append(("index.html", page("index.html",
    "Preschool and Community Centre in Groutville | Breakthrough Centre",
    "Non-profit preschool and community centre in Groutville, near KwaDukuza (Stanger) and Ballito. Our Academy, Sunday Kidz Club and outreach have served families since 1990.",
    home + HOME_FAQ[0], extra_ld=HOME_FAQ[1])))

def gallery_html(items, label="Photo gallery", cls=""):
    """items: list of (image name, description). A moving carousel: every frame is the same 4:3 size,
    the whole photo shows (object-fit: contain) on a blurred fill of itself, and a tap opens the lightbox."""
    slides = []
    for n, (g, alt) in enumerate(items, 1):
        big = 1600 if os.path.exists(os.path.join(SITE, "images", g + "-1600.webp")) else 800
        slides.append(
            f'<li class="slide" aria-label="{n} of {len(items)}">'
            f'<button type="button" class="slide-frame" data-full="images/{g}-{big}.webp">'
            f'<span class="slide-bg" aria-hidden="true" style="background-image:url(images/{g}-800.webp)"></span>'
            f'{pic(g, alt, sizes="(max-width: 600px) 85vw, (max-width: 900px) 50vw, 400px")}</button>'
            f'<p class="slide-cap" aria-hidden="true">{e(alt)}</p></li>')
    return (f'<div class="carousel{" " + cls if cls else ""}" data-carousel><ul class="carousel-track" aria-label="{e(label)}">{"".join(slides)}</ul>'
            '<div class="carousel-controls">'
            '<button type="button" class="cbtn prev" aria-label="Previous photo"><span aria-hidden="true">&#8249;</span></button>'
            '<button type="button" class="cbtn pause" aria-label="Pause the slideshow"><span aria-hidden="true">&#10074;&#10074;</span></button>'
            '<button type="button" class="cbtn next" aria-label="Next photo"><span aria-hidden="true">&#8250;</span></button>'
            '</div></div>')


LIGHTBOX = '<dialog class="lightbox"><button class="close" type="button">Close</button><img src="" alt=""><p></p></dialog>'

AWARDS = [
    # (title, year or detail, story, photo name or None, photo description)
    ("North Coast Big 5 Service Excellence Award", "2nd place, Community category, 19 April 2012",
     "Our Sugar Rush Big 5 award, celebrated at home with the certificate in hand.",
     "big5-award-2012-presentation", "A proud moment at home: holding our North Coast Big 5 Service Excellence Award, 2012"),
    ("Nedbank Local Heroes Award", "R10 000, August 2008",
     "We put the prize straight back into the children: in 2009 it bought a soccer machine, a pool table and other resources for the Kidz Club.",
     "sb-news-2008-nedbank-cheque", "Ps Trevor and Jessica with the Nedbank cheque and some of our preschool children, 2008"),
    ("KwaDukuza Municipality Mayoral Awards", "1st place, Community Development category",
     "Recognised by our own municipality for the difference made in the community. Jessica received the award at the KwaDukuza Mayoral Awards celebration.",
     "mayoral-awards-clipping", "Newspaper page from the KwaDukuza Mayoral Awards celebration, with Jessica among the Community Development winners"),
    ("Lubners INHOUSE Club National Heroes Award", "R10 000, March 2006",
     "Chosen from entries across South Africa, after a Radha Roopsingh Primary teacher nominated Ps Trevor and Jessica as \"national heroes\".",
     "sb-news-2006-heroes-cheque", "Ps Trevor and Jessica receiving the INHOUSE Club Heroes Award cheque, 2006"),
    ("Our story in a national magazine", "INHOUSE Club magazine, 2006",
     "\"Lighting up Etete\" told readers across South Africa about the little blue tin house and the work being done there.",
     "sb-news-2006-lighting-up-etete", "Our little blue tin house in INHOUSE magazine's \"Lighting up Etete\" feature, 2006"),
    ("Jet Club Icon", "Recognition",
     "Honoured as a Jet Club Icon for our work in the community.", None, ""),
]

def award_badge(label):
    rays = "".join(f'<rect x="58" y="6" width="4" height="22" rx="2" fill="#f6d21f" transform="rotate({a} 60 60)"/>' for a in range(0, 360, 30))
    return (f'<svg viewBox="0 0 120 120" role="img" aria-label="{e(label)} award badge" class="badge">{rays}'
            f'<circle cx="60" cy="60" r="34" fill="#e4661b"/><circle cx="60" cy="60" r="27" fill="none" stroke="#fff" stroke-width="2" opacity=".7"/>'
            f'<path d="M60 42l5.3 10.8 11.9 1.7-8.6 8.4 2 11.8L60 69.1l-10.6 5.6 2-11.8-8.6-8.4 11.9-1.7z" fill="#fff"/></svg>')

def award_cards():
    out = []
    for title, when, story, img, alt in AWARDS:
        media = pic(img, alt, sizes="(max-width: 720px) 100vw, 33vw") if img else award_badge(title)
        out.append(f'<article class="award-card"><div class="award-media{"" if img else " is-badge"}">{media}</div>'
                   f'<h3>{e(title)}</h3><p class="award-when">{e(when)}</p><p>{e(story)}</p></article>')
    return "".join(out)

JOURNEY = [
    ("journey-01-10-october-1990", "10 October 1990: a day that would alter the trajectory of this community. Our first Kidz Club children and an outdoor show with clowns"),
    ("journey-02-birth-of-kidz-club", "The birth of the Kidz Club: children gathering on the field, with puppet shows and clowns"),
    ("journey-03-memorable-childhood", "Creating a memorable childhood: a field full of our Kidz Club children and their soccer ball"),
    ("journey-04-keep-hope-alive", "In the midst of adversity, keep hope alive: neighbours waving with the food parcels we handed out"),
    ("journey-05-house-home-to-many-2005", "2005: the little blue house becomes a home to many, with church in the garden and Ps Trevor dedicating a little one"),
    ("journey-06-creche-4-learners", "Our crèche and preschool started with an enrolment of just 4 learners, with a jungle gym beside the blue house"),
    ("journey-07-marquee-2006", "2006: from the blue house into a marquee"),
    ("journey-08-structure-2007", "2007: from the marquee into a structure"),
    ("journey-09-laying-blocks", "Ps Trevor laying the blocks for our new building, one at a time"),
    ("journey-10-foundations", "The foundations going down, with friends lending a hand"),
    ("journey-11-structure-into-building", "From the structure into a building: our new centre taking shape, block by block"),
    ("journey-12-spiritual-parents-2009", "2009: Ps Trevor and Jessica with our spiritual parents, Dr Jonathan and Ps Helen David"),
]

MOMENTS_GAL = [
    ("sb-early-outdoor-assembly", "An early Kidz Club gathering outdoors, with rows and rows of children"),
    ("sb-outreach-early-gathering", "Ps Trevor with children at one of our early outreach visits"),
    ("sb-kidz-club-1990-field", "1990: Kidz Club was formed on 10 October 1990, and the children gathered on the field in Etete"),
    ("sb-clown-1990", "One of our very first Kidz Club clowns, in polka dots and a red wig"),
    ("sb-kidz-club-1990-group", "Some of our first Kidz Club children, from the early 1990s"),
    ("sb-kidz-club-1990-puppet-show", "An early outdoor puppet show and clown performance, with balloons and home-made signs"),
    ("sb-clowns-early-team", "Our clown team in full face paint, ready to entertain the children"),
    ("sb-outreach-johannesburg-camp", "Taking Kidz Club to children in a squatter camp in Johannesburg"),
    ("sb-tin-house-2009", "The little blue tin house on the hill in Etete where it all began"),
    ("sb-news-2006-thank-you-kids", "Our preschool children saying THANK YOU inside the tin house, 2006"),
    ("sb-academy-opening-mural", "The mural at Daddy's Daycare and Pre-school, ready for the official opening of Breakthrough Centre Academy"),
    ("sb-academy-opening-ribbon", "Cutting the ribbon at the official opening of Breakthrough Centre Academy"),
    ("sb-academy-opening-guests", "Smiling guests at the official opening of Breakthrough Centre Academy"),
    ("sb-news-2007-trevor-40th", "Ps Trevor with Jessica, Taldon and Tamsyn at his surprise 40th birthday party at the centre, 2007"),
    ("kidz-club-1990s", "The 1990s: Jessica Nair and the passionate team who started Kidz Club, entertaining a crowd of children on the grass"),
    ("kidz-club-ballet-2009", "2009: our Kidz Club ballet girls in their white dresses outside the little blue tin house"),
    ("pam-mills-kidz-club", "Pam Mills, who taught ballet at Kidz Club alongside Jessica, with a hall full of our children"),
    ("national-planning-ps-raj", "Ps Raj with Ps Trevor and Jessica Nair at a national planning workshop"),
    ("meeting-community-leaders", "Sitting around the table with important leaders from our community"),
    ("founders-kidz-club-party", "Ps Trevor and Jessica in matching yellow, surrounded by hundreds of children at a Kidz Club party"),
]

# ---------- About
about = page_head("Our story",
    "Breakthrough Centre began on 10 October 1990 as the first community-based project in Etete, Groutville. Thirty-six years on, it's a busy community centre with a special heart for young children.",
    ["heritage-day-circle", "anniversary-cake-cutting", "community-gathering"]) + f"""
<section class="section"><div class="wrap split top">
<div class="measure">
<h2>A positive place to be</h2>
<p>We started with one simple idea: children and young people need a good place to be, away from the problems on the streets around them. Give them that, plus people who believe in them, and they can rise above hard circumstances.</p>
<p>On 10 October 1990 children of the community began to gather at the Kidz Club in front of a little blue house on a hill in Groutville. Jessica had grown up in that house, and there was very little for young people to do in Etete, so she started a Christian Kidz Club in her mother's garden on Saturday afternoons, with puppets, clowns, songs, games and a lesson.</p>
<p>When Jessica married Ps Trevor in 1994 they moved away for a while, and her sister Shavera kept the club going. In 1999 they came back and took it over again. By then 80 to 90 children were meeting every Saturday at the Radha Roopsingh School, and by 2002 it was up to 250. That year the club was registered as a non-profit organisation, the KC (Kidz Club) Community Centre, and Jessica's mother donated the little blue tin house to be used as the community centre.</p>
<p>That three-roomed tin house became a crèche, a preschool, a community centre and a church, used by about 200 young people every week. The preschool, first called Daddy's Daycare and Pre-school, became Breakthrough Centre Academy. The children kept coming and the club kept growing into the Breakthrough Centre we have today, open to people of every age and background. <a href="news.html">Read our story in the news</a>.</p>
</div>
<div>
<h2>Milestones</h2>
<ol class="timeline">
<li><span class="year">1990</span>Our story starts in a little blue house on a hill, where children gather for the first Kidz Club on 10 October.</li>
<li><span class="year">1994</span>Jessica marries Ps Trevor. While they are away, her sister Shavera keeps Kidz Club going.</li>
<li><span class="year">1999</span>Jessica and Ps Trevor take over Kidz Club again, and our story appears in the newspaper for the first time.</li>
<li><span class="year">2001</span>1,500 children come to the Kidz Club Christmas party, and a second branch opens in Shakaskraal.</li>
<li><span class="year">2002</span>Kidz Club is registered as a non-profit organisation, the KC Community Centre.</li>
<li><span class="year">2005</span>The little blue house becomes a home to many, and our crèche and preschool (today Breakthrough Centre Academy) opens with just 4 learners.</li>
<li><span class="year">2006</span>Ps Trevor and Jessica win the Lubners INHOUSE Club National Heroes Award, and our little blue tin house is featured in INHOUSE magazine. We grow out of the blue house and into a marquee.</li>
<li><span class="year">2007</span>The marquee becomes a more solid structure, Pam Mills starts ballet classes for our girls, and more than 500 children come to the Christmas party.</li>
<li><span class="year">2008</span>Our first Youth Day rally launches the Youth Club, and we win the Nedbank Local Heroes Award.</li>
<li><span class="year">2009</span>The Nedbank prize buys a soccer machine, a pool table, table tennis and games for the Kidz Club, and we open a youth help desk.</li>
<li><span class="year">2012</span>We win 2nd place in the community category of the North Coast Big 5 Service Excellence Awards, and take blankets and food parcels to needy neighbours in Etete.</li>
<li><span class="year">2013</span>Feeding schemes for hungry children, followed in August 2014 by a gift box distribution for a hall full of children.</li>
<li><span class="year">2018</span>Members of Parliament visit the centre on 28 March, focusing on early childhood and youth development.</li>
<li><span class="year">2021</span>We distribute baby formula from Durban to Tugela during the KZN unrest, and are awarded the lease of a brand-new community crèche and pre-school in Shakaskraal.</li>
<li><span class="year">2025</span>Friends, partners and families celebrate our 35th anniversary together.</li>
<li><span class="year">2026</span>We celebrate 36 years of God's amazing grace.</li>
</ol></div>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><h2>Our journey, from a little blue house</h2><p class="lead">From children gathering on a field in 1990, to the blue tin house, a marquee, a structure and finally a building of our own. Use the arrows or swipe to walk through our story.</p></div>
{gallery_html(JOURNEY, "Our journey since 1990", "carousel--single")}
</div></section>

<section class="section tint"><div class="wrap split top">
<div><h2>Leadership and governance</h2>
<p>Breakthrough Centre was founded by Ps. Trevor and Jessica Nair. An Executive Committee steers the organisation, sub-committees run each department and report back to it, and a team of volunteers keeps every programme, event and project running smoothly.</p>
{photo("founders-and-exco", "Ps Trevor and Jessica with our Executive Committee, the team who keep everything running", "tall", "Our founders, Ps Trevor and Jessica Nair, with the Executive Committee")}</div>
<div><h3>Executive Committee</h3>
<ul class="people">
<li><strong>Mr P. Nair</strong>Founder. Full-time Manager, Breakthrough Centre</li>
<li><strong>Mrs S. Nair</strong>Founder. Departmental Head, Department of Education</li>
<li><strong>Mrs A.S. Gwamanda</strong>Executive Committee member</li>
<li><strong>Mrs V. Govindasamy</strong>Executive Committee member</li>
<li><strong>Ms Tamsyn Jeiel</strong>Executive Committee member</li></ul></div>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><h2>Highlights and recognition</h2><p class="lead">For 36 years Breakthrough Centre has served Etete through setbacks and challenges, and that track record has been recognised by government, business and the media.</p></div>
<div class="split top">
<div>
<h3>Visit by Members of Parliament, 28 March 2018</h3>
<p>Breakthrough Centre was one of the organisations selected when Members of Parliament visited eleven wards in the iLembe District. The Honourable MEC for Transport and Community Safety, Mr Mxolisi Kaunda, saw how a children's club started 28 years earlier had become a multifaceted community centre. Academy learners danced and shared their dreams, and Larry the puppet delivered a serious message with plenty of laughs.</p>
<h3>Representing iLembe District</h3>
<p>The Office of the Premier invited Breakthrough Centre to represent the iLembe District in reviewing the National Plan of Action priorities for children.</p>
<h3>International guests</h3>
<p>Academy learners welcomed international speakers Dr Jonathan and Helen David to South Africa. The welcome was screened in Malaysia to delegates from 42 countries.</p>
</div>
<div>{photo("anniversary-cake-35", "Our 35th anniversary cake, topped with the Breakthrough Centre sun, 2025", "wide", "Celebrating 35 years, 2025")}</div>
</div></div></section>

<section class="section"><div class="wrap">
<div class="section-head"><h2>Our awards</h2><p class="lead">Every award belongs to the children, families, volunteers and friends who have walked this road with us.</p></div>
<div class="award-cards">{award_cards()}</div>
</div></section>

<section class="section tint"><div class="wrap">
<div class="section-head"><h2>Moments through the years</h2><p class="lead">A few snapshots from our family album. The photos move on their own; tap one to see it bigger.</p></div>
{gallery_html(MOMENTS_GAL)}
</div></section>
{LIGHTBOX}
""" + cta("Come and see our work", "Visit the centre at 170 Old Main Road, Etete, or send us a message.")
pages.append(("about.html", page("about.html", "Our Story: 36 Years in Groutville | Breakthrough Centre",
    "How a children's club in Etete, Groutville grew into a community centre and preschool. Our story since 1990, our leaders and the awards we've received.", about)))

VAL_GAL = [
    ("valentines-boy", "Ready for the party: one of our learners looking smart in white on Valentine's Day 2026"),
    ("valentines-girl", "Dressed up in red: one of our little ones on Valentine's Day 2026"),
    ("valentines-red-dress", "Feeling special: all smiles in a red dress and flower crown"),
    ("valentines-smile", "A big Valentine's Day smile from one of our learners, 2026"),
    ("valentines-balloon", "Lots of love: one of our learners holding an \"I love you\" balloon"),
]
ACADEMY_ARCHIVE_GAL = [
    ("journey-06-creche-4-learners", "Where it all began: our crèche and preschool started with just 4 learners"),
    ("sb-academy-opening-mural", "The mural from our Daddy's Daycare and Pre-school days"),
    ("sb-academy-opening-ribbon", "Cutting the ribbon at the official opening of Breakthrough Centre Academy"),
    ("sb-news-2007-grade-r-graduation", "Teacher Eunice Thabede with her Grade R graduates, 2007 (North Coast Courier)"),
    ("sb-news-2007-sports-day", "Tug-of-war at our preschool sports day, 2007 (North Coast Courier)"),
    ("sb-concert-2012", "Our little performers on stage at the 2012 concert"),
    ("sb-back-to-school-hampers-bca", "Ps Trevor with two of our graduates and their back-to-school hampers"),
    ("sb-news-2014-graduation", "Our Grade R class of 2014 with their certificates and trophies"),
]
ACADEMY_GAL = [
    ("academy-pretend-kitchen", "Our little chefs in their BCA T-shirts cooking up a storm in the play kitchen"),
    ("academy-shop-role-play", "Playing shop with real price tags: counting and money skills, with big smiles"),
    ("academy-nature-binoculars", "Explorers with home-made binoculars, spotting the animals and leaves on the nature table"),
    ("academy-leaf-magnifier", "A careful look at a leaf through the magnifying glass"),
    ("academy-coding-grids", "Coding without a computer: drawing arrows to guide each picture across the grid"),
    ("academy-pattern-building", "Building long rainbow rows and pegboard patterns, one colour at a time"),
    ("academy-colouring-worksheets", "Heads down and colouring in, with a pot full of kokis between friends"),
    ("sunshine-craft", "Our little ones making paper suns, just like the one in our logo"),
    ("water-play", "Splash time: our learners in their BCA T-shirts around the water play pool"),
    ("parachute-play", "Everyone holding on for parachute play on the grass"),
    ("space-art", "Our young astronauts making a space collage of planets, stars and rockets"),
    ("garden-planting", "Little gardeners planting and watering in our Academy vegetable garden"),
    ("building-blocks", "Building colourful block patterns together"),
    ("leaf-art", "Leaf art laid out on our alphabet play mat"),
    ("finger-painting", "Two of our learners happily getting their hands green with finger paint"),
    ("shape-sorting", "Sorting shapes at the outdoor table"),
    ("outdoor-learning-circle", "Our learners in a circle outside for a sorting game"),
    ("solar-system-project", "Our learners hard at work on their solar system project"),
    ("ball-play", "Ball games at our bright red and yellow tables"),
]


# ---------- Academy (playful)
ACADEMY_FAQ = faq("Questions parents ask", [
    ("What age can my child start?", "We take children from the age of two."),
    ("What will my child learn?", "A structured programme in Maths, Science, Languages and Life Skills, with our \"I can read\" programme building strong reading from the start. Every learner also takes part in our concert and graduation."),
    ("Where is the Academy?", f"At Breakthrough Centre, {ADDRESS}, near KwaDukuza (Stanger), Shakaskraal and Ballito. Since 2021 we also run a community-based creche and preschool in Shakaskraal."),
    ("How do I ask about a place?", f"WhatsApp {PHONE_DISPLAY} and we'll let you know about places and registration."),
    ("Can parents be involved?", "Yes. We hold parent meetings every term, and parents can attend free workshops on supporting their child's learning."),
])
ac_msg = "Hi, I would like to find out about places at Breakthrough Centre Academy."
academy = page_head("Breakthrough Centre Academy",
    "Our preschool and early childhood development (ECD) centre in Etete, Groutville. Families from KwaDukuza, Shakaskraal and along the Dolphin Coast trust us with their little ones from the age of two.",
    ["academy-graduate-2026", "back-to-school-learner-2026", "sunshine-craft"],
    f'<div class="btn-row"><a class="btn btn-whatsapp" href="{wa(ac_msg)}" rel="noopener">{WA_ICON}Ask about places</a></div>') + f"""
<section class="section"><div class="wrap split">
<div class="measure">
<h2>We don't lower the bar</h2>
<p>We opened in 2005 in a small house with four learners. We've grown quickly since then for one reason: we refuse to lower our standards. You can't lower the bar and expect excellent results, and the start a child gets here stays with them for life.</p>
<p>Every child follows a structured programme in Maths, Science, Languages and Life Skills. Even our two-year-olds are building their vocabulary and learning the first steps of reading and writing. Along the way we teach good manners, respect for others and healthy eating habits.</p>
<p>In 2021 we were also awarded the lease of a brand-new community-based crèche and pre-school in Shakaskraal.</p>
</div>
{photo("rocket-counting", "Our learners counting rockets and matching the numbers in maths", "tall")}
</div></section>

<section class="section tint"><div class="wrap split">
<div class="bubble"><h2>"I can read"</h2>
<p>Many children pass through life not having mastered the art of reading, and the consequences reach far beyond the classroom. <em>I can read</em> takes a practical, hands-on approach to teaching reading with the South African child in mind.</p>
<p>The manual forms part of the curriculum at Breakthrough Centre Academy, and learners as young as 3 have developed sound literacy foundations through this programme. Local schools and parents also attend our workshops on helping children apply foundational patterns in reading.</p>
{photo("i-can-read-learner", "One of our little readers hard at work on her I can read sheet, surrounded by her favourite books", "tall", "Little readers, big imaginations")}</div>
<div class="measure"><h2>Reading, speaking and growing in confidence</h2>
<p>Poor literacy is a national concern. Our Literacy and Language Development programme has become a model for strong results in foundational reading, mathematics and public speaking, and our learners leave with confidence and healthy self-esteem.</p>
{photo("i-can-read-parent-workshop", "Jessica presenting an I can read workshop to parents, helping them build strong reading habits at home", "tall", "Jessica sharing I can read with our parents")}</div>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><h2>A week at the Academy</h2><p class="lead">Cooking, shopping, coding, exploring, painting, planting and splashing in the water pool: this is what learning looks like for our little ones. The photos move on their own; tap one to see it bigger.</p></div>
{gallery_html(ACADEMY_GAL)}
</div></section>
{LIGHTBOX}

<section class="section"><div class="wrap">
<div class="section-head"><h2>Dressed up for Valentine's Day 2026</h2><p class="lead">Our learners love a reason to celebrate, from Heritage Day to the end-of-year function.</p></div>
{gallery_html(VAL_GAL, "Valentine's Day 2026")}</div></div></section>

<section class="section tint"><div class="wrap split">
{photo("academy-heritage-day", "Our Academy learners in their traditional dress on Heritage Day", "tall", "Heritage Day at the Academy")}
<div class="measure"><h2>Proud of who we are</h2>
<p>On Heritage Day our learners come to school in traditional dress, sing, dance and celebrate the cultures that make South Africa special. Learning to honour where we come from builds confidence and respect for others.</p>
{photo("academy-with-principal", "A car full of happy faces: our learners on an outing with their principal", "wide", "Out and about with our principal")}</div>
</div></section>

<section class="section olive"><div class="wrap split">
<div><h2>Parents as partners</h2>
<p>You're part of the team. Every term we hold parent meetings where you can see your child's progress and get to know the teachers, plus free workshops on how to help your child do their best at home.</p>
<h2>Time to shine</h2>
<p>Every learner gets a turn on stage at our Annual Concert and Graduation: speaking, storytelling, dancing, acting and singing in front of a proud crowd.</p>
{photo("bca-concert-2019-fairies", "Our little fairies and a very serious young prince on stage at the BCA concert, 2019", "wide", "Our little fairies at the BCA concert, 2019")}</div>
{photo("academy-graduate-2026-red", "One of our Class of 2026 graduates, cap on and scroll in hand", "tall")}
</div></section>

<section class="section tint"><div class="wrap">
<div class="section-head"><h2>Our Grade R graduates of 2022</h2><p class="lead">Caps on, certificates and trophies in hand, and so much to be proud of. Every one of these little graduates left us ready for big school.</p></div>
{photo("bca-grade-r-graduates-2022", "Our proud Grade R graduates of 2022 in their caps and gowns, holding their certificates and trophies, with Ps Trevor, Jessica and their teachers", "pano", "Breakthrough Centre Academy Grade R graduates, 2022")}
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><h2>From our archive</h2><p class="lead">Our preschool started out as Daddy's Daycare and Pre-school in the little blue tin house. Here are a few moments from the years since. <a href="news.html">Read our story in the news</a>.</p></div>
{gallery_html(ACADEMY_ARCHIVE_GAL, "Academy archive")}
</div></section>
""" + cta("Enrol your child", f"We'd love to welcome your family. WhatsApp {PHONE_DISPLAY} to find out about places and registration.", "WhatsApp about places", ac_msg)
pages.append(("academy.html", page("academy.html",
    "Preschool in Groutville, KwaDukuza | Breakthrough Centre Academy",
    "Looking for a preschool near KwaDukuza, Shakaskraal or Ballito? Our Groutville Academy helps children from age two read, count and speak with confidence.",
    academy + ACADEMY_FAQ[0], og_image="back-to-school-2026", body_class="playful",
    extra_ld=[{"@context": "https://schema.org", "@type": "Preschool", "name": "Breakthrough Centre Academy",
              "url": BASE_URL + "academy.html", "telephone": PHONE_INTL, "foundingDate": "2005",
              "address": ORG_LD["address"], "parentOrganization": {"@id": BASE_URL + "#organization"},
              "sameAs": [FB_ACADEMY]}, ACADEMY_FAQ[1]])))

# ---------- Kidz Club (playful)
KC_GAL = [
    ("journey-03-memorable-childhood", "Creating a memorable childhood: a field full of our Kidz Club children"),
    ("journey-02-birth-of-kidz-club", "The birth of the Kidz Club in 1990"),
    ("sb-kidz-club-early-outdoor-show", "Clowns and leaders putting on a show for a crowd of children in the early years"),
    ("sb-kidz-club-early-hall", "A hall packed with happy Kidz Club children in the early days"),
    ("sb-kidz-club-early-group-outside", "A big Kidz Club group outside the centre"),
    ("sb-siza-water-puppet-booth", "Our puppet theatre and play equipment, sponsored by Siza Water"),
    ("sb-outreach-shakaskraal-clown", "A clown leading games for children in Shakaskraal"),
    ("sb-movie-day-kidz-club", "Movie day at Kidz Club, with a room full of excited children"),
    ("sb-fun-and-games-early", "Fun and games on the grass in the early days of Kidz Club"),
    ("sb-puppets-early", "Our puppets popping up over the puppet theatre"),
    ("sb-christmas-1999-gifts", "Our children holding up their Christmas presents, 1999"),
    ("sb-kidz-club-banner-march", "Kidz Club on the march with our big painted banner"),
    ("sb-training-future-leaders", "Training future leaders at Kidz Club"),
    ("sb-news-2007-ballerinas", "Our first ballerinas in their striped outfits with teacher Pam Mills, 2007 (North Coast Courier)"),
    ("sb-news-2008-youth-day-ballet", "Our little ballerinas dancing at the 2008 Youth Day talent show (North Coast Courier)"),
    ("sb-news-waffles-day", "Waffle day: Ps Trevor serving waffles, ice cream and syrup to our Kidz Club (newspaper clipping)"),
    ("kidz-club-worship", "Our children singing their hearts out in praise and worship at Sunday Kidz Club"),
    ("kidz-club-soccer", "Our Kidz Club children kicking a ball around on the field in Etete"),
    ("kidz-club-easter-meal", "Our children tucking into a plate of food at the Kidz Club Easter celebration"),
    ("kidz-club-cupcakes", "Cupcakes all round on Father's Day at Kidz Club"),
    ("kidz-club-contest-winners", "Proud Kidz Club children showing off their contest prizes"),
    ("kidz-club-play", "One of our little ones zooming around on a toy bike"),
    ("kidz-club-mothers-day-2023", "Our mums and children outside the centre for Mother's Day at Kidz Club, 2023"),
    ("kidz-club-early-days", "Our Kidz Club children in their caps in front of a mural, from our early years"),
    ("kidz-club-crowd-2006", "Hundreds of children gathered with us for a children's event in 2006"),
    ("kidz-club-ballet-2009", "2009: our ballet girls in white outside the little blue tin house"),
    ("partners-kidz-club-balls", "Friends of Kidz Club handing out shiny new balls at the centre door"),
    ("kidz-club-heritage-day", "Our Kidz Club girls in traditional Zulu dress on Heritage Day"),
    ("kidz-club-madiba-day", "Our children around the Happy Birthday Madiba banner they made for Mandela Day"),
    ("kidz-club-smiles", "Big smiles from some of our Kidz Club children"),
    ("kidz-club-gifts", "Our Kidz Club children holding up their new colouring books and gifts"),
    ("kidz-club-reading-mat", "Reading time on the mat at Kidz Club"),
    ("kidz-club-reading-table", "Our children working through their reading and colouring sheets at Kidz Club"),
    ("kidz-club-hall", "A hall full of our children listening to the Kidz Club lesson"),
    ("kidz-club-story-on-steps", "Story time with our little ones on the steps of the centre"),
    ("kidz-club-outdoor-lesson", "A Kidz Club lesson out on the veranda"),
    ("kidz-club-praise-outside", "Our children singing and praising outside the centre"),
    ("kidz-club-group-outside", "Our Kidz Club family, children and leaders together outside"),
    ("kidz-club-line-up", "Lining up with one of our Kidz Club leaders for the next activity"),
    ("kidz-club-foosball", "Our children around the soccer machine at Kidz Club"),
    ("kidz-club-games-room", "Our young people in the Kidz Club games room, with the pool table the Nedbank award bought"),
    ("kidz-club-toys", "Our toddlers busy with toys at Kidz Club"),
    ("kidz-club-vegetable-garden", "Our Kidz Club vegetable garden in 2009"),
    ("spin-da-flava-visit", "The Spin Da Flava team on a visit to our Kidz Club"),
    ("larry-with-children", "Larry the puppet with a crowd of very excited children"),
    ("larry-puppet", "Larry peeping over his puppet stage"),
]
kidz = page_head("Kidz Club",
    "Every Sunday morning from 8 to 10, children from Etete, Groutville and around KwaDukuza come together for praise, a Bible story, games, friends and a lot of encouragement.",
    ["kidz-club-worship", "kidz-club-contest-winners", "kidz-club-cupcakes"]) + f"""
<section class="section"><div class="wrap split">
<div><p class="big-time">Sundays<br>8 to 10am</p>
<p class="lead">At Breakthrough Centre, 170 Old Main Road, Etete. All children in our community are welcome, rain or shine.</p>
<p>This is where Breakthrough Centre began on 10 October 1990: a children's club that gave young people somewhere good to be. Thirty-six years later, Sunday mornings are still the heartbeat of the centre, and some of the children who came as toddlers now come back to encourage the next group to stay in school and finish strong. In the early days our girls even learned ballet at Kidz Club, taught by Pam Mills alongside Jessica, outside the little blue tin house.</p></div>
{photo("kidz-club-sunday", "Our children and young people together at Sunday Kidz Club in Groutville", "wide")}
</div></section>

<section class="section tint"><div class="wrap">
<div class="section-head"><h2>What happens on a Sunday</h2><p class="lead">The Kidz Club is the most exciting place to be on a Sunday morning. Children are blessed with a memorable childhood through the activities we give them, in a safe and secure environment supervised by trained professionals.</p></div>
<div class="ways">
<div><h3>Praise and worship</h3><p>The highlight of the morning. The children lead the songs, learn new ones in just a couple of sessions, and fill the hall with noise.</p></div>
<div><h3>Stories and reading</h3><p>A Bible story every week (Daniel in the lions' den, young Joseph and his coat, the prodigal son, Samson, Hannah and more), plus time with books and worksheets to build reading skills.</p></div>
<div><h3>Life lessons</h3><p>Friendship, gratitude, respect, a servant's heart, what Freedom Day and Youth Day mean, and how to stay safe. We've talked about bullying, gender-based violence and child protection too.</p></div>
<div><h3>Games, crafts and sport</h3><p>Arts and crafts, sport, a game of Monopoly building entrepreneurial skills, Scrabble setting foundational literacy patterns, the all-time favourite soccer machine and plenty of other games.</p></div>
<div><h3>Feeding every Sunday</h3><p>There is nothing more rewarding than putting a smile on the face of a child, so every Sunday the children share a meal together.</p></div>
<div><h3>The annual Christmas party</h3><p>The highlight of our calendar. Our annual Kidz Club party ensures that every child receives a gift for Christmas and a sumptuous treat.</p></div>
<div><h3>Special days</h3><p>Easter, Mother's Day, Father's Day, Mandela Day, Women's Day, Heritage Day and birthdays all get celebrated.</p></div>
<div><h3>Visitors</h3><p>Guests share with the children: an officer from Umhlali SAPS on substance and child abuse, Metro World Child South Africa on bullying, local churches who serve a meal, the Spin Da Flava team, and former Kidz Club members.</p></div>
</div></div></section>

<section class="section"><div class="wrap split">
{photo("kidz-club-contest-prizes", "Our Kidz Club children on stage collecting their prizes at the My City, My Future contest", "tall")}
<div class="measure"><h2>My City, My Future</h2>
<p>At our "My City, My Future" contest, Kidz Club children shared their hopes and dreams for their community. The winner took home a R500 education voucher, the runners-up won hampers, five children received book prizes for their effort, and every child who took part got a pencil case.</p>
<p>Hearing a new generation speak about their future gives us real hope for South Africa.</p></div>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><h2>Kidz Club in pictures</h2><p class="lead">Thirty-six years of Sunday mornings: a garden, games, gifts, Heritage Day, Larry and a lot of happy faces. The photos move on their own; tap one to see it bigger.</p></div>
{gallery_html(KC_GAL)}
</div></section>
{LIGHTBOX}

<section class="section tint"><div class="wrap split">
<div class="bubble"><h2>Meet Larry!</h2>
<p>Larry the puppet appears occasionally to give the children a good moral lesson, while making lots of mistakes himself in a very hilarious manner. We call him Laugh Out Larry.</p>
<p>During the pandemic Larry found himself in the Ballito Television studio, presenting daily kids' programmes to children in their homes. You can catch the Laugh Out Larry Show on YouTube.</p></div>
{photo("larry-stage", "Larry the puppet on his stage, ready to make the children laugh", "wide", "Larry the puppet")}
</div></section>
""" + cta("Come and join us", f"Questions about Kidz Club? Call or WhatsApp {PHONE_DISPLAY}.", "WhatsApp us", "Hi, I have a question about Sunday Kidz Club.")
pages.append(("kidz-club.html", page("kidz-club.html", "Sunday Kidz Club in Groutville, KwaDukuza | Breakthrough Centre",
    "Looking for something for your children on a Sunday? Kidz Club meets every Sunday from 8 to 10am at Breakthrough Centre, Etete, Groutville. Home of Larry the puppet.",
    kidz, og_image="kidz-club-worship", body_class="playful",
    extra_ld={"@context": "https://schema.org", "@type": "Event", "name": "Sunday Kidz Club",
              "eventSchedule": {"@type": "Schedule", "byDay": "https://schema.org/Sunday", "startTime": "08:00", "endTime": "10:00",
                                "repeatFrequency": "P1W", "scheduleTimezone": "Africa/Johannesburg"},
              "location": {"@type": "Place", "name": "Breakthrough Centre", "address": ORG_LD["address"]},
              "organizer": {"@id": BASE_URL + "#organization"}})))

# ---------- Community / social development
CP_GAL = [
    ("child-protection-day-2026", "A hall full of our little superheroes at the 2026 Child Protection event"),
    ("child-protection-heroes-2026", "Three of our young superheroes at the 2026 Child Protection event"),
    ("child-protection-march", "Our children, volunteers and a few brave clowns marching through Etete for child protection"),
    ("child-protection-march-placards", "Our learners holding up their placards: it shouldn't hurt to be a child"),
    ("child-protection-march-crowd", "Our children marching along the road in Etete, speaking out against child abuse"),
    ("child-protection-programme", "Our leaders and children performing at the annual Child Protection programme"),
    ("child-protection-march-flags", "Hundreds of our children with flags at the Child Protection March"),
    ("child-protection-little-marcher", "Our littlest marcher leading the way with her own hand-drawn poster, while the clowns and the crowd follow behind"),
    ("child-protection-superhero-dance", "Our little superheroes dancing in the street with South African flags while the town stops to watch"),
    ("child-protection-saps", "Our friends from SAPS came out to march with us, and so did a very happy turtle"),
    ("child-protection-paramedics", "Paramedics and emergency workers stood shoulder to shoulder with our children and their posters"),
    ("child-protection-march-superhero", "Even a superhero joined our Child Protection March on the main road"),
    ("founders-child-protection", "Ps Trevor and Jessica in their superhero costumes for the Child Protection March"),
]
HELP_GAL = [
    ("journey-04-keep-hope-alive", "In the midst of adversity, keep hope alive: neighbours waving with their food parcels"),
    ("sb-food-distribution-collage", "Kidz Club food distribution: Ps Trevor and Jessica with families and a car full of food"),
    ("sb-clothes-distribution-early", "Handing out clothes to children at the centre"),
    ("sb-outreach-hospital-children", "Visiting children in hospital"),
    ("sb-outreach-shakaskraal", "Outreach to children in Shakaskraal"),
    ("sb-gift-of-givers-children", "Hundreds of children waiting on the grass when Gift of the Givers visited Breakthrough Centre"),
    ("sb-gift-of-givers-jessica", "Jessica handing out toiletries during the Gift of the Givers visit"),
    ("sb-gift-of-givers-queue", "Our community queuing outside the centre for the Gift of the Givers distribution"),
    ("food-parcel-outreach", "Handing a food parcel to one of our neighbours during an outreach in Etete"),
    ("outreach-in-the-rain", "Our neighbours waiting under umbrellas for blankets and food parcels"),
    ("gift-box-hall-2014", "A hall full of children at our gift box distribution, August 2014"),
    ("feeding-scheme-2013", "Our volunteers handing out food to children outside the centre, December 2013"),
    ("feeding-scheme-children", "Children sharing a meal together on the grass, from our feeding scheme"),
    ("lotus-fm-jessica", "Jessica on air with Lotus FM, telling listeners about our school shoe distribution"),
    ("lotus-fm-trevor", "Ps Trevor in the Lotus FM studio for the school shoe distribution"),
    ("distribution-trevor-parcels", "Ps Trevor handing out parcels to mums and grannies at one of our distributions"),
    ("school-shoes-lotus-fm", "Learners proudly holding their new school shoes from our Lotus FM partnership"),
    ("community-meal-bethel", "Sitting down on the ground to share a meal with our Kidz Club children"),
    ("elderly-distribution", "Our team handing out blankets and gifts to our elderly neighbours"),
    ("feeding-and-distribution", "A bakkie loaded with food parcels, ready to go out to families"),
    ("feeding-cooldrinks", "Our volunteers serving food and cooldrinks to a line of hungry children"),
    ("community-handout", "Children holding the parcels our volunteers handed out"),
    ("community-children-field", "Our volunteers with a group of children in Etete"),
    ("hospital-visit-gifts", "Visiting children in hospital with gifts to brighten their day"),
    ("hospital-visit-baby", "Visiting a little one in hospital"),
    ("netball-hoops-sasko", "Our girls playing netball with the hoops donated by Sasko"),
    ("girls-health-hygiene-2", "Our girls holding up their signs: Dream Big, I am Enough"),
]
XMAS_GAL = [
    ("sb-christmas-2000-show", "Christmas 2000: the show in full swing for a crowd of children"),
    ("sb-christmas-2001-games", "Christmas 2001: party games with the clowns"),
    ("sb-christmas-2000-900-kids", "Christmas 2000: about 900 children at our Kidz Club party"),
    ("sb-clown-christmas-2000", "A clown welcoming the children at the 2000 Christmas party"),
    ("sb-christmas-2001-crowd", "Christmas 2001: 1,500 children lined up on the field"),
    ("sb-christmas-2002-collage", "Christmas 2002: cooking for 1,500 children with our many volunteers"),
    ("sb-christmas-2003-etete", "Christmas 2003 in Etete: dancing and party packs"),
    ("sb-christmas-2003-shakashead", "Christmas 2003 in Shakashead, one of three parties that year"),
    ("sb-christmas-2007-team", "Our 2007 Christmas party team with Spin the Flava"),
    ("sb-christmas-2007-spin-da-flava", "Spin the Flava handing out treats at our 2007 Christmas party"),
    ("christmas-carols-alberlito-stairs", "Our carol singers on the stairs at Alberlito Hospital"),
    ("christmas-party-stage", "Our Kidz Club children on stage with their Christmas gifts"),
    ("christmas-party-gifts", "A room full of our children opening their Christmas presents"),
    ("christmas-shoebox-gifts", "The joy of opening a Christmas shoebox gift"),
    ("christmas-gifts-etete", "Our children with their Christmas gifts beside the sun and eagle mural"),
]
SCHOOLS_GAL = [
    ("schools-event-folders", "Learners from our partner schools at Breakthrough Centre, each holding a new folder, with the friends who made the day happen"),
    ("inter-school-competition-winners", "Proud winners of an inter-school competition at Breakthrough Centre, holding their certificates and trophies"),
    ("partners-speak-out-school", "Friends who work with us, at a school event calling for an end to violence"),
]
PARTNERS_GAL = [
    ("partners-gift-bags-academy", "Friends of the centre bringing gift bags for our Academy children, one of our past projects"),
    ("partners-kidz-club-balls", "Friends handing out new balls to our Kidz Club children"),
    ("partners-speak-out-school", "Friends who work with us, ready to speak out at a school event"),
]
YOUTH_GAL = [
    ("sb-youth-camp-river", "Pure joy: our young people splashing in the river on youth camp"),
    ("sb-youth-camp-group", "Our girls together at youth camp"),
    ("sb-youth-camp-obstacle", "Helping each other over the log wall at youth camp"),
    ("sb-news-2008-youth-day-winners", "Winners of our first Youth Day talent contest with Jessica, 2008 (North Coast Courier)"),
    ("sb-youth-day-2008-crowd", "Young people lining up at our 2008 Youth Day rally"),
    ("sb-news-sewing-classes", "Learning to sew at our free sewing classes (newspaper clipping)"),
]
COMM_FAQ = faq("Community questions", [
    ("Does Breakthrough Centre help families in need in KwaDukuza?", f"Yes. Over the years we've handed out blankets, food parcels, hot meals, school shoes, gift boxes and baby formula to families in Etete and across KwaDukuza. If you know of a family in need, WhatsApp {PHONE_DISPLAY}."),
    ("When is the Child Protection event?", "We host it every year with local schools and organisations. The date is announced on our Facebook page, and children and parents are welcome."),
    ("Can my business, school or church partner with you?", f"Please do. Businesses, schools, churches and individuals have sponsored meals, books, sports equipment, school shoes and gifts. WhatsApp {PHONE_DISPLAY} and let's talk."),
])
community = page_head("Community projects",
    "Breakthrough Centre makes its impact on an ongoing basis, from poverty alleviation programmes to education and empowerment. We see a need and, where possible, we address the need.",
    ["child-protection-heroes-2026", "blanket-outreach", "christmas-gifts-etete"]) + f"""
<section class="section"><div class="wrap split">
<div class="measure">
<h2>Child protection is everyone's business</h2>
<p>A highlight of our year is the Annual Child Protection Event, where the town comes to a standstill as little ones join together with strategic people to make a clarion call declaring an end to child abuse, upholding child protection as one community. The theme "Every child a superhero" sees every child dress up as their favourite superhero, march through the town and speak out against child abuse.</p>
<p>Would you like to partner with us in this exciting event? <a href="{wa('Hi, I would like to partner with Breakthrough Centre on the Child Protection Event.')}" rel="noopener">Contact us for more information</a>.</p>
<p>In earlier years our learners, volunteers and a few brave clowns marched through the streets of Etete with home-made placards and slogans like "It shouldn't hurt to be a child".</p>
</div>
{photo("child-protection-captains-2026", "Two little Captain Americas ready to stand up for children at our 2026 Child Protection event", "tall")}
</div>
<div class="wrap"><blockquote class="pullquote">
<p>Many times our hearts are broken when we hear of cases of child abuse that could have been avoided if more preventative measures had been in place. This is one of the reasons Breakthrough Centre focuses on prevention to eradicate this evil in society: empowering parents to detect unsafe environments and decisions. Our children are surrounded by unsafe environments, but we can teach them how to protect themselves, how to speak out against abuse, and how to guard themselves and their friends when there is danger. One of our slogans, "Every child has a voice", inspires children in the area of public speaking. We as guardians of this city have a responsibility to amplify this voice.</p>
<cite>Breakthrough Centre</cite></blockquote></div></section>

<section class="section"><div class="wrap">
<div class="section-head"><h2>Standing up for children, in pictures</h2><p class="lead">The photos move on their own; tap one to see it bigger.</p></div>
{gallery_html(CP_GAL)}
</div></section>

<section class="section tint"><div class="wrap split top">
<div class="measure"><h2>Safety tips for parents and caregivers</h2>
<p>The danger of trafficking and kidnapping affects every community. We put these tips together for parents in Etete and KwaDukuza. Please share them with other parents, caregivers and schools.</p></div>
<ul class="checklist">
<li>Have a trusted person drop off and fetch your child when you can't, and arrange for someone to meet them if they walk part of the way home.</li>
<li>Encourage children to walk home from school in groups, and to lock gates and doors if they're home alone.</li>
<li>Agree that you'll never change pick-up plans without telling your child first, so "your mum sent me to fetch you" is never a reason to go with someone.</li>
<li>Practise what to do if someone grabs them, and teach them emergency numbers.</li>
<li>Teach children not to accept sweets or treats from strangers.</li>
<li>If you work, consider an aftercare facility or a library where your child can wait safely.</li>
<li>Know what your child does online and on devices, and set clear boundaries.</li>
<li>Teach sons to respect girls and their boundaries, and daughters likewise. Discipline starts at home.</li>
<li>Name a teacher or trusted adult your child can go to in an emergency, and speak well of police and safety officers so your child will trust them.</li>
</ul></div></section>

<section class="section"><div class="wrap split">
{photo("blanket-outreach", "Wrapping a warm blanket around one of our neighbours on a rainy outreach day in Etete", "wide")}
<div><h2>Practical help when it's needed most</h2>
<ul class="checklist">
<li><strong>Blankets and food parcels:</strong> in keeping with Isaiah 58:7, our team has carried blankets and food parcels to elderly and needy neighbours in Etete, even in pouring rain.</li>
<li><strong>Feeding schemes:</strong> meals for hungry children, from our feeding programmes in 2013 to the plates of food shared at Kidz Club today.</li>
<li><strong>Gift boxes and school shoes:</strong> gift boxes for a hall full of children in August 2014, and new school shoes for learners in partnership with Lotus FM, where Jessica and Ps Trevor went on air to share the story.</li>
<li><strong>Mums and babies:</strong> diapers for babies, and clothing and linen for their mums.</li>
<li><strong>Hospital visits:</strong> visiting sick children and babies in hospital and bringing them gifts.</li>
<li><strong>Relief in hard times:</strong> hot meals during Covid-19, food hampers for families, and baby formula from Durban to Tugela during the 2021 unrest in KZN.</li>
<li><strong>Jumpstart:</strong> work-readiness training that prepares young people for their first jobs.</li></ul></div>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><h2>Outreach through the years</h2><p class="lead">The photos move on their own; tap one to see it bigger.</p></div>
{gallery_html(HELP_GAL)}
</div></section>
{LIGHTBOX}

<section class="section olive"><div class="wrap split">
<div><h2>Christmas cheer</h2>
<p>Our team has taken Christmas carols to patients and staff at Alberlito Hospital in Ballito. The highlight of our calendar is the annual Kidz Club Christmas party, where every child receives a gift and a sumptuous treat, made possible by friends of the centre.</p></div>
{photo("christmas-carols-alberlito", "Our team singing Christmas carols for patients and staff at Alberlito Hospital, Ballito", "wide")}
</div>
<div class="wrap" style="margin-top:2rem">{gallery_html(XMAS_GAL)}</div></section>

<section class="section"><div class="wrap split">
{photo("girls-health-hygiene", "Our girls with their Fearless masks at the health, hygiene and etiquette programme", "wide")}
<div class="measure"><h2>Health, hygiene and etiquette</h2>
<p>Breakthrough Centre hosts girl and boy empowerment programmes, providing young people with hygiene packs while teaching them about health, hygiene and etiquette.</p>
<p>Preparing young people for their future careers starts now. So in whatever we teach, we train them for life.</p></div>
</div></section>

<section class="section"><div class="wrap split">
<div class="measure">
<h2>Investing in local schools</h2>
<p>Tomorrow's leaders are sitting in today's classrooms, so we invest in local public schools. Our programmes bring teachers, parents, officials and everyone with a stake in education around the same table. In 2026 Jessica Nair ran parent workshops and spoke at the Boys Talk and Girls Talk sessions at Radha Roopsingh Primary School. <a href="training.html">See our training work</a>.</p>
<h2>Potential Unleashed: contests and performances</h2>
<p>Our inter-school contests in art, poetry and talent help young people find out what they're good at. Children get a stage, an audience and skills that can shape their future. Even during the pandemic we kept the contests going online.</p>
</div>
{photo("working-with-schools", "Learners from our local high schools taking part in one of our programmes", "tall")}
</div>
<div class="wrap" style="margin-top:2rem">{gallery_html(SCHOOLS_GAL)}</div></section>

<section class="section"><div class="wrap split">
<div class="measure"><h2>Our young people</h2>
<p>In 2008 our first Youth Day rally brought together about 170 young people for raps, art, modelling, poetry, singing and dancing, and we launched our Youth Club for 12 to 21-year-olds. Since then our youth have been on camps where they climb, splash in the river and make friends for life, and a youth help desk gives teenagers somewhere to turn with problems like drugs, abuse, pregnancy and peer pressure.</p>
<h2>Skills for life</h2>
<p>Our free sewing classes gave women from Etete a three-month course and a chance to earn, on machines donated by Siza Water. Over the years the centre has also offered computer classes, homework help, literacy and skills training, and HIV/AIDS and abuse awareness.</p></div>
{gallery_html(YOUTH_GAL, "Our young people")}
</div></section>

<section class="section tint"><div class="wrap split">
{photo("library-books-donation", "Our Academy learners diving into the library books donated by Prince's Grant Bookclub", "wide")}
<div><h2>Friends who make it possible: our sponsors</h2>
<p>None of this happens alone. Thank you to everyone who has stood with us, including:</p>
<ul class="checklist">
<li>Sasko, for netball hoop stands and soccer goal posts</li>
<li>Prince's Grant Bookclub, for library books for the Academy</li>
<li>Lotus FM, for partnering with us on school shoes</li>
<li>Bethel Baptist Church, who ministered to our children and served them a meal</li>
<li>Metro World Child South Africa and Umhlali SAPS, who spoke to our children</li>
<li>The Friends of the Kidz Club and every family who sponsors meals, treats and gifts</li></ul></div>
</div>
<div class="wrap" style="margin-top:2rem"><h3>People who work with us</h3>{gallery_html(PARTNERS_GAL)}</div></section>

<section class="section"><div class="wrap split">
<div class="measure"><h2>Recognised for community development</h2>
<p>On 19 April 2012 Breakthrough Centre won 2nd place in the community category of the North Coast Big 5 Service Excellence Awards. We've also been honoured with 1st place in the KwaDukuza Municipality Mayoral Awards (Community Development category), the Nedbank Local Heroes Award (2009) and the In-house Club National Heroes Award (2006). <a href="about.html">Read our story</a>.</p></div>
{photo("big5-award-2012-presentation", "A proud moment at home: holding our North Coast Big 5 Service Excellence Award, 2nd place in the community category, 2012", "tall", "A proud moment: our Big 5 award, 2012")}
</div></section>
""" + cta("Partner with us", "Schools, businesses, churches and individuals work with us on outreach, events and relief. Let's talk.", "WhatsApp us", "Hi, I would like to partner with Breakthrough Centre.")
pages.append(("community.html", page("community.html", "Community Outreach in KwaDukuza and Groutville | Breakthrough Centre",
    "Child protection events, blankets and food parcels, feeding schemes, school shoes and Christmas outreach in Etete, Groutville and KwaDukuza since 1990.",
    community + COMM_FAQ[0], extra_ld=COMM_FAQ[1], og_image="child-protection-day-2026")))

# ---------- Weddings / marriage officer
WED_FAQ = faq("Wedding questions", [
    ("Do you register the marriage with Home Affairs?", "Yes. Registering your marriage at Home Affairs is part of our service, and on the day you receive your marriage certificate and copies of the marriage and witness registers."),
    ("Can we have a traditional or non-traditional ceremony?", "Either. We work with you to create the ceremony that fits your story."),
    ("Where can the ceremony take place?", "Couples have married with us on the beach, in halls and at reception venues along the Dolphin Coast. Tell us where you'd like it to be."),
    ("What documents do we need?", "Certified copies of the bride's, groom's and two witnesses' IDs, three colour photos each, and extra documents if you have a pre-nuptial agreement or one partner is not a South African citizen. The full list is above."),
    ("How do we book?", f"WhatsApp {PHONE_DISPLAY} to talk about your date and ceremony."),
])
gal = ["wedding-canopy", "wedding-vows", "wedding-beach-setup", "wedding-bride-vows", "wedding-beach-guests",
       "wedding-reception-table", "wedding-family", "wedding-cake", "wedding-napkin", "wedding-reception-hall",
       "wedding-cake-family", "wedding-coastal-path"]
gal_alt = {
    "wedding-canopy": "A couple saying \"I do\" under a floral canopy at an evening ceremony",
    "wedding-vows": "A bride and groom exchanging vows before our marriage officer",
    "wedding-beach-setup": "White chairs and a decorated arch waiting for the couple, overlooking the sea",
    "wedding-bride-vows": "A bride saying her vows at a ceremony led by our marriage officer",
    "wedding-beach-guests": "Family and friends gathered for a beach wedding on the Dolphin Coast",
    "wedding-reception-table": "A reception table dressed with flowers and fairy lights",
    "wedding-family": "A happy couple surrounded by family on their big day",
    "wedding-cake": "The newlyweds cutting their wedding cake",
    "wedding-napkin": "Mr and Mrs: a little detail from the reception table",
    "wedding-reception-hall": "A reception hall glowing in purple light",
    "wedding-cake-family": "The newlyweds cutting the cake with family close by",
    "wedding-coastal-path": "The coastal path down to a beach wedding",
}
gallery = gallery_html([(g, gal_alt[g]) for g in gal], "Weddings by our marriage officer")
weddings = page_head("Marriage officer",
    "Getting married in KwaDukuza, Ballito or anywhere on the Dolphin Coast? We'll make your ceremony personal and meaningful, traditional or not, and handle the registration at Home Affairs.",
    ["wedding-vows", "wedding-canopy", "wedding-beach-setup"],
    f'<div class="btn-row"><a class="btn btn-whatsapp" href="{wa("Hi, I would like to book the marriage officer.")}" rel="noopener">{WA_ICON}Book your ceremony</a></div>') + f"""
<section class="section"><div class="wrap">
<div class="section-head"><h2>Your love story, your way</h2><p class="lead">We sit down with you, get to know your story and shape a ceremony that feels like you, whether it's barefoot on the beach or an evening celebration in a hall.</p></div>
{gallery}
</div></section>
<dialog class="lightbox"><button class="close" type="button">Close</button><img src="" alt=""><p></p></dialog>

<section class="section tint"><div class="wrap split top">
<div><h2>What to bring for registration</h2>
<div class="need"><h3>Clear photocopies of IDs</h3>
<ul class="checklist"><li>Bride and groom</li><li>2 witnesses</li></ul>
<p>We will have them certified. IDs must be photocopies, not printed copies of photos.</p>
<ul class="checklist"><li>Card ID: front and back on the same page</li><li>Book ID: the complete open front, photocopied</li></ul></div>
<div class="need"><h3>Photos</h3><p>3 colour photos each of the bride and groom, preferably 4 x 4 cm.</p></div></div>
<div>
<div class="need"><h3>Marrying with a pre-nuptial agreement</h3><p>A letter from your attorney, on their letterhead, with both your and your partner's details, stating that a pre-nuptial agreement is in place. This must be done before the date of registration.</p></div>
<div class="need"><h3>If your partner is not a South African citizen</h3>
<ul class="checklist"><li>A "letter of no impediment" from their country of origin or embassy</li><li>A valid, current visa</li><li>An appointment for an interview with an immigration official at Home Affairs</li></ul></div>
<div class="need"><h3>On the day of registration you will receive</h3>
<ul class="checklist"><li>A valid marriage certificate</li><li>A copy of your marriage register</li><li>A copy of your witness register</li></ul></div>
</div></div></section>
""" + cta("Planning your wedding?", f"Call or WhatsApp {PHONE_DISPLAY} to talk about your ceremony.", "WhatsApp the marriage officer", "Hi, I would like to book the marriage officer.")
pages.append(("weddings.html", page("weddings.html", "Marriage Officer in KwaDukuza and Ballito | Breakthrough Centre",
    "Need a marriage officer near KwaDukuza or Ballito? Personal ceremonies, traditional or non-traditional, plus Home Affairs registration. See what to bring.",
    weddings + WED_FAQ[0], extra_ld=WED_FAQ[1], og_image="wedding-canopy")))

# ---------- Training
training = page_head("Training and development",
    "Practical workshops, leadership and mentoring for parents, teachers, young people and community groups across KwaDukuza and the iLembe District.",
    ["boys-talk-2026", "school-talk-learners-2026", "computer-class"]) + f"""
<section class="section"><div class="wrap split">
<div class="measure"><h2>Equipping people to thrive</h2>
<p>Good intentions go further with the right skills. Through workshops, mentoring and one-on-one time, we give people practical tools they can use straight away at school, at work, at home and in their community.</p>
<h3>What we offer</h3>
<ul class="checklist"><li>Workshops for educators, parents and community groups</li><li>Leadership and mentoring programmes</li>
<li>Jumpstart work-readiness training for young people</li><li>Free parent workshops at Breakthrough Centre Academy</li></ul></div>
{photo("computer-class", "Our young people learning computer skills at the centre", "wide")}
</div></section>

<section class="section tint"><div class="wrap split">
{photo("boys-talk-2026", "Jessica speaking to the boys at Radha Roopsingh Primary's Boys Talk, 2026", "tall")}
<div class="measure"><h2>Out in our schools and communities</h2>
<p>Our co-founder Jessica Nair spends a lot of time in local schools and churches, sharing what 36 years with children and families have taught us.</p>
<ul class="checklist">
<li><strong>Parent workshops:</strong> in 2026 she presented two workshops to parents at Radha Roopsingh Primary School on how to monitor and support their children's learning and build strong reading habits at home.</li>
<li><strong>Boys Talk and Girls Talk:</strong> on 28 August 2026 she spoke to learners at the school's Boys Talk and Girls Talk sessions.</li>
<li><strong>Women's conferences:</strong> she was a guest speaker at the Bloom Women's Conference hosted by Sanctuary of Hope on 29 August 2026.</li>
<li><strong>Children's ministry leaders:</strong> we take our Kidz Club leaders to training days and worship experiences, so the next generation of leaders keeps growing.</li></ul>
<p>Would you like a workshop or a speaker for your school, church or group? Get in touch.</p></div>
</div></section>
""" + cta("Book a workshop", f"To arrange training for your school, organisation or group, call or WhatsApp {PHONE_DISPLAY}.", "WhatsApp us", "Hi, I would like to book a workshop.")
pages.append(("training.html", page("training.html", "Workshops and Mentoring in KwaDukuza | Breakthrough Centre",
    "Workshops for educators, parents and community groups, leadership and mentoring programmes and Jumpstart work-readiness training at Breakthrough Centre, Groutville.",
    training, og_image="boys-talk-2026")))

# ---------- Prayer
prayer = page_head("Prayer and counselling",
    "Going through something hard? You don't have to face it alone. Come and be heard, in a safe and caring place in Groutville.",
    ["children-praying", "heritage-day-circle", "community-gathering"]) + f"""
<section class="section"><div class="wrap split">
<div class="measure"><h2>Walking with you</h2>
<p>Grief, family strain, worry about the future: whatever you're carrying, we'll listen without judging. We pray with you, offer personal guidance and walk with you and your family through the hard seasons, with faith, hope and resilience.</p>
<p>If you would like prayer, or would like to speak to someone, call or WhatsApp {PHONE_DISPLAY} and we'll arrange a time to meet.</p>
<h3>Children who pray</h3><p>Prayer is part of every Sunday at Kidz Club. Our children pray for each other, their families, their teachers, our community and our nation.</p></div>
{photo("children-praying", "Our children with their heads bowed, praying together in Groutville", "wide")}
</div></section>
""" + cta("Reach out", "Send us a message and we'll arrange a time to meet.", "WhatsApp us", "Hi, I would like to speak to someone for prayer or counselling.")
pages.append(("prayer.html", page("prayer.html", "Prayer and counselling in Groutville | Breakthrough Centre",
    "A safe, caring space for prayer, spiritual growth and emotional healing at Breakthrough Centre in Etete, Groutville. Call or WhatsApp 081 775 1488.",
    prayer, og_image="children-praying")))

# ---------- Events
events = page_head("What's on",
    "There's always something happening at the centre. Here's what comes around each year. For exact dates, follow us on Facebook.",
    ["child-protection-heroes-2026", "graduation-2025", "anniversary-cake-35"]) + f"""
<section class="section"><div class="wrap">
<ul class="events">
<li><h3>Kidz Club</h3><p>Every Sunday, 8 to 10am.</p></li>
<li><h3>Annual Concert and Graduation</h3><p>Every Academy learner on stage, with public speaking, storytelling, dance, drama and singing.</p></li>
<li><h3>Annual Child Protection Event</h3><p>"Every child a superhero": children dress up as their favourite superhero, march through the town and speak out against child abuse. <a href="community.html">See the photos</a>.</p></li>
<li><h3>Potential Unleashed contests</h3><p>Inter-school contests in art, poetry and talent.</p></li>
<li><h3>Parent meetings and workshops</h3><p>Held every term at the Academy.</p></li>
<li><h3>Annual Kidz Club Christmas party</h3><p>The highlight of our calendar: every child receives a gift for Christmas and a sumptuous treat. We also take carols to Alberlito Hospital.</p></li>
<li><h3>Kidz Club special days</h3><p>Easter, Mother's Day, Father's Day, Women's Day and Heritage Day celebrations, plus contests like My City, My Future.</p></li>
<li><h3>Our anniversary</h3><p>Every 10 October we give thanks for another year since the children's club began in 1990.</p></li>
</ul>
<div class="btn-row"><a class="btn btn-ghost" href="{FB_CENTRE}" rel="noopener">Breakthrough Centre on Facebook</a><a class="btn btn-ghost" href="{FB_ACADEMY}" rel="noopener">Academy on Facebook</a></div>
</div></section>
""" + cta("Want to be part of an event?", "We welcome volunteers, sponsors and partner schools.", "WhatsApp us", "Hi, I would like to help with an event.")
pages.append(("events.html", page("events.html", "Events in Groutville: Kidz Club, Graduation and More | Breakthrough Centre",
    "What's on at Breakthrough Centre, Groutville: Sunday Kidz Club, our Concert and Graduation, the Child Protection event, school contests and Christmas outreach.",
    events, og_image="anniversary-cake-35")))

# ---------- In the news (owner's scrapbook, 7 Nov 2026)
def framed(img, alt):
    big = 1600 if os.path.exists(os.path.join(SITE, "images", img + "-1600.webp")) else 800
    return (f'<button type="button" class="slide-frame" data-full="images/{img}-{big}.webp">'
            f'<span class="slide-bg" aria-hidden="true" style="background-image:url(images/{img}-800.webp)"></span>'
            f'{pic(img, alt, sizes="(max-width: 760px) 100vw, 50vw")}</button>')

NEWS = [
  ("The early years", [
    ("1999", "Our first newspaper story", "Fresh air and fun keeps kids away from crime", "sb-news-1999-jessica-kids",
     "Jessica with some of our Kidz Club children in 1999",
     "Our very first media coverage. Every Saturday from 2 to 4pm, 80 to 90 children met at the Radha Roopsingh School for praise and worship, games, puppetry, clowning, drama and a lesson. Jessica had started the club to keep local children away from crime and drugs, and Ps Trevor had just begun music classes, teaching the children to sing and play guitar. To buy Christmas gifts, the two of them sold children's books and stationery, and did clowning and puppet shows at birthday parties.",
     "Race is not an issue for us."),
    ("2000", "From our scrapbook", "Etete Millennium Party", "sb-news-2000-millennium-party",
     "Our Kidz Club children spelling out WELCOME at the Etete Millennium Party",
     "Etete welcomed the new millennium with a party, and the children's message to everyone who came was simply: WELCOME.", None),
    ("30 November 2001", "The North Coast Courier", "The magic of Christmas", "sb-news-2001-magic-of-christmas",
     "Hundreds of happy children with our clowns at the 2001 Kidz Club Christmas party",
     "1,500 children came to our Christmas party, up from 900 the year before. Every child received a gift, donated by the parents of Umhlali Primary, and a hot meal, donated by Quick Plumbers in Shakaskraal. The club had 200 full-time members and had just opened a second branch in Shakaskraal, and the Umhlali police helped bring those children to Etete so that everyone could join in.", None),
    ("2002", "Our fight against crime and poverty", "Kids Club shines a little light", "sb-news-2002-shines-a-little-light",
     "Some of the hundreds of children from Etete and surrounding areas who came to Kidz Club in 2002",
     "Between 100 and 250 children, from toddlers to 18-year-olds, were coming every Saturday to sing, play and learn. We ran a feeding programme twice a month with help from our church and local businesses, and children who had been with us for five years or more had become assistants, teaching the little ones about abuse and other issues.", None),
    ("2005", "Christmas party 2005", "Santa visits Etete", "sb-news-2005-santa-visits-etete",
     "Kidz Club children with the toys and food hampers handed out at the 2005 Christmas party",
     "Over 1,300 children and 200 parents came to our Christmas party at Radha Roopsingh Primary. The children went home with toys and party packs, and parents received food hampers of rice, flour, beans and dhall.",
     "In the past 15 years, we have seen many children grow into successful people."),
  ]),
  ("Heroes, ballet and a growing centre", [
    ("31 March 2006", "The North Coast Courier", "Shakaskraal couple win national heroes awards", "sb-news-2006-heroes-cheque",
     "Ps Trevor and Jessica receiving the R10 000 INHOUSE Club Heroes Award cheque, 2006",
     "Radha Roopsingh Primary teacher Simi Persad nominated Ps Trevor and Jessica as \"national heroes\", and they won the Lubners INHOUSE Club Heroes Award, chosen from entries across South Africa. The R10 000 prize went towards building the centre.", None),
    ("2006", "INHOUSE Club magazine", "Lighting up Etete", "sb-news-2006-lighting-up-etete",
     "The little blue tin house in Etete, featured in INHOUSE magazine in 2006",
     "Our story in a national magazine. It told how Jessica started Kidz Club in the garden of the home she grew up in, and how the little blue tin house had become a preschool, crèche, community centre and church used by about 200 young people every week. Jessica's mother donated the house to be used as a community centre.",
     "The charm of the little, blue corrugated iron house"),
    ("22 June 2007", "The North Coast Courier", "\"Never give up your dreams\"", "sb-news-2007-nair-family",
     "Ps Trevor and Jessica with their children Taldon and Tamsyn, 2007",
     "A profile of Jessica: mother, wife, schoolteacher, counsellor and co-founder. She started Kidz Club on 10 October 1990. After she married Ps Trevor in 1994 they moved away, and her sister Shavera kept the club going until they came back in 1999 and took it over again. In 2002 the club was registered as a non-profit organisation.",
     "Dreams are not born without sacrifice, dedication and commitment."),
    ("5 October 2007", "The North Coast Courier", "Surprise celebration for community centre founder", "sb-news-2007-trevor-40th",
     "Ps Trevor with Jessica, Taldon and Tamsyn at his surprise 40th birthday party",
     "The children and our church family threw Ps Trevor a surprise 40th birthday party at the centre, with drums, dancers and speeches about how he and the centre had changed their lives.", None),
    ("19 October 2007", "The North Coast Courier", "Ballerinas in the making", "sb-news-2007-ballerinas",
     "Our Kidz Club ballet girls showing off a ballet step with their teacher, Pam Mills",
     "Ten little girls from Etete were learning ballet, thanks to Pam Mills of Ballito. Pam began by teaching line dancing, asked the girls one afternoon if they would like to learn ballet, and they never looked back.", None),
    ("30 November 2007", "The North Coast Courier", "Happy faces this Christmas", "sb-news-2007-spin-da-flava-kids",
     "Spin the Flava and our team with children at the 2007 Christmas party",
     "More than 500 children came to our Christmas party at Radha Roopsingh Primary. Christian group Spin the Flava entertained them, and everyone had breyani for lunch.", None),
    ("21 December 2007", "The North Coast Courier", "Day care creche and graduation", "sb-news-2007-grade-r-graduation",
     "Teacher Eunice Thabede with her Grade R graduates, 2007",
     "Our preschool, then called Daddy's Day Care and Creche, held its Grade R graduation and a sports day with a tug-of-war. Teacher Eunice Thabede stood proudly with her graduates.", None),
    ("4 July 2008", "The North Coast Courier", "Youth day talent show", "sb-news-2008-youth-day-winners",
     "Winners of the 2008 Youth Day talent contest with Jessica",
     "Our first Youth Day rally drew about 170 young people, who showed off raps, art, modelling, poetry, singing and dancing. We used the day to launch our Youth Club for 12 to 21-year-olds, meeting every Saturday.", None),
    ("1 August 2008", "North Coast Times", "Caught in the spirit of the Kidz Club", None, None,
     "Thiasha Naidoo, then a Grade 10 learner from Shakaskraal, volunteered at Kidz Club for her community project. Today she is Dr Thiasha Naidoo.", None),
    ("5 September 2008", "Stanger Weekly", "Community centre wins Heroes award", "sb-news-2008-nedbank-cheque",
     "Ps Trevor and Jessica with Nedbank's cheque and some of our preschool children, 2008",
     "We won R10 000 in the Nedbank Heroes competition, our second award for community work. The cheque was handed over at the centre by the Nedbank Ballito manager. The money was for sports equipment and indoor games, with the rest going to our building fund.", None),
    ("2009", "From our scrapbook", "Giving the kids a chance", "sb-news-2009-giving-kids-chance",
     "Etete youth with the pool table and soccer machine bought with the Nedbank award",
     "With the Nedbank prize we bought table tennis, a pool table, a table-top soccer machine, board games and soccer balls. We also opened a youth help desk for young people facing issues such as teenage pregnancy, drugs, abuse and peer pressure.",
     "Children in the area can still do what they love but in a controlled environment"),
  ]),
  ("Christmas, sponsors and empowerment", [
    ("", "From our scrapbook", "Kidz Club Christmas fun in Nkobongo", "sb-news-nkobongo-christmas",
     "Children in Nkobongo with their Christmas presents from Kidz Club",
     "More than 900 children in Nkobongo received early Christmas presents at the Nkobongo community hall, after a party in Etete for over 1,500 children earlier that December.", None),
    ("", "From our scrapbook", "Kidz Club Christmas Party", "sb-news-standard-bank-toys",
     "Standard Bank's John Lynch handing over toys to Ps Trevor and Jessica for the Christmas party",
     "KwaDukuza Standard Bank branch manager John Lynch handed over toys for our annual Christmas party at Radha Roopsingh School.", None),
    ("", "Stanger Weekly", "Festive food hampers", "sb-news-festive-hampers",
     "Families with the food hampers they received from the centre at Christmas",
     "Disadvantaged families were treated to a meal, clothes and a food hamper on Christmas Day, so that they could enjoy the festive season too.", None),
    ("", "From our scrapbook", "Ho ho ho", "sb-news-ho-ho-ho",
     "Kidz Club children showing off their Christmas gifts",
     "Over 300 children from disadvantaged homes came to our annual Christmas party, with face painting (Spiderman was the favourite), a puppet show about preventing child abuse, dancing and games.",
     "We want every child to experience the joy Christmas brings."),
    ("", "From our scrapbook", "Free sewing classes offered", "sb-news-sewing-classes",
     "A student at her sewing machine during our free sewing classes",
     "Women from Etete took a free three-month sewing course at the centre every day. Siza Water donated five sewing machines, an overlocker and two irons, and Stanger Waste Centre sponsored the material. Teacher Timna Tweedie ran the classes.", None),
    ("", "From our scrapbook", "Waffles, ice-cream and syrup", "sb-news-waffles-day",
     "Ps Trevor, syrup in hand, serving waffles to our Kidz Club children",
     "Many of our children had never had a waffle, so our volunteers made waffles with ice cream and syrup for the whole Kidz Club.", None),
    ("", "From our scrapbook", "Ballerinas perform for local clubs", "sb-news-ballerinas-wednesday-club",
     "Our ballerinas with members of the Wednesday Club who sponsored their classes",
     "Our ballet girls put on a performance for the Wednesday Club and the Sugarland Book Club, who sponsor their classes. By then Pam Mills had been teaching ballet as a volunteer for three years.", None),
    ("", "From our scrapbook", "Usha struts her stuff", None, None,
     "Mrs India South Africa contestant Usha Hemraj chose our community centre as her charity, and the proceeds of her dinner and dance at the Durban City Hall came to the centre.", None),
  ]),
  ("Breakthrough Centre and the Academy", [
    ("21 March", "From our scrapbook", "Human Rights Day celebrated in writing", "sb-news-human-rights-day",
     "Finalists and winners of our Human Rights Day art and poetry contest",
     "Eight local schools came to Breakthrough Centre for our Human Rights Day art and poetry writing contest: Groutville High, Sizani Combined Primary, Tinley Manor Primary, Radha Roopsingh Primary, Shakaskraal Primary, Shakaskraal Secondary, Nonhlevu Secondary and Shakaskraal S.A. Primary. Highway Radio's Phindile Phewa and artist Shavera Sayed judged.", None),
    ("29 November 2014", "From our scrapbook", "Talent in torrents", "sb-news-2014-graduation",
     "The Breakthrough Centre Academy Grade R class of 2014 with their certificates",
     "At the Breakthrough Centre Academy Concert and Graduation, learners from 2 to 6 years old performed dances, sketches, songs and recitals. Our Grade R class of 2014 graduated in style.", None),
  ]),
]

def news_cards(items):
    out = []
    for when, paper, head, img, alt, story, quote in items:
        meta = " · ".join(x for x in (paper, when) if x)
        q = f'<blockquote class="news-quote">"{e(quote)}"</blockquote>' if quote else ""
        media = f'<div class="news-media">{framed(img, alt)}</div>' if img else ""
        out.append(f'<article class="news-card{"" if img else " no-photo"}">{media}<div class="news-body">'
                   f'<p class="news-meta">{e(meta)}</p><h3>{e(head)}</h3><p>{e(story)}</p>{q}</div></article>')
    return "".join(out)

news = page_head("Our story in the news",
    "Thirty-six years of newspaper clippings, magazine pages and photos from our scrapbook. Each one tells part of the story of a little Kidz Club that grew into Breakthrough Centre.",
    ["sb-news-2006-lighting-up-etete", "sb-kidz-club-1990-field", "sb-news-2001-magic-of-christmas"]) + "".join(
    f'''<section class="section{" tint" if i % 2 else ""}"><div class="wrap">
<div class="section-head"><h2>{e(title)}</h2></div>
<div class="news-grid">{news_cards(items)}</div></div></section>''' for i, (title, items) in enumerate(NEWS)) + f"""
<section class="section"><div class="wrap"><p class="small-print">Newspaper headlines and photos are from the North Coast Courier, Stanger Weekly, North Coast Times and INHOUSE Club magazine, kept in our scrapbook. The stories above are our own short summaries. Tap a photo to see it bigger.</p></div></section>
{{LIGHTBOX}}
""".replace("{LIGHTBOX}", LIGHTBOX) + cta("Be part of the next chapter", "Thirty-six years on, there is still so much to do. Volunteer, partner with us or simply come and visit.", "WhatsApp us", "Hi, I read your story and would like to get involved.")
pages.append(("news.html", page("news.html", "Our Story in the News: Kidz Club and Breakthrough Centre since 1990",
    "Newspaper and magazine stories about Kidz Club and Breakthrough Centre in Etete, Groutville since 1999: Christmas parties for 1,500 children, national heroes awards and more.",
    news, og_image="sb-news-2006-lighting-up-etete")))

# ---------- Get involved
involved = page_head("Get involved",
    "How do you change the world? By touching one little life at a time. Everything we've done in 36 years has happened because ordinary people gave their time, skills and support.",
    ["kidz-club-juice", "heritage-day-circle", "community-outreach-crowd"]) + f"""
<section class="section"><div class="wrap">
<div class="ways">
<div><h2>Volunteer</h2><p>Volunteers make everything here run, from Sunday mornings to big events. If you have a few hours, a useful skill or simply a heart for children and families, we'd love to meet you.</p></div>
<div><h2>Partner with us</h2><p>Businesses, schools and organisations partner with us on events, contests, relief work and the Academy. Let's talk about how we can work together.</p></div>
<div><h2>Give</h2><p>Donations help us care for children and families in our community. Contact the office to find out how to give.</p></div>
<div><h2>Visit the centre</h2><p>Come and see our work for yourself at 170 Old Main Road, Etete, on the Dolphin Coast. <a href="contact.html">Get directions</a>.</p></div>
</div></div></section>
""" + cta("Get in touch", f"Call or WhatsApp {PHONE_DISPLAY} and we'll help you find the best way to be involved.", "WhatsApp us", "Hi, I would like to get involved at Breakthrough Centre.")
pages.append(("get-involved.html", page("get-involved.html", "Volunteer, partner or give | Breakthrough Centre, Groutville",
    "Volunteer, partner with us, give or visit Breakthrough Centre, a non-profit community centre in Etete, Groutville, KwaDukuza.",
    involved, og_image="kidz-club-juice")))

# ---------- Contact
contact = f"""
<section class="page-head"><div class="wrap">
<div><h1>Contact us</h1><p class="lead">We'd love to hear from you, whether you'd like to enrol your child, volunteer, partner with us or visit the centre.</p>
<div class="btn-row"><a class="btn btn-whatsapp" href="{wa()}" rel="noopener">{WA_ICON}WhatsApp {PHONE_DISPLAY}</a><a class="btn btn-ghost" href="tel:{PHONE_INTL}">Call {PHONE_DISPLAY}</a></div></div>
{mini_burst(["back-to-school-2026", "kidz-club-costumes", "wedding-canopy"])}
</div></section>
<section class="section"><div class="wrap contact-grid">
<ul class="contact-list">
<li><span class="label">Call or WhatsApp</span><a href="tel:{PHONE_INTL}">{PHONE_DISPLAY}</a></li>
<li><span class="label">Visit us</span>{ADDRESS}<br><a href="{MAPS}" rel="noopener">Open in Google Maps</a></li>
<li><span class="label">Follow us on Facebook</span><a href="{FB_CENTRE}" rel="noopener">Breakthrough Centre</a><br><a href="{FB_ACADEMY}" rel="noopener">Breakthrough Centre Academy</a></li>
<li><span class="label">Kidz Club</span>Sundays, 8 to 10am</li>
</ul>
<iframe class="map" title="Map showing Breakthrough Centre, 170 Old Main Road, Etete, Groutville" src="{MAP_EMBED}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
</div>
<div class="wrap"><p>Breakthrough Centre is a registered non-profit organisation: 081-061-NPO.</p></div></section>
"""
pages.append(("contact.html", page("contact.html", "Contact Us | Breakthrough Centre, Groutville, KwaDukuza",
    "Call or WhatsApp 081 775 1488, or visit us at 170 Old Main Road, Etete, Groutville, between KwaDukuza and Ballito. Get directions and a map.",
    contact)))

# ---------- 404
page("404.html", "Page not found | Breakthrough Centre", "This page could not be found.",
     f"""<section class="page-head"><div class="wrap"><div><h1>This page isn't here</h1>
<p class="lead">The link may be old or mistyped. Try the <a href="index.html">home page</a>, or WhatsApp us on {PHONE_DISPLAY}.</p></div></div></section>""")

# ---------- sitemap + robots
today = date.today().isoformat()
with open(os.path.join(SITE, "sitemap.xml"), "w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for path, url in pages:
        pri = "1.0" if path == "index.html" else "0.8"
        f.write(f"  <url><loc>{url}</loc><lastmod>{today}</lastmod><priority>{pri}</priority></url>\n")
    f.write("</urlset>\n")
with open(os.path.join(SITE, "robots.txt"), "w") as f:
    f.write(f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}sitemap.xml\n")
open(os.path.join(SITE, ".nojekyll"), "w").close()
print("built", len(pages) + 1, "pages")
