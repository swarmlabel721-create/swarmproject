#!/usr/bin/env python3
"""TOM TED TOD static site builder.

content/*.json を読み、dist/ に静的HTMLを書き出す。外部ライブラリ不要。
Netlify の本番ビルド（CONTEXT=production）では status が "sample" / "draft" のデータを出さない。
"""
import json
import os
import shutil
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
DIST = ROOT / "dist"
PRODUCTION = os.environ.get("CONTEXT") == "production"
VISIBLE = {"public"} if PRODUCTION else {"public", "sample"}


def load_dir(name):
    items = []
    for p in sorted((CONTENT / name).glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        if d.get("status", "public") in VISIBLE:
            items.append(d)
    return items


SITE = json.loads((CONTENT / "site.json").read_text(encoding="utf-8"))
ARTWORKS = sorted(load_dir("artworks"), key=lambda a: (a.get("order", 999), a["id"]))
ARTISTS = {a["id"]: a for a in load_dir("artists")}
EVENTS = load_dir("events")
LOGS = load_dir("logs")
NEWS = load_dir("news")
ART_BY_ID = {a["id"]: a for a in ARTWORKS}


def by_date(items):
    return sorted(items, key=lambda x: str(x.get("date", "")), reverse=True)


def e(s):
    return escape(str(s or ""))


def paras(text):
    return "".join(f"<p>{e(p).replace(chr(10), '<br>')}</p>" for p in str(text or "").split("\n\n") if p.strip())


def slug(art_id):
    return art_id.lower()


def sample_tag(item):
    return '<span class="tag tag-sample">SAMPLE</span>' if item.get("status") == "sample" else ""


NAV = [
    ("HOME", "/"),
    ("ORIGIN", "/origin/"),
    ("EARTH LOG", "/earth-log/"),
    ("ARCHIVE", "/archive/"),
    ("ENCOUNTERS", "/encounters/"),
    ("SIGNALS", "/signals/"),
    ("CONNECT", "/connect/"),
]


def page(path, title, body, active="", desc=""):
    nav = "".join(
        f'<li><a href="{href}"{" aria-current=\"page\"" if label == active else ""}>{label}</a></li>'
        for label, href in NAV
    )
    full_title = f"{title} — {SITE['name']}" if title else f"{SITE['name']} — AN ALIEN IN LOVE WITH EARTH"
    description = desc or "地球を愛するエイリアン、TOM TED TOD。出会う文化によって姿を変えながら、彼の旅は続いていく。"
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(full_title)}</title>
<meta name="description" content="{e(description)}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:image" content="{e(SITE['hero_image'])}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Share+Tech+Mono&family=Noto+Sans+JP:wght@300;400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<a class="skip" href="#main">本文へスキップ</a>
<header class="nav">
  <a class="nav-logo" href="/">TOM<em>.</em>TED<em>.</em>TOD</a>
  <button class="nav-toggle" aria-expanded="false" aria-controls="nav-menu" aria-label="メニューを開く"><span></span><span></span></button>
  <nav id="nav-menu" aria-label="メイン"><ul class="nav-links">{nav}</ul></nav>
  <div class="nav-status" aria-hidden="true"><span class="status-dot"></span>SYSTEM ACTIVE</div>
</header>
<main id="main">
{body}
</main>
<footer class="footer">
  <ul class="footer-links">{nav}</ul>
  <div class="footer-sys">
    <a href="{e(SITE['x_url'])}" rel="noopener" target="_blank">X {e(SITE['x_handle'])}</a><br>
    {e(SITE['name'])} / EARTH OBSERVATION LOG
  </div>
</footer>
<script src="/assets/site.js" defer></script>
</body>
</html>
"""
    out = DIST / path.strip("/") / "index.html" if path != "/" else DIST / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")


def header(eyebrow, title, intro="", code=""):
    return f"""<section class="page-head">
  <p class="eyebrow">{e(eyebrow)}<span class="code">{e(code)}</span></p>
  <h1 class="page-title">{e(title)}</h1>
  {f'<p class="lead">{e(intro)}</p>' if intro else ''}
</section>"""


def section_head(label, code="", more=None):
    m = f'<a class="more" href="{more[1]}">{e(more[0])} →</a>' if more else ""
    return f'<div class="section-head"><h2 class="eyebrow">{e(label)}<span class="code">{e(code)}</span></h2>{m}</div>'


def empty(msg):
    return f'<p class="empty">// {e(msg)}</p>'


def img_tag(img, cls="", loading="lazy"):
    if not img:
        return f'<div class="noimg {cls}" role="img" aria-label="写真準備中"><span>NO IMAGE<br>[要確認] 写真提供待ち</span></div>'
    return f'<img class="{cls}" src="{e(img["src"])}" alt="{e(img.get("alt", ""))}" loading="{loading}">'


# ---------- cards ----------

def artwork_card(a):
    img = a["images"][0] if a.get("images") else None
    kind = "CUSTOM" if a.get("kind") == "custom" else "BASE"
    artist = ARTISTS.get(a.get("artist", ""), {}).get("display_name", "")
    return f"""<a class="work-card" href="/archive/{slug(a['id'])}/">
  <div class="work-img">{img_tag(img)}<span class="tag tag-kind">{kind}</span></div>
  <div class="work-info">
    <span class="mono dim">{e(a['id'])} / {e(a.get('year'))}</span>
    <span class="work-title">{e(a['title'])}</span>
    {f'<span class="mono small">ARTIST: {e(artist)}</span>' if artist else ''}
  </div>
</a>"""


def log_card(l):
    img = l["images"][0] if l.get("images") else None
    return f"""<article class="log-card">
  <div class="log-img">{img_tag(img)}</div>
  <div class="log-body">
    <p class="meta"><span class="date">{e(l.get('date'))}</span><span class="tag">LOCATION: {e(l.get('place'))}</span>{sample_tag(l)}</p>
    <h3 class="log-title">{e(l['title'])}</h3>
    <div class="text">{paras(l.get('body'))}</div>
    {related_works(l.get('artworks', []))}
  </div>
</article>"""


def related_works(ids):
    links = [f'<a href="/archive/{slug(i)}/">{e(i)}</a>' for i in ids if i in ART_BY_ID]
    return f'<p class="mono small related">WORK: {" / ".join(links)}</p>' if links else ""


def event_row(ev):
    links = "".join(f'<a href="{e(u["url"])}" rel="noopener" target="_blank">{e(u.get("label") or u["url"])} ↗</a>' for u in ev.get("links", []))
    return f"""<li class="row" id="{e(ev['id'])}">
  <span class="date">{e(ev.get('date'))}</span>
  <span class="tag">{e(ev.get('type'))}</span>
  <div class="row-body">
    <h3 class="row-title">{e(ev['title'])}</h3>
    {f'<p class="mono small dim">LOCATION: {e(ev.get("place"))}</p>' if ev.get('place') else ''}
    <div class="text">{paras(ev.get('description'))}</div>
    {related_works(ev.get('artworks', []))}
    {f'<p class="links">{links}</p>' if links else ''}
  </div>
</li>"""


def news_row(n):
    return f"""<li class="row" id="{e(n['id'])}">
  <span class="date">{e(n.get('date'))}</span>
  <span class="tag">{e(n.get('type'))}</span>
  <div class="row-body">
    <h3 class="row-title">{e(n['title'])}</h3>
    <div class="text">{paras(n.get('body'))}</div>
    {related_works(n.get('artworks', []))}
  </div>
</li>"""


# ---------- pages ----------

def build_home():
    ja = e(SITE["hero_ja"]).replace("\n", "<br>")
    logs = by_date(LOGS)[:3]
    works = ARTWORKS[:3]
    activity = by_date(
        [dict(x, _kind="event") for x in EVENTS] + [dict(x, _kind="news") for x in NEWS]
    )[:4]
    body = f"""
<section class="hero" aria-label="TOM TED TOD">
  <div class="hero-photo">
    <img src="{e(SITE['hero_image'])}" alt="{e(SITE['hero_image_alt'])}" fetchpriority="high">
  </div>
  <div class="hud hud-tl" aria-hidden="true">CASE TTT-001<br>─────<br>SUBJECT ACTIVE</div>
  <div class="hud hud-tr" aria-hidden="true"><span class="rec">● REC</span><br>─────<br>CAM_01</div>
  <div class="hud hud-bl" aria-hidden="true">LOCATION<br>EARTH</div>
  <div class="hero-copy">
    <p class="signal">▸ SIGNAL RECEIVED</p>
    <h1 class="hero-title">{e(SITE['hero_title'])}</h1>
    <p class="hero-en">{e(SITE['hero_en'])}<br><span>{e(SITE['hero_en_sub'])}</span></p>
    <p class="hero-ja">{ja}</p>
  </div>
</section>

<section class="section">
  {section_head("WHO IS HE", "// 01 ORIGIN", ("ORIGIN", "/origin/"))}
  <p class="statement">{e(SITE['origin_lead'])}</p>
</section>

<section class="section">
  {section_head("EARTH LOG", "// 02 LATEST", ("ALL LOGS", "/earth-log/"))}
  <div class="log-list">{''.join(log_card(l) for l in logs) or empty('記録準備中')}</div>
</section>

<section class="section">
  {section_head("ARCHIVE", "// 03 WORKS", ("ALL WORKS", "/archive/"))}
  <div class="work-grid">{''.join(artwork_card(a) for a in works) or empty('作品準備中')}</div>
</section>

<section class="section">
  {section_head("RECENT ACTIVITY", "// 04 EXHIBITION / SIGNALS", ("SIGNALS", "/signals/"))}
  <ul class="rows">{''.join(event_row(x) if x['_kind'] == 'event' else news_row(x) for x in activity) or empty('準備中')}</ul>
</section>

<section class="section connect-band">
  {section_head("COLLABORATION", "// 05 CONNECT")}
  <p class="statement">{e(SITE['collab_intro'])}</p>
  <p><a class="btn btn-primary" href="/connect/">CONNECT →</a></p>
</section>
"""
    page("/", "", body, "HOME")


def build_origin():
    pts = "".join(
        f'<div class="spec-row"><span class="spec-key">{e(p["label"])}</span><span class="spec-val">{e(p["text"])}</span></div>'
        for p in SITE["origin_points"]
    )
    base = ART_BY_ID.get("TT-B000")
    base_link = f'<p><a class="more" href="/archive/{slug(base["id"])}/">BASE BODY の記録を見る →</a></p>' if base else ""
    body = f"""{header("SUBJECT PROFILE / ORIGIN", "ORIGIN", "", "// 01")}
<section class="section origin">
  <div class="origin-photo">{img_tag({'src': SITE['hero_image'], 'alt': SITE['hero_image_alt']})}</div>
  <div>
    <p class="statement">{e(SITE['origin_lead'])}</p>
    <div class="spec">{pts}</div>
    {base_link}
  </div>
</section>"""
    page("/origin/", "ORIGIN", body, "ORIGIN")


def build_earthlog():
    logs = by_date(LOGS)
    body = f"""{header("FIELD OBSERVATION / EARTH LOG", "EARTH LOG", SITE['earthlog_intro'], f"// {len(logs):02d} ENTRIES")}
<section class="section"><div class="log-list">{''.join(log_card(l) for l in logs) or empty('記録準備中')}</div></section>"""
    page("/earth-log/", "EARTH LOG", body, "EARTH LOG")


def build_archive():
    customs = [a for a in ARTWORKS if a.get("kind") == "custom"]
    bases = [a for a in ARTWORKS if a.get("kind") != "custom"]
    body = f"""{header("WORK RECORDS / ARCHIVE", "ARCHIVE", SITE['archive_intro'], f"// {len(ARTWORKS):02d} RECORDS")}
<section class="section">
  {section_head("BASE BODY", "// 素体")}
  <div class="work-grid">{''.join(artwork_card(a) for a in bases) or empty('準備中')}</div>
</section>
<section class="section">
  {section_head("CUSTOM WORKS", "// カスタム作品")}
  <div class="work-grid">{''.join(artwork_card(a) for a in customs) or empty('準備中')}</div>
</section>"""
    page("/archive/", "ARCHIVE", body, "ARCHIVE")
    for a in ARTWORKS:
        build_artwork(a)


def build_artwork(a):
    artist = ARTISTS.get(a.get("artist", ""))
    imgs = a.get("images") or [None]
    gallery = "".join(
        f'<figure>{img_tag(i, loading="eager" if n == 0 else "lazy")}'
        + (f'<figcaption class="mono small dim">PHOTO: {e(i.get("credit"))}</figcaption>' if i and i.get("credit") else "")
        + "</figure>"
        for n, i in enumerate(imgs)
    )
    # 活動履歴：作品自身の history + 作品を参照する Event / News / Log を日付順に合成
    hist = [dict(h, _src="history") for h in a.get("history", [])]
    hist += [{"date": ev.get("date"), "type": ev.get("type"), "title": ev["title"], "place": ev.get("place"), "href": f"/encounters/#{ev['id']}"} for ev in EVENTS if a["id"] in ev.get("artworks", [])]
    hist += [{"date": n.get("date"), "type": n.get("type"), "title": n["title"], "href": f"/signals/#{n['id']}"} for n in NEWS if a["id"] in n.get("artworks", [])]
    hist += [{"date": l.get("date"), "type": "EARTH LOG", "title": l["title"], "place": l.get("place"), "href": "/earth-log/"} for l in LOGS if a["id"] in l.get("artworks", [])]
    hist = by_date(hist)
    hist_html = "".join(
        f"""<li class="row"><span class="date">{e(h.get('date'))}</span><span class="tag">{e(h.get('type'))}</span>
<div class="row-body"><h3 class="row-title">{f'<a href="{e(h["href"])}">{e(h["title"])}</a>' if h.get('href') else e(h['title'])}</h3>
{f'<p class="mono small dim">LOCATION: {e(h.get("place"))}</p>' if h.get('place') else ''}
{f'<p class="text">{e(h.get("description"))}</p>' if h.get('description') else ''}
{f'<p class="links"><a href="{e(h["url"])}" rel="noopener" target="_blank">LINK ↗</a></p>' if h.get('url') else ''}</div></li>"""
        for h in hist
    )
    links = "".join(f'<a href="{e(u["url"])}" rel="noopener" target="_blank">{e(u.get("label") or u["url"])} ↗</a>' for u in a.get("links", []))
    rows = [
        ("RECORD", a["id"]),
        ("TYPE", "CUSTOM WORK / カスタム作品" if a.get("kind") == "custom" else "BASE BODY / 素体"),
        ("YEAR", a.get("year")),
        ("ARTIST", artist["display_name"] if artist else ""),
        ("TECHNIQUE", a.get("technique")),
        ("CONTEXT", a.get("context")),
    ]
    spec = "".join(f'<div class="spec-row"><span class="spec-key">{k}</span><span class="spec-val">{e(v)}</span></div>' for k, v in rows if v)
    body = f"""<section class="page-head">
  <p class="eyebrow"><a href="/archive/">ARCHIVE</a> / {e(a['id'])}<span class="code">// WORK RECORD</span></p>
  <h1 class="page-title">{e(a['title'])}</h1>
</section>
<section class="section work-detail">
  <div class="work-gallery">{gallery}</div>
  <div>
    <div class="spec">{spec}</div>
    <div class="text">{paras(a.get('description'))}</div>
    {f'<p class="links">{links}</p>' if links else ''}
  </div>
</section>
<section class="section">
  {section_head("ACTIVITY HISTORY", "// 作品のその後")}
  <ul class="rows">{hist_html or empty('活動履歴はまだありません')}</ul>
</section>"""
    page(f"/archive/{slug(a['id'])}/", a["title"], body, "ARCHIVE", a.get("description", "")[:120])


def build_encounters():
    evs = by_date(EVENTS)
    artists = [a for a in ARTISTS.values()]
    artist_html = "".join(
        f'<div class="spec-row"><span class="spec-key">{e(a["display_name"])}</span><span class="spec-val">{e(a.get("bio"))}</span></div>'
        for a in artists
    )
    body = f"""{header("COLLABORATION RECORDS / ENCOUNTERS", "ENCOUNTERS", SITE['encounters_intro'], f"// {len(evs):02d} RECORDS")}
<section class="section">
  {section_head("EXHIBITIONS & PROJECTS", "// 展示・企画")}
  <ul class="rows">{''.join(event_row(x) for x in evs) or empty('準備中')}</ul>
</section>
<section class="section">
  {section_head("ARTISTS", "// 参加作家")}
  <div class="spec">{artist_html or empty('準備中')}</div>
</section>"""
    page("/encounters/", "ENCOUNTERS", body, "ENCOUNTERS")


def build_signals():
    ns = by_date(NEWS)
    body = f"""{header("TRANSMISSIONS / SIGNALS", "SIGNALS", SITE['signals_intro'], f"// {len(ns):02d} SIGNALS")}
<section class="section"><ul class="rows">{''.join(news_row(x) for x in ns) or empty('準備中')}</ul></section>"""
    page("/signals/", "SIGNALS", body, "SIGNALS")


def build_connect():
    notes = "".join(f"<li>{e(n)}</li>" for n in SITE["connect_notes"])
    body = f"""{header("CONTACT CHANNEL / CONNECT", "CONNECT", SITE['collab_intro'], "// 06")}
<section class="section connect">
  <form class="form" name="connect" method="POST" action="/connect/thanks/" data-netlify="true" netlify-honeypot="bot-field">
    <input type="hidden" name="form-name" value="connect">
    <p class="hp"><label>空欄のまま <input name="bot-field"></label></p>
    <label class="field"><span class="field-label">ご用件 <em>必須</em></span>
      <select name="type" required>
        <option value="">選択してください</option>
        <option>参加希望（カスタム制作）</option>
        <option>展示・協業の相談</option>
        <option>取材・その他</option>
      </select></label>
    <label class="field"><span class="field-label">お名前 <em>必須</em></span><input name="name" required autocomplete="name"></label>
    <label class="field"><span class="field-label">メールアドレス <em>必須</em></span><input type="email" name="email" required autocomplete="email"></label>
    <fieldset class="field"><legend class="field-label">サイト上での公開名義の希望</legend>
      <label class="radio"><input type="radio" name="name_policy" value="実名" > 実名</label>
      <label class="radio"><input type="radio" name="name_policy" value="活動名"> 活動名</label>
      <label class="radio"><input type="radio" name="name_policy" value="匿名"> 匿名</label>
      <label class="radio"><input type="radio" name="name_policy" value="未定" checked> 未定・相談したい</label>
    </fieldset>
    <label class="field"><span class="field-label">活動がわかるリンク（任意）</span><input type="url" name="link" placeholder="https://"></label>
    <label class="field"><span class="field-label">内容 <em>必須</em></span><textarea name="message" rows="6" required></textarea></label>
    <button class="btn btn-primary" type="submit">SEND SIGNAL →</button>
  </form>
  <aside class="notes">
    <h2 class="eyebrow">BEFORE YOU SEND<span class="code">// NOTES</span></h2>
    <ul>{notes}</ul>
  </aside>
</section>"""
    page("/connect/", "CONNECT", body, "CONNECT")
    page("/connect/thanks/", "送信完了", f"""{header("SIGNAL RECEIVED", "THANK YOU", "送信を受け付けました。内容を確認のうえ、ご連絡します。", "// 06")}
<section class="section"><a class="btn btn-ghost" href="/">← HOME</a></section>""", "CONNECT")


def build_404():
    page("/404/", "NOT FOUND", f"""{header("SIGNAL LOST", "404", "ページが見つかりません。", "// ERROR")}
<section class="section"><a class="btn btn-ghost" href="/">← HOME</a></section>""")
    shutil.move(DIST / "404" / "index.html", DIST / "404.html")
    (DIST / "404").rmdir()


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copytree(ROOT / "src" / "assets", DIST / "assets")
    shutil.copytree(ROOT / "images", DIST / "images")
    shutil.copytree(ROOT / "admin", DIST / "admin")
    shutil.copy(ROOT / "converter.html", DIST / "converter.html")
    build_home()
    build_origin()
    build_earthlog()
    build_archive()
    build_encounters()
    build_signals()
    build_connect()
    build_404()
    print(f"built: production={PRODUCTION} artworks={len(ARTWORKS)} logs={len(LOGS)} events={len(EVENTS)} news={len(NEWS)}")


if __name__ == "__main__":
    main()
