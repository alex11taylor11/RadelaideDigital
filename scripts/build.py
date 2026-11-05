"""Builds the Radelaide.Digital website from data/stories.json.

Run from the repository root:  python3 scripts/build.py
Only stories from the last 3 months (92 days) are shown, newest first.
Set BUILD_DATE=YYYY-MM-DD to pretend "today" is a different day.
"""
import datetime as dt
import html
import json
import os
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WINDOW_DAYS = 92
SITE = "Radelaide.Digital"
TAGLINE = "Tech news from the Festival State."

CATS = [
    ("government", "Government", "Government Services",
     "How the SA public sector is going digital: online services, AI policy, cyber and the money behind it.", "#00e5ff"),
    ("health", "Health", "Digital Health",
     "Electronic medical records, virtual care and the systems behind SA hospitals and ambulances.", "#ff3df2"),
    ("education", "Education", "Education & Skills",
     "AI in classrooms, school digital strategy and building a digitally skilled workforce.", "#c6ff00"),
    ("business", "Business", "Business & Industry",
     "Programs, grants and advice helping South Australian businesses go digital.", "#ffb300"),
    ("cities", "Smart Cities", "Smart Cities & Data",
     "Digital twins, sensors and data projects reshaping how Adelaide's councils work.", "#4dffb8"),
]
CAT = {c[0]: c for c in CATS}
PHOTOS, BANNER = {}, None
e = html.escape


def today():
    if os.environ.get("BUILD_DATE"):
        return dt.date.fromisoformat(os.environ["BUILD_DATE"])
    return dt.datetime.now(ZoneInfo("Australia/Adelaide")).date()


def nice(d):
    return f"{d.day} {d.strftime('%b %Y')}"


def load(now):
    with open(os.path.join(ROOT, "data", "stories.json")) as f:
        stories = json.load(f)
    cutoff = now - dt.timedelta(days=WINDOW_DAYS)
    out = []
    for s in stories:
        if s["category"] not in CAT:
            raise SystemExit(f"Unknown category {s['category']!r} in: {s['headline']}")
        d = dt.date.fromisoformat(s["date"])
        if cutoff <= d <= now:
            s["_d"] = d
            s["_label"] = s.get("date_label") or nice(d)
            out.append(s)
    out.sort(key=lambda s: s["_d"], reverse=True)
    return stories, out


def load_photos():
    with open(os.path.join(ROOT, "data", "photos.json")) as f:
        return {p["id"]: p for p in json.load(f)}


def assign_photos(all_stories, shown, photos):
    """Give every shown story its own photo; never show the same photo twice.

    Stories keep a photo once given one (saved back to stories.json). A story
    without a photo gets the first unused photo from its category's pool; if the
    pool is used up it is shown without a picture rather than repeating one.
    Returns the set of photo ids used on the site.
    """
    used = {pid for pid, p in photos.items() if p["category"] == "banner"}
    changed = False
    for s in sorted(shown, key=lambda s: s["_d"]):  # older stories keep priority
        pid = s.get("photo")
        if pid and (pid not in photos or pid in used):
            print(f"WARNING: photo {pid!r} for '{s['headline']}' is unknown or already used; reassigning.")
            pid = None
        if not pid:
            pid = next((i for i, p in photos.items() if p["category"] == s["category"] and i not in used), None)
            if pid:
                s["photo"] = pid
            else:
                s.pop("photo", None)
                print(f"NOTE: no unused {s['category']} photo left for '{s['headline']}'; showing it without a picture.")
            changed = True
        if pid:
            used.add(pid)
    if changed:
        clean = [{k: v for k, v in s.items() if not k.startswith("_")} for s in all_stories]
        with open(os.path.join(ROOT, "data", "stories.json"), "w") as f:
            json.dump(clean, f, indent=2, ensure_ascii=False)
            f.write("\n")
    return used


def credit(p):
    lic = f'<a href="{e(p["license_url"])}" target="_blank" rel="noopener">{e(p["license"])}</a>' if p.get("license_url") else e(p["license"])
    return f'Photo: <a href="{e(p["page"])}" target="_blank" rel="noopener">{e(p["author"])}</a>, {lic}'


def nav(active):
    links = ['<a href="index.html"%s>Front Page</a>' % (' aria-current="page"' if active == "home" else "")]
    for slug, short, *_ in CATS:
        cur = ' aria-current="page"' if active == slug else ""
        links.append(f'<a href="{slug}.html"{cur}>{e(short)}</a>')
    return "\n        ".join(links)


def card(s, big=False):
    c = CAT[s["category"]]
    url = e(s["url"])
    p = PHOTOS.get(s.get("photo"))
    art = ""
    if p:
        art = f"""<figure class="card__art">
          <a href="{url}" target="_blank" rel="noopener" tabindex="-1"><img src="{e(p['file'])}" alt="{e(p['alt'])}" loading="lazy" width="960" height="540"></a>
          <figcaption>{credit(p)}</figcaption>
        </figure>"""
    return f"""<article class="card{' card--big' if big else ''}{'' if p else ' card--noimg'}" style="--accent:{c[4]}">
        {art}
        <div class="card__meta"><a class="tag" href="{c[0]}.html">{e(c[1])}</a><time datetime="{s['date']}">{e(s['_label'])}</time></div>
        <h3><a href="{url}" target="_blank" rel="noopener">{e(s['headline'])}</a></h3>
        <p>{e(s['summary'])}</p>
        <a class="src" href="{url}" target="_blank" rel="noopener">Read at {e(s['source'])} &#8599;</a>
      </article>"""


EMPTY = '<p class="empty">No new stories on this desk in the last three months. Check back soon.</p>'

TICKER = "".join(f"<span>{t}</span>" for t in [
    "RADELAIDE.DIGITAL", "GOVERNMENT", "HEALTH", "EDUCATION", "BUSINESS", "SMART CITIES",
    "TECH NEWS FROM THE FESTIVAL STATE"])

LOGO = '<span class="logo__name">Radelaide</span><span class="logo__hi">.Digital</span>'


def page(active, title, desc, body, updated):
    full = SITE if active == "home" else f"{title} | {SITE}"
    return f"""<!doctype html>
<html lang="en-AU">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(full)}</title>
  <meta name="description" content="{e(desc)}">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%230a0b0f'/><text x='16' y='23' font-family='monospace' font-size='18' font-weight='700' text-anchor='middle' fill='%23c6ff00'>R.</text></svg>">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <div class="ticker" aria-hidden="true"><div class="ticker__track">
    {TICKER}
    {TICKER}
  </div></div>
  <header class="masthead">
    <div class="wrap masthead__inner">
      <a class="logo" href="index.html">{LOGO}</a>
      <p class="motto">{e(TAGLINE)}</p>
    </div>
    <nav class="wrap nav" aria-label="Sections">
        {nav(active)}
    </nav>
  </header>
  <main class="wrap">
{body}
  </main>
  <footer class="footer">
    <div class="wrap">
      <p class="logo logo--sm">{LOGO}</p>
      <p>An independent roundup of digital transformation news from Adelaide and South Australia. We show stories from the last three months, newest first. Each story is a short summary that links to the original reporting. Read the source for full details. Not affiliated with any organisation mentioned.</p>
      <p class="mono">Last updated {nice(updated)} &middot; <a href="credits.html">Photo credits</a></p>
    </div>
  </footer>
</body>
</html>
"""


def home(stories, updated):
    if not stories:
        body = f'    <section class="cat-head"><h1>Quiet news day</h1>{EMPTY}</section>'
        return page("home", SITE, TAGLINE, body, updated)
    lead, latest = stories[0], stories[1:7]
    sections = []
    for slug, short, name, blurb, color in CATS:
        items = [s for s in stories if s["category"] == slug][:3]
        lis = "\n".join(
            f'<li><a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["headline"])}</a><span>{e(s["_label"])}</span></li>'
            for s in items) or f"<li>{EMPTY}</li>"
        sections.append(f"""      <section class="desk" style="--accent:{color}">
        <a class="desk__art" href="{slug}.html" tabindex="-1" aria-hidden="true"><img src="images/{slug}.svg" alt="" loading="lazy" width="400" height="225"></a>
        <h3><a href="{slug}.html">{e(name)} <span aria-hidden="true">&#8594;</span></a></h3>
        <p>{e(blurb)}</p>
        <ul>{lis}</ul>
      </section>""")
    latest_html = ""
    if latest:
        latest_html = f"""    <h2 class="section-title"><span>Latest wire</span></h2>
    <div class="grid">
      {"".join(card(s) for s in latest)}
    </div>
"""
    body = f"""    <div class="banner">
      <img src="{e(BANNER['file'])}" alt="{e(BANNER['alt'])}" width="960" height="540">
      <p class="banner__text">Digital transformation news from <span>the Festival State</span></p>
      <p class="banner__credit">{credit(BANNER)}</p>
    </div>
    <section class="hero">
      <p class="kicker mono">// Top story</p>
      {card(lead, big=True)}
      <aside class="hero__side">
        <p class="kicker mono">// The last 3 months</p>
        <p class="big-stat">{len(stories)}</p>
        <p>digital transformation stories from across South Australia, newest first and refreshed every morning.</p>
      </aside>
    </section>
{latest_html}    <h2 class="section-title"><span>The desks</span></h2>
    <div class="desks">
{chr(10).join(sections)}
    </div>"""
    return page("home", SITE, "Digital transformation news from Adelaide and South Australia: government services, health, education, business and smart cities.", body, updated)


def category(slug, stories, updated):
    _, short, name, blurb, color = CAT[slug]
    items = [s for s in stories if s["category"] == slug]
    grid = f'<div class="grid">\n      {"".join(card(s) for s in items)}\n    </div>' if items else EMPTY
    body = f"""    <section class="cat-head" style="--accent:{color}">
      <div>
        <p class="kicker mono">// Desk</p>
        <h1>{e(name)}</h1>
        <p>{e(blurb)}</p>
      </div>
      <img class="cat-head__art" src="images/{slug}.svg" alt="" width="400" height="225">
    </section>
    {grid}"""
    return page(slug, name, f"{name} news from Adelaide and South Australia. {blurb}", body, updated)


def credits_page(used, updated):
    rows = "\n".join(
        f"""      <li><img src="{e(p['file'])}" alt="" loading="lazy" width="160" height="90"><div><strong>{e(p['alt'])}</strong><br>{credit(p)}<br><span class="mono">{e(p['title'])}</span></div></li>"""
        for i, p in PHOTOS.items() if i in used)
    body = f"""    <section class="cat-head" style="--accent:#c6ff00">
      <div>
        <p class="kicker mono">// About</p>
        <h1>Photo credits</h1>
        <p>Photos are from Wikimedia Commons and used under the licences shown. Thank you to the photographers. Illustrations are original to this site.</p>
      </div>
    </section>
    <ul class="credits">
{rows}
    </ul>"""
    return page("credits", "Photo credits", "Photo credits for Radelaide.Digital.", body, updated)


def main():
    global PHOTOS, BANNER
    now = today()
    all_stories, stories = load(now)
    PHOTOS = load_photos()
    BANNER = next(p for p in PHOTOS.values() if p["category"] == "banner")
    used = assign_photos(all_stories, stories, PHOTOS)
    with open(os.path.join(ROOT, "credits.html"), "w") as f:
        f.write(credits_page(used, now))
    with open(os.path.join(ROOT, "index.html"), "w") as f:
        f.write(home(stories, now))
    for slug, *_ in CATS:
        with open(os.path.join(ROOT, f"{slug}.html"), "w") as f:
            f.write(category(slug, stories, now))
    print(f"Built {len(CATS) + 1} pages with {len(stories)} stories (window from {now - dt.timedelta(days=WINDOW_DAYS)} to {now}).")


if __name__ == "__main__":
    main()
