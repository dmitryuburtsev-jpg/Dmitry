"""Сборочные чертежи хозблока (листы А3) по model/model.json и model/parts.json.

python3 drawings/make_drawings.py  ->  drawings/khozblok_chertezhi.pdf + drawings/list_N.png
"""
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Polygon, Rectangle, Circle, Arc
from matplotlib.image import imread

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "model"))
import build_model as BM  # noqa: E402

MODEL = json.loads((ROOT / "model" / "model.json").read_text())
PARTS = json.loads((ROOT / "model" / "parts.json").read_text())
LV = MODEL["levels"]
P = MODEL["params"]
L, W = P["L"], P["W"]
IN = MODEL["interior"]
EL = {e["id"]: e for e in MODEL["elements"]}
ZF = LV["floor"]                       # ±0.000 — чистый пол
TAN = math.tan(math.radians(P["roof_pitch"]))
COS = math.cos(math.radians(P["roof_pitch"]))

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["hatch.linewidth"] = 0.35
PT = 72 / 25.4                         # пунктов в 1 мм бумаги
LW_MAIN, LW_THIN, LW_BOLD = 0.5 * PT, 0.18 * PT, 0.7 * PT
FS = 2.5 * PT                          # 2,5 мм шрифт
FS_S = 2.0 * PT
FS_T = 3.5 * PT

FILL = {"wood": "#f6ecd9", "timber": "#f6ecd9", "osb": "#f3e3c3", "plywood": "#f6ecd9",
        "board": "#f1e2c6", "glass": "#e3eff6", "concrete": "#e6e6e6", "deck": "#eadcc4",
        "rubber": "#d9d9d9", "black": "#d0d0d0", "dark": "#dcdcdc", "steel": "#e8ecef",
        "wall_sheet": "#ffffff", "trim": "#ffffff", "roof_sheet": "#ffffff", "pvc": "#ffffff",
        "door": "#efe6e0", "lamp": "#fffbe6", "pegboard": "#e9ecef", "grey": "#eeeeee",
        "red": "#f7e1dd", "orange": "#fbe9d6", "green": "#e2f0e0", "blue": "#dde8f3",
        "yellow": "#fbf2d2", "gravel": "#eeeeee"}


# ============================================================ лист и виды
class Sheet:
    def __init__(self, title, num, total, scale_note=""):
        self.fig = plt.figure(figsize=(420 / 25.4, 297 / 25.4))
        ax = self.fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, 420); ax.set_ylim(0, 297); ax.axis("off")
        ax.set_aspect("equal")
        self.ax = ax
        ax.add_patch(Rectangle((20, 5), 395, 287, fill=False, lw=LW_BOLD))
        self.stamp(title, num, total, scale_note)

    def stamp(self, title, num, total, scale_note):
        ax = self.ax
        x0, y0, w, h = 230, 5, 185, 55
        ax.add_patch(Rectangle((x0, y0), w, h, fill=False, lw=LW_BOLD))
        # левая часть — графы подписей
        for i in range(1, 11):
            ax.plot([x0, x0 + 65], [y0 + 5 * i, y0 + 5 * i], lw=LW_THIN if i not in (6,) else LW_MAIN, c="k")
        for dx in (7, 17, 40, 55, 65):
            ax.plot([x0 + dx, x0 + dx], [y0, y0 + h], lw=LW_MAIN, c="k")
        rows = [("Разраб.", "Claude"), ("Пров.", ""), ("Т.контр.", ""), ("", ""), ("Н.контр.", ""), ("Утв.", "")]
        for i, (a, b) in enumerate(rows):
            yy = y0 + 27.5 - 5 * i - 2.5 + 0
            self.t(x0 + 1, y0 + 25 - 5 * i + 1.3, a, FS_S, ha="left")
            self.t(x0 + 18, y0 + 25 - 5 * i + 1.3, b, FS_S, ha="left")
        self.t(x0 + 41, y0 + 1.3, "09.2026", FS_S * 0.9, ha="left")
        for i, a in enumerate(["Изм.", "Кол.уч", "Лист", "№ док.", "Подп.", "Дата"]):
            xs = [x0, x0 + 7, x0 + 17, x0 + 27, x0 + 40, x0 + 55][i]
        self.t(x0 + 1, y0 + 31.3, "Изм.  Кол.уч  Лист  №док.   Подп.   Дата", FS_S * 0.8, ha="left")
        # правая часть
        ax.plot([x0 + 65, x0 + w], [y0 + 40, y0 + 40], lw=LW_MAIN, c="k")
        ax.plot([x0 + 65, x0 + w], [y0 + 15, y0 + 15], lw=LW_MAIN, c="k")
        ax.plot([x0 + 135, x0 + 135], [y0, y0 + 40], lw=LW_MAIN, c="k")
        ax.plot([x0 + 135, x0 + w], [y0 + 35, y0 + 35], lw=LW_MAIN, c="k")
        ax.plot([x0 + 135, x0 + w], [y0 + 30, y0 + 30], lw=LW_MAIN, c="k")
        for dx in (150, 165):
            ax.plot([x0 + dx, x0 + dx], [y0 + 30, y0 + 40], lw=LW_MAIN, c="k")
        self.t(x0 + 125, y0 + 47.5, "ХБ-6.0х2.3-АР", FS_T * 1.1, weight="bold")
        self.t(x0 + 100, y0 + 30, "Хозблок 6,0 × 2,3 м (по крыше)\nкаркасный, утеплённый,\nс наполнением для хранения", FS, linespacing=1.4)
        self.t(x0 + 100, y0 + 7.5, title, FS * 1.1, weight="bold", linespacing=1.3)
        self.t(x0 + 142.5, y0 + 37.5, "Стадия", FS_S); self.t(x0 + 157.5, y0 + 37.5, "Лист", FS_S)
        self.t(x0 + 175, y0 + 37.5, "Листов", FS_S)
        self.t(x0 + 142.5, y0 + 32.5, "Р", FS); self.t(x0 + 157.5, y0 + 32.5, str(num), FS)
        self.t(x0 + 175, y0 + 32.5, str(total), FS)
        self.t(x0 + 160, y0 + 22.5, "Частный заказ", FS)
        if scale_note:
            self.t(x0 + 160, y0 + 16.8, scale_note, FS_S)
        self.t(x0 + 160, y0 + 8, "Размеры — мм,\nотметки — м", FS_S, linespacing=1.3)

    def t(self, x, y, s, size=FS, ha="center", va="center", rot=0, **kw):
        self.ax.text(x, y, s, fontsize=size, ha=ha, va=va, rotation=rot, **kw)

    def table(self, x, y, cols, rows, head=None, rh=5.0, size=FS_S, wrap_bold_first=False):
        """Таблица: x,y — левый верхний угол; cols — ширины колонок (мм)."""
        ax = self.ax
        allrows = ([head] if head else []) + rows
        tw = sum(cols)
        for i, r in enumerate(allrows):
            yy = y - i * rh
            ax.plot([x, x + tw], [yy, yy], c="k", lw=LW_MAIN if i <= 1 else LW_THIN)
            cx = x
            for j, (c, cell) in enumerate(zip(cols, r)):
                bold = (head and i == 0)
                ha = "left" if j > 0 and not bold and isinstance(cell, str) and len(cell) > 6 else "center"
                self.t(cx + (1.2 if ha == "left" else c / 2), yy - rh / 2, str(cell), size, ha=ha,
                       weight="bold" if bold else "normal")
                cx += c
        yb = y - len(allrows) * rh
        ax.plot([x, x + tw], [yb, yb], c="k", lw=LW_MAIN)
        cx = x
        for c in [0] + cols:
            cx += c
            ax.plot([cx, cx], [y, yb], c="k", lw=LW_MAIN)
        return yb

    def save(self, pdf, png):
        pdf.savefig(self.fig)
        self.fig.savefig(png, dpi=160)
        plt.close(self.fig)


class View:
    """Вид в масштабе 1:s. (a, b) — координаты модели в мм, (ox, oy) — положение a=0,b=0 на листе."""

    def __init__(self, sh, ox, oy, s):
        self.sh, self.ax, self.ox, self.oy, self.s = sh, sh.ax, ox, oy, s

    def p(self, a, b):
        return self.ox + a / self.s, self.oy + b / self.s

    def line(self, a0, b0, a1, b1, lw=LW_MAIN, ls="-", c="k", z=3):
        (x0, y0), (x1, y1) = self.p(a0, b0), self.p(a1, b1)
        self.ax.plot([x0, x1], [y0, y1], lw=lw, ls=ls, c=c, zorder=z, solid_capstyle="butt")

    def poly(self, pts, fc="white", ec="k", lw=LW_THIN, z=2, hatch=None, ls="-", closed=True):
        self.ax.add_patch(Polygon([self.p(a, b) for a, b in pts], closed=closed, fc=fc, ec=ec, lw=lw,
                                  zorder=z, hatch=hatch, ls=ls, fill=fc is not None))

    def rect(self, a0, b0, a1, b1, **kw):
        self.poly([(a0, b0), (a1, b0), (a1, b1), (a0, b1)], **kw)

    def text(self, a, b, s, size=FS, **kw):
        x, y = self.p(a, b)
        self.sh.t(x, y, s, size, **kw)

    # ------- размеры
    def dim(self, a0, b0, a1, b1, off, text=None, horiz=True, size=FS_S, ext=True):
        """Линейный размер. horiz=True — вдоль a на уровне b0+off (мм модели)."""
        if horiz:
            bb = b0 + off
            if ext:
                self.line(a0, b0, a0, bb + math.copysign(1.5 * self.s, off), lw=LW_THIN)
                self.line(a1, b1, a1, bb + math.copysign(1.5 * self.s, off), lw=LW_THIN)
            self.line(a0 - 1.5 * self.s, bb, a1 + 1.5 * self.s, bb, lw=LW_THIN)
            for a in (a0, a1):
                self.line(a - 0.9 * self.s, bb - 0.9 * self.s, a + 0.9 * self.s, bb + 0.9 * self.s, lw=LW_MAIN)
            x, y = self.p((a0 + a1) / 2, bb)
            val = text if text is not None else f"{abs(a1 - a0):.0f}"
            if abs(a1 - a0) / self.s < len(val) * 1.6 + 1:
                x = self.p(max(a0, a1), bb)[0] + 1 + len(val) * 0.8
            self.sh.t(x, y + 1.3, val, size)
        else:
            aa = a0 + off
            if ext:
                self.line(a0, b0, aa + math.copysign(1.5 * self.s, off), b0, lw=LW_THIN)
                self.line(a1, b1, aa + math.copysign(1.5 * self.s, off), b1, lw=LW_THIN)
            self.line(aa, b0 - 1.5 * self.s, aa, b1 + 1.5 * self.s, lw=LW_THIN)
            for b in (b0, b1):
                self.line(aa - 0.9 * self.s, b - 0.9 * self.s, aa + 0.9 * self.s, b + 0.9 * self.s, lw=LW_MAIN)
            x, y = self.p(aa, (b0 + b1) / 2)
            val = text if text is not None else f"{abs(b1 - b0):.0f}"
            if abs(b1 - b0) / self.s < len(val) * 1.6 + 1:
                y = self.p(aa, max(b0, b1))[1] + 1 + len(val) * 0.8
            self.sh.t(x - 1.3, y, val, size, rot=90)

    def chain(self, vals, b, off, horiz=True):
        for v0, v1 in zip(vals[:-1], vals[1:]):
            if horiz:
                self.dim(v0, b, v1, b, off)
            else:
                self.dim(b, v0, b, v1, off, horiz=False)

    def level(self, a, b, z_abs, right=True, text=None):
        """Отметка высоты (z_abs — от низа обвязки, выводится относительно чистого пола)."""
        v = (z_abs - ZF) / 1000
        s = text or (("±0,000" if abs(v) < 5e-4 else f"{v:+.3f}".replace(".", ",")))
        x, y = self.p(a, b)
        d = 1 if right else -1
        self.ax.plot([x, x + d * 14], [y, y], c="k", lw=LW_THIN, zorder=4)
        self.ax.add_patch(Polygon([(x + d * 3, y), (x + d * 1.3, y + 1.7), (x + d * 4.7, y + 1.7)],
                                  closed=True, fc="none", ec="k", lw=LW_THIN, zorder=4))
        self.ax.plot([x + d * 1.3, x + d * 14], [y + 1.7, y + 1.7], c="k", lw=LW_THIN, zorder=4)
        self.sh.t(x + d * 8.5, y + 3.3, s, FS_S)

    def label(self, a, b, a2, b2, num):
        """Позиционная выноска: от точки (a,b) к кружку с номером в (a2,b2)."""
        x0, y0 = self.p(a, b)
        x1, y1 = self.p(a2, b2)
        self.ax.plot([x0, x1], [y0, y1], c="k", lw=LW_THIN, zorder=6)
        self.ax.add_patch(Circle((x0, y0), 0.45, color="k", zorder=6))
        self.ax.add_patch(Circle((x1, y1), 2.6, fc="white", ec="k", lw=LW_THIN, zorder=6))
        self.sh.t(x1, y1, str(num), FS_S, zorder=7)

    def title(self, a, b, s, scale):
        x, y = self.p(a, b)
        self.sh.t(x, y, s, FS_T, weight="bold")
        w = len(s) * 1.25
        self.ax.plot([x - w, x + w], [y - 2.6, y - 2.6], c="k", lw=LW_MAIN)
        self.sh.t(x + w + 2, y, f"М 1:{scale}", FS, ha="left")


# ------- штриховки/слои
def zigzag(v, a0, b0, a1, b1, along_a=True, lw=LW_THIN):
    """Условное обозначение утеплителя — зигзаг внутри прямоугольника."""
    if along_a:
        h = b1 - b0
        n = max(2, int(abs(a1 - a0) / (h * 0.6)))
        pts = [(a0 + (a1 - a0) * i / n, b0 if i % 2 == 0 else b1) for i in range(n + 1)]
    else:
        h = a1 - a0
        n = max(2, int(abs(b1 - b0) / (abs(h) * 0.6)))
        pts = [(a0 if i % 2 == 0 else a1, b0 + (b1 - b0) * i / n) for i in range(n + 1)]
    v.poly(pts, fc=None, ec="k", lw=lw, closed=False, z=3)


def cut_timber(v, a0, b0, a1, b1):
    v.rect(a0, b0, a1, b1, fc="#f6ecd9", ec="k", lw=LW_MAIN, z=3)
    v.line(a0, b0, a1, b1, lw=LW_THIN, z=3)
    v.line(a0, b1, a1, b0, lw=LW_THIN, z=3)


def cut_sheet(v, a0, b0, a1, b1, kind="osb"):
    fc = {"osb": "#f3e3c3", "board": "#f6ecd9", "concrete": "#e6e6e6", "ins": "#fff8dc"}[kind]
    hatch = {"osb": "....", "board": "////", "concrete": "..", "ins": None}[kind]
    v.rect(a0, b0, a1, b1, fc=fc, ec="k", lw=LW_MAIN, hatch=hatch, z=3)


def membrane(v, pts, color="#1f5fbf"):
    v.poly(pts, fc=None, ec=color, lw=LW_THIN * 1.4, ls=(0, (3, 1.5)), closed=False, z=4)


def profile_line(v, a0, b0, a1, b1, amp=8, pitch=115, vertical=True, lw=LW_MAIN):
    """Профлист в разрезе — трапециевидная линия."""
    pts = []
    if vertical:
        n = int(abs(b1 - b0) / pitch) + 1
        for i in range(n):
            b = b0 + i * pitch * (1 if b1 > b0 else -1)
            pts += [(a0, b), (a0, b + 25), (a0 - amp, b + 40), (a0 - amp, b + 75), (a0, b + 90)]
        pts = [(a, min(b, b1)) for a, b in pts]
    v.poly(pts, fc=None, ec="k", lw=lw, closed=False, z=4)


# ------- проекция деталей 3D-модели
MAP = {
    # a, b, «расстояние до зрителя» (меньше — ближе)
    "front": (lambda b: (b[0], b[3], b[2], b[5]), lambda b: b[1]),
    "back": (lambda b: (L - b[3], L - b[0], b[2], b[5]), lambda b: -b[4]),
    "left": (lambda b: (W - b[4], W - b[1], b[2], b[5]), lambda b: b[0]),
    "right": (lambda b: (b[1], b[4], b[2], b[5]), lambda b: -b[3]),
    "top": (lambda b: (b[0], b[3], b[1], b[4]), lambda b: -b[5]),
}


def draw_parts(v, parts, view, lw=LW_THIN, clip=None, fill=True, ec="k"):
    fa, fd = MAP[view]
    for p in sorted(parts, key=lambda p: -fd(p["b"])):
        a0, a1, b0, b1 = fa(p["b"])
        if clip:
            ca0, cb0, ca1, cb1 = clip
            a0, a1, b0, b1 = max(a0, ca0), min(a1, ca1), max(b0, cb0), min(b1, cb1)
            if a1 <= a0 or b1 <= b0:
                continue
        if a1 - a0 < 0.5 or b1 - b0 < 0.5:
            continue
        fc = FILL.get(p["mat"], "white") if fill else "white"
        v.rect(a0, b0, a1, b1, fc=fc, ec=ec, lw=lw, z=2)


def parts_where(groups=None, ids=None, pref=None, pred=None):
    out = []
    for p in PARTS:
        if groups and p["group"] not in groups:
            continue
        if ids and p["id"] not in ids:
            continue
        if pref and not any(p["id"].startswith(x) for x in pref):
            continue
        if pred and not pred(p):
            continue
        out.append(p)
    return out


def roof_z(y):
    return LV["ridge"] - TAN * abs(y - W / 2)


# ============================================================ ЛИСТ 1 — фасады
def sheet_facades(pdf, n, total):
    sh = Sheet("Фасады.\nЦветовое решение", n, total, "М 1:50")
    s = 50
    g = LV["ground"]

    def long_facade(ox, oy, view, name):
        v = View(sh, ox, oy - g / s, s)
        groups = {"front": ["foundation", "clad_front", "openings", "roof", "site"],
                  "back": ["foundation", "cladding", "roof"]}[view]
        pp = parts_where(groups=groups, pred=lambda p: not (p["group"] == "cladding" and
                                                            (p["b"][1] < 100 or p["b"][0] < -5 and p["b"][3] < 5 or p["b"][3] > L + 5 and p["b"][0] > L - 5)))
        if view == "back":
            pp = [p for p in pp if p["group"] != "cladding" or p["b"][1] > W - 5]
        plate = [p for p in pp if p["mat"] == "wall_sheet" and p["b"][3] - p["b"][0] > 5000]
        rest = [p for p in pp if p not in plate]
        draw_parts(v, plate, view)
        draw_parts(v, rest, view)
        # земля
        v.line(-700, g, L + 1300, g, lw=LW_BOLD)
        for a in range(-700, L + 1300, 250):
            v.line(a, g, a - 150, g - 150, lw=LW_THIN)
        # размеры
        v.dim(-100, LV["ridge"], 5900, LV["ridge"], 450, "6000 (по крыше)")
        v.dim(-12, g, L + 12, g, -420, f"{L + 24:.0f}")
        if view == "front":
            ch = [-12, 650, 1650, 2420, 3380, 4150, 5150, L + 12]
            v.chain(ch, g, -220)
        v.level(L + 350, g, g, right=True)
        v.level(L + 350, ZF, ZF)
        v.level(L + 350, P["win_top"], P["win_top"])
        v.level(L + 350, LV["roof_at_wall"] - 60, LV["roof_at_wall"] - 60,)
        v.level(L + 350, LV["ridge"], LV["ridge"])
        v.line(L, ZF, L + 350, ZF, lw=LW_THIN, ls=(0, (4, 2)))
        v.line(L, LV["ridge"], L + 350, LV["ridge"], lw=LW_THIN, ls=(0, (4, 2)))
        if view == "front":
            v.line(L, P["win_top"], L + 350, P["win_top"], lw=LW_THIN, ls=(0, (4, 2)))
        v.title(L / 2 - 500, g - 850, name, s)
        return v

    def end_facade(ox, oy, view, name):
        v = View(sh, ox, oy - g / s, s)
        # в торцевом виде a — горизонталь вдоль ширины
        mirror = view == "left"
        A = (lambda y: W - y) if mirror else (lambda y: y)
        ya, yb = -12, W + 12
        # профлист: контур стены с фронтоном
        top = lambda y: roof_z(y) - 45
        pts = [(A(ya), -40), (A(yb), -40), (A(yb), top(yb)), (A(W / 2), top(W / 2)), (A(ya), top(ya))]
        v.poly(pts, fc="white", ec="k", lw=LW_MAIN)
        y = ya + 57
        while y < yb - 18:
            v.line(A(y), -40, A(y), top(y) - 10, lw=LW_THIN * 0.8)
            y += 115
        # цокольный отлив и углы
        v.rect(A(ya) - (30 if not mirror else -30), -60, A(yb) + (30 if not mirror else -30), 5, fc="white", lw=LW_THIN)
        for yy in (ya, yb):
            v.rect(A(yy) - 30, -40, A(yy) + 30, top(yy), fc="white", lw=LW_THIN)
        # кровля — торец листа и ветровая планка
        for sg in (1, -1):
            e0 = -50 if sg > 0 else W + 50
            v.poly([(A(e0), roof_z(e0) - 150), (A(W / 2), roof_z(W / 2) - 150 + 0),
                    (A(W / 2), roof_z(W / 2)), (A(e0), roof_z(e0))], fc="white", lw=LW_MAIN)
            v.poly([(A(e0), roof_z(e0)), (A(W / 2), roof_z(W / 2)), (A(W / 2), roof_z(W / 2) + 20),
                    (A(e0), roof_z(e0) + 20)], fc="#dddddd", lw=LW_THIN)
        # блоки
        for yc in (50, W - 50):
            v.rect(A(yc) - 120, g, A(yc) + 120, 0, fc="#e6e6e6", lw=LW_THIN, hatch="..")
        # ступени (сбоку)
        st = [p for p in PARTS if p["id"] in ("step_landing", "step_1")]
        for p in st:
            v.rect(A(p["b"][1]), p["b"][2], A(p["b"][4]), p["b"][5], fc="#eadcc4", lw=LW_THIN)
        v.line(A(-900), g, A(W + 400), g, lw=LW_BOLD)
        for a in range(-900, W + 400, 250):
            v.line(A(a), g, A(a) - 150, g - 150, lw=LW_THIN)
        v.dim(A(-50), LV["ridge"], A(W + 50), LV["ridge"], 380, "2300 (по крыше)")
        v.dim(A(ya), g, A(yb), g, -300, f"{W + 24:.0f}")
        v.dim(A(W + 50) + (0 if mirror else 0), g, A(W + 50), LV["ridge"], (-380 if mirror else 380),
              f"{LV['ridge'] - g:.0f}", horiz=False)
        v.text(A(W / 2), LV["roof_at_wall"] + 150, f"i={P['roof_pitch']}°", FS_S)
        v.title(W / 2, g - 850, name, s)
        return v

    long_facade(45, 205, "front", "Главный фасад")
    long_facade(45, 100, "back", "Задний фасад")
    end_facade(262, 205, "left", "Левый торец")
    end_facade(345, 205, "right", "Правый торец")

    # цветовое решение
    sh.t(322, 131, "Ведомость отделки фасадов", FS * 1.1, weight="bold")
    rows = [
        ["Стены", "Профлист С8-1150, 0,45 мм, полимер", "RAL 6005*"],
        ["Нащельники, углы,", "Доборные элементы, полимер", "RAL 9003"],
        ["наличники, отливы", "", ""],
        ["Кровля", "Профлист С20-1100, 0,45 мм, оцинк.", "металлик"],
        ["Конёк, ветр. планки", "Оцинкованная сталь / полимер", "по кровле"],
        ["Окна", "ПВХ, 2-кам. стеклопакет", "белые"],
        ["Дверь", "Металлическая, пр-во РФ", "RAL 8017"],
        ["Ступени", "Доска 40 мм, антисептик", "тик/орех"],
    ]
    sh.table(232, 127, [36, 58, 22], rows, head=["Элемент", "Материал", "Цвет"], rh=4.6)
    sh.t(232, 83, "* Цвет стен — по выбору заказчика. Варианты визуализации:\n"
         "  RAL 6005 зелёный мох · RAL 8017 шоколад · RAL 5005 синий ·\n"
         "  RAL 3005 вишня · RAL 1015 слоновая кость (images/color_*.png).\n"
         "Отметка ±0,000 — уровень чистого пола.", FS_S, ha="left", va="top", linespacing=1.4)
    sh.save(*pdf, ) if False else None
    return sh


# ============================================================ ЛИСТ 2 — план
EXPL = [
    (21, "Верстак 2000×650, h=900", "1", "каркас брус 50×100, столешница фанера 2×18"),
    (22, "Тиски слесарные 125 мм", "1", "на болтах М10"),
    (23, "Тумба-кассетница под верстак", "1", "4 ящика, металл"),
    (24, "Перфопанель 750×1000", "1", "с набором крючков 50 шт"),
    (25, "Стеллаж 3000×500×2100, 5 ярусов", "1", "брус 50×50, полки ОСБ 18"),
    (26, "Инструментальная стена", "1", "2 рейки + 12 держателей"),
    (27, "Антресоль 2430×400 на кронштейнах", "1", "ОСБ 18, h=1900 от пола"),
    (28, "Полки для ГСМ/мелочей 690×280", "2", "ОСБ 18, h=1250 / 1650"),
    (29, "Рейка с крюками (шланг, удлинитель, триммер)", "1", "правый торец, h=1550"),
    (30, "Место газонокосилки", "—", "600×900"),
    (31, "Место мотоблока / культиватора", "—", "650×1400"),
    (32, "Место садовой тачки", "—", "600×1400"),
    (33, "Коврик резиновый под технику", "1", "2130×1350, 6 мм"),
    (34, "Светильник LED 1200 мм (опция)", "2", "при подключении эл-ва"),
]


def plan_walls(v, zcut=1100):
    """Стены на плане: разрез на высоте zcut."""
    C = LV["clad"]
    T = P["wall_t"]
    osb = P["osb_wall"]
    door = EL["door"]
    wins = [EL["window_0"], EL["window_1"]]
    # отрезки фронтальной стены без проёмов (окна на высоте zcut тоже вырезаны)
    op = sorted([(door["x0"], door["x1"])] + [(w["x0"], w["x1"]) for w in wins])
    segs, a = [], 0
    for o0, o1 in op:
        segs.append((a, o0)); a = o1
    segs.append((a, L))

    def wall_x(x0, x1, y_out, sgn):
        # sgn: +1 — стена у y=0 (внутрь +y), -1 — у y=W
        yo = y_out
        yi = yo + sgn * T
        v.rect(x0, min(yo, yi), x1, max(yo, yi), fc="#fff8dc", ec="k", lw=LW_MAIN, z=3)
        zigzag(v, x0, min(yo, yi) + 10, x1, max(yo, yi) - 10)
        v.rect(x0, min(yi, yi + sgn * osb), x1, max(yi, yi + sgn * osb), fc="#f3e3c3", ec="k", lw=LW_MAIN, z=3)
        v.rect(x0, min(yo, yo - sgn * C), x1, max(yo, yo - sgn * C), fc="#333", ec="k", lw=LW_THIN, z=3)

    for x0, x1 in segs:
        wall_x(max(x0, T), min(x1, L - T), 0, 1)
    wall_x(T, L - T, W, -1)

    def wall_y(x_out, sgn):
        xo, xi = x_out, x_out + sgn * T
        v.rect(min(xo, xi), 0, max(xo, xi), W, fc="#fff8dc", ec="k", lw=LW_MAIN, z=3)
        zigzag(v, min(xo, xi) + 10, 0, max(xo, xi) - 10, W, along_a=False)
        v.rect(min(xi, xi + sgn * osb), T, max(xi, xi + sgn * osb), W - T, fc="#f3e3c3", ec="k", lw=LW_MAIN, z=3)
        v.rect(min(xo, xo - sgn * C), -C, max(xo, xo - sgn * C), W + C, fc="#333", ec="k", lw=LW_THIN, z=3)
    wall_y(0, 1)
    wall_y(L, -1)
    # стойки каркаса в разрезе (угловые и у проёмов)
    for p in parts_where(groups=["frame", "frame_front"], pred=lambda p: p["b"][2] <= 200 and p["b"][5] > zcut
                         and (p["b"][3] - p["b"][0]) <= 60 or (p["b"][4] - p["b"][1]) <= 60 and p["b"][2] <= 200 and p["b"][5] > zcut and p["group"] in ("frame", "frame_front")):
        b = p["b"]
        if b[5] - b[2] < 1500:
            continue
        v.rect(b[0], b[1], b[3], b[4], fc="#f6ecd9", ec="k", lw=LW_MAIN, z=4)
        v.line(b[0], b[1], b[3], b[4], lw=LW_THIN, z=4)
    # окна в плане
    for w in wins:
        x0, x1 = w["x0"], w["x1"]
        v.rect(x0, -C - 30, x1, 90, fc="white", ec="k", lw=LW_THIN, z=4)
        for yy in (20, 55, 90):
            v.line(x0, yy, x1, yy, lw=LW_THIN, z=5)
        v.rect(x0 - 30, 90, x1 + 30, 240, fc="white", ec="k", lw=LW_THIN, z=4)  # подоконник
        v.rect(x0 - 40, -C - 110, x1 + 40, -C, fc="white", ec="k", lw=LW_THIN, z=4)  # отлив
    # дверь: открывание наружу, петли слева
    x0, x1 = door["x0"], door["x1"]
    v.rect(x0, 0, x0 + 55, 70, fc="#666", lw=LW_THIN, z=4)
    v.rect(x1 - 55, 0, x1, 70, fc="#666", lw=LW_THIN, z=4)
    lw_ = door["leaf_w"]
    v.rect(x0 + 55, -lw_, x0 + 105, 0, fc="#999", lw=LW_THIN, z=4)
    X, Y = v.p(x0 + 55, 0)
    v.ax.add_patch(Arc((X, Y), 2 * lw_ / v.s, 2 * lw_ / v.s, theta1=-90, theta2=0, lw=LW_THIN, zorder=4))


def sheet_plan(pdf, n, total):
    sh = Sheet("План с расстановкой\nоборудования. План фундамента", n, total, "М 1:25, 1:75")
    s = 25
    v = View(sh, 62, 125, s)
    zc = ZF + 1100
    # пол
    v.rect(IN["x0"], IN["y0"], IN["x1"], IN["y1"], fc="white", ec="none", z=1)
    # оборудование ниже плоскости разреза — сверху вниз
    eq = parts_where(groups=["equip"], pred=lambda p: p["b"][2] < zc and p["id"] not in ("lamp0", "lamp1"))
    eqc = []
    for p in eq:
        b = list(p["b"]); b[5] = min(b[5], zc)
        eqc.append(dict(p, b=b))
    draw_parts(v, eqc, "top")
    # выше разреза — штрихпунктир
    for p in ["antresol", "gsm_shelf0", "pegboard", "toolrail0"]:
        b = [q for q in PARTS if q["id"] == p][0]["b"]
        v.rect(b[0], b[1], b[3], b[4], fc=None, ec="k", lw=LW_THIN, ls=(0, (6, 2, 1, 2)), z=5)
    plan_walls(v, zc)
    # ступени
    for p in parts_where(groups=["site"]):
        b = p["b"]; v.rect(b[0], b[1], b[3], b[4], fc="#eadcc4", lw=LW_THIN)
    v.text(P["door"]["x_c"], -600, "Вход", FS_S)
    # блоки фундамента (пунктир)
    for p in parts_where(groups=["foundation"], pred=lambda p: p["id"].startswith("block")):
        b = p["b"]; v.rect(b[0], b[1], b[3], b[4], fc=None, lw=LW_THIN, ls=(0, (3, 2)), z=6)
    # зона техники
    v.text(4650, 1500, "Зона хранения\nсадовой техники", FS_S, style="italic", linespacing=1.2)
    v.text(1500, 1180, "проход 830", FS_S, style="italic")
    # размеры
    C = LV["clad"]
    v.dim(0, W + C, L, W + C, 600, f"{L:.0f} (по каркасу)")
    v.chain([IN["x0"], IN["x0"] + 2000, 3150 + IN["x0"], IN["x1"]], W + C, 300)
    v.chain([-C, 650, 1650, 2420, 3380, 4150, 5150, L + C], -C, -900)
    v.dim(L + C, -C, L + C, W + C, 700, f"{W + 2 * C:.0f}", horiz=False)
    v.dim(L + C, IN["y0"], L + C, IN["y1"], 380, f"{IN['y1'] - IN['y0']:.0f}", horiz=False)
    v.chain([IN["y0"], IN["y0"] + 650, IN["y1"] - 500, IN["y1"]], -C, -500, horiz=False)
    v.text(1600, 1400, f"Хозблок  S = {(IN['x1'] - IN['x0']) * (IN['y1'] - IN['y0']) / 1e6:.1f} м²".replace(".", ","),
           FS, weight="bold")
    # позиции
    lab = [(21, 900, 500, 900, -1350), (22, 1850, 760, 1850, -1350), (23, 400, 600, 400, -1350),
           (24, 115, 1100, 650, 1000), (25, 1500, 1850, 1500, 3250), (26, 4300, 2070, 4300, 3250),
           (27, 3600, 1800, 3600, 3250), (28, 3700, 200, 3700, -1350), (29, 5670, 800, 6300, 1100),
           (30, 3900, 700, 6300, 300), (31, 4600, 1100, 6300, 700), (32, 5400, 1300, 6300, 1500),
           (33, 3620, 1300, 3250, 1150)]
    for num, a, b, a2, b2 in lab:
        v.label(a, b, a2, b2, num)
    # оси
    for a, t in [(0, "1"), (L, "2")]:
        v.line(a, W + C, a, W + 1700, lw=LW_THIN, ls=(0, (8, 2, 1, 2)))
        x, y = v.p(a, W + 1800); sh.ax.add_patch(Circle((x, y), 3.5, fc="white", ec="k", lw=LW_THIN)); sh.t(x, y, t, FS)
    for b, t in [(0, "А"), (W, "Б")]:
        v.line(-C, b, -850, b, lw=LW_THIN, ls=(0, (8, 2, 1, 2)))
        x, y = v.p(-950, b); sh.ax.add_patch(Circle((x, y), 3.5, fc="white", ec="k", lw=LW_THIN)); sh.t(x, y, t, FS)
    v.title(L / 2 - 400, W + 1750, "План на отм. +1,100 с расстановкой оборудования", s)

    # экспликация
    sh.t(371, 283, "Экспликация оборудования", FS * 1.1, weight="bold")
    rows = [[str(a), b, c] for a, b, c, _ in EXPL]
    yb = sh.table(328, 279, [8, 71, 8], rows, head=["Поз.", "Наименование", "Кол."], rh=4.8, size=FS_S * 0.92)
    sh.t(328, yb - 3, "Материалы наполнения — лист 6.", FS_S, ha="left")

    # план фундамента 1:50
    vf = View(sh, 333, 150, 75)
    vf.rect(0, 0, L, W, fc=None, ec="k", lw=LW_THIN, ls=(0, (6, 2)))
    for p in parts_where(groups=["frame"], pred=lambda p: p["id"].startswith("base")):
        b = p["b"]; vf.rect(b[0], b[1], b[3], b[4], fc="#f6ecd9", lw=LW_THIN)
    for p in parts_where(groups=["foundation"], pred=lambda p: p["id"].startswith("block")):
        b = p["b"]; vf.rect(b[0], b[1], b[3], b[4], fc="#cccccc", lw=LW_MAIN, hatch="..", z=4)
    xs = [BM.block_x[0], BM.block_x[1], BM.block_x[2], BM.block_x[3]]
    vf.chain([0] + xs + [L], W, 500)
    vf.dim(L, 0, L, W, 500, horiz=False)
    vf.title(L / 2 - 300, -700, "План фундамента", 75)
    sh.t(328, 128, "Опоры — блоки бетонные 400×200×200 (8 шт.)\nна песчано-щебёночной подушке 100 мм,\n"
         "гидроизоляция — рубероид в 2 слоя.\nГоризонтальность обвязки выставить\n"
         "подкладками из рубероида/пластин ±5 мм.", FS_S, ha="left", va="top", linespacing=1.4)
    return sh


# ============================================================ ЛИСТ 3 — разрез и узлы
PIE = [
    ("Кровля", ["Профлист С20 оцинкованный 0,45 мм", "Обрешётка доска 25×100, шаг 300",
                "Гидроизоляция (Изоспан D)", "Стропила 50×100, шаг 575 (фермы)"]),
    ("Потолок", ["Нижний пояс фермы 50×100", "Утеплитель мин. вата 100 мм",
                 "Пароизоляция (Изоспан B)", "ОСБ-3 9 мм"]),
    ("Стена", ["Профлист С8 0,45 мм, полимер", "Ветро-влагозащита (Изоспан А)",
               "Каркас 50×100, шаг ≤600 + утеплитель 100", "Пароизоляция (Изоспан B)", "ОСБ-3 9 мм"]),
    ("Пол", ["ОСБ-3 12 мм", "Доска обрезная 25 мм", "Пароизоляция (Изоспан B)",
             "Утеплитель мин. вата 100 мм между лагами 50×150", "Ветро-влагозащита (Изоспан А)",
             "Черновой пол доска 25 мм на черепном бруске 40×40"]),
]


def section_structure(v, detail=False):
    """Поперечный разрез по несущим слоям. a = y (фасад слева), b = z."""
    T, C = P["wall_t"], LV["clad"]
    g = LV["ground"]
    bh = P["base_h"]
    zs_top = LV["plate_top"] - P["top_plate"]
    # фундамент
    for yc in (50, W - 50):
        cut_sheet(v, yc - 120, g, yc + 120, 0, "concrete")
    # нижняя обвязка (разрез)
    cut_timber(v, 0, 0, T, bh)
    cut_timber(v, W - T, 0, W, bh)
    # пол
    cut_sheet(v, T, 20, W - T, 45, "board")
    v.rect(T, 45, W - T, bh, fc="#fff8dc", ec="k", lw=LW_MAIN, z=3)
    zigzag(v, T, 50, W - T, bh - 5)
    cut_sheet(v, T, bh, W - T, bh + 25, "board")
    cut_sheet(v, T, bh + 25, W - T, ZF, "osb")
    membrane(v, [(T, 18), (W - T, 18)])
    membrane(v, [(T, bh + 2), (W - T, bh + 2)])
    for yy in (T + 20, W - T - 60):
        cut_timber(v, yy, 20 - 0, yy + 40, 60) if detail else None
    # стены
    for y0, sgn in ((0, 1), (W, -1)):
        yi = y0 + sgn * T
        v.rect(min(y0, yi), bh, max(y0, yi), zs_top, fc="#fff8dc", ec="k", lw=LW_MAIN, z=3)
        zigzag(v, min(y0, yi) + 10, bh + 10, max(y0, yi) - 10, zs_top - 10, along_a=False)
        cut_timber(v, min(y0, yi), zs_top, max(y0, yi), LV["plate_top"])
        cut_sheet(v, min(yi, yi + sgn * 9), ZF, max(yi, yi + sgn * 9), LV["ceil"], "osb")
        membrane(v, [(yi + sgn * 1, ZF), (yi + sgn * 1, LV["ceil"])])
        membrane(v, [(y0 - sgn * 3, -40), (y0 - sgn * 3, LV["chord_top"] + 90)])
        # профлист
        yo = y0 - sgn * C
        v.line(yo, -40, yo, LV["roof_at_wall"] - 50 - (0 if sgn > 0 else 0), lw=LW_BOLD)
        v.line(yo - sgn * 8, -40, yo - sgn * 8, LV["roof_at_wall"] - 50, lw=LW_THIN)
        # отлив
        v.poly([(y0, -10), (y0 - sgn * 55, -10), (y0 - sgn * 55, -60)], fc=None, lw=LW_MAIN, closed=False)
    # потолок
    cut_sheet(v, T, LV["ceil"], W - T, LV["plate_top"], "osb")
    membrane(v, [(T, LV["plate_top"] + 2), (W - T, LV["plate_top"] + 2)])
    v.rect(T, LV["plate_top"], W - T, LV["chord_top"], fc="#fff8dc", ec="k", lw=LW_MAIN, z=3)
    zigzag(v, T, LV["plate_top"] + 8, W - T, LV["chord_top"] - 8)
    # ферма за плоскостью разреза (видимые линии)
    v.rect(-30, LV["plate_top"], W + 30, LV["chord_top"], fc=None, ec="k", lw=LW_THIN, z=2)
    kp = LV["ridge"] - 20 - 25 - 100 / COS
    v.rect(W / 2 - 50, LV["chord_top"], W / 2 + 50, kp, fc="#f6ecd9", ec="k", lw=LW_THIN, z=2)
    for sg in (1, -1):
        e0 = -50 if sg > 0 else W + 50
        top = lambda y: roof_z(y) - 45
        pts = [(e0, top(e0)), (W / 2, top(W / 2)), (W / 2, top(W / 2) - 100 / COS), (e0, top(e0) - 100 / COS)]
        v.poly(pts, fc="#f6ecd9", ec="k", lw=LW_THIN, z=2)
        # обрешётка (разрез)
        for k in range(5):
            s_ = 60 + k * ((W / 2 + 50) / COS - 120) / 4
            y = -50 + s_ * COS if sg > 0 else W + 50 - s_ * COS
            z = roof_z(y) - 20
            ang = math.radians(P["roof_pitch"]) * sg
            ca, sa = math.cos(ang), math.sin(ang)
            corners = [(-50, 0), (50, 0), (50, -25), (-50, -25)]
            v.poly([(y + u * ca - w_ * sa * 0, z + u * sa + w_ * ca) for u, w_ in corners], fc="#f6ecd9",
                   ec="k", lw=LW_MAIN, z=4)
        # лист кровли
        v.poly([(e0, roof_z(e0)), (W / 2, roof_z(W / 2)), (W / 2, roof_z(W / 2) - 20), (e0, roof_z(e0) - 20)],
               fc="#999", ec="k", lw=LW_MAIN, z=4)
        membrane(v, [(e0, roof_z(e0) - 48), (W / 2, roof_z(W / 2) - 48)])
    # конёк
    v.poly([(W / 2 - 190, roof_z(W / 2 - 190) + 8), (W / 2, LV["ridge"] + 30), (W / 2 + 190, roof_z(W / 2 + 190) + 8)],
           fc=None, lw=LW_MAIN, closed=False, z=5)
    # земля
    v.line(-800, g, W + 800, g, lw=LW_BOLD)
    for a in range(-800, W + 800, 200):
        v.line(a, g, a - 120, g - 120, lw=LW_THIN)


def sheet_section(pdf, n, total):
    sh = Sheet("Разрез 1-1. Узлы 1, 2.\nСостав конструкций", n, total, "М 1:20, 1:10")
    s = 20
    g = LV["ground"]
    v = View(sh, 60, 80 - g / s, s)
    xcut = 2250
    # помещение и оборудование за плоскостью разреза (вид в сторону левого торца)
    v.rect(IN["y0"], ZF, IN["y1"], LV["ceil"], fc="white", ec="none", z=1)
    eq = parts_where(groups=["equip"], pred=lambda p: p["b"][0] < xcut and p["id"] not in ("lamp0", "lamp1"))
    draw_parts(v, eq, "right", clip=(IN["y0"], ZF, IN["y1"], LV["ceil"]))
    section_structure(v)
    # размеры
    v.dim(-50, LV["ridge"], W + 50, LV["ridge"], 350, "2300")
    v.dim(0, g, W, g, -320, f"{W}")
    v.chain([0, IN["y0"], IN["y0"] + 650, IN["y1"] - 500, IN["y1"], W], g, -130)
    v.dim(W + 12, ZF, W + 12, LV["ceil"], 380, "2170", horiz=False)
    v.dim(W + 12, g, W + 12, LV["ridge"], 700, f"{LV['ridge'] - g:.0f}", horiz=False)
    v.chain([g, 0, P['base_h'], ZF], W + 12, 380, horiz=False)
    v.dim(W + 12, LV["ceil"], W + 12, LV["ridge"], 380, f"{LV['ridge'] - LV['ceil']:.0f}", horiz=False)
    v.dim(IN["y0"], ZF, IN["y0"], ZF + 900, -330, "900", horiz=False)
    for z in (g, ZF, LV["ceil"], LV["ridge"]):
        v.level(-520, z, z, right=False)
        v.line(-520, z, -12 if z != LV["ridge"] else W / 2, z, lw=LW_THIN, ls=(0, (4, 2)))
    v.text(1000, ZF + 300, "проход 832", FS_S, style="italic")
    # маркеры узлов
    for (a, b, r, num) in [(40, 120, 380, 1), (40, 2420, 380, 2)]:
        x, y = v.p(a, b)
        sh.ax.add_patch(Circle((x, y), r / s, fc="none", ec="k", lw=LW_THIN, ls=(0, (4, 2)), zorder=7))
        sh.ax.add_patch(Circle((x - r / s - 3, y), 2.6, fc="white", ec="k", lw=LW_THIN, zorder=7))
        sh.t(x - r / s - 3, y, str(num), FS_S, zorder=8)
    v.title(W / 2, g - 900, "Разрез 1-1", s)
    sh.t(60, 60, "Разрез выполнен на расстоянии 2250 мм от левого торца, вид на левый торец\n"
         "(верстак, стеллаж, перфопанель).", FS_S, ha="left", va="top", linespacing=1.4)

    # узлы 1:10
    def node(ox, oy, a0, b0, a1, b1, name, labels):
        vn = View(sh, ox - a0 / 10, oy - b0 / 10, 10)
        sh.ax.add_patch(Rectangle(vn.p(a0, b0), (a1 - a0) / 10, (b1 - b0) / 10, fill=False, lw=LW_THIN, ls=(0, (4, 2))))
        clip = Rectangle(vn.p(a0, b0), (a1 - a0) / 10, (b1 - b0) / 10, transform=sh.ax.transData)
        n_before = len(sh.ax.patches), len(sh.ax.lines)
        section_structure(vn, detail=True)
        eqn = parts_where(groups=["equip"], pred=lambda p: p["b"][0] < xcut and p["id"].startswith("bench"))
        for art in sh.ax.patches[n_before[0]:] + sh.ax.lines[n_before[1]:]:
            art.set_clip_path(clip)
        for i, (a, b, text) in enumerate(labels):
            tx, ty = ox + (a1 - a0) / 10 + 4, oy + (b1 - b0) / 10 - 4 - i * 5.2
            x, y = vn.p(a, b)
            sh.ax.plot([x, tx - 1, tx + 1], [y, ty, ty], c="k", lw=LW_THIN, zorder=8)
            sh.ax.add_patch(Circle((x, y), 0.4, color="k", zorder=8))
            sh.t(tx + 2, ty, text, FS_S * 0.95, ha="left")
        sh.t(ox + (a1 - a0) / 20, oy - 5, name, FS * 1.1, weight="bold")

    node(222, 200, -200, -260, 450, 380, "Узел 1  М 1:10",
         [(-16, 250, "Профлист С8"), (-3, 150, "Ветрозащита"), (50, 250, "Утеплитель 100"),
          (104, 330, "ОСБ-3 9 мм"), (300, ZF - 5, "ОСБ-3 12 мм"), (300, 160, "Доска 25 мм"),
          (300, 100, "Утеплитель 100"), (300, 32, "Черн. пол 25"), (50, 75, "Обвязка 100×150"),
          (-40, -40, "Отлив цокольный"), (50, -120, "Блок 400×200×200")])
    node(222, 110, -200, 2250, 450, 2780, "Узел 2  М 1:10",
         [(250, LV["ridge"] - 20 - (W / 2 - 250) * TAN, "Профлист С20"), (380, 2718, "Обрешётка 25×100"),
          (150, 2620, "Стропило 50×100"), (300, 2440, "Утеплитель 100"), (300, LV["plate_top"] - 4, "ОСБ-3 9 мм"),
          (50, LV["plate_top"] - 20, "Верхняя обвязка 50×100"), (50, 2250 + 40, "Утеплитель стены"),
          (-12, 2400, "Профлист С8")])

    # состав конструкций
    y = 285
    sh.t(372, y, "Состав конструкций (снаружи внутрь)", FS * 1.1, weight="bold")
    y -= 6
    for head, items in PIE:
        sh.t(328, y, head + ":", FS, ha="left", weight="bold"); y -= 4.3
        for i, it in enumerate(items):
            sh.t(331, y, f"{i + 1}. {it}", FS_S * 0.95, ha="left"); y -= 3.9
        y -= 1.5
    sh.t(328, y - 2, "Примечания:\n1. Высота помещения в чистоте 2170 мм —\n   под металлическую дверь 2050×960.\n"
         "2. Пароизоляцию укладывать с нахлёстом 100 мм,\n   стыки проклеить соединительной лентой.\n"
         "3. Пиломатериал — хвойных пород, 1–2 сорт,\n   обработать антисептиком.\n"
         "4. Утеплитель — минвата плотн. ≥ 35 кг/м³.", FS_S, ha="left", va="top", linespacing=1.35)
    return sh


# ============================================================ ЛИСТ 4 — развёртки стен
def sheet_elevations(pdf, n, total):
    sh = Sheet("Развёртки внутренних стен\nс оборудованием", n, total, "М 1:30")
    s = 30
    ww, hh = IN["x1"] - IN["x0"], IN["y1"] - IN["y0"]

    def room_view(ox, oy, view, name, labels, a_range):
        v = View(sh, ox, oy - ZF / s, s)
        a0, a1 = a_range
        v.rect(a0, ZF, a1, LV["ceil"], fc="#fbf6ec", ec="none", z=1)
        # детали оборудования, открытые из помещения
        def inside(p):
            b = p["b"]
            return b[3] > IN["x0"] - 1 and b[0] < IN["x1"] + 1 and b[4] > IN["y0"] - 1 and b[1] < IN["y1"] + 1
        near = {"front": lambda b: b[4] >= IN["y1"] - 120,      # задняя стена
                "back": lambda b: b[1] <= IN["y0"] + 150,      # стена с дверью
                "right": lambda b: b[0] <= IN["x0"] + 150,     # левый торец
                "left": lambda b: b[3] >= IN["x1"] - 150}[view]
        pp = parts_where(groups=["equip"], pred=lambda p: inside(p) and near(p["b"]) and not p["id"].startswith("lamp"))
        op = parts_where(groups=["openings"], pred=lambda p: p["b"][4] > 60) if view == "back" else []
        fa, fd = MAP[view]
        draw_parts(v, op + pp, view, clip=(a0, ZF, a1, LV["ceil"]))
        v.rect(a0, ZF, a1, LV["ceil"], fc=None, ec="k", lw=LW_BOLD, z=6)
        v.dim(a0, LV["ceil"], a1, LV["ceil"], 250)
        v.dim(a1, ZF, a1, LV["ceil"], 250, "2170", horiz=False)
        for num, a, b, a2, b2 in labels:
            v.label(a, b, a2, b2, num)
        v.title((a0 + a1) / 2, ZF - (1050 if view == "back" else 450), name, s)
        return v

    # задняя стена — вид изнутри к +Y: a = x
    v1 = room_view(40, 190, "front", "Развёртка А — задняя стена", [
        (25, 1500, ZF + 1700, 1500, LV["ceil"] + 600), (26, 4200, ZF + 1300, 4200, LV["ceil"] + 600),
        (27, 5000, ZF + 1910, 5000, LV["ceil"] + 600)], (IN["x0"], IN["x1"]))
    v1.chain([IN["x0"], IN["x0"] + 3000, IN["x0"] + 3150, IN["x1"] - 60, IN["x1"]], ZF, -250)
    for h in (150, 600, 1050, 1500, 1950):
        pass
    v1.chain([ZF + h for h in (150, 600, 1050, 1500, 1950)], IN["x0"], -250, horiz=False)
    # фронтальная стена изнутри — к -Y: a = L - x
    v2 = room_view(40, 82, "back", "Развёртка Б — стена с дверью и окнами", [
        (21, L - 1100, ZF + 700, L - 1100, ZF - 300), (22, L - 1850, ZF + 950, L + 1000, ZF + 1300),
        (28, L - 3780, ZF + 1650, -350, ZF + 1650), (30, L - 3950, ZF + 300, L - 3400 + 0, ZF - 300),
        (31, L - 4700, ZF + 500, L - 4700, ZF - 300), (32, L - 5400, ZF + 400, L - 5400, ZF - 300),
        (23, L - 400, ZF + 500, L - 250, ZF - 300)], (L - IN["x1"], L - IN["x0"]))
    v2.chain([L - IN["x1"], L - 5150, L - 4150, L - 3380, L - 2420, L - 1650, L - 650, L - IN["x0"]], ZF, -650)
    v2.chain([ZF, P["win_top"] - 1000, P["win_top"]], L - IN["x0"], 700, horiz=False)
    # левый торец изнутри — к -X: a = y
    v3 = room_view(300, 190, "right", "Развёртка В — левый торец", [
        (24, 1100, ZF + 1500, 1100, LV["ceil"] + 600), (25, 1850, ZF + 1100, 2350, ZF + 1100),
        (21, 400, ZF + 700, -550, ZF + 700)], (IN["y0"], IN["y1"]))
    v3.chain([IN["y0"], IN["y0"] + 700, IN["y0"] + 1450, IN["y1"]], ZF, -250)
    v3.chain([ZF, ZF + 900, ZF + 950, ZF + 1950, LV["ceil"]], IN["y0"], -300, horiz=False)
    # правый торец изнутри — к +X: a = W - y
    v4 = room_view(300, 82, "left", "Развёртка Г — правый торец", [
        (29, W - 800, ZF + 1550, W + 500, ZF + 1550), (32, W - 700, ZF + 300, W + 500, ZF + 300),
        (26, W - 2060, ZF + 1500, W - 2400, ZF + 1500), (27, W - 1900, ZF + 1920, W - 2400, ZF + 1920)],
        (W - IN["y1"], W - IN["y0"]))
    v4.chain([W - IN["y1"], W - IN["y1"] + 400 * 0 + 450, W - IN["y0"] - 250, W - IN["y0"]], ZF, -250)
    sh.t(300, 32, "Позиции — по экспликации (лист 2).\nВысоты даны от уровня чистого пола.",
         FS_S, ha="left", va="top", linespacing=1.4) if False else None
    return sh


# ============================================================ ЛИСТ 5 — каркас
def lumber_spec():
    spec = defaultdict(lambda: [0, 0.0])
    for e in MODEL["elements"]:
        if e.get("group") not in ("frame", "roof") or "sec" not in e:
            continue
        if e["kind"] == "box":
            b = e["b"]; ln = max(b[3] - b[0], b[4] - b[1], b[5] - b[2])
        else:
            ln = max(e["s"])
        sec = e["sec"]
        mult = 2 if sec.startswith("2x") else 1
        sec = sec.replace("2x", "")
        spec[sec][0] += mult
        spec[sec][1] += ln * mult / 1000
    out = []
    for sec, (cnt, ln) in sorted(spec.items()):
        a, b = map(int, sec.split("x"))
        out.append((sec, cnt, ln, a * b * ln / 1e6))
    return out


def sheet_frame(pdf, n, total):
    sh = Sheet("Каркас. Схемы\nраскладки элементов", n, total, "М 1:50, 1:20")
    s = 50

    def elev(ox, oy, prefs, view, name, a_rng):
        v = View(sh, ox, oy, s)
        pp = parts_where(pref=prefs)
        pp = [p for p in pp if p["group"] in ("frame", "frame_front")]
        draw_parts(v, [p for p in pp if not p["id"].startswith("br_")], view, lw=LW_THIN)
        fa = MAP[view][0]
        for e in MODEL["elements"]:           # раскосы — наклонной линией
            if e["kind"] != "rbox" or not any(e["id"].startswith(x) for x in prefs):
                continue
            ang = math.radians(e["ry"] or e["rx"])
            ln = max(e["s"])
            c = e["c"]
            if e["ry"]:
                d = (ln / 2 * math.cos(ang), 0, -ln / 2 * math.sin(ang))
            else:
                d = (0, ln / 2 * math.cos(ang), ln / 2 * math.sin(ang))
            p0 = [c[i] - d[i] for i in range(3)]; p1 = [c[i] + d[i] for i in range(3)]
            a0 = fa([p0[0], p0[1], p0[2]] * 2)[0]; a1 = fa([p1[0], p1[1], p1[2]] * 2)[0]
            v.line(a0, p0[2], a1, p1[2], lw=LW_BOLD * 1.4, c="#b08850")
        v.title(sum(a_rng) / 2, -480, name, s)
        return v, pp

    v, _ = elev(35, 222, ["wf_", "br_f", "base_front"], "front", "Стена по оси А (с проёмами)", (0, L))
    v.chain([0, 650, 1650, 2420, 3380, 4150, 5150, L], LV["plate_top"], 250)
    v.dim(L, 0, L, LV["plate_top"], 280, horiz=False)
    v.chain([0, P["base_h"], P["win_top"] - 1000, P["win_top"]], 0, -250, horiz=False)
    v, _ = elev(35, 155, ["wb_", "br_b", "base_back"], "back", "Стена по оси Б", (0, L))
    v.dim(0, LV["plate_top"], L, LV["plate_top"], 250)
    v, _ = elev(35, 88, ["wl_", "br_l", "base_left"], "left", "Торцевая стена (ось 1)", (0, W))
    v.dim(0, LV["plate_top"], W, LV["plate_top"], 250)
    v, _ = elev(105, 88, ["wr_", "br_r", "base_right"], "right", "Торцевая стена (ось 2)", (0, W))
    v.dim(0, LV["plate_top"], W, LV["plate_top"], 250)

    # план каркаса пола 1:40
    vf = View(sh, 190, 222, s)
    for p in parts_where(groups=["foundation"], pred=lambda p: p["id"].startswith("block")):
        b = p["b"]; vf.rect(b[0], b[1], b[3], b[4], fc=None, lw=LW_THIN, ls=(0, (3, 2)), z=6)
    draw_parts(vf, parts_where(pref=["base_", "joist_"]), "top", lw=LW_THIN)
    vf.chain([0] + [round(x) for x in BM.joist_x] + [L], W, 300)
    vf.dim(L, 0, L, W, 250, horiz=False)
    vf.title(L / 2, -480, "Каркас пола (обвязка, лаги)", s)

    # ферма 1:20
    vt = View(sh, 192, 172 - LV["plate_top"] / 20, 20)
    fr = parts_where(pref=["chord_0", "rafter_0", "kingpost_0"])
    draw_parts(vt, [p for p in fr if not p["id"].startswith("rafter")], "right", lw=LW_THIN)
    for sg in (1, -1):
        e0 = -50 if sg > 0 else W + 50
        top = lambda y: roof_z(y) - 45
        vt.poly([(e0, top(e0)), (W / 2, top(W / 2)), (W / 2, top(W / 2) - 100 / COS), (e0, top(e0) - 100 / COS)],
                fc="#f6ecd9", lw=LW_MAIN, z=4)
        vt.poly([(W / 2 - sg * 300, top(W / 2 - sg * 300) - 100 / COS), (W / 2 - sg * 300, LV["chord_top"])],
                fc=None, lw=LW_THIN, closed=False) if False else None
    for yy in (0, W - 100):
        vt.rect(yy, LV["plate_top"] - 50, yy + 100, LV["plate_top"], fc="#ddd", lw=LW_THIN)
    vt.dim(-50, LV["chord_top"], W + 50, LV["chord_top"], -420, "2300")
    vt.dim(0, LV["chord_top"], W, LV["chord_top"], -250, f"{W}")
    vt.dim(W + 50, LV["plate_top"], W + 50, LV["ridge"] - 45, 250, f"{LV['ridge'] - 45 - LV['plate_top']:.0f}", horiz=False)
    vt.text(W * 0.25, roof_z(W * 0.25) + 120, f"{P['roof_pitch']}°", FS_S)
    vt.title(W / 2, LV["plate_top"] - 700, f"Ферма Ф-1 ({P['truss_count']} шт., шаг 575)", 20)

    # 3D каркаса
    img = ROOT / "images" / "frame.png"
    if img.exists():
        im = imread(img)
        h, w = im.shape[:2]
        crop = im[int(h * 0.05):int(h * 0.95), int(w * 0.18):int(w * 0.85)]
        sh.ax.imshow(crop, extent=(322, 413, 150, 150 + 91 * crop.shape[0] / crop.shape[1]), zorder=1)

    # спецификация пиломатериала
    rows = []
    names = {"100x150": "Брус (обвязка)", "50x150": "Доска (лаги пола)", "50x100": "Доска (стойки, фермы)",
             "25x100": "Доска (раскосы, обрешётка)"}
    tot = 0
    for sec, cnt, ln, vol in lumber_spec():
        rows.append([names.get(sec, "Пиломатериал"), sec.replace("x", "×"), f"{cnt}", f"{ln:.1f}", f"{vol:.2f}"])
        tot += vol
    rows.append(["Итого по каркасу", "", "", "", f"{tot:.2f}"])
    sh.t(300, 129, "Спецификация пиломатериала каркаса (без запаса)", FS * 1.05, weight="bold")
    sh.table(232, 125, [58, 20, 18, 22, 22], rows, head=["Наименование", "Сечение", "Шт.", "Длина, м", "Объём, м³"], rh=4.6)
    sh.t(232, 92, "Узлы соединения: стойки к обвязке — уголки 90×90 + саморезы 5×50;\n"
         "фермы к верхней обвязке — уголки 70×70 и косые гвозди 4×100;\nлаги к обвязке — опоры бруса 50×150.\n"
         "Сборку вести в порядке: блоки → обвязка+лаги → черновой пол → стены →\n"
         "фермы → обрешётка/кровля → окна/дверь → утепление → отделка.",
         FS_S, ha="left", va="top", linespacing=1.4)
    return sh


# ============================================================ ЛИСТ 6 — оборудование
def sheet_equipment(pdf, n, total):
    sh = Sheet("Оборудование для хранения.\nДеталировка, спецификация", n, total, "М 1:20, 1:25")
    s = 20
    # верстак — вид спереди (из помещения к -Y: как развёртка Б)
    bench = parts_where(pref=["bench_", "vise"], pred=lambda p: p["group"] == "equip" and p["id"] != "bench_stuff")
    v = View(sh, 35 - (L - 2000) / s, 222, s)
    x0 = IN["x0"]
    draw_parts(v, [dict(p, b=[p["b"][0] - x0, p["b"][1], p["b"][2] - ZF, p["b"][3] - x0, p["b"][4], p["b"][5] - ZF])
                   for p in bench], "back")
    v.line(L - 2200, 0, L + 100, 0, lw=LW_MAIN)
    v.dim(L - 2000, 0, L, 0, -150, "2000")
    v.chain([0, 180, 900 - 140, 900], L, 250, horiz=False)
    v.title(L - 1000, -480, "Верстак (поз. 21) — вид спереди", s)
    # вид сбоку
    vs = View(sh, 165, 222, s)
    draw_parts(vs, [dict(p, b=[p["b"][0], p["b"][1] - IN["y0"], p["b"][2] - ZF, p["b"][3], p["b"][4] - IN["y0"], p["b"][5] - ZF])
                    for p in bench], "right")
    vs.line(-100, 0, 750, 0, lw=LW_MAIN)
    vs.dim(0, 0, 650, 0, -150, "650")
    vs.title(325, -480, "Вид сбоку", s)

    # стеллаж — фасад 1:25
    s2 = 25
    rack = parts_where(pref=["rack_post", "rack_shelf", "rack_rail"])
    vr = View(sh, 35, 95, s2)
    draw_parts(vr, [dict(p, b=[p["b"][0] - x0, p["b"][1], p["b"][2] - ZF, p["b"][3] - x0, p["b"][4], p["b"][5] - ZF])
                    for p in rack], "front")
    vr.line(-100, 0, 3100, 0, lw=LW_MAIN)
    vr.chain([0, 1000, 2000, 3000], 2100, 250)
    vr.chain([0, 150, 600, 1050, 1500, 1950, 2100], 3000, 250, horiz=False)
    vr.title(1500, -600, "Стеллаж (поз. 25) — фасад", s2)
    vr2 = View(sh, 185, 95, s2)
    draw_parts(vr2, [dict(p, b=[p["b"][0], p["b"][1] - (IN["y1"] - 500), p["b"][2] - ZF, p["b"][3],
                                p["b"][4] - (IN["y1"] - 500), p["b"][5] - ZF]) for p in rack], "right")
    vr2.line(-100, 0, 600, 0, lw=LW_MAIN)
    vr2.dim(0, 2100, 500, 2100, 250, "500")
    vr2.title(250, -600, "Бок", s2)

    # инструментальная стена + антресоль 1:25
    tw = parts_where(pref=["toolrail", "tool_wall", "antresol"], pred=lambda p: p["id"] != "antresol_stuff")
    xo = IN["x0"] + 3150
    vt = View(sh, 240, 90, s2)
    draw_parts(vt, [dict(p, b=[p["b"][0] - xo, p["b"][1], p["b"][2] - ZF, p["b"][3] - xo, p["b"][4], p["b"][5] - ZF])
                    for p in tw], "front")
    vt.line(-100, 0, 2550, 0, lw=LW_MAIN)
    vt.dim(0, 0, IN["x1"] - 60 - xo, 0, -120)
    vt.chain([0, 1250, 1650, 1900], IN["x1"] - 60 - xo, 250, horiz=False)
    vt.title(1100, -170, "Инстр. стена и антресоль (поз. 26, 27)", s2)

    # спецификация
    rows = [
        ["21", "Брус 50×100 (ножки, царги)", "м", "14"],
        ["21", "Фанера ФСФ 18 мм (столешница 2 слоя, борт)", "лист", "2"],
        ["21", "ОСБ-3 12 мм (нижняя полка)", "м²", "1,1"],
        ["22", "Тиски слесарные 125 мм + болты М10", "шт", "1"],
        ["23", "Тумба-кассетница металл., 4 ящика", "шт", "1"],
        ["24", "Перфопанель стальная 750×1000 + крючки", "компл", "1"],
        ["25", "Брусок 50×50 (стойки 8×2,1 м)", "м", "17"],
        ["25", "Брусок 25×50 (царги под полки)", "м", "30"],
        ["25,27,28", "ОСБ-3 18 мм (полки)", "лист", "4"],
        ["26", "Доска строганая 25×100 (рейки)", "м", "5"],
        ["26", "Держатель инструмента настенный", "шт", "12"],
        ["27,28", "Кронштейн полочный 300/400 мм", "шт", "9"],
        ["29", "Крюки настенные большие (шланг, удлинитель)", "шт", "6"],
        ["33", "Коврик резиновый 6 мм", "м²", "2,9"],
        ["—", "Саморезы, уголки, лак/антисептик", "компл", "1"],
    ]
    sh.t(322, 285, "Спецификация материалов наполнения", FS * 1.05, weight="bold")
    sh.table(232, 281, [14, 128, 12, 14], rows, head=["Поз.", "Наименование", "Ед.", "Кол."], rh=4.6)
    sh.t(232, 203, "Указания:\n1. Верстак крепить к стене и полу уголками; столешница —\n"
         "   2 слоя фанеры на клею и саморезах, торец — кромка из доски.\n"
         "2. Стеллаж крепить к каркасу стены через ОСБ в стойки (саморезы\n   6×90), нагрузка на полку до 80 кг.\n"
         "3. Держатели инструмента — на рейки, рейки — в стойки каркаса.\n"
         "4. Деревянные элементы покрыть антисептиком/лаком.\n"
         "5. Зона техники у двери — порог-пандус съёмный (опция).",
         FS_S, ha="left", va="top", linespacing=1.4)
    return sh


def main():
    out = ROOT / "drawings"
    sheets = [sheet_facades, sheet_plan, sheet_section, sheet_elevations, sheet_frame, sheet_equipment]
    with PdfPages(out / "khozblok_chertezhi.pdf") as pdf:
        for i, f in enumerate(sheets, 1):
            sh = f(pdf, i, len(sheets))
            sh.save(pdf, out / f"list_{i}.png")
            print("лист", i, "готов")


if __name__ == "__main__":
    main()
