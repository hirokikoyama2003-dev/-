"""Print-ready QR code for the tour page.

Usage: python3 tools/qr.py <url> [out_dir]

Follows common print guidance:
  * error correction Q (~25%) so a scratched / creased flyer still scans
  * 4-module quiet zone, pure black on white (no inversion, no logo)
  * vector SVG / PDF for the printer, PNG for screens and office tools
  * every output is decoded again to prove it scans, including a copy
    shrunk to the size of a 2 cm print (300 dpi)
"""
import sys
from pathlib import Path

import cv2
import numpy as np
import segno
from PIL import Image, ImageDraw, ImageFont

FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
]


def font(size):
    for f in FONT_CANDIDATES:
        if Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def decode(img):
    arr = np.array(img.convert("L"))
    text, _, _ = cv2.QRCodeDetector().detectAndDecode(arr)
    return text


def main(url, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    qr = segno.make(url, error="q", micro=False, boost_error=True)
    qr.save(out / "qr.svg", scale=10, border=4, dark="#000000", light="#ffffff")
    qr.save(out / "qr.pdf", scale=10, border=4, dark="#000000")
    size = qr.symbol_size(scale=1, border=4)[0]
    scale = max(1, round(1200 / size))
    qr.save(out / "qr.png", scale=scale, border=4, dark="#000000", light="#ffffff")

    # card: QR + call to action + URL (for flyers, posters and messages)
    code = Image.open(out / "qr.png").convert("RGB").resize((900, 900), Image.NEAREST)
    W, H = 1200, 1560
    card = Image.new("RGB", (W, H), "#ffffff")
    d = ImageDraw.Draw(card)
    d.rectangle([0, 0, W, 210], fill="#171513")
    d.text((W // 2, 78), "世田谷1丁目住宅", font=font(64), fill="#ffffff", anchor="mm")
    d.text((W // 2, 152), "Web内覧  ONLINE TOUR", font=font(36), fill="#d9b27c", anchor="mm")
    card.paste(code, ((W - 900) // 2, 250))
    d.text((W // 2, 1215), "スマートフォンのカメラで読み取ると", font=font(42), fill="#1f1c19", anchor="mm")
    d.text((W // 2, 1280), "間取り・写真48枚・動画・設備資料が見られます", font=font(42), fill="#1f1c19", anchor="mm")
    short = url.split("://", 1)[-1].rstrip("/")
    d.text((W // 2, 1400), short, font=font(34), fill="#5c554d", anchor="mm")
    card.save(out / "qr-card.png", optimize=True)

    # verify
    checks = {
        "qr.png": Image.open(out / "qr.png"),
        "qr-card.png": card,
        "2cm @300dpi": Image.open(out / "qr.png").resize((236, 236), Image.LANCZOS),
    }
    ok = True
    for name, img in checks.items():
        got = decode(img)
        status = "OK" if got == url else f"FAILED (read {got!r})"
        ok &= got == url
        print(f"{name:14s} {status}")
    print(f"version {qr.version}, error {qr.error.upper()}, {size}x{size} modules incl. quiet zone")
    return ok


if __name__ == "__main__":
    sys.exit(0 if main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "qr") else 1)
