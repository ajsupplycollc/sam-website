"""Turn published YouTube videos into /videos/<slug>/ pages (embed + transcript + VideoObject schema).
Run: python _internal/build_video_pages.py VIDEO_ID [VIDEO_ID...]   (from repo root; needs yt-dlp on PATH)
ponytail: transcript is the YouTube auto-caption, deduped; no rewrite pass. Titles come from YouTube as-is."""
import json, os, re, sys, html, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_pages import ROOT, SITE, head_css, EXTRA_CSS, SERVICES, INDUSTRIES

def fetch(vid, tmp):
    subprocess.run(["yt-dlp","--skip-download","--write-auto-sub","--write-sub","--sub-lang","en","--sub-format","vtt",
                    "--write-info-json","-o",os.path.join(tmp,"v"),f"https://www.youtube.com/watch?v={vid}"],
                   check=True, capture_output=True)
    info = json.load(open(os.path.join(tmp,"v.info.json"),encoding="utf-8"))
    vtt = os.path.join(tmp,"v.en.vtt")
    return info, open(vtt,encoding="utf-8").read() if os.path.exists(vtt) else ""

def transcript(vtt):
    """Rolling auto-captions repeat the previous cue's last line; drop exact repeats."""
    out=[]
    for block in re.split(r"\n\s*\n", vtt):
        lines=[re.sub(r"<[^>]+>","",l).strip() for l in block.splitlines() if l.strip() and "-->" not in l]
        lines=[l for l in lines if not l.startswith(("WEBVTT","Kind:","Language:"))]
        for l in lines:
            if l and (not out or l!=out[-1]): out.append(l)
    return " ".join(out)

def slugify(s):
    s=re.sub(r"#\w+","",s); s=re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-")
    return s[:70].rstrip("-") or "video"

def page(vid, info, text):
    e=html.escape
    title=re.sub(r"\s*#\w+","",info["title"]).strip()
    if re.match(r"^v\d{5,}[a-z0-9]+\s*-\s*", title):            # TikTok-id junk title -> use first line of description
        title=(info.get("description") or "").split("\n")[0].strip()[:90] or title
    slug=slugify(title); url=f"{SITE}/videos/{slug}/"
    desc=(info.get("description") or "").split("\n\n")[0].replace("\n"," ").strip()
    desc=re.sub(r"\s*-?Posted by .*$","",desc)[:155]
    d=info["upload_date"]; iso=f"{d[:4]}-{d[4:6]}-{d[6:]}"
    ld={"@context":"https://schema.org","@type":"VideoObject","name":title,"description":desc or title,
        "thumbnailUrl":f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg","uploadDate":iso,
        "duration":f"PT{int(info.get('duration') or 0)}S","embedUrl":f"https://www.youtube.com/embed/{vid}",
        "contentUrl":f"https://www.youtube.com/watch?v={vid}","transcript":text,
        "publisher":{"@type":"Organization","name":"Strange Advanced Marketing","url":SITE+"/"}}
    sents=[s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z])", text) if s.strip()]
    paras="".join(f"<p>{e(' '.join(sents[i:i+3]))}</p>" for i in range(0,len(sents),3)) or "<p>Transcript not available.</p>"
    svc="".join(f'<a href="/services/{s}/">{e(SERVICES[s]["name"])}</a>' for s in SERVICES)
    ind="".join(f'<a href="/industries/{s}/">{e(INDUSTRIES[s]["name"])}</a>' for s in INDUSTRIES)
    body=f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} | Strange Advanced Marketing</title>
<meta name="description" content="{e(desc or title)}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc or title)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://i.ytimg.com/vi/{vid}/hqdefault.jpg">
<meta name="theme-color" content="#fafbfd">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<script type="application/ld+json">{json.dumps(ld)}</script>
{head_css()}
{EXTRA_CSS}
<style>.video{{position:relative;padding-top:56.25%;border-radius:12px;overflow:hidden;border:1px solid var(--line);background:#000;margin:0 0 22px}}
.video iframe{{position:absolute;inset:0;width:100%;height:100%;border:0}}
.video.short{{max-width:360px;padding-top:0;height:640px;margin-left:auto;margin-right:auto}}</style>
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
</head>
<body>
<nav><div class="nav-in">
  <a href="/"><img src="/logo-light.png" alt="Strange Advanced Marketing"></a>
  <a class="nav-back" href="/#contact">Book a free consultation &rarr;</a>
</div></nav>
<header class="head">
  <div class="circuit" id="circuit-head"></div>
  <div class="head-in">
    <div class="kick">Video &middot; {iso}</div>
    <h1>{e(title)}</h1>
  </div>
</header>
<div class="wrap">
  <div class="video{' short' if (info.get('height') or 0) > (info.get('width') or 1) else ''}"><iframe src="https://www.youtube-nocookie.com/embed/{vid}" title="{e(title)}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe></div>
  <p class="answer">{e(desc or title)}</p>
  <h2>Transcript</h2>
  {paras}
  <p style="margin-top:28px"><a class="cta" href="/#contact">See this running in your business &mdash; free 30-minute consultation</a></p>
  <h2>Services</h2><div class="links">{svc}</div>
  <h2>Industries</h2><div class="links">{ind}</div>
  <div class="foot">&copy; 2026 Strange Advanced Marketing. Miami, FL. &middot; <a href="/privacy/">Privacy</a> &middot; <a href="/terms/">Terms</a></div>
</div>
<script>
function circuit(el,seedOffset){{if(!el)return;const w=1600,h=el.parentElement.offsetHeight+100;let s=42+seedOffset;
const rnd=()=>{{s=(s*16807)%2147483647;return s/2147483647}};
let p="";let n="";
for(let i=0;i<26;i++){{let x=Math.floor(rnd()*w),y=Math.floor(rnd()*h);let path=`M${{x}} ${{y}}`;
for(let k=0;k<3;k++){{const dx=(rnd()>.5?1:-1)*(40+rnd()*120),dy=(rnd()>.5?1:-1)*(30+rnd()*90);
rnd()>.5?(x+=dx,path+=` h${{Math.round(dx)}}`):(y+=dy,path+=` v${{Math.round(dy)}}`)}}
p+=`<path d="${{path}}" fill="none" stroke="var(--trace)" stroke-width="1.4"/>`;
n+=`<circle cx="${{x}}" cy="${{y}}" r="3.2" fill="none" stroke="var(--node)" stroke-width="1.4"/>`}}
el.innerHTML=`<svg viewBox="0 0 ${{w}} ${{h}}" preserveAspectRatio="xMidYMid slice" style="opacity:.5">${{p}}${{n}}</svg>`}}
circuit(document.getElementById("circuit-head"),{abs(hash(vid))%50});
</script>
</body>
</html>
"""
    return slug, url, body

def main(ids):
    sm_path=os.path.join(ROOT,"sitemap.xml"); sm=open(sm_path,encoding="utf-8").read(); add=""
    for vid in ids:
        with tempfile.TemporaryDirectory() as tmp:
            info, vtt = fetch(vid, tmp)
        text=transcript(vtt)
        # DM -> direct messages (site copy, not TTS, but keep the brand rule consistent)
        text=re.sub(r"\bDM me\b","Message me",text); text=re.sub(r"\bDM\b","message",text)
        slug,url,body=page(vid,info,text)
        out=os.path.join(ROOT,"videos",slug); os.makedirs(out,exist_ok=True)
        open(os.path.join(out,"index.html"),"w",encoding="utf-8").write(body)
        if url not in sm: add+=f"  <url><loc>{url}</loc><lastmod>2026-08-22</lastmod></url>\n"
        assert "VideoObject" in body and len(text)>50, vid
        print(vid,"->",url,f"({len(text)} chars transcript)")
    if add: open(sm_path,"w",encoding="utf-8").write(sm.replace("</urlset>",add+"</urlset>"))

if __name__=="__main__":
    main(sys.argv[1:])
