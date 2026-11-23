"""Make web images from the original photos.

Usage: python3 tools/images.py <dir with 0.JPG ... 47.JPG>

  img/{n}-l.webp   1600px long edge  (lightbox)
  img/{n}-t.webp    520px long edge  (thumbnails)
  img/{n}-m.webp    960px long edge  (highlight cards)
  img/hero-640.webp, img/hero-1000.webp  (exterior, hero)
  img/og.jpg        1200x630 share image

EXIF (camera data, orientation) is applied and then dropped.
"""
import sys
from pathlib import Path

from PIL import Image, ImageOps

from data import HIGHLIGHTS

OUT = Path(__file__).resolve().parent.parent / "site" / "img"


def load(src, n):
    return ImageOps.exif_transpose(Image.open(src / f"{n}.JPG")).convert("RGB")


def save(im, box, name, q):
    im = im.copy()
    im.thumbnail(box, Image.LANCZOS)
    im.save(OUT / name, "WEBP", quality=q, method=6)


def main(src):
    src = Path(src)
    OUT.mkdir(parents=True, exist_ok=True)
    for n in range(48):
        im = load(src, n)
        save(im, (1600, 1600), f"{n}-l.webp", 80)
        save(im, (520, 520), f"{n}-t.webp", 72)
    for pid, *_ in HIGHLIGHTS:
        save(load(src, pid), (960, 960), f"{pid}-m.webp", 76)
    hero = load(src, 0)
    for w in (640, 1000):
        h = round(hero.height * w / hero.width)
        hero.resize((w, h), Image.LANCZOS).save(OUT / f"hero-{w}.webp", "WEBP", quality=74, method=6)
    og = ImageOps.fit(load(src, 25), (1200, 630), Image.LANCZOS)
    og.save(OUT / "og.jpg", "JPEG", quality=82, optimize=True, progressive=True)


if __name__ == "__main__":
    main(sys.argv[1])
