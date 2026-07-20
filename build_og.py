"""Generate 1200x630 OG social share image for strangeadvancedmarketing.com (light theme, 7/19 rework)"""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1200, 630
HERE = os.path.dirname(__file__)
OUT_PNG = os.path.join(HERE, "og-image.png")
OUT_JPG = os.path.join(HERE, "og.jpg")
LOGO = os.path.join(HERE, "logo-light.png")

INK = (20, 27, 51)
MUT = (90, 100, 125)
ACCENT = (30, 111, 217)
TRACE = (207, 224, 243)
BG = (250, 251, 253)

FONT_BOLD = [r"C:\Windows\Fonts\georgiab.ttf", r"C:\Windows\Fonts\georgia.ttf", r"C:\Windows\Fonts\segoeuib.ttf"]
FONT_SERIF = [r"C:\Windows\Fonts\georgiai.ttf", r"C:\Windows\Fonts\georgia.ttf"]
FONT_REG = [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"]

def first_font(paths, size):
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

bg = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(bg)

# faint circuitry traces (the logo language)
import random
rnd = random.Random(7)
for _ in range(16):
    x, y = rnd.randint(0, W), rnd.randint(0, H)
    for _ in range(3):
        if rnd.random() > .5:
            nx = x + rnd.choice([-1, 1]) * rnd.randint(50, 150)
            draw.line([(x, y), (nx, y)], fill=TRACE, width=2)
            x = nx
        else:
            ny = y + rnd.choice([-1, 1]) * rnd.randint(35, 100)
            draw.line([(x, y), (x, ny)], fill=TRACE, width=2)
            y = ny
    draw.ellipse([x - 4, y - 4, x + 4, y + 4], outline=(169, 200, 233), width=2)

# top accent line
draw.rectangle([0, 0, W, 5], fill=ACCENT)

pad = 70
# logo lockup top-left
if os.path.exists(LOGO):
    logo = Image.open(LOGO).convert("RGBA")
    logo.thumbnail((360, 110), Image.LANCZOS)
    bg.paste(logo, (pad, 56), logo)

# headline
y_head = 220
h1 = first_font(FONT_BOLD, 78)
h1i = first_font(FONT_SERIF, 78)
draw.text((pad, y_head), "AI that actually", font=h1, fill=INK)
bbox = draw.textbbox((pad, y_head), "AI that actually", font=h1)
draw.text((bbox[2] + 22, y_head), "works.", font=h1i, fill=ACCENT)

tag = first_font(FONT_REG, 30)
draw.text((pad, y_head + 115), "AI agents, automated workflows & memory systems", font=tag, fill=MUT)
draw.text((pad, y_head + 158), "for real businesses. Deployed and supported by us.", font=tag, fill=MUT)

# bottom row
y_stats = H - 95
draw.line([(pad, y_stats - 24), (W - pad, y_stats - 24)], fill=(228, 234, 243), width=2)
num_f = first_font(FONT_BOLD, 34)
lbl_f = first_font(FONT_REG, 16)
stats = [("10-15 hrs", "SAVED PER WEEK"), ("Free", "30-MIN CONSULTATION"), ("24 hrs", "RESPONSE TIME")]
col_w = (W - 2 * pad) / 3
for i, (num, lbl) in enumerate(stats):
    cx = pad + int(col_w * i)
    draw.text((cx, y_stats), num, font=num_f, fill=ACCENT)
    draw.text((cx, y_stats + 46), lbl, font=lbl_f, fill=MUT)

url_f = first_font(FONT_REG, 20)
url = "strangeadvancedmarketing.com"
ub = draw.textbbox((0, 0), url, font=url_f)
draw.text((W - pad - (ub[2] - ub[0]), 66), url, font=url_f, fill=MUT)

bg.save(OUT_PNG, "PNG", optimize=True)
bg.save(OUT_JPG, "JPEG", quality=90)
print(f"Wrote {OUT_PNG} + {OUT_JPG}")
