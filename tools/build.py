"""Build site/index.html from tools/template.html, data.py and plans.py.

Usage:  python3 tools/build.py
Images in site/img must already exist (see README for how they were made).
"""
import html
import json
import re
from pathlib import Path

from data import DOCS, FLOOR_SUMMARY, HIGHLIGHTS, PHOTOS, SECTIONS, SIZES, VIDEO
from plans import FLOORS

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
IMG = SITE / "img"

SVG_FONT = ("font-family=\"'Hiragino Sans','Hiragino Kaku Gothic ProN','Noto Sans JP','Yu Gothic',Meiryo,sans-serif\" "
            "text-anchor=\"middle\" dominant-baseline=\"central\"")


def abs_xy(floor, px, py):
    w, h = SIZES[floor]
    return round(px / 100 * w, 1), round(py / 100 * h, 1)


def webp_size(path):
    """Width/height of a WebP file (VP8, VP8L and VP8X)."""
    b = path.read_bytes()
    fmt = b[12:16]
    if fmt == b"VP8X":
        return 1 + int.from_bytes(b[24:27], "little"), 1 + int.from_bytes(b[27:30], "little")
    if fmt == b"VP8 ":
        return int.from_bytes(b[26:28], "little") & 0x3FFF, int.from_bytes(b[28:30], "little") & 0x3FFF
    if fmt == b"VP8L":
        v = int.from_bytes(b[21:25], "little")
        return (v & 0x3FFF) + 1, ((v >> 14) & 0x3FFF) + 1
    raise ValueError(path)


def pdf_pages(path):
    data = path.read_bytes()
    counts = [int(m) for m in re.findall(rb"/Type\s*/Pages\b[^>]*?/Count\s+(\d+)", data)]
    counts += [int(m) for m in re.findall(rb"/Count\s+(\d+)[^>]*?/Type\s*/Pages\b", data)]
    return max(counts) if counts else None


def esc(s):
    return html.escape(s, quote=True)


def main():
    # ---- gallery items (photos + video) in walkthrough order
    items, sec_of = [], {}
    for sec, ids in SECTIONS:
        for pid in ids:
            if pid == "V":
                x, y = abs_xy(VIDEO["floor"], VIDEO["x"], VIDEO["y"])
                items.append(dict(type="video", f=VIDEO["floor"], x=x, y=y, t=VIDEO["title"], sec=sec,
                                  src=VIDEO["src"], poster=VIDEO["poster"], thumb=VIDEO["poster"]))
                continue
            f, px, py, title = PHOTOS[pid]
            x, y = abs_xy(f, px, py)
            w, h = webp_size(IMG / f"{pid}-l.webp")
            items.append(dict(type="photo", id=pid, f=f, x=x, y=y, t=title, sec=sec, w=w, h=h,
                              large=f"img/{pid}-l.webp", thumb=f"img/{pid}-t.webp"))
            sec_of[pid] = sec
    assert len([i for i in items if i["type"] == "photo"]) == len(PHOTOS), "every photo must be in a section"
    index_of = {it["id"]: n for n, it in enumerate(items) if it["type"] == "photo"}
    video_index = next(n for n, it in enumerate(items) if it["type"] == "video")

    # ---- documents (a document may be split into several PDF files)
    def human(size):
        return f"{size / 1048576:.1f}MB" if size >= 1048576 else f"{max(1, round(size / 1024))}KB"

    docs, listed = [], {}
    for key, (f, px, py, files, name, note, area) in DOCS.items():
        files = files if isinstance(files, list) else [files]
        parts, first_page, total = [], 1, 0
        for k, file in enumerate(files, 1):
            p = SITE / "docs" / file
            size, pages = p.stat().st_size, pdf_pages(p)
            label = f"{k}/{len(files)}" if len(files) > 1 else "PDF"
            parts.append(dict(file=f"docs/{file}", label=label, mb=human(size),
                              range=f"{first_page}〜{first_page + pages - 1}ページ"))
            first_page += pages
            total += size
        x, y = abs_xy(f, px, py)
        docs.append(dict(key=key, f=f, x=x, y=y, name=name, note=note, area=area, parts=parts,
                         pages=first_page - 1, mb=human(total), big=total > 10 * 1048576))
        listed.setdefault(files[0], []).append(len(docs) - 1)

    # ---- plans
    plans_html, tabs, summaries = [], [], []
    for fl in FLOORS:
        n = fl["n"]
        cx, cy, cw, ch = fl["crop"]
        plans_html.append(
            f'<div class="plan-floor" data-floor="{n}"{"" if n == 1 else " hidden"}>'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {cw} {ch}" {SVG_FONT} role="img" aria-label="{n}階の間取り図">'
            f'<g class="rot" transform="translate({-cx} {-cy})"><g id="f{n}-base">{fl["base"]}</g><g class="lbls">{fl["labels"]}</g></g>'
            f'</svg><div class="pins"></div></div>')
        n_photo = sum(1 for it in items if it["f"] == n and it["type"] == "photo")
        n_video = sum(1 for it in items if it["f"] == n and it["type"] == "video")
        tabs.append(f'<button type="button" role="tab" data-floor="{n}" aria-selected="{"true" if n == 1 else "false"}"'
                    f'{"" if n == 1 else " tabindex=\"-1\""}>{n}F<small>写真{n_photo}{"＋動画" if n_video else ""}</small></button>')
        summaries.append(f'<ul class="summary" data-floor="{n}"{"" if n == 1 else " hidden"}>'
                         + "".join(f"<li>{esc(s)}</li>" for s in FLOOR_SUMMARY[n]) + "</ul>")

    # ---- highlights
    hl = []
    for pid, title, text in HIGHLIGHTS:
        w, h = webp_size(IMG / f"{pid}-m.webp")
        hl.append(f'<button type="button" class="hl-card" data-i="{index_of[pid]}">'
                  f'<img src="img/{pid}-m.webp" alt="{esc(PHOTOS[pid][3])}" loading="lazy" decoding="async" width="{w}" height="{h}">'
                  f'<div><h3>{esc(title)}</h3><p>{esc(text)}</p></div></button>')

    # ---- gallery
    chips, gal = [], []
    for k, (sec, ids) in enumerate(SECTIONS):
        chips.append(f'<a href="#g{k}">{esc(sec)}</a>')
        cells = []
        for pid in ids:
            if pid == "V":
                cells.append(f'<button type="button" class="g-item" data-i="{video_index}" aria-label="{esc(VIDEO["title"])}">'
                             f'<img src="{VIDEO["poster"]}" alt="" loading="lazy" decoding="async" width="360" height="640">'
                             f'<span class="play"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></span><span class="vt">{VIDEO["duration"]}</span></button>')
                continue
            tw, th = webp_size(IMG / f"{pid}-t.webp")
            cells.append(f'<button type="button" class="g-item" data-i="{index_of[pid]}" aria-label="{esc(PHOTOS[pid][3])}">'
                         f'<img src="img/{pid}-t.webp" alt="{esc(PHOTOS[pid][3])}" loading="lazy" decoding="async" width="{tw}" height="{th}"></button>')
        gal.append(f'<div class="g-sec" id="g{k}"><h3>{esc(sec)}<small>{len(ids)}</small></h3><div class="grid">{"".join(cells)}</div></div>')

    # ---- documents list (deduplicated by file, grouped by floor)
    groups = {1: [], 2: [], 3: []}
    for file, idxs in listed.items():
        d = docs[idxs[0]]
        areas = "・".join(dict.fromkeys(docs[i]["area"] for i in idxs))
        badge = '<span class="badge">大容量</span>' if d["big"] else ""
        text = (f'<span class="doc-ic">PDF</span><span class="doc-t"><b>{esc(d["name"])}{badge}</b>'
                f'<span>{esc(d["note"])}</span><em>{esc(areas)} ・ {d["pages"]}ページ ・ {d["mb"]}</em></span>')
        go = '<svg class="doc-go" viewBox="0 0 24 24"><path d="M14 3h7v7h-2V6.4l-9.3 9.3-1.4-1.4L17.6 5H14V3zM5 5h6v2H5v12h12v-6h2v8H3V5h2z"/></svg>'
        if len(d["parts"]) == 1:
            groups[d["f"]].append(f'<li><a class="doc" href="{d["parts"][0]["file"]}" target="_blank" rel="noopener">{text}{go}</a></li>')
        else:
            links = "".join(f'<a href="{p["file"]}" target="_blank" rel="noopener">{p["label"]}<small>{p["range"]}・{p["mb"]}</small></a>'
                            for p in d["parts"])
            groups[d["f"]].append(f'<li><div class="doc">{text}</div><div class="doc-parts">{links}</div></li>')
    docs_html = "".join(f'<div class="doc-group"><h3>{n}階</h3><ul class="docs">{"".join(v)}</ul></div>'
                        for n, v in groups.items() if v)

    data = dict(items=items, docs=docs, floors=[dict(n=fl["n"], crop=fl["crop"]) for fl in FLOORS])
    n_photos = len(PHOTOS)

    out = (Path(__file__).parent / "template.html").read_text()
    for key, val in {
        "__DATA__": json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        "__PLANS__": "".join(plans_html),
        "__TABS__": "".join(tabs),
        "__SUMMARIES__": "".join(summaries),
        "__HIGHLIGHTS__": "".join(hl),
        "__CHIPS__": "".join(chips),
        "__GALLERY__": "".join(gal),
        "__DOCS__": docs_html,
        "__NPHOTOS__": str(n_photos),
    }.items():
        assert key in out, key
        out = out.replace(key, val)
    (SITE / "index.html").write_text(out)
    print(f"site/index.html  {len(out) / 1024:.0f} KB  items={len(items)} docs={len(docs)}")

    # ---- claude.ai Artifact variant: same page without the document wrapper
    # (the Artifact host adds doctype/head/body itself); assets are published
    # from site/ at the same relative paths.
    head = out[out.index("<head>") + 6:out.index("</head>")]
    body = out[out.index("<body>") + 6:out.index("</body>")]
    style = head[head.index("<style>"):head.index("</style>") + 8]
    art = ('<title>世田谷1丁目住宅</title>\n'
           '<meta name="claude:viewport-fit-sides" content="cover">\n'
           f'{style}\n{body}')
    (ROOT / "artifact").mkdir(exist_ok=True)
    (ROOT / "artifact" / "index.html").write_text(art)
    print(f"artifact/index.html  {len(art) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
