#!/usr/bin/env python3
"""Run: python3 build.py   -> writes the finished site into ./site
Names go in data/<country>/<category>.txt, one per line:  Name | meaning | origin
Pages with no data file show dummy names and stay noindex until you add real ones.
Optional content/<country>/<category>.meta: title / description / h1 lines (keywords).
Your own text goes in content/<country>/<category>.html (optional, shown under the list)
and content/<country>/index.html (optional, shown on the country hub)."""
import os, shutil, html

SITE = "Random Names"
BASE = "https://random-names.netlify.app"
MIN_INDEX = 50                # pages with fewer names get noindex until you fill them

BASIC = [("boy-names", "Boy Names"), ("girl-names", "Girl Names"), ("random-names", "Random Names")]
LAST = ("last-names", "Last Names")
COUNTRIES = {
    "united-states": ("United States", "American", [LAST, ("unisex-names", "Unisex Names")]),
    "united-kingdom": ("United Kingdom", "British", [LAST]),
    "canada": ("Canada", "Canadian", [LAST]),
    "australia": ("Australia", "Australian", [LAST, ("nicknames", "Nicknames")]),
    "india": ("India", "Indian", [LAST, ("hindu-names", "Hindu Names"), ("muslim-names", "Muslim Names"), ("sikh-names", "Sikh Names")]),
    "philippines": ("Philippines", "Filipino", [("nicknames", "Nicknames"), LAST]),
    "malaysia": ("Malaysia", "Malaysian", [("malay-names", "Malay Names"), ("chinese-names", "Chinese Names"), ("indian-names", "Indian Names")]),
    "singapore": ("Singapore", "Singaporean", [("chinese-names", "Chinese Names"), ("malay-names", "Malay Names"), ("indian-names", "Indian Names"), LAST]),
}

CSS = """
:root{--bg:#fff;--ink:#16181d;--mut:#667085;--line:#e6e8ee;--soft:#f5f6f9;--acc:#3b5bdb;--accs:#edf1ff}
@media(prefers-color-scheme:dark){:root{--bg:#10131a;--ink:#eef0f5;--mut:#9aa3b5;--line:#252b38;--soft:#181c26;--acc:#8ba3ff;--accs:#1d2540}}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 Inter,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:inherit;text-decoration:none}a:focus-visible,button:focus-visible,input:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
.w{max-width:960px;margin:0 auto;padding:0 20px}
header{border-bottom:1px solid var(--line)}header .w{display:flex;justify-content:space-between;align-items:center;height:60px}
.logo{font-weight:700;font-size:19px;letter-spacing:-.02em}nav a{color:var(--mut);margin-left:20px;font-size:15px}nav a:hover{color:var(--ink)}
.crumbs{color:var(--mut);font-size:14px;margin:26px 0 6px}.crumbs a:hover{color:var(--ink)}
h1{font-size:clamp(28px,5vw,42px);line-height:1.15;letter-spacing:-.03em;margin:6px 0 10px}
.lead{color:var(--mut);max-width:60ch;margin:0 0 26px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:12px;margin:0 0 40px}
.card{display:block;border:1px solid var(--line);border-radius:14px;padding:18px;transition:border-color .15s,background .15s}
.card:hover{border-color:var(--acc);background:var(--accs)}.card b{display:block;font-size:17px}.card span{color:var(--mut);font-size:14px}
.tools{position:sticky;top:0;background:var(--bg);padding:12px 0;z-index:5;border-bottom:1px solid var(--line)}
.row{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
input[type=search]{flex:1;min-width:200px;border:1px solid var(--line);background:var(--soft);color:var(--ink);border-radius:12px;padding:11px 14px;font:inherit}
.btn{border:0;background:var(--acc);color:#fff;border-radius:12px;padding:11px 18px;font:inherit;font-weight:600;cursor:pointer}
.btn.alt{background:var(--soft);color:var(--ink);border:1px solid var(--line)}
.az{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}.az button{border:1px solid var(--line);background:none;color:var(--mut);border-radius:8px;min-width:32px;height:32px;cursor:pointer;font:inherit;font-size:14px}
.az button[aria-pressed=true]{background:var(--acc);border-color:var(--acc);color:#fff}
#pick{display:none;margin:18px 0 0;padding:16px 18px;border-radius:14px;background:var(--accs);font-size:20px;font-weight:600}#pick small{display:block;color:var(--mut);font-size:14px;font-weight:400}
#count{color:var(--mut);font-size:14px;margin:18px 0 8px}
ul#list{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:0 28px}
#list li{padding:11px 0;border-bottom:1px solid var(--line);cursor:pointer}#list li:hover b{color:var(--acc)}
#list b{font-size:17px}#list small{display:block;color:var(--mut);font-size:14px}#list li[hidden]{display:none}
.more{display:block;margin:26px auto}.ad{min-height:100px;margin:28px 0}
.copy{margin:40px 0}.copy h2{font-size:24px;letter-spacing:-.02em}.copy p,.copy li{max-width:70ch}
footer{border-top:1px solid var(--line);margin-top:60px;padding:28px 0;color:var(--mut);font-size:14px}
.empty{padding:30px;border:1px dashed var(--line);border-radius:14px;color:var(--mut)}
"""

JS = """
const L=[...document.querySelectorAll('#list li')],q=document.getElementById('q'),m=document.getElementById('more'),c=document.getElementById('count'),p=document.getElementById('pick');
let a='',n=60;
function f(){const s=q.value.trim().toLowerCase();let t=0;
L.forEach(li=>{const ok=li.dataset.n.includes(s)&&(!a||li.dataset.n[0]===a);if(ok)t++;li.hidden=!(ok&&t<=n)});
m.hidden=t<=n;c.textContent=t.toLocaleString()+' names'}
q.oninput=()=>{n=60;f()};
m.onclick=()=>{n+=120;f()};
document.querySelectorAll('.az button').forEach(b=>b.onclick=()=>{const on=b.getAttribute('aria-pressed')==='true';
document.querySelectorAll('.az button').forEach(x=>x.setAttribute('aria-pressed','false'));
a=on?'':b.dataset.l;b.setAttribute('aria-pressed',String(!on));n=60;f()});
document.getElementById('rnd').onclick=()=>{const li=L[Math.floor(Math.random()*L.length)];
p.style.display='block';p.innerHTML=li.innerHTML}
L.forEach(li=>li.onclick=()=>{navigator.clipboard&&navigator.clipboard.writeText(li.querySelector('b').textContent)});
f();
"""

def read_names(country, cat):
    path = os.path.join("data", country, cat + ".txt")
    out, seen = [], set()
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            parts = [x.strip() for x in line.split("|")]
            if parts[0] and not parts[0].startswith("#") and parts[0].lower() not in seen:
                seen.add(parts[0].lower())
                out.append((parts[0], parts[1] if len(parts) > 1 else "", parts[2] if len(parts) > 2 else ""))
    return sorted(out, key=lambda x: x[0].lower())

def read_copy(country, cat):
    path = os.path.join("content", country, cat + ".html")
    return open(path, encoding="utf-8").read() if os.path.exists(path) else ""

def read_meta(country, cat):
    """Optional content/<country>/<cat>.meta with lines like:  title: ...  /  description: ...  /  h1: ..."""
    path = os.path.join("content", country, cat + ".meta")
    m = {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            if ":" in line:
                k, v = line.split(":", 1)
                m[k.strip().lower()] = v.strip()
    return m

def dummy_names():
    return [(f"{l}. Sample name {i}", "Dummy meaning", "Dummy origin") for l in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" for i in range(1, 5)]

def page(title, desc, path, body, noindex=False):
    robots = '<meta name="robots" content="noindex,follow">' if noindex else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{BASE}{path}">{robots}<style>{CSS}</style></head><body>
<header><div class="w"><a class="logo" href="/">{SITE}</a><nav><a href="/">Countries</a></nav></div></header>
<main class="w">{body}</main>
<footer><div class="w">&copy; 2026 {SITE}</div></footer></body></html>"""

def write(path, content):
    full = os.path.join("site", path.strip("/"), "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(content)

def main():
    shutil.rmtree("site", ignore_errors=True)
    urls = ["/"]
    cards = ""
    for slug, (name, demo, extra) in COUNTRIES.items():
        cats = BASIC + extra
        cards += f'<a class="card" href="/{slug}/"><b>{name}</b><span>{demo} names</span></a>'
        # hub page
        cc = ""
        for cs, cl in cats:
            cnt = len(read_names(slug, cs)) or len(dummy_names())
            cc += f'<a class="card" href="/{slug}/{cs}/"><b>{demo} {cl}</b><span>{cnt:,} names</span></a>'
        body = (f'<div class="crumbs"><a href="/">Home</a> / {name}</div><h1>{demo} Names</h1>'
                f'<p class="lead">Browse names from {name} by category.</p><div class="grid">{cc}</div>'
                f'<div class="copy">{read_copy(slug, "index")}</div>')
        hm = read_meta(slug, "index")
        write(f"/{slug}/", page(hm.get("title", f"{demo} Names: Boy, Girl and Random | {SITE}"), hm.get("description", f"Browse {demo} names from {name}: boy names, girl names, random names and more."), f"/{slug}/", body))
        urls.append(f"/{slug}/")
        # category pages
        for cs, cl in cats:
            names = read_names(slug, cs)
            dummy = not names
            if dummy:
                names = dummy_names()
            meta = read_meta(slug, cs)
            h1 = meta.get("h1", f"{demo} {cl}")
            letters = sorted({n[0][0].upper() for n in names if n[0][0].isalpha()})
            az = "".join(f'<button aria-pressed="false" data-l="{l.lower()}">{l}</button>' for l in letters)
            items = "".join(
                f'<li data-n="{html.escape(n.lower())}"><b>{html.escape(n)}</b>'
                f'<small>{html.escape(" · ".join(x for x in (mean, org) if x))}</small></li>'
                for n, mean, org in names)
            listing = (f'<div class="tools"><div class="row"><input id="q" type="search" placeholder="Search {h1.lower()}" aria-label="Search names">'
                       f'<button class="btn" id="rnd">Random name</button></div><div class="az">{az}</div></div>'
                       f'<div id="pick"></div><div id="count"></div><ul id="list">{items}</ul>'
                       f'<button class="btn alt more" id="more">Show more</button><script>{JS}</script>') if names else \
                      '<div class="empty">This list is being added. Please check back soon.</div>'
            body = (f'<div class="crumbs"><a href="/">Home</a> / <a href="/{slug}/">{name}</a> / {cl}</div>'
                    f'<h1>{h1}</h1><p class="lead">{demo} {cl.lower()} with meanings. Search, filter by letter, or tap a name to copy it.</p>'
                    f'<div class="ad" aria-hidden="true"></div>{listing}<div class="ad" aria-hidden="true"></div>'
                    f'<div class="copy">{read_copy(slug, cs)}</div>')
            thin = dummy or len(names) < MIN_INDEX
            title = meta.get("title", f"{h1} with Meanings | {SITE}")
            desc = meta.get("description", f"{len(names):,} {h1.lower()} with meanings and origins. Search and filter the full list.")
            write(f"/{slug}/{cs}/", page(title, desc, f"/{slug}/{cs}/", body, noindex=thin))
            if not thin:
                urls.append(f"/{slug}/{cs}/")
    home = (f'<h1>Names from around the world</h1><p class="lead">Pick a country, then browse boy names, girl names, random names and more.</p>'
            f'<div class="grid">{cards}</div>')
    write("/", page(f"{SITE}: Names by Country", "Browse boy, girl and random names by country, with meanings and origins.", "/", home))
    open("site/sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                        + "".join(f"<url><loc>{BASE}{u}</loc></url>" for u in urls) + "</urlset>")
    open("site/robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    print(f"Built {len(urls)} indexable URLs. Pages under {MIN_INDEX} names are set to noindex.")

main()
