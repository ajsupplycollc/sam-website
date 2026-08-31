"""Generate /services/* and /industries/* landing pages from one data dict.
Run: python _internal/build_pages.py   (from repo root). Idempotent; overwrites generated pages only.
ponytail: string template, no Jinja. Reuses the privacy-page head/styles verbatim."""
import json, os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://strangeadvancedmarketing.com"

SERVICES = {
 "ai-agents": dict(
  name="AI Agents for Small Business",
  kick="Service",
  h1="An AI agent that already knows your business and works it 24/7",
  answer="An AI agent from Strange Advanced Marketing is a private assistant trained on your pricing, your customers, and your voice. It sends quotes, chases invoices, triages your inbox, and books jobs — from a text or a voice note, in English or Spanish. We build it, deploy it, and support it.",
  desc="AI agents built for real businesses: quoting, follow-ups, inbox triage, and scheduling, run by voice note from your phone. Built, deployed, and supported by SAM in Miami, FL.",
  does=["Quotes customers from your real price list while they're still on the phone",
        "Follows up on open estimates and unpaid invoices without you remembering to",
        "Reads your inbox and tells you the three things that actually need you",
        "Answers by text or voice — you talk to it the way you text a foreman"],
  steps=[("Audit","We map how your business actually runs: tools, pricing, the hours that leak."),
         ("Build","The agent is wired to your tools (QuickBooks, Google, Jobber, Housecall Pro, Square) and loaded with your memory."),
         ("Run","It works every day. Nothing sends without your one-tap approval until you turn that off.")],
  fits=["Owner-operators doing paperwork after dinner","Shops where quotes wait until someone is back at a desk","Businesses with one person holding every customer's history in their head"],
  faq=[("Do I need to be technical?","No. You talk to it like you text. We handle the build, the hosting, and the support."),
       ("Will it send things without me?","Not unless you tell it to. Every outbound message starts with your one-tap approval."),
       ("Does it work in Spanish?","Yes. Typed or voice, English or Spanish."),
       ("What does it cost?","Start with a free 30-minute consultation. You'll leave with a roadmap and real numbers before anything is built.")],
 ),
 "automated-workflows": dict(
  name="Automated Workflows",
  kick="Service",
  h1="The repeatable stuff, made automatic",
  answer="Automated workflows from Strange Advanced Marketing handle lead capture and reply, missed-call text-back, invoice chasing, and inbox triage — connected to the tools you already run on. Every message still waits for your one-tap approval.",
  desc="Lead capture, missed-call text-back, invoice chasing, and inbox triage automated and connected to the tools you already use. Built and supported by SAM, Miami, FL.",
  does=["A new lead comes in from web, Angi, or a phone call and gets a reply in your voice within minutes",
        "Missed calls get a text back before the customer calls the next shop",
        "Open invoices get nudged on day 3, day 7, day 14 — automatically",
        "Your inbox is sorted into needs-you, handled, and noise"],
  steps=[("Map","We list every repeatable task that eats your week and rank them by hours saved."),
         ("Connect","Workflows plug into your existing tools. No new software to learn."),
         ("Approve","You approve with one tap from your phone. The workflow does the rest.")],
  fits=["Home-service and trade businesses living on inbound leads","Anyone who has lost a job because a call went to voicemail","Owners still chasing invoices by hand"],
  faq=[("Which tools do you connect to?","QuickBooks, Google Workspace, Jobber, Housecall Pro, CompanyCam, Square, Shopify, HubSpot, and most anything with an API."),
       ("What if a workflow gets something wrong?","Every outbound action is gated on your approval until you're confident. You can always see what it did and why."),
       ("How long does setup take?","Most first workflows are live within a week of the audit."),
       ("What does it cost?","Free 30-minute consultation first. We only scope what pays for itself.")],
 ),
 "memory-systems": dict(
  name="Business Memory Systems",
  kick="Service",
  h1="AI that actually remembers your business",
  answer="A memory system from Strange Advanced Marketing stores every customer, quote, job, and conversation and makes it searchable in plain English — then carries that history into every reply your AI writes. Ask what you quoted the Hendersons last spring and get the number in two seconds.",
  desc="Searchable business memory: every customer, quote, job, and conversation, answerable in plain English and carried into every AI reply. Built by SAM, Miami, FL.",
  does=["Ask any question about any customer, job, or quote and get the real answer",
        "Your AI's replies already know the history — no re-explaining",
        "Nothing lives only in someone's head or an old text thread",
        "Runs on your own machine if you want it to — your data never leaves"],
  steps=[("Ingest","We pull in your existing records: invoices, emails, texts, spreadsheets, CRM."),
         ("Connect","Every new interaction is captured automatically going forward."),
         ("Ask","You ask questions out loud. It answers from your real data.")],
  fits=["Businesses with years of customers and no system of record","Owners who are the only one who knows the history","Anyone about to hire and needing to hand off knowledge"],
  faq=[("Where does my data live?","Cloud or on a machine you own. Sovereign deployments keep everything on your hardware."),
       ("Does it replace my CRM?","No. It sits alongside whatever you use and makes it answerable."),
       ("How far back can it go?","As far back as your records go. We've loaded 15 years of history."),
       ("What does it cost?","Free 30-minute consultation, then a fixed scope with real numbers.")],
 ),
 "ai-strategy": dict(
  name="AI Strategy & Audit",
  kick="Service",
  h1="Not sure where to start? Start with the audit.",
  answer="The Strange Advanced Marketing AI audit maps how your business actually runs — tools, workflows, and where the hours leak — and hands you a roadmap with real numbers: what to build first, what it costs, and what it gives back.",
  desc="An AI strategy audit for small business: what to automate first, what it costs, what it returns. From SAM, Miami, FL. Starts with a free 30-minute consultation.",
  does=["A ranked list of what to automate first, by hours saved",
        "Real cost and payback numbers, not a pitch deck",
        "A map of your tools and how they should talk to each other",
        "A plan you can hand to anyone — including us"],
  steps=[("Discover","A free 30-minute call. We learn how the business runs today."),
         ("Audit","We go through your tools, your week, and your numbers."),
         ("Roadmap","You get the plan. Build with us or don't — it's yours.")],
  fits=["Owners who know AI should be helping and don't know where","Businesses that tried a chatbot and got nothing out of it","Anyone planning a hire they'd rather not make"],
  faq=[("Is the consultation really free?","Yes. 30 minutes, no pitch. You leave with at least one thing you can do yourself."),
       ("Do I have to build with you afterward?","No. The roadmap is yours either way."),
       ("How long does the audit take?","Usually one to two weeks from the first call."),
       ("What does it cost?","The discovery call is free. Audit pricing is quoted on the call based on the size of the business.")],
 ),
 "ai-setup-rescue": dict(
  name='AI Setup Rescue',
  kick='Service',
  h1='Your AI setup worked for a week. We fix that.',
  answer='Strange Advanced Marketing repairs AI setups that small businesses built themselves and that stopped working: chatbots that went quiet, Zapier and Make automations that silently quit, custom GPT or Claude projects that drifted, agents that answer wrong. We find the real cause, fix it, and leave it monitored so you know if it ever breaks again.',
  desc='We fix broken AI setups for small businesses: dead chatbots, silent Zapier and Make automations, drifting GPT or Claude builds. Diagnosis first, then a real quote. SAM, Miami, FL.',
  does=['Your chatbot answers again, and answers right', 'Silent automations found and restarted, with an alarm on them this time', 'A straight answer on what broke, in plain English', 'A monitor that tells you the day something stops, instead of a customer telling you a month later'],
  steps=[('Diagnose', "A free look at what you built and what it's doing now. We tell you what broke and what the fix costs before anything starts."), ('Fix', "We repair the setup you have, or tell you honestly when it's cheaper to rebuild it right."), ('Watch', 'The fixed setup gets a health check that pings you if it ever stops working again.')],
  fits=['Owners who built something with a no-code tool and it quietly died', 'Businesses that paid someone for a chatbot that customers stopped using', 'Anyone whose automation ran for months and stopped after an update'],
  faq=[('What kinds of setups do you fix?', 'Chatbots, Zapier and Make and n8n automations, custom GPTs, Claude projects, and AI agents other people built.'), ('What does a rescue cost?', 'The diagnosis is free. Most repairs land between a $500 fix and a $1,500 rebuild, quoted before we start.'), ('Did I do something wrong?', "Usually not. Tools update, APIs change, and setups built once with no monitoring break silently. That's the normal failure mode, not a user error."), ("Can you make it so this doesn't happen again?", 'Yes. Every rescue leaves with monitoring, so silence gets caught the same day.')],
 ),
 "pricing": dict(
  name='What AI Setup Actually Costs',
  kick='Pricing',
  h1='Real numbers, before you ever get on a call',
  answer='Strange Advanced Marketing publishes its pricing: entry setups start at $500, a full AI employee stack starts at $1,500, and rescue work on broken setups is quoted after a free diagnosis. Here is what each tier includes and how that compares to doing it yourself or hiring a dev shop.',
  desc='AI setup pricing for small businesses, published: $500 entry setups, $1,500+ full agent stacks, rescue quotes after a free diagnosis. SAM, Miami, FL.',
  does=['$500 entry setup: one working assistant on your machine, wired to your phone, doing one job well', '$1,500 and up, full stack: agents, automated workflows, business memory, a dashboard, and support', 'Rescue work: free diagnosis first, then a quote, most land between a fix and a rebuild', 'No subscriptions required to start. You own what we build.'],
  steps=[('Compare', "DIY no-code tools run free to about $100 a month, and you do all the work and the babysitting. Dev shops start around $15,000. We're the middle: done for you, small-business priced."), ('Scope', 'A free 30-minute call. You leave with a number for your situation, not a range.'), ('Build', 'Fixed scope, stated price, your approval on everything that goes out.')],
  fits=['Owners comparing us against buying software and figuring it out themselves', 'Businesses burned by open-ended agency retainers', 'Anyone who wants the number before the pitch'],
  faq=[('Why publish prices?', "Because every competitor page says 'book a call.' You should know if we're in your budget before you spend 30 minutes with us."), ("What's the monthly cost after setup?", 'Entry setups can run with no monthly fee. Full stacks include a support plan we scope with you, stated up front.'), ('Is the $500 setup real or a teaser?', "Real. One assistant, one job, working on your own machine. It's how several of our clients started."), ('What about big custom builds?', 'If your scope is genuinely bigger than a full stack, we say so and quote it fixed, or tell you if a dev shop is the better fit.')],
 ),
}

# Industries mirror the public "Recent builds" cards — anonymized, no client names (see feedback_nothing_client_facing_without_approval).
INDUSTRIES = {
 "auto-glass": dict(
  name="AI for Auto Glass Shops", kick="Industry",
  h1="Windshield quotes while the customer is still on the phone",
  answer="Strange Advanced Marketing builds AI agents for auto glass shops that quote from your real parts data, follow up on open estimates, and answer the phone's overflow by text — so quotes go out in the moment instead of after dinner.",
  desc="AI quoting and follow-up for auto glass shops, wired to your real parts data. Built and supported by SAM, Miami, FL.",
  does=["Instant quotes from your actual parts and labor data","Missed-call text-back so the customer doesn't call the next shop","Estimate follow-up on a schedule you set","A site built to rank for the searches that bring in jobs"],
  steps=[("Audit","We look at how quotes happen today and where they stall."),("Build","Quoting agent wired to your parts data and your phone line."),("Run","Quotes go out live. You approve with one tap.")],
  fits=["Single-location shops where the owner quotes everything","Shops losing after-hours calls to competitors","Anyone whose quotes wait until someone is at a desk"],
  faq=[("Does it know my parts pricing?","Yes. It quotes from your data, not a generic table."),("Can it handle insurance jobs?","It drafts; you approve. Insurance-specific steps stay in your hands."),("What does it cost?","Free 30-minute consultation first.")],
  proof="South Florida auto glass shop: instant windshield quoting wired to real parts data, plus a 12-page site built to rank. Quotes that used to wait until after dinner now go out while the customer is still on the phone.",
 ),
 "lawn-care-landscaping": dict(
  name="AI for Lawn Care & Landscaping", kick="Industry",
  h1="The after-dark paperwork shift is gone",
  answer="Strange Advanced Marketing builds pocket-office agents for lawn care and landscaping operators that quote, invoice, and remember every customer conversation — run by voice note from the truck.",
  desc="A pocket-office AI agent for lawn care and landscaping: quotes, invoices, and customer memory by voice note. Built by SAM, Miami, FL.",
  does=["Quote a job from the truck by voice note","Invoices sent and chased automatically","Every customer's history answerable in plain English","Landscape supply and turf pricing loaded in"],
  steps=[("Audit","We map your route, your pricing, and your paperwork."),("Build","Agent wired to your invoicing and your phone."),("Run","You talk, it works. Approve with one tap.")],
  fits=["Owner-operators doing invoices at 10pm","Crews growing past what one person can remember","Turf and landscape supply businesses with repeat customers"],
  faq=[("Can I use it from the truck?","Yes. Voice note in, quote out."),("Does it do recurring billing?","Yes, with your approval gate."),("What does it cost?","Free 30-minute consultation first.")],
  proof="Lawn care operator: a pocket-office agent that quotes, invoices, and remembers every customer conversation. The after-dark paperwork shift is gone.",
 ),
 "ecommerce": dict(
  name="AI for Shopify & E-commerce Brands", kick="Industry",
  h1="Run the store from your phone, by voice note",
  answer="Strange Advanced Marketing builds Telegram agents wired into Shopify stores: orders, customers, and daily numbers answered by voice note — no dashboard logins, no end-of-day spreadsheet ritual.",
  desc="A voice-driven AI agent wired into Shopify: orders, customers, and daily numbers from your phone. Built by SAM, Miami, FL.",
  does=["Daily numbers, delivered, not looked up","Customer and order questions answered instantly","Inventory and fulfillment flags before they become problems","Replies to customers drafted in your voice"],
  steps=[("Audit","We map your store, your apps, and your daily ritual."),("Build","Agent wired to Shopify and your support inbox."),("Run","Ask it anything. Approve what goes out.")],
  fits=["Founder-run brands without an ops hire","Stores with a daily spreadsheet ritual","Anyone checking five dashboards a day"],
  faq=[("Does it work with Shopify?","Yes, natively. Other platforms on request."),("Can it answer customer emails?","It drafts; you approve with one tap."),("What does it cost?","Free 30-minute consultation first.")],
  proof="Shopify apparel brand: a Telegram agent wired into the store. The owner runs it from his phone. No dashboard logins, no end-of-day spreadsheet ritual.",
 ),
 "distributors-wholesale": dict(
  name="AI for Distributors & Multi-Company Owners", kick="Industry",
  h1="Ask your books a question out loud. Get the real number back.",
  answer="Strange Advanced Marketing builds always-on agents for distributors and owners of multiple companies: a command dashboard across every entity, QuickBooks wired in read-only, and an agent that runs on a machine you own.",
  desc="An always-on AI agent and command dashboard for distributors and multi-company owners, with QuickBooks wired in read-only. Built by SAM, Miami, FL.",
  does=["One dashboard across every company you own","QuickBooks questions answered out loud, read-only and safe","Runs on your own hardware — sovereign, your data stays","Reorder, receivables, and vendor follow-up handled"],
  steps=[("Audit","We map every entity, every tool, every number you check."),("Build","Agent on your machine, dashboard across the portfolio, QuickBooks connected read-only."),("Run","Ask. Approve. It works while you don't.")],
  fits=["Owners juggling two or more companies","Distributors with receivables slipping","Anyone who wants AI without their data leaving the building"],
  faq=[("Is QuickBooks access safe?","Read-only. It can answer, it cannot change your books."),("Does it have to run in the cloud?","No. Sovereign deployments run on hardware you own."),("What does it cost?","Free 30-minute consultation first.")],
  proof="Peptide distributor, multiple companies: an always-on agent on his own machine, a command dashboard across every company, and QuickBooks wired in read-only. He asks his books a question out loud and gets the real number back in seconds.",
 ),
 "home-services-contractors": dict(
  name="AI for Contractors & Home Services", kick="Industry",
  h1="Every lead answered. Every estimate followed up.",
  answer="Strange Advanced Marketing builds AI agents and workflows for contractors and home-service businesses: lead reply in minutes, missed-call text-back, estimate follow-up, and invoice chasing — connected to Jobber, Housecall Pro, CompanyCam, and QuickBooks.",
  desc="AI lead reply, missed-call text-back, estimate follow-up, and invoice chasing for contractors and home services. Built by SAM, Miami, FL.",
  does=["Leads from web, Angi, and calls get a reply in your voice within minutes","Missed calls get a text back","Estimates followed up on day 3, 7, 14","Invoices chased without you"],
  steps=[("Audit","We map where leads come from and where they die."),("Build","Workflows wired to your field software and your phone."),("Run","You approve with one tap. The rest is handled.")],
  fits=["Roofing, paving, pool, HVAC, electrical, plumbing, remodel","Anyone paying for leads and losing them to voicemail","Businesses where the owner is the only closer"],
  faq=[("Which field software do you support?","Jobber, Housecall Pro, CompanyCam, ServiceTitan, QuickBooks, Google."),("Will it talk to my customers without me?","Only with your approval, until you decide otherwise."),("What does it cost?","Free 30-minute consultation first.")],
  proof=None,
 ),
}

def head_css():
    src = open(os.path.join(ROOT, "privacy", "index.html"), encoding="utf-8").read()
    return re.search(r"<style>.*?</style>", src, re.S).group(0)

EXTRA_CSS = """<style>
.answer{font-size:1.15rem;color:var(--ink);line-height:1.6;margin-bottom:8px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin:18px 0 8px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px}
.card .n{font-family:var(--serif);font-size:1.5rem;color:var(--accent);line-height:1}
.card h3{font-size:1rem;margin:8px 0 6px;color:var(--ink)}
.card p{margin:0;font-size:15px}
.proof{border-left:3px solid var(--accent);padding:10px 16px;background:var(--panel);border-radius:0 10px 10px 0;margin:18px 0}
.cta{display:inline-block;background:var(--accent);color:#fff;padding:13px 22px;border-radius:10px;font-weight:600;margin-top:10px}
.cta:hover{background:var(--accent-ink);text-decoration:none}
.links a{display:inline-block;margin:0 14px 8px 0;font-size:15px}
details{border-top:1px solid var(--line);padding:12px 0}
summary{cursor:pointer;color:var(--ink);font-weight:600}
details p{margin:8px 0 0}
</style>"""

def page(slug, kind, d):
    url = f"{SITE}/{kind}/{slug}/"
    e = html.escape
    faq_ld = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in d["faq"]]}
    svc_ld = {"@context":"https://schema.org","@type":"Service","name":d["name"],"url":url,
        "description":d["desc"],"areaServed":["Miami, FL","United States"],
        "provider":{"@type":"Organization","name":"Strange Advanced Marketing","url":SITE+"/","email":"sam@strangeadvancedmarketing.com"}}
    does = "".join(f"<li>{e(x)}</li>" for x in d["does"])
    steps = "".join(f'<div class="card"><div class="n">{i+1}</div><h3>{e(t)}</h3><p>{e(p)}</p></div>' for i,(t,p) in enumerate(d["steps"]))
    fits = "".join(f"<li>{e(x)}</li>" for x in d["fits"])
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q,a in d["faq"])
    proof = f'<div class="proof"><b>Running right now:</b> {e(d["proof"])}</div>' if d.get("proof") else ""
    other = "".join(f'<a href="/services/{s}/">{e(SERVICES[s]["name"])}</a>' for s in SERVICES if not (kind=="services" and s==slug))
    other_ind = "".join(f'<a href="/industries/{s}/">{e(INDUSTRIES[s]["name"])}</a>' for s in INDUSTRIES if not (kind=="industries" and s==slug))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(d["name"])} | Strange Advanced Marketing</title>
<meta name="description" content="{e(d["desc"])}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{e(d["name"])} — Strange Advanced Marketing">
<meta property="og:description" content="{e(d["desc"])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/og.jpg">
<meta name="theme-color" content="#fafbfd">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<script type="application/ld+json">{json.dumps(svc_ld)}</script>
<script type="application/ld+json">{json.dumps(faq_ld)}</script>
{head_css()}
{EXTRA_CSS}
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
    <div class="kick">{e(d["kick"])}</div>
    <h1>{e(d["h1"])}</h1>
  </div>
</header>
<div class="wrap">
  <p class="answer">{e(d["answer"])}</p>
  {proof}
  <h2>What it does</h2>
  <ul>{does}</ul>
  <h2>How it works</h2>
  <div class="grid">{steps}</div>
  <h2>Who it fits</h2>
  <ul>{fits}</ul>
  <h2>Questions we get</h2>
  {faq}
  <p style="margin-top:28px"><a class="cta" href="/#contact">Book a free 30-minute consultation</a></p>
  <h2>Services</h2><div class="links">{other}</div>
  <h2>Industries</h2><div class="links">{other_ind}</div>
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
circuit(document.getElementById("circuit-head"),{sum(map(ord,slug))%50});
</script>
</body>
</html>
"""

def main():
    urls = []
    for kind, data in (("services", SERVICES), ("industries", INDUSTRIES)):
        for slug, d in data.items():
            out = os.path.join(ROOT, kind, slug)
            os.makedirs(out, exist_ok=True)
            open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(page(slug, kind, d))
            urls.append(f"{SITE}/{kind}/{slug}/")
    # sitemap: append any missing generated urls
    sm_path = os.path.join(ROOT, "sitemap.xml"); sm = open(sm_path, encoding="utf-8").read()
    add = "".join(f"  <url><loc>{u}</loc><lastmod>2026-08-22</lastmod></url>\n" for u in urls if u not in sm)
    if add:
        sm = sm.replace("</urlset>", add + "</urlset>"); open(sm_path, "w", encoding="utf-8").write(sm)
    print(f"wrote {len(urls)} pages; sitemap +{add.count('<url>')}")
    # self-check
    for u in urls:
        f = os.path.join(ROOT, u[len(SITE)+1:], "index.html"); t = open(f, encoding="utf-8").read()
        assert 'name="description"' in t and "FAQPage" in t and "/#contact" in t, f
        assert "zip" not in t.lower() and "33" not in re.findall(r"\b33\d{3}\b", t), f  # no address leak
    print("self-check ok")

if __name__ == "__main__":
    main()

# Case studies — copy limited to what is ALREADY public on the homepage "Recent builds" cards (no client names, no numbers
# Jereme hasn't published). Expand only after he approves naming.  (feedback_never_invent_client_facing_options)
CASES = {
 "auto-glass-instant-quoting": dict(ind="auto-glass", name="Auto glass shop, South Florida",
  h1="Quotes that used to wait until after dinner now go out while the customer is on the phone",
  before="Every windshield quote ran through the owner. Calls came in all day; quotes went out at night, after the shop closed — and some customers had already called the next shop.",
  built=["Instant quoting wired to the shop's real parts data","Missed-call text-back and estimate follow-up","A 12-page website built to rank for the searches that bring in jobs"],
  after="Quotes go out while the customer is still on the phone. The owner approves with one tap instead of typing every quote by hand."),
 "shopify-brand-voice-agent": dict(ind="ecommerce", name="Shopify apparel brand",
  h1="The owner runs the store from his phone, by voice note",
  before="Running the store meant logging into Shopify, checking five dashboards, and an end-of-day spreadsheet ritual.",
  built=["A Telegram agent wired into the store: orders, customers, and daily numbers","Voice-note in, answer out","Customer replies drafted in the owner's voice, sent on approval"],
  after="No dashboard logins, no end-of-day spreadsheet. The owner asks and gets the number."),
 "lawn-care-pocket-office": dict(ind="lawn-care-landscaping", name="Lawn care operator",
  h1="The after-dark paperwork shift is gone",
  before="Quotes, invoices, and customer history all lived in the owner's head and his phone. Office work happened at 9pm.",
  built=["A pocket-office agent that quotes and invoices from the truck","Memory of every customer conversation, answerable in plain English","Invoice chasing on a schedule"],
  after="The agent works the paperwork shift instead. The owner's evenings are his again."),
 "multi-company-distributor-command-center": dict(ind="distributors-wholesale", name="Peptide distributor, multiple companies",
  h1="He asks his books a question out loud and gets the real number back in seconds",
  before="Several companies, several sets of books, and no single place to see them. Every number meant opening QuickBooks and digging.",
  built=["An always-on agent running on his own machine (sovereign — his data stays with him)","A command dashboard across every company","QuickBooks wired in read-only"],
  after="One question, one answer, across the whole portfolio. Nothing can change the books; everything can be asked."),
}

def case_page(slug, d):
    e=html.escape; url=f"{SITE}/work/{slug}/"; ind=INDUSTRIES[d["ind"]]
    built="".join(f"<li>{e(x)}</li>" for x in d["built"])
    ld={"@context":"https://schema.org","@type":"Article","headline":d["h1"],"about":d["name"],"url":url,
        "author":{"@type":"Organization","name":"Strange Advanced Marketing","url":SITE+"/"},"datePublished":"2026-08-22"}
    others="".join(f'<a href="/work/{s}/">{e(c["name"])}</a>' for s,c in CASES.items() if s!=slug)
    tpl=page("auto-glass","industries",INDUSTRIES["auto-glass"])   # borrow head/nav/footer/script verbatim
    head=tpl.split("<body>")[0]; tail="<script>"+tpl.split("<script>")[-1]
    head=re.sub(r"<title>.*?</title>",f"<title>{e(d['name'])} — case study | Strange Advanced Marketing</title>",head)
    head=re.sub(r'<meta name="description" content=".*?">',f'<meta name="description" content="{e(d["h1"])}. What we built for a {e(d["name"].lower())} and what changed.">',head)
    head=re.sub(r'<link rel="canonical" href=".*?">',f'<link rel="canonical" href="{url}">',head)
    head=re.sub(r'<meta property="og:(title|description|url)" content=".*?">',"",head)
    head=re.sub(r'<script type="application/ld\+json">.*?</script>\s*',"",head,flags=re.S)
    head=head.replace("</head>",f'<script type="application/ld+json">{json.dumps(ld)}</script>\n</head>')
    body=f"""<body>
<nav><div class="nav-in">
  <a href="/"><img src="/logo-light.png" alt="Strange Advanced Marketing"></a>
  <a class="nav-back" href="/#contact">Book a free consultation &rarr;</a>
</div></nav>
<header class="head"><div class="circuit" id="circuit-head"></div><div class="head-in">
  <div class="kick">Case study &middot; {e(d["name"])}</div><h1>{e(d["h1"])}</h1></div></header>
<div class="wrap">
  <h2>Before</h2><p>{e(d["before"])}</p>
  <h2>What we built</h2><ul>{built}</ul>
  <h2>After</h2><p class="answer">{e(d["after"])}</p>
  <p style="margin-top:28px"><a class="cta" href="/#contact">See this running in your business &mdash; free 30-minute consultation</a></p>
  <h2>Related</h2><div class="links"><a href="/industries/{d["ind"]}/">{e(ind["name"])}</a>{others}</div>
  <div class="foot">&copy; 2026 Strange Advanced Marketing. Miami, FL. &middot; <a href="/privacy/">Privacy</a> &middot; <a href="/terms/">Terms</a></div>
</div>
"""
    return head+body+tail

def build_cases():
    sm_path=os.path.join(ROOT,"sitemap.xml"); sm=open(sm_path,encoding="utf-8").read(); add=""
    for slug,d in CASES.items():
        out=os.path.join(ROOT,"work",slug); os.makedirs(out,exist_ok=True)
        t=case_page(slug,d); open(os.path.join(out,"index.html"),"w",encoding="utf-8").write(t)
        assert t.count("<h1>")==1 and "Article" in t and 'canonical" href="'+SITE+"/work/" in t
        u=f"{SITE}/work/{slug}/"
        if u not in sm: add+=f"  <url><loc>{u}</loc><lastmod>2026-08-22</lastmod></url>\n"
    if add: open(sm_path,"w",encoding="utf-8").write(sm.replace("</urlset>",add+"</urlset>"))
    print("cases:",len(CASES))
