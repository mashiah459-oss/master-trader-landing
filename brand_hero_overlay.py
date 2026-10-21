"""
Stamp crisp Hebrew brand name + slogan onto a clean abstract scene (cool-blue).
AI mangles Hebrew, so the scene is generated text-free and the text is baked here.
Usage: python3 brand_hero_overlay.py <src.png> <out.png> "<slogan>"
"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from bidi.algorithm import get_display

SRC = sys.argv[1] if len(sys.argv) > 1 else "images/club-hero-abs-1.png"
OUT = sys.argv[2] if len(sys.argv) > 2 else "images/club-hero-branded.png"
SLOGAN = sys.argv[3] if len(sys.argv) > 3 else "המקום הבריא לסוחר היומי"
BRAND = "מועדון הסוחר המתמיד"

WHITE = (238, 242, 248)
BLUE = (143, 184, 255)      # #8fb8ff accent
INK = (176, 188, 206)
FD = "/System/Library/Fonts/Supplemental/"
F_BOLD = FD + "Arial Bold.ttf"
F_REG = FD + "Arial.ttf"


def heb(s):
    return get_display(s)


def font(size, bold=True):
    return ImageFont.truetype(F_BOLD if bold else F_REG, size)


def center_x(d, W, text, fnt, stroke=0):
    bb = d.textbbox((0, 0), text, font=fnt, stroke_width=stroke)
    return (W - (bb[2] - bb[0])) / 2 - bb[0], bb


def draw_center(d, W, cy, text, fnt, fill, stroke=0, shadow=True):
    x, bb = center_x(d, W, text, fnt, stroke)
    y = cy - (bb[3] - bb[1]) / 2 - bb[1]
    if shadow:
        d.text((x + 2, y + 3), text, font=fnt, fill=(0, 0, 0, 170), stroke_width=stroke)
    d.text((x, y), text, font=fnt, fill=fill, stroke_width=stroke,
           stroke_fill=fill if stroke else None)
    return y


def spaced(d, W, cy, text, fnt, fill, sp):
    ws = [d.textbbox((0, 0), c, font=fnt)[2] for c in text]
    x = (W - (sum(ws) + sp * (len(text) - 1))) / 2
    for c, w in zip(text, ws):
        d.text((x, cy), c, font=fnt, fill=fill)
        x += w + sp


def main():
    img = Image.open(SRC).convert("RGB")
    W = 1600
    H = int(img.height * W / img.width)
    img = img.resize((W, H), Image.LANCZOS)

    # soft center band scrim so text reads over the chart
    scrim = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(scrim)
    top, bot = int(H * 0.20), int(H * 0.80)
    mid = (top + bot) / 2
    for y in range(top, bot):
        t = 1 - abs(y - mid) / (mid - top)          # 0..1..0 feather
        sd.line([(0, y), (W, y)], fill=int(165 * (t ** 1.1)))
    scrim = scrim.filter(ImageFilter.GaussianBlur(26))
    dark = Image.new("RGB", (W, H), (8, 11, 18))
    img = Image.composite(dark, img, scrim).convert("RGBA")

    d = ImageDraw.Draw(img, "RGBA")

    # eyebrow (Latin, letter-spaced)
    eb = font(30)
    spaced(d, W, int(H * 0.30), list("MASTERTRADER"), eb, (*BLUE, 235), sp=10)

    # brand name — bold white with a soft blue glow
    bf = font(int(W * 0.066))                       # ~106px
    bt = heb(BRAND)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gx, gbb = center_x(gd, W, bt, bf)
    gy = int(H * 0.45) - (gbb[3] - gbb[1]) / 2 - gbb[1]
    gd.text((gx, gy), bt, font=bf, fill=(*BLUE, 255))
    glow = glow.filter(ImageFilter.GaussianBlur(22))
    img = Image.alpha_composite(img, glow)
    d = ImageDraw.Draw(img, "RGBA")
    draw_center(d, W, int(H * 0.45), bt, bf, WHITE, stroke=1)

    # thin blue divider
    d.line([(W * 0.36, int(H * 0.565)), (W * 0.64, int(H * 0.565))], fill=(*BLUE, 220), width=2)

    # slogan
    sf = font(int(W * 0.034), bold=False)           # ~54px
    draw_center(d, W, int(H * 0.64), heb(SLOGAN), sf, (*INK, 255), shadow=True)

    img.convert("RGB").save(OUT)
    print(f"saved {OUT}  ({W}x{H})  slogan={SLOGAN}")


if __name__ == "__main__":
    main()
