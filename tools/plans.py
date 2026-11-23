"""Vector floor plans for 世田谷1丁目住宅.

Coordinates use the pixel grid of the original floor plan images
(1F: 585x257, 2F: 642x240, 3F: 642x270) so the photo pin positions from
the original tour map 1:1. Walls come from tools/plan/walls-N.svgfrag
(traced from the original drawing); everything else is drawn here.
"""
from pathlib import Path

HERE = Path(__file__).parent

C = {
    "room": "#fbf8f3",
    "wet": "#eaf1f5",
    "sto": "#efe3cb",
    "garage": "#e9e8e4",
    "out": "#f2f1ee",
    "tile": "#e4e0d9",
    "wall": "#34302c",
    "line": "#8a837a",
    "win": "#9fb4c2",
    "heat": "#cf7f4f",
    "ink": "#2a2622",
    "sub": "#6f675e",
}

LINE = f'fill="none" stroke="{C["line"]}" stroke-width=".75" stroke-linecap="round" stroke-linejoin="round"'
DASH = f'fill="none" stroke="{C["line"]}" stroke-width=".7" stroke-dasharray="2.2 1.6"'


def rect(x, y, w, h, fill, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" {extra}/>'


def path(d, style=LINE):
    return f'<path d="{d}" {style}/>'


def win(x, y, w, h):
    """Window inside a wall gap: white sash with a thin glazing line."""
    if w >= h:
        cy = y + h / 2
        glass = f'M{x},{cy - .9}H{x + w}M{x},{cy + .9}H{x + w}'
    else:
        cx = x + w / 2
        glass = f'M{cx - .9},{y}V{y + h}M{cx + .9},{y}V{y + h}'
    return (rect(x, y, w, h, "#ffffff", f'stroke="{C["line"]}" stroke-width=".6"')
            + path(glass, f'fill="none" stroke="{C["win"]}" stroke-width=".7"'))


def door(leaf, arc):
    return path(leaf, LINE) + path(arc, f'fill="none" stroke="{C["line"]}" stroke-width=".6" stroke-dasharray="1.4 1"')


def hinge_marks(xs, y, up=True):
    s = -1 if up else 1
    return "".join(path(f'M{x},{y} l3,{s * 4.5} l3,{-s * 4.5}') for x in xs)


def stairs(x0, x1, y0, y1, step_from, step_to, step):
    d = "".join(f'M{t},{y0}V{y1}' for t in frange(step_from, step_to, step))
    return path(d)


def frange(a, b, s):
    out, v = [], a
    while v <= b + 1e-6:
        out.append(round(v, 2))
        v += s
    return out


def arrow_head(x, y, direction):
    if direction == "right":
        return f'<path d="M{x},{y}l-5,-2.6v5.2z" fill="{C["line"]}"/>'
    return f'<path d="M{x},{y}l5,-2.6v5.2z" fill="{C["line"]}"/>'


def _text(t, y, size, weight, color, extra=""):
    halo = 'paint-order="stroke" stroke="#ffffff" stroke-width="2.4" stroke-linejoin="round"'
    return f'<text y="{y:.2f}" font-size="{size}" font-weight="{weight}" fill="{color}" {halo}{extra}>{t}</text>'


def label(x, y, main, sub=None, size=8.5, sub_size=6.2, color=None, weight=700, v=False, r=None):
    """Room label, wrapped in a <g> so the page can keep it upright when the
    plan is rotated for portrait phones.

    main may contain "\n" for multiple lines.
    v=True: when rotated, show the text vertically (one character per line,
            Japanese tategaki) - for long narrow spaces.
    r=(x, y): different anchor to use when rotated.
    """
    color = color or C["ink"]
    lines = main.split("\n")
    lh = size * 1.18
    total = len(lines) * lh + (sub_size * 1.3 if sub else 0)
    top = -total / 2
    parts = [_text(ln, top + lh * (k + .5), size, weight, color) for k, ln in enumerate(lines)]
    if sub:
        parts.append(_text(sub, top + len(lines) * lh + sub_size * .65, sub_size, 500, C["sub"]))
    body = f'<g class="h">{"".join(parts)}</g>'
    if v:
        chars = list(main.replace("\n", ""))
        vh = size * 1.06
        vtop = -len(chars) * vh / 2
        vparts = []
        for k, ch in enumerate(chars):
            cy = vtop + vh * (k + .5)
            extra = f' transform="rotate(90 0 {cy:.2f})"' if ch in "ー－" else ""
            vparts.append(_text(ch, cy, size, weight, color, extra))
        body += f'<g class="v">{"".join(vparts)}</g>'
    rx = f' data-rx="{r[0]}" data-ry="{r[1]}"' if r else ""
    cls = "lbl has-v" if v else "lbl"
    return f'<g class="{cls}" data-x="{x}" data-y="{y}"{rx} transform="translate({x},{y})">{body}</g>'


def tag(x, y, text, size=5.2, v=False, r=None):
    return label(x, y, text, size=size, color=C["sub"], weight=600, v=v, r=r)


def walls(n):
    frag = (HERE / "plan" / f"walls-{n}.svgfrag").read_text()
    return frag.replace('class="fp-walls"', f'fill="{C["wall"]}"')


# --------------------------------------------------------------------------- 1F
def floor1():
    fills = "".join([
        rect(24, 38, 144, 182, C["room"]),            # 防音室
        rect(168, 38, 68, 105, C["wet"]),             # 洗面・トイレ
        rect(236, 38, 92, 74, C["wet"]),              # 浴室
        rect(328, 30, 177, 96, C["garage"]),          # ガレージ
        rect(362, 125, 143, 38, C["out"]),            # ポーチ・アプローチ
        rect(168, 140, 200, 78, C["room"]),           # ホール
        rect(368, 164, 64, 54, C["tile"]),            # 玄関土間
        f'<path d="M434,167H462V181H500V214H434Z" fill="{C["sto"]}"/>',  # SIC
        rect(236, 112, 13, 28, C["sto"]),             # 棚
        rect(250, 112, 76, 28, C["sto"]),             # 収納
        rect(329, 131, 33, 10, C["sto"]),             # 収納
        rect(97, 190, 69, 25, C["sto"]),              # クローゼット
        rect(251, 181, 48, 33, C["sto"]),             # 階段下収納
    ])
    fixtures = "".join([
        # windows
        win(20, 79, 7, 41), win(20, 132, 7, 40), win(172, 35, 60, 6),
        win(324, 53, 7, 43), win(342, 215, 11, 7), win(444, 215, 25, 7),
        # doors
        door("M167,171H141", "M141,171A26,26 0 0 1 167,145"),
        door("M233,141V115", "M233,115A26,26 0 0 0 207,141"),
        door("M237,104H262", "M237,79A25,25 0 0 1 262,104"),
        door("M430,213H405", "M430,188A25,25 0 0 0 405,213"),
        door("M174,222V234", "M174,234A12,12 0 0 0 186,222"),
        # entrance sliding door + step
        path("M368,161.5H420M368,164.5H420"),
        path("M420,161.5H448M420,164.5H448", DASH),
        path("M366.5,166V214M369.5,166V214"),
        # porch / garage outlines
        path("M420,125V161M431,125V161M331,125H503M503,34V125"),
        # bath unit
        rect(239, 41, 86, 67, "none", f'stroke="{C["wall"]}" stroke-width="1"'),
        rect(295, 46, 27, 58, "#ffffff", f'rx="5" stroke="{C["line"]}" stroke-width=".75"'),
        rect(299.5, 51, 18, 48, "none", f'rx="8" stroke="{C["line"]}" stroke-width=".6"'),
        f'<circle cx="304" cy="75" r="1.3" fill="none" stroke="{C["line"]}" stroke-width=".6"/>',
        rect(285, 70, 6, 12, "#ffffff", f'stroke="{C["line"]}" stroke-width=".6"'),
        rect(257, 44, 32, 4, "#ffffff", f'rx="1.5" stroke="{C["line"]}" stroke-width=".6"'),
        # vanity (double bowl) + toilet
        rect(170, 41, 64, 19, "#ffffff", f'stroke="{C["line"]}" stroke-width=".6"'),
        path("M202,41V60"),
        rect(178, 45, 15, 11, "none", f'rx="2.5" stroke="{C["line"]}" stroke-width=".7"'),
        rect(210, 45, 15, 11, "none", f'rx="2.5" stroke="{C["line"]}" stroke-width=".7"'),
        rect(181.5, 130, 13, 7, "#ffffff", f'rx="1.2" stroke="{C["line"]}" stroke-width=".7"'),
        f'<ellipse cx="188" cy="121" rx="6.5" ry="8.5" fill="#ffffff" stroke="{C["line"]}" stroke-width=".7"/>',
        # stairs
        rect(170, 179, 78, 35, "none", f'stroke="{C["line"]}" stroke-width=".75"'),
        stairs(170, 248, 179, 214, 195, 240, 9),
        path("M186,183V197H243"), arrow_head(247, 197, "right"),
        # storage details
        path("M258,112V140"), hinge_marks([263, 313], 140, up=False), hinge_marks([103, 152], 190),
        rect(283, 189, 16, 21, "none", DASH), rect(300, 183, 9, 23, "#ffffff", f'stroke="{C["line"]}" stroke-width=".6"'),
        path("M436,177.5H462M480,182V213", DASH),
        rect(472, 158, 18, 15, "#ffffff", f'stroke="{C["line"]}" stroke-width=".7"'),
        rect(28, 43, 39, 15, "none", DASH),
        # car
        rect(347, 54, 142, 50, "#ffffff", f'rx="15" stroke="{C["line"]}" stroke-width=".8"'),
        rect(373, 60, 68, 38, "none", f'rx="10" stroke="{C["line"]}" stroke-width=".6"'),
        path("M441,62Q452,79 441,96M381,62Q373,79 381,96"),
        path("M434,54l2,-4h5l1,4M434,104l2,4h5l1,-4"),
    ])
    labels = "".join([
        label(96, 110, "防音室", "約9.4帖", size=10, sub_size=7),
        label(206, 95, "洗面・トイレ", "約2.9帖", size=7.2, r=(204, 103)),
        label(268, 80, "浴室", size=8),
        label(407, 79, "ガレージ", size=7, color=C["sub"]),
        label(380, 191, "玄関", size=7),
        label(467, 197, "シューズ\nクローク", "約1.2帖", size=6, sub_size=5.4),
        label(322, 163, "ホール", size=7.4),
        tag(290, 127, "収納", 6),
        tag(345.5, 136.5, "収納", 4.6),
        tag(242.5, 126, "棚", 5),
        tag(131, 203, "クローゼット", 6, v=True),
        tag(266, 195, "階段下収納", 5.2),
        tag(291, 200, "床下", 4.4),
        label(481, 165.5, "宅配\nBOX", size=4.2, color=C["sub"], weight=600),
        tag(47.5, 50.5, "AC", 5),
        tag(226, 186, "UP", 5),
    ])
    return dict(n=1, w=585, h=257, crop=(10, 16, 572, 228), base=fills + walls(1) + fixtures, labels=labels)


# --------------------------------------------------------------------------- 2F
def floor2():
    fills = "".join([
        f'<path d="M150,27H366V19H505V206H150Z" fill="{C["room"]}"/>',   # LDK + キッチン
        rect(81, 30, 68, 59, C["sto"]),               # パントリー
        rect(81, 90, 68, 79, C["room"]),              # ワークスペース
        rect(81, 173, 68, 34, C["out"]),              # バルコニー(西)
        rect(510, 19, 53, 188, C["out"]),             # バルコニー(東)
        rect(153, 172, 68, 35, C["sto"]),             # 洗濯機置場
        rect(221, 31, 62, 17, C["sto"]),              # 吊戸棚
        rect(290, 31, 68, 17, C["sto"]),              # スタディコーナー
        rect(290, 66, 82, 95, C["heat"], f'fill-opacity=".07" stroke="{C["heat"]}" stroke-width=".7" stroke-dasharray="2.2 1.6"'),
        rect(380, 66, 107, 106, C["heat"], f'fill-opacity=".07" stroke="{C["heat"]}" stroke-width=".7" stroke-dasharray="2.2 1.6"'),
    ])
    fixtures = "".join([
        win(228, 24, 56, 6), win(499, 59, 11, 101), win(92, 167, 50, 7),
        door("M229,211V223", "M229,223A11,11 0 0 0 240,212"),
        # partitions toward kitchen
        path("M150,31V58"), path("M150,58V88M150,104V168", DASH),
        # pantry shelves, fridge, upper cabinets, desk
        path("M96,43H148M96,31V88", DASH),
        rect(153, 31, 21, 20, "none", DASH),
        rect(221, 31, 62, 17, "none", DASH), rect(290, 31, 68, 17, "none", DASH),
        # island kitchen
        rect(180, 91, 102, 36, "#ffffff", f'rx="1.5" stroke="{C["line"]}" stroke-width=".8"'),
        rect(190, 96, 25, 15, "none", f'rx="1" stroke="{C["line"]}" stroke-width=".7"'),
        "".join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{C["line"]}" stroke-width=".6"/>'
                for cx, cy, r in ((197, 101, 2.6), (208, 101, 2.6), (202.5, 107.5, 2.2))),
        rect(243, 96, 27, 14, "none", f'rx="3" stroke="{C["line"]}" stroke-width=".7"'),
        f'<circle cx="252" cy="112.5" r="1.1" fill="{C["line"]}"/><circle cx="262" cy="112.5" r="1.1" fill="{C["line"]}"/>',
        # TV board, lighting rail, AC
        path("M369,40H497", DASH), path("M283,106H357M283,111H357", DASH),
        rect(481, 162, 15, 38, "none", DASH), rect(84, 133, 14, 36, "none", DASH),
        path("M101,92V168"),
        # laundry
        rect(157, 181, 19, 24, "none", DASH), path("M176,190H220", DASH),
        hinge_marks([158, 211], 172),
        # balcony rail
        path("M553,22V204M558,22V204"),
        # stairs (UP to 3F / DN to 1F)
        path("M225,170H287"), rect(287, 167, 82, 4, "#d8d3cb"),
        stairs(225, 369, 170, 204, 259, 367, 9),
        path("M242,172V186H315"), arrow_head(319, 186, "right"),
        path("M366,186H332"), arrow_head(328, 186, "left"),
        path("M321,171V180L317,184L325,190L321,194V204", f'fill="none" stroke="{C["line"]}" stroke-width=".9"'),
    ])
    labels = "".join([
        label(433, 118, "LDK", "約22.4帖", size=11, sub_size=7.4),
        label(231, 143, "キッチン", size=7.4),
        tag(331, 73, "床暖房", 5.4), tag(433, 73, "床暖房", 5.4),
        tag(433, 33, "TVボード", 5.4, v=True),
        tag(324, 39.5, "スタディコーナー", 5, v=True),
        tag(252, 39.5, "吊戸棚", 5.4, v=True),
        tag(163.5, 41, "冷蔵庫", 4.4),
        tag(320, 118, "ライティングレール", 4.4, v=True),
        label(122, 74, "パントリー", "約1.7帖", size=6.6, r=(106, 62)),
        tag(122, 37.5, "可動棚", 4.6, v=True),
        label(125, 128, "ワークスペース", "約2.3帖", size=6.4),
        tag(115, 191, "バルコニー", 6, v=True),
        tag(535, 96, "バルコニー", 6),
        tag(166.5, 193, "洗濯機", 4.4),
        tag(199, 199, "可動棚", 4.6),
        tag(91, 151, "AC", 4.6), tag(488.5, 181, "AC", 4.6),
        tag(240, 165, "UP", 5), tag(356, 197, "DN", 5),
    ])
    return dict(n=2, w=642, h=240, crop=(68, 8, 506, 222), base=fills + walls(2) + fixtures, labels=labels)


# --------------------------------------------------------------------------- 3F
def floor3():
    fills = "".join([
        rect(163, 67, 68, 136, C["room"]),            # 納戸
        f'<path d="M235,82H327V172H347V203H235Z" fill="{C["room"]}"/>',  # 洋室5.0
        rect(281, 66, 46, 16, C["room"]), rect(415, 66, 63, 16, C["room"]),  # 出窓
        rect(333, 82, 48, 35, C["wet"]),              # トイレ
        rect(333, 117, 48, 123, C["room"]),           # ホール
        rect(385, 82, 120, 138, C["room"]),           # 洋室6.6
        rect(386, 220, 119, 20, C["sto"]),            # クローゼット
        rect(207, 208, 141, 32, C["room"]),           # 階段
        rect(512, 58, 26, 186, C["out"]),             # 吹抜
    ])
    fixtures = "".join([
        win(281, 65, 46, 5), win(415, 65, 63, 5), win(360, 77, 13, 5), win(505, 128, 5, 63),
        door("M381,118V144", "M355,118A26,26 0 0 0 381,144"),
        door("M347,201V176", "M347,176A25,25 0 0 0 322,201"),
        door("M369,245V257", "M369,257A11,11 0 0 0 380,246"),
        # sliding doors
        path("M382.2,198V216M384.8,210V228"),
        path("M231.5,84V110M234.5,84V110M231.5,174.5V203M234.5,174.5V203"),
        # toilet + hand wash
        rect(334, 93, 6, 13, "#ffffff", f'rx="1" stroke="{C["line"]}" stroke-width=".7"'),
        f'<ellipse cx="348" cy="99.5" rx="8.5" ry="6.2" fill="#ffffff" stroke="{C["line"]}" stroke-width=".7"/>',
        rect(333, 121, 19, 45, "#ffffff", f'stroke="{C["line"]}" stroke-width=".7"'),
        rect(337, 132, 11, 15, "none", f'rx="2.5" stroke="{C["line"]}" stroke-width=".7"'),
        # AC
        rect(312, 85, 15, 33, "none", DASH), rect(390, 87, 32, 14, "none", DASH),
        # closet folding doors
        path("M392,220q4,-5 8,0q4,-5 8,0q4,-5 8,0q4,-5 8,0M478,220q4,-5 8,0q4,-5 8,0q4,-5 8,0"),
        # void
        rect(512, 58, 26, 186, "none", DASH), path("M512,58L538,244M538,58L512,244", DASH),
        # stairs (DN)
        rect(207, 208, 141, 32, "none", f'stroke="{C["line"]}" stroke-width=".75"'),
        stairs(207, 348, 208, 240, 240, 348, 9),
        path("M347,224H245"), arrow_head(241, 224, "left"),
        # outline of lower roof / site
        path("M135,62L147.5,148L141,154L149,154L166,247"),
        path("M238,62.5H344V56.5H548V62"),
    ])
    labels = "".join([
        label(446, 150, "洋室", "約6.6帖", size=10, sub_size=7),
        label(281, 138, "洋室", "約5.0帖", size=10, sub_size=7),
        label(197, 130, "納戸", "約4.0帖", size=9, sub_size=6.6),
        label(367, 92, "トイレ", size=6.4),
        label(366, 200, "ホール", size=7),
        tag(342.5, 158, "手洗い", 4.4),
        tag(446, 231, "クローゼット", 6, v=True),
        tag(525, 150, "吹抜", 6.4),
        tag(304, 75, "出窓", 5), tag(446.5, 75, "出窓", 5),
        tag(319.5, 101.5, "AC", 4.6), tag(406, 94.5, "AC", 4.6),
        tag(361, 226, "DN", 5),
    ])
    return dict(n=3, w=642, h=270, crop=(125, 46, 430, 216), base=fills + walls(3) + fixtures, labels=labels)


FLOORS = [floor1(), floor2(), floor3()]
