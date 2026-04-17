"""Generate 1200x630 OG social share image for strangeadvancedmarketing.com"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

W, H = 1200, 630
OUT = os.path.join(os.path.dirname(__file__), "og-image.png")
LOGO = os.path.join(os.path.dirname(__file__), "sam-circle.png")

# Fonts — try Inter, fall back to Windows system fonts
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\Inter-Black.ttf",
    r"C:\Windows\Fonts\segoeuib.ttf",  # Segoe UI Bold
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\Arial.ttf",
]
FONT_REGULAR = [
    r"C:\Windows\Fonts\Inter-Regular.ttf",
    r"C:\Windows\Fonts\segoeui.ttf",
    r"C:\Windows\Fonts\arial.ttf",
]

def first_font(paths, size):
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

# Base gradient background — navy to black, matches hero
bg = Image.new("RGB", (W, H), (10, 10, 10))
draw = ImageDraw.Draw(bg)
for y in range(H):
    # radial-ish: darker corners, tinted blue center
    t = abs(y - H / 2) / (H / 2)
    r = int(10 + (26 - 10) * (1 - t) * 0.6)
    g = int(10 + (26 - 10) * (1 - t) * 0.6)
    b = int(10 + (46 - 10) * (1 - t) * 0.9)
    draw.line([(0, y), (W, y)], fill=(r, g, b))

# Subtle cyan accent line at top (scan line effect)
for x in range(W):
    alpha = int(180 * (1 - abs(x - W/2) / (W/2)) ** 2)
    if alpha > 0:
        draw.point((x, 2), fill=(0, 212, 255))
        draw.point((x, 3), fill=(0, 212, 255))

# Left column: logo + brand label + headline + stats
padding_x = 70
y = 80

# Logo
if os.path.exists(LOGO):
    logo = Image.open(LOGO).convert("RGBA")
    logo.thumbnail((110, 110), Image.LANCZOS)
    bg.paste(logo, (padding_x, y), logo)

# Brand label
font_label = first_font(FONT_REGULAR, 22)
draw.text((padding_x + 130, y + 25), "STRANGE ADVANCED MARKETING",
          font=font_label, fill=(0, 212, 255))
draw.text((padding_x + 130, y + 55), "AI systems. Voice-driven. Built in Miami.",
          font=first_font(FONT_REGULAR, 20), fill=(153, 153, 153))

# Headline
y_head = y + 155
font_h1 = first_font(FONT_CANDIDATES, 72)
font_h1_accent = first_font(FONT_CANDIDATES, 72)
# "S.A.M" in cyan
draw.text((padding_x, y_head), "S.A.M", font=font_h1, fill=(0, 212, 255))
# measure
bbox = draw.textbbox((padding_x, y_head), "S.A.M", font=font_h1)
after_sam_x = bbox[2] + 18
draw.text((after_sam_x, y_head), "builds AI systems", font=font_h1, fill=(255, 255, 255))

# Line 2
draw.text((padding_x, y_head + 85), "that run your business.",
          font=font_h1, fill=(255, 255, 255))

# Tagline
font_tag = first_font(FONT_REGULAR, 26)
draw.text((padding_x, y_head + 190),
          "You talk. AI executes. Quoting, scheduling, follow-ups — via voice note.",
          font=font_tag, fill=(204, 204, 204))

# Bottom stats row
y_stats = H - 100
stat_font_num = first_font(FONT_CANDIDATES, 40)
stat_font_lbl = first_font(FONT_REGULAR, 15)

stats = [
    ("353+", "SESSIONS"),
    ("9", "LIVE PRODUCTS"),
    ("100%", "VOICE-TO-EXEC"),
    ("<60 sec", "RESPONSE"),
]
col_w = (W - 2 * padding_x) / len(stats)
for i, (num, lbl) in enumerate(stats):
    cx = padding_x + int(col_w * i)
    draw.text((cx, y_stats), num, font=stat_font_num, fill=(0, 212, 255))
    draw.text((cx, y_stats + 54), lbl, font=stat_font_lbl, fill=(102, 102, 102))

# Separator above stats
draw.line([(padding_x, y_stats - 20), (W - padding_x, y_stats - 20)], fill=(30, 42, 58), width=1)

# URL in top right
font_url = first_font(FONT_REGULAR, 18)
url = "strangeadvancedmarketing.com"
bbox = draw.textbbox((0, 0), url, font=font_url)
url_w = bbox[2] - bbox[0]
draw.text((W - padding_x - url_w, 40), url, font=font_url, fill=(102, 102, 102))

bg.save(OUT, "PNG", optimize=True)
print(f"Wrote {OUT} ({os.path.getsize(OUT)} bytes)")
