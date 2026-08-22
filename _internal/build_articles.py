"""Mirror free Strange Intel (Substack) posts as /articles/<slug>/ pages.
Run: python _internal/build_articles.py   (from repo root; fetches the RSS).
Skips paywalled posts. Strips the old CTA footer (stale $500 / 15-minute copy that the site deliberately no longer
shows — see commit 58ba822) and replaces it with the site CTA. ponytail: RSS HTML is kept as-is apart from that."""
import os, re, sys, json, html, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_pages import ROOT, SITE, head_css, EXTRA_CSS, SERVICES, INDUSTRIES

FEED="https://strangeintel.substack.com/feed"
DROP=re.compile(r"(\$\d|15-minute|15 minute|Posted by Claude Code|^\s*(&#8212;|—)\s*Jereme|Want it installed\?|StrangeAdvancedMarketing\.com\s*(&#8594;|→)|Setup (from|starts at)|retainer|reader-supported|subscribe|upgrade to paid|paid subscriber)", re.I)

def clean(body):
    """Drop paragraphs carrying the stale CTA. Works on <p>/<h*> blocks; anything else passes through."""
    out=[]
    for block in re.split(r"(?=<(?:p|h[1-6]|ul|ol|blockquote)\b)", body):
        text=html.unescape(re.sub(r"<[^>]+>"," ",block))
        if DROP.search(text): continue
        out.append(block)
    b="".join(out)
    b=re.sub(r"<h1\b","<h2",b); b=re.sub(r"</h1>","</h2>",b)          # page already has its H1
    b=re.sub(r'\s(class|style|data-[\w-]+)="[^"]*"',"",b)             # substack classes mean nothing here
    b=re.sub(r"<div[^>]*>|</div>","",b)
    return b.strip()

def slugify(s):
    return re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-")[:70].rstrip("-")

def main():
    xml=urllib.request.urlopen(urllib.request.Request(FEED,headers={"User-Agent":"Mozilla/5.0"}),timeout=30).read().decode("utf-8")
    sm_path=os.path.join(ROOT,"sitemap.xml"); sm=open(sm_path,encoding="utf-8").read(); add=""; made=[]
    for it in re.findall(r"<item>(.*?)</item>",xml,re.S):
        title=html.unescape(re.search(r"<title><!\[CDATA\[(.*?)\]\]>",it).group(1)).strip()
        link=re.search(r"<link>(.*?)</link>",it).group(1).strip()
        date=re.search(r"<pubDate>(.*?)</pubDate>",it).group(1)
        desc=html.unescape(re.search(r"<description><!\[CDATA\[(.*?)\]\]>",it,re.S).group(1)).strip()[:155]
        body=re.search(r"<content:encoded><!\[CDATA\[(.*?)\]\]></content:encoded>",it,re.S)
        if not body: continue
        body=body.group(1)
        if re.search(r"paywall|subscribe to (read|continue)|This post is for paid subscribers",body,re.I):
            print("SKIP paywalled:",title[:60]); continue
        import email.utils, datetime
        iso=datetime.datetime(*email.utils.parsedate(date)[:6]).strftime("%Y-%m-%d")
        slug=slugify(title); url=f"{SITE}/articles/{slug}/"; e=html.escape
        content=clean(body)
        assert "$" not in re.sub(r"<[^>]+>","",content), title   # pricing must not leak (58ba822)
        ld={"@context":"https://schema.org","@type":"Article","headline":title,"description":desc,"datePublished":iso,
            "url":url,"author":{"@type":"Person","name":"Jereme Strange"},
            "publisher":{"@type":"Organization","name":"Strange Advanced Marketing","url":SITE+"/"},"sameAs":link}
        svc="".join(f'<a href="/services/{s}/">{e(SERVICES[s]["name"])}</a>' for s in SERVICES)
        page=f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} | Strange Advanced Marketing</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/og.jpg">
<meta name="theme-color" content="#fafbfd">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<script type="application/ld+json">{json.dumps(ld)}</script>
{head_css()}
{EXTRA_CSS}
<style>.art h2{{margin-top:34px}} .art h3{{margin:24px 0 8px;color:var(--ink)}} .art pre{{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px;overflow-x:auto;font-size:14px;margin-bottom:14px}} .art code{{font-family:var(--mono,ui-monospace,monospace);font-size:.92em}} .art img{{border-radius:10px;margin:10px 0}} .art hr{{border:0;border-top:1px solid var(--line);margin:28px 0}}</style>
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
</head>
<body>
<nav><div class="nav-in">
  <a href="/"><img src="/logo-light.png" alt="Strange Advanced Marketing"></a>
  <a class="nav-back" href="/#contact">Book a free consultation &rarr;</a>
</div></nav>
<header class="head"><div class="circuit" id="circuit-head"></div><div class="head-in">
  <div class="kick">Article &middot; {iso}</div><h1>{e(title)}</h1>
  <p class="updated">By Jereme Strange &middot; also on <a href="{link}">Strange Intel</a></p></div></header>
<div class="wrap art">
  {content}
  <p style="margin-top:28px"><a class="cta" href="/#contact">Want this in your business? Free 30-minute consultation</a></p>
  <h2>Services</h2><div class="links">{svc}</div>
  <div class="foot">&copy; 2026 Strange Advanced Marketing. Miami, FL. &middot; <a href="/privacy/">Privacy</a> &middot; <a href="/terms/">Terms</a> &middot; <a href="/articles/">All articles</a></div>
</div>
<script>
function circuit(el,o){{if(!el)return;const w=1600,h=el.parentElement.offsetHeight+100;let s=42+o;const r=()=>{{s=(s*16807)%2147483647;return s/2147483647}};let p="",n="";for(let i=0;i<26;i++){{let x=Math.floor(r()*w),y=Math.floor(r()*h),d=`M${{x}} ${{y}}`;for(let k=0;k<3;k++){{const dx=(r()>.5?1:-1)*(40+r()*120),dy=(r()>.5?1:-1)*(30+r()*90);r()>.5?(x+=dx,d+=` h${{Math.round(dx)}}`):(y+=dy,d+=` v${{Math.round(dy)}}`)}}p+=`<path d="${{d}}" fill="none" stroke="var(--trace)" stroke-width="1.4"/>`;n+=`<circle cx="${{x}}" cy="${{y}}" r="3.2" fill="none" stroke="var(--node)" stroke-width="1.4"/>`}}el.innerHTML=`<svg viewBox="0 0 ${{w}} ${{h}}" preserveAspectRatio="xMidYMid slice" style="opacity:.5">${{p}}${{n}}</svg>`}}circuit(document.getElementById("circuit-head"),{abs(hash(slug))%50});
</script>
</body>
</html>
"""
        out=os.path.join(ROOT,"articles",slug); os.makedirs(out,exist_ok=True)
        open(os.path.join(out,"index.html"),"w",encoding="utf-8").write(page)
        made.append((iso,title,slug,desc))
        if url not in sm: add+=f"  <url><loc>{url}</loc><lastmod>{iso}</lastmod></url>\n"
        print(iso,"->",url)
    # hub
    made.sort(reverse=True); e=html.escape
    cards="".join(f'<a class="card" href="/articles/{s}/" style="display:block;text-decoration:none"><p style="font-size:12px;color:var(--faint)">{d}</p><h3>{e(t)}</h3><p>{e(ds)}</p></a>' for d,t,s,ds in made)
    hub=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Articles | Strange Advanced Marketing</title>
<meta name="description" content="Field notes on running a business with AI agents, Claude Code, and AI search visibility. From Strange Advanced Marketing, Miami, FL.">
<link rel="canonical" href="{SITE}/articles/"><meta name="theme-color" content="#fafbfd">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
{head_css()}{EXTRA_CSS}<style>.wrap{{max-width:1120px}}</style>
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="apple-touch-icon" href="/apple-touch-icon.png"></head><body>
<nav><div class="nav-in"><a href="/"><img src="/logo-light.png" alt="Strange Advanced Marketing"></a><a class="nav-back" href="/#contact">Book a free consultation &rarr;</a></div></nav>
<header class="head"><div class="circuit" id="circuit-head"></div><div class="head-in"><div class="kick">Articles</div><h1>Field notes from running a business on AI</h1></div></header>
<div class="wrap"><div class="grid" style="grid-template-columns:repeat(auto-fill,minmax(300px,1fr))">{cards}</div>
<div class="foot">&copy; 2026 Strange Advanced Marketing. Miami, FL. &middot; <a href="/privacy/">Privacy</a> &middot; <a href="/terms/">Terms</a></div></div>
<script>function circuit(el,o){{if(!el)return;const w=1600,h=el.parentElement.offsetHeight+100;let s=42+o;const r=()=>{{s=(s*16807)%2147483647;return s/2147483647}};let p="",n="";for(let i=0;i<26;i++){{let x=Math.floor(r()*w),y=Math.floor(r()*h),d=`M${{x}} ${{y}}`;for(let k=0;k<3;k++){{const dx=(r()>.5?1:-1)*(40+r()*120),dy=(r()>.5?1:-1)*(30+r()*90);r()>.5?(x+=dx,d+=` h${{Math.round(dx)}}`):(y+=dy,d+=` v${{Math.round(dy)}}`)}}p+=`<path d="${{d}}" fill="none" stroke="var(--trace)" stroke-width="1.4"/>`;n+=`<circle cx="${{x}}" cy="${{y}}" r="3.2" fill="none" stroke="var(--node)" stroke-width="1.4"/>`}}el.innerHTML=`<svg viewBox="0 0 ${{w}} ${{h}}" preserveAspectRatio="xMidYMid slice" style="opacity:.5">${{p}}${{n}}</svg>`}}circuit(document.getElementById("circuit-head"),23);</script>
</body></html>"""
    open(os.path.join(ROOT,"articles","index.html"),"w",encoding="utf-8").write(hub)
    if f"{SITE}/articles/</loc>" not in sm: add+=f"  <url><loc>{SITE}/articles/</loc><lastmod>2026-08-22</lastmod></url>\n"
    if add: open(sm_path,"w",encoding="utf-8").write(sm.replace("</urlset>",add+"</urlset>"))
    print("articles:",len(made))
    return made

if __name__=="__main__":
    main()
