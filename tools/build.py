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
EMAIL = "bcacademy170@gmail.com"
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
    dict(a=104, r=690, img="graduate-certificate", label="Academy", href="academy.html",
         alt="a Breakthrough Centre Academy graduate with her certificate and trophy"),
    dict(a=88, r=760, img="kidz-club-costumes", label="Kidz Club", href="kidz-club.html",
         alt="children in costumes at Kidz Club"),
    dict(a=72, r=790, img="community-gathering", label="Community", href="community.html",
         alt="community members gathered for an outreach day"),
    dict(a=56, r=770, img="wedding-vows", label="Weddings", href="weddings.html",
         alt="a couple exchanging vows before our marriage officer"),
    dict(a=40, r=720, img="computer-class", label="Training", href="training.html",
         alt="young people learning computer skills"),
    dict(a=24, r=650, img="children-praying", label="Prayer", href="prayer.html",
         alt="children praying together"),
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
<p>{ADDRESS}<br>Call or WhatsApp <a href="tel:{PHONE_INTL}">{PHONE_DISPLAY}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></p></div></div>
<div><h2>Our work</h2><ul>
<li><a href="academy.html">Breakthrough Centre Academy</a></li><li><a href="kidz-club.html">Kidz Club</a></li>
<li><a href="community.html">Social development</a></li><li><a href="weddings.html">Marriage officer</a></li>
<li><a href="training.html">Training and development</a></li><li><a href="prayer.html">Prayer and counselling</a></li></ul></div>
<div><h2>Find us</h2><ul>
<li><a href="{FB_CENTRE}" rel="noopener">Breakthrough Centre on Facebook</a></li>
<li><a href="{FB_ACADEMY}" rel="noopener">Breakthrough Centre Academy on Facebook</a></li>
<li><a href="events.html">What's on</a></li><li><a href="get-involved.html">Get involved</a></li><li><a href="contact.html">Contact and directions</a></li></ul></div>
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
    "image": BASE_URL + "images/heritage-day-flag-wide-800.jpg",
    "description": "Community centre and early childhood development centre in Etete, Groutville, near KwaDukuza and Ballito, KwaZulu-Natal. Registered NPO 081-061-NPO.",
    "foundingDate": "1990-10-10",
    "telephone": PHONE_INTL,
    "email": EMAIL,
    "address": {"@type": "PostalAddress", "streetAddress": "170 Old Main Road, Etete", "addressLocality": "Groutville",
                "addressRegion": "KwaZulu-Natal", "addressCountry": "ZA"},
    "areaServed": ["Groutville", "KwaDukuza", "Shakaskraal", "Ballito", "iLembe District"],
    "sameAs": [FB_CENTRE, FB_ACADEMY],
}


def page(path, title, desc, body, og_image="heritage-day-flag-wide", extra_ld=None, body_class=""):
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
<meta property="og:image" content="{BASE_URL}images/{og_image}-800.jpg">
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
<h1>A preschool and community centre for Groutville and KwaDukuza</h1>
<p class="lead">Since 1990 we've been a safe, hopeful place for the children and families of Etete. Little ones learn to read and count at our Academy, children come together every Sunday at Kidz Club, and families across KwaDukuza and the North Coast find a helping hand when they need it.</p>
<div class="btn-row"><a class="btn btn-whatsapp" href="{wa()}" rel="noopener">{WA_ICON}WhatsApp {PHONE_DISPLAY}</a><a class="btn btn-ghost" href="about.html">Our story</a></div>
</div>
<div class="burst-wrap">{home_burst()}</div>
</div></section>

<section class="section tint"><div class="wrap split">
<div>
<h2>It started with a children's club</h2>
<p>On 10 October 1990 a handful of children met in a borrowed classroom in Etete. That club never stopped. It moved into a small house, then a tent, and today it's a full community centre with its own preschool, Breakthrough Centre Academy, where children from the age of two learn to read, count and speak up with confidence.</p>
<p>We're a registered non-profit organisation (081-061-NPO) in Groutville, between KwaDukuza (Stanger) and Ballito, and we serve families right across the iLembe District. What drives us hasn't changed in 36 years: helping people of every age reach their God-given potential.</p>
<p><a href="about.html">Read our story</a></p>
</div>
{photo("graduation-class", "Breakthrough Centre Academy graduates in caps and gowns with their teachers, Groutville")}
</div></section>

<section class="section"><div class="wrap">
<div class="pillars">
<div><h2>Our vision</h2><ul>
<li>A transformed city, empowered communities and an educated next generation.</li>
<li>Young people trained, nurtured and developed to be responsible in their schools, communities and workplaces.</li>
<li>"A new breed without greed": a generation living with righteousness and integrity.</li>
<li>A strategic response to poverty, crime, HIV/Aids and today's challenges.</li></ul></div>
<div><h2>Our mission</h2><ul>
<li>Reduce the effects of crime and poverty through empowerment, social development and life skills.</li>
<li>Provide a caring, supportive and safe environment for children and youth.</li>
<li>Run awareness and support programmes that meet present-day challenges.</li>
<li>Effect lasting change in lifestyles through ongoing training and mentoring.</li></ul></div>
<div><h2>Our values</h2><p>Everyone who serves at Breakthrough Centre commits to:</p>
<ul class="values"><li>Honesty</li><li>Integrity</li><li>Respect</li><li>Dedication</li><li>Excellence</li><li>Accountability</li><li>Non-discrimination</li></ul></div>
</div></div></section>

<section class="section olive"><div class="wrap">
<div class="section-head"><h2>How we can help you</h2><p class="lead">A preschool, a Sunday club, community projects, weddings, training and a listening ear, all at one address in Etete.</p></div>
<div class="services">
<article class="service"><div class="photo">{pic("preschool-classroom", "Learners at their tables in a Breakthrough Centre Academy classroom", sizes="(max-width: 560px) 100vw, 33vw")}</div>
<h3><a href="academy.html">Preschool: Breakthrough Centre Academy</a></h3><p>An ECD centre in Groutville since 2005. Your child learns Maths, Science, Languages and Life Skills, and starts reading with our "I can read" programme.</p></article>
<article class="service"><div class="photo">{pic("kidz-club-juice", "A volunteer pouring juice for children at Kidz Club", sizes="(max-width: 560px) 100vw, 33vw")}</div>
<h3><a href="kidz-club.html">Sunday Kidz Club</a></h3><p>Every Sunday from 8 to 10am. Games, stories, care and a lot of encouragement, with Larry the puppet never far away.</p></article>
<article class="service"><div class="photo">{pic("community-outreach-crowd", "Hundreds of children at a Breakthrough Centre outreach", sizes="(max-width: 560px) 100vw, 33vw")}</div>
<h3><a href="community.html">Community projects</a></h3><p>School contests, our yearly Child Protection event, Jumpstart work readiness for young people, food hampers and hot meals.</p></article>
<article class="service"><div class="photo">{pic("wedding-beach-setup", "A beach wedding set up on the Dolphin Coast", sizes="(max-width: 560px) 100vw, 33vw")}</div>
<h3><a href="weddings.html">Weddings and marriage officer</a></h3><p>A personal ceremony on the beach, in a hall or wherever you choose, and we register your marriage with Home Affairs.</p></article>
<article class="service"><div class="photo">{pic("computer-class", "Young people learning computer skills at Breakthrough Centre", sizes="(max-width: 560px) 100vw, 33vw")}</div>
<h3><a href="training.html">Workshops and training</a></h3><p>Practical workshops, leadership and mentoring for parents, teachers, young people and community groups.</p></article>
<article class="service"><div class="photo">{pic("children-praying", "Children praying together at Breakthrough Centre", sizes="(max-width: 560px) 100vw, 33vw")}</div>
<h3><a href="prayer.html">Prayer and counselling</a></h3><p>Going through something hard? Talk to someone who will listen, pray with you and walk with you.</p></article>
</div></div></section>

<section class="section night"><div class="wrap split">
<div><p class="motto">How do you change the world?</p>
<p>By touching one little life at a time. Give an hour, share a skill, partner with us or simply come and visit. There's a place for you here.</p>
<div class="btn-row"><a class="btn btn-whatsapp" href="{wa('Hi Breakthrough Centre, I would like to get involved.')}" rel="noopener">{WA_ICON}WhatsApp us</a><a class="btn btn-ghost" style="color:#fff;border-color:#fff" href="get-involved.html">Ways to help</a></div></div>
{photo("heritage-day-flag", "Academy learners in traditional dress around a South African flag on Heritage Day", "wide")}
</div></section>
"""
pages.append(("index.html", page("index.html",
    "Preschool and Community Centre in Groutville | Breakthrough Centre",
    "Non-profit preschool and community centre in Groutville, near KwaDukuza (Stanger) and Ballito. Our Academy, Sunday Kidz Club and outreach have served families since 1990.",
    home + HOME_FAQ[0], extra_ld=HOME_FAQ[1])))

# ---------- About
about = page_head("Our story",
    "Breakthrough Centre began on 10 October 1990 as the first community-based project in Etete, Groutville. Thirty-six years on, it's a busy community centre with a special heart for young children.",
    ["heritage-day-circle", "graduation-class", "community-gathering"]) + f"""
<section class="section"><div class="wrap split top">
<div class="measure">
<h2>A positive place to be</h2>
<p>We started with one simple idea: children and young people need a good place to be, away from the problems on the streets around them. Give them that, plus people who believe in them, and they can rise above hard circumstances.</p>
<p>The children kept coming, so the club kept moving. From a borrowed classroom to a small house, from the house to a tent, and finally into the community centre we have today, open to people of every age and background.</p>
</div>
<div>
<h2>Milestones</h2>
<ol class="timeline">
<li><span class="year">1990</span>A children's club starts on 10 October in borrowed space at a local school.</li>
<li><span class="year">2005</span>Breakthrough Centre Academy opens in a small house with just 4 learners.</li>
<li><span class="year">2018</span>Members of Parliament visit the centre on 28 March, focusing on early childhood and youth development.</li>
<li><span class="year">2021</span>We distribute baby formula from Durban to Tugela during the KZN unrest, and are awarded the lease of a brand-new community crèche and pre-school in Shakaskraal.</li>
<li><span class="year">2026</span>We celebrate 36 years of God's amazing grace.</li>
</ol></div>
</div></section>

<section class="section tint"><div class="wrap split top">
<div><h2>Leadership and governance</h2>
<p>Breakthrough Centre was founded by Ps. Trevor and Jessica Nair. An Executive Committee steers the organisation, sub-committees run each department and report back to it, and a team of volunteers keeps every programme, event and project running smoothly.</p></div>
<div><h3>Executive Committee</h3>
<ul class="people">
<li><strong>Mr P. Nair</strong>Full-time Manager, Breakthrough Centre</li>
<li><strong>Mrs S. Nair</strong>Departmental Head, Department of Education</li>
<li><strong>Mrs A.S. Gwamanda</strong>Senior Administration Clerk, Department of Education</li>
<li><strong>Mrs V. Govindasamy</strong>Night Manager, Alberlito Hospital</li>
<li><strong>Ms Tamsyn Jeiel</strong>Projects Manager</li></ul></div>
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
<div><h3>Awards</h3><ul class="awards">
<li>1st place, KwaDukuza Municipality Mayoral Awards for Community Development</li>
<li>Nedbank Heroes Award</li>
<li>Lubners "Inhouse Club" National Heroes Award</li>
<li>2nd place, Sugar Rush Big 5, Community category</li>
<li>Jet Club Icon</li></ul>
{photo("graduation-class", "Breakthrough Centre Academy graduation with teachers and learners holding certificates", "wide")}</div>
</div></div></section>
""" + cta("Come and see our work", "Visit the centre at 170 Old Main Road, Etete, or send us a message.")
pages.append(("about.html", page("about.html", "Our Story: 36 Years in Groutville | Breakthrough Centre",
    "How a children's club in Etete, Groutville grew into a community centre and preschool. Our story since 1990, our leaders and the awards we've received.", about)))

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
    ["graduate-certificate", "heritage-day-flag", "back-to-school"],
    f'<div class="btn-row"><a class="btn btn-whatsapp" href="{wa(ac_msg)}" rel="noopener">{WA_ICON}Ask about places</a></div>') + f"""
<section class="section"><div class="wrap split">
<div class="measure">
<h2>We don't lower the bar</h2>
<p>We opened in 2005 in a small house with four learners. We've grown quickly since then for one reason: we refuse to lower our standards. You can't lower the bar and expect excellent results, and the start a child gets here stays with them for life.</p>
<p>Every child follows a structured programme in Maths, Science, Languages and Life Skills. Even our two-year-olds are building their vocabulary and learning the first steps of reading and writing. Along the way we teach good manners, respect for others and healthy eating habits.</p>
<p>In 2021 we were also awarded the lease of a brand-new community-based crèche and pre-school in Shakaskraal.</p>
</div>
{photo("preschool-classroom", "Learners working at colourful tables in a Breakthrough Centre Academy classroom", "tall")}
</div></section>

<section class="section tint"><div class="wrap split">
<div class="bubble"><h2>"I can read"</h2>
<p><em>I can read</em> is a manual that builds sound reading patterns in young learners, so they have the literacy skills they need for future learning. It is part of every child's curriculum, and learners on the programme have astounded their teachers with their reading levels.</p></div>
<div class="measure"><h2>Reading, speaking and growing in confidence</h2>
<p>Poor literacy is a national concern. Our Literacy and Language Development programme has become a model for strong results in foundational reading, mathematics and public speaking, and our learners leave with confidence and healthy self-esteem.</p></div>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><h2>Dressed up for Valentine's Day 2026</h2><p class="lead">Our learners love a reason to celebrate, from Heritage Day to the end-of-year function.</p></div>
<div class="prints">
<figure class="print">{pic("valentines-boy", "Academy learner in a white shirt on Valentine's Day 2026", sizes="(max-width: 820px) 50vw, 20vw")}<figcaption>Ready for the party</figcaption></figure>
<figure class="print">{pic("valentines-girl", "Academy learner dressed in red on Valentine's Day 2026", sizes="(max-width: 820px) 50vw, 20vw")}<figcaption>Dressed up in red</figcaption></figure>
<figure class="print">{pic("valentines-red-dress", "Smiling Academy learner in a red dress and flower crown", sizes="(max-width: 820px) 50vw, 20vw")}<figcaption>Feeling special</figcaption></figure>
<figure class="print">{pic("valentines-smile", "Happy Academy learner smiling on Valentine's Day 2026", sizes="(max-width: 820px) 50vw, 20vw")}<figcaption>All smiles</figcaption></figure>
<figure class="print">{pic("valentines-balloon", "Academy learner holding an I love you balloon", sizes="(max-width: 820px) 50vw, 20vw")}<figcaption>Lots of love</figcaption></figure>
</div></div></section>

<section class="section olive"><div class="wrap split">
<div><h2>Parents as partners</h2>
<p>You're part of the team. Every term we hold parent meetings where you can see your child's progress and get to know the teachers, plus free workshops on how to help your child do their best at home.</p>
<h2>Time to shine</h2>
<p>Every learner gets a turn on stage at our Annual Concert and Graduation: speaking, storytelling, dancing, acting and singing in front of a proud crowd.</p></div>
{photo("graduate-certificate", "Academy graduate in cap and gown with her certificate and trophy", "tall")}
</div></section>
""" + cta("Enrol your child", f"We'd love to welcome your family. WhatsApp {PHONE_DISPLAY} to find out about places and registration.", "WhatsApp about places", ac_msg)
pages.append(("academy.html", page("academy.html",
    "Preschool in Groutville, KwaDukuza | Breakthrough Centre Academy",
    "Looking for a preschool near KwaDukuza, Shakaskraal or Ballito? Our Groutville Academy helps children from age two read, count and speak with confidence.",
    academy + ACADEMY_FAQ[0], og_image="graduation-class", body_class="playful",
    extra_ld=[{"@context": "https://schema.org", "@type": "Preschool", "name": "Breakthrough Centre Academy",
              "url": BASE_URL + "academy.html", "telephone": PHONE_INTL, "foundingDate": "2005",
              "address": ORG_LD["address"], "parentOrganization": {"@id": BASE_URL + "#organization"},
              "sameAs": [FB_ACADEMY]}, ACADEMY_FAQ[1]])))

# ---------- Kidz Club (playful)
kidz = page_head("Kidz Club",
    "Every Sunday morning from 8 to 10, children from Etete, Groutville and around KwaDukuza come together for fun, friendship and a lot of encouragement.",
    ["kidz-club-costumes", "kidz-club-juice", "kidz-club-meal"]) + f"""
<section class="section"><div class="wrap split">
<div><p class="big-time">Sundays<br>8 to 10am</p>
<p class="lead">At Breakthrough Centre, 170 Old Main Road, Etete. All children in our community are welcome.</p>
<p>This is where Breakthrough Centre began in 1990: a children's club that gave young people somewhere good to be. Thirty-six years later, Sunday mornings are still the heartbeat of the centre.</p></div>
{photo("kidz-club-sunday", "Children and young people at Sunday Kidz Club in Groutville", "wide")}
</div></section>

<section class="section tint"><div class="wrap split">
<div class="bubble"><h2>Meet Larry!</h2>
<p>Larry the puppet is Kidz Club's favourite character. When Covid-19 closed our doors for a while, Larry kept the children learning with daily programmes on Ballito TV. Search for the Laugh Out Larry Show on YouTube to watch the episodes.</p></div>
{photo("kidz-club-meal", "Young children sharing a meal at Kidz Club", "wide")}
</div></section>
""" + cta("Come and join us", f"Questions about Kidz Club? Call or WhatsApp {PHONE_DISPLAY}.", "WhatsApp us", "Hi, I have a question about Sunday Kidz Club.")
pages.append(("kidz-club.html", page("kidz-club.html", "Sunday Kidz Club in Groutville, KwaDukuza | Breakthrough Centre",
    "Looking for something for your children on a Sunday? Kidz Club meets every Sunday from 8 to 10am at Breakthrough Centre, Etete, Groutville. Home of Larry the puppet.",
    kidz, og_image="kidz-club-costumes", body_class="playful",
    extra_ld={"@context": "https://schema.org", "@type": "Event", "name": "Sunday Kidz Club",
              "eventSchedule": {"@type": "Schedule", "byDay": "https://schema.org/Sunday", "startTime": "08:00", "endTime": "10:00",
                                "repeatFrequency": "P1W", "scheduleTimezone": "Africa/Johannesburg"},
              "location": {"@type": "Place", "name": "Breakthrough Centre", "address": ORG_LD["address"]},
              "organizer": {"@id": BASE_URL + "#organization"}})))

# ---------- Community / social development
community = page_head("Community projects",
    "Beyond the Academy we work alongside local schools, young people and families across KwaDukuza and the iLembe District, through contests, campaigns, training and practical help.",
    ["community-gathering", "community-outreach-crowd", "kidz-club-juice"]) + f"""
<section class="section"><div class="wrap split top">
<div class="measure">
<h2>Investing in local schools</h2>
<p>Tomorrow's leaders are sitting in today's classrooms, so we invest in local public schools. Our programmes bring teachers, parents, officials and everyone with a stake in education around the same table.</p>
<h2>Potential Unleashed: contests and performances</h2>
<p>Our inter-school contests in art, poetry and talent help young people find out what they're good at. Children get a stage, an audience and skills that can shape their future. Even during the pandemic we kept the contests going online.</p>
<h2>Annual Child Protection Event</h2>
<p>Every year local schools and organisations join us to stand together against child abuse, domestic violence and human trafficking. Our own Academy learners lead the Every Child Has a Voice campaign and carry its message to the community.</p>
</div>
{photo("kidz-club-costumes", "Children in costumes waving South African flags at a community event", "tall")}
</div></section>

<section class="section olive"><div class="wrap split">
{photo("community-gathering", "Community members gathered outside Breakthrough Centre for an outreach day", "wide")}
<div><h2>Jumpstart and relief work</h2>
<p>The Jumpstart Programme prepares young people for the world of work.</p>
<ul class="checklist">
<li><strong>Baby formula distribution:</strong> during the 2021 unrest in KZN, we were entrusted with distributing baby formula from Durban to Tugela, so vulnerable families were cared for.</li>
<li><strong>Food hampers:</strong> regular distributions to families in need.</li>
<li><strong>Hot meals:</strong> hot meal distribution in the community.</li>
<li><strong>Christmas outreach:</strong> bringing Christmas cheer to children at a local school.</li></ul></div>
</div></section>
""" + cta("Partner with us", "Schools, businesses and organisations work with us on contests, events and relief. Let's talk.", "WhatsApp us", "Hi, I would like to partner with Breakthrough Centre.")
pages.append(("community.html", page("community.html", "Community Projects in KwaDukuza and iLembe | Breakthrough Centre",
    "School programmes, inter-school contests, a yearly Child Protection event, Jumpstart work readiness, food hampers and hot meals across KwaDukuza and iLembe.",
    community, og_image="community-gathering")))

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
    "wedding-canopy": "Couple at an evening wedding ceremony under a floral canopy",
    "wedding-vows": "Bride and groom exchanging vows before the Breakthrough Centre marriage officer",
    "wedding-beach-setup": "Beach wedding set up with white chairs and a decorated arch overlooking the sea",
    "wedding-bride-vows": "Bride saying her vows at a ceremony led by our marriage officer",
    "wedding-beach-guests": "Guests seated at a beach wedding on the Dolphin Coast",
    "wedding-reception-table": "Wedding reception table decorated with flowers and fairy lights",
    "wedding-family": "Couple and family at a wedding ceremony",
    "wedding-cake": "Bride and groom cutting their wedding cake",
    "wedding-napkin": "Mr and Mrs wedding napkin with a gold spoon",
    "wedding-reception-hall": "Wedding reception hall with purple lighting",
    "wedding-cake-family": "Newlyweds cutting the cake with family",
    "wedding-coastal-path": "Coastal path leading down to a beach wedding venue",
}
gallery = "".join(
    f'<button type="button" data-full="images/{g}-{1600 if os.path.exists(os.path.join(SITE, "images", g + "-1600.webp")) else 800}.webp">'
    f'{pic(g, gal_alt[g], sizes="(max-width: 600px) 100vw, 33vw")}</button>' for g in gal)
weddings = page_head("Marriage officer",
    "Getting married in KwaDukuza, Ballito or anywhere on the Dolphin Coast? We'll make your ceremony personal and meaningful, traditional or not, and handle the registration at Home Affairs.",
    ["wedding-vows", "wedding-canopy", "wedding-beach-setup"],
    f'<div class="btn-row"><a class="btn btn-whatsapp" href="{wa("Hi, I would like to book the marriage officer.")}" rel="noopener">{WA_ICON}Book your ceremony</a></div>') + f"""
<section class="section"><div class="wrap">
<div class="section-head"><h2>Your love story, your way</h2><p class="lead">We sit down with you, get to know your story and shape a ceremony that feels like you, whether it's barefoot on the beach or an evening celebration in a hall.</p></div>
<div class="gallery">{gallery}</div>
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
    ["computer-class", "preschool-classroom", "graduation-class"]) + f"""
<section class="section"><div class="wrap split">
<div class="measure"><h2>Equipping people to thrive</h2>
<p>Good intentions go further with the right skills. Through workshops, mentoring and one-on-one time, we give people practical tools they can use straight away at school, at work, at home and in their community.</p>
<h3>What we offer</h3>
<ul class="checklist"><li>Workshops for educators, parents and community groups</li><li>Leadership and mentoring programmes</li>
<li>Jumpstart work-readiness training for young people</li><li>Free parent workshops at Breakthrough Centre Academy</li></ul></div>
{photo("computer-class", "Young people learning computer skills at Breakthrough Centre", "wide")}
</div></section>
""" + cta("Book a workshop", f"To arrange training for your school, organisation or group, call or WhatsApp {PHONE_DISPLAY}, or email <a href=\"mailto:{EMAIL}\" style=\"color:#fff\">{EMAIL}</a>.", "WhatsApp us", "Hi, I would like to book a workshop.")
pages.append(("training.html", page("training.html", "Workshops and Mentoring in KwaDukuza | Breakthrough Centre",
    "Workshops for educators, parents and community groups, leadership and mentoring programmes and Jumpstart work-readiness training at Breakthrough Centre, Groutville.",
    training, og_image="computer-class")))

# ---------- Prayer
prayer = page_head("Prayer and counselling",
    "Going through something hard? You don't have to face it alone. Come and be heard, in a safe and caring place in Groutville.",
    ["children-praying", "heritage-day-circle", "community-gathering"]) + f"""
<section class="section"><div class="wrap split">
<div class="measure"><h2>Walking with you</h2>
<p>Grief, family strain, worry about the future: whatever you're carrying, we'll listen without judging. We pray with you, offer personal guidance and walk with you and your family through the hard seasons, with faith, hope and resilience.</p>
<p>If you would like prayer, or would like to speak to someone, call or WhatsApp {PHONE_DISPLAY}, or email <a href="mailto:{EMAIL}">{EMAIL}</a>, and we'll arrange a time to meet.</p></div>
{photo("children-praying", "Children praying together at Breakthrough Centre in Groutville", "wide")}
</div></section>
""" + cta("Reach out", "Send us a message and we'll arrange a time to meet.", "WhatsApp us", "Hi, I would like to speak to someone for prayer or counselling.")
pages.append(("prayer.html", page("prayer.html", "Prayer and counselling in Groutville | Breakthrough Centre",
    "A safe, caring space for prayer, spiritual growth and emotional healing at Breakthrough Centre in Etete, Groutville. Call or WhatsApp 081 775 1488.",
    prayer, og_image="children-praying")))

# ---------- Events
events = page_head("What's on",
    "There's always something happening at the centre. Here's what comes around each year. For exact dates, follow us on Facebook.",
    ["valentines-red-dress", "heritage-day-flag", "graduation-class"]) + f"""
<section class="section"><div class="wrap">
<ul class="events">
<li><h3>Kidz Club</h3><p>Every Sunday, 8 to 10am.</p></li>
<li><h3>Annual Concert and Graduation</h3><p>Every Academy learner on stage, with public speaking, storytelling, dance, drama and singing.</p></li>
<li><h3>Annual Child Protection Event</h3><p>Schools and organisations standing together against child abuse, domestic violence and human trafficking.</p></li>
<li><h3>Potential Unleashed contests</h3><p>Inter-school contests in art, poetry and talent.</p></li>
<li><h3>Parent meetings and workshops</h3><p>Held every term at the Academy.</p></li>
<li><h3>Christmas outreach</h3><p>Bringing Christmas cheer to children at a local school.</p></li>
</ul>
<div class="btn-row"><a class="btn btn-ghost" href="{FB_CENTRE}" rel="noopener">Breakthrough Centre on Facebook</a><a class="btn btn-ghost" href="{FB_ACADEMY}" rel="noopener">Academy on Facebook</a></div>
</div></section>
""" + cta("Want to be part of an event?", "We welcome volunteers, sponsors and partner schools.", "WhatsApp us", "Hi, I would like to help with an event.")
pages.append(("events.html", page("events.html", "Events in Groutville: Kidz Club, Graduation and More | Breakthrough Centre",
    "What's on at Breakthrough Centre, Groutville: Sunday Kidz Club, our Concert and Graduation, the Child Protection event, school contests and Christmas outreach.",
    events, og_image="valentines-red-dress")))

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
""" + cta("Get in touch", f"Call or WhatsApp {PHONE_DISPLAY}, or email <a href=\"mailto:{EMAIL}\" style=\"color:#fff\">{EMAIL}</a>, and we'll help you find the best way to be involved.", "WhatsApp us", "Hi, I would like to get involved at Breakthrough Centre.")
pages.append(("get-involved.html", page("get-involved.html", "Volunteer, partner or give | Breakthrough Centre, Groutville",
    "Volunteer, partner with us, give or visit Breakthrough Centre, a non-profit community centre in Etete, Groutville, KwaDukuza.",
    involved, og_image="kidz-club-juice")))

# ---------- Contact
contact = f"""
<section class="page-head"><div class="wrap">
<div><h1>Contact us</h1><p class="lead">We'd love to hear from you, whether you'd like to enrol your child, volunteer, partner with us or visit the centre.</p>
<div class="btn-row"><a class="btn btn-whatsapp" href="{wa()}" rel="noopener">{WA_ICON}WhatsApp {PHONE_DISPLAY}</a><a class="btn btn-ghost" href="tel:{PHONE_INTL}">Call {PHONE_DISPLAY}</a></div></div>
{mini_burst(["heritage-day-circle", "kidz-club-costumes", "wedding-canopy"])}
</div></section>
<section class="section"><div class="wrap contact-grid">
<ul class="contact-list">
<li><span class="label">Call or WhatsApp</span><a href="tel:{PHONE_INTL}">{PHONE_DISPLAY}</a></li>
<li><span class="label">Visit us</span>{ADDRESS}<br><a href="{MAPS}" rel="noopener">Open in Google Maps</a></li>
<li><span class="label">Email us</span><a href="mailto:{EMAIL}">{EMAIL}</a></li>
<li><span class="label">Follow us on Facebook</span><a href="{FB_CENTRE}" rel="noopener">Breakthrough Centre</a><br><a href="{FB_ACADEMY}" rel="noopener">Breakthrough Centre Academy</a></li>
<li><span class="label">Kidz Club</span>Sundays, 8 to 10am</li>
</ul>
<iframe class="map" title="Map showing Breakthrough Centre, 170 Old Main Road, Etete, Groutville" src="{MAP_EMBED}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
</div>
<div class="wrap"><p>Breakthrough Centre is a registered non-profit organisation: 081-061-NPO.</p></div></section>
"""
pages.append(("contact.html", page("contact.html", "Contact Us | Breakthrough Centre, Groutville, KwaDukuza",
    "Call or WhatsApp 081 775 1488, email bcacademy170@gmail.com, or visit us at 170 Old Main Road, Etete, Groutville, between KwaDukuza and Ballito.",
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
