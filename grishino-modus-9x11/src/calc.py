"""Геометрия участка и расчёты сетей для варианта «Гришино-Модус 9х11».
Координаты — метры от точки н2 (левый тыльный угол): x вправо, y к улице (улица при y = 32)."""
from math import hypot, sqrt

def L(pts):
    return sum(hypot(b[0]-a[0], b[1]-a[1]) for a, b in zip(pts, pts[1:]))

def seg_dist(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx-ax, by-ay
    t = max(0, min(1, ((px-ax)*dx+(py-ay)*dy)/(dx*dx+dy*dy)))
    return hypot(px-(ax+t*dx), py-(ay+t*dy))

def poly_dist(p, pts):
    return min(seg_dist(p, a, b) for a, b in zip(pts, pts[1:]))

def rect_dist(r1, r2):
    (x1, y1, w1, h1), (x2, y2, w2, h2) = r1, r2
    dx = max(x2-(x1+w1), x1-(x2+w2), 0); dy = max(y2-(y1+h1), y1-(y2+h2), 0)
    return hypot(dx, dy)

def rn(v, d=2):
    s = f"{v:,.{d}f}".replace(",", " ").replace(".", ",")
    return s

def money(v):
    return f"{int(round(v)):,}".replace(",", " ")

# ---------- дом 9,0 × 11,5 (эскиз заказчика) ----------
HX0, HX1 = 9.0, 18.0          # оси 1 и 3
AX2 = HX0 + 3.6               # ось 2
YG, YV, YB, YA = 14.5, 23.5, 24.5, 26.0   # оси Г, В, Б, А (А — к улице)
HOUSE = (HX0, YG, 9.0, 11.5)
HEATED = [(9, 14.5), (18, 14.5), (18, 23.5), (12.6, 23.5), (12.6, 24.5), (9, 24.5)]
TERRACE = [(9, 24.5), (12.6, 24.5), (12.6, 23.5), (18, 23.5), (18, 26), (9, 26)]
STEPS = (12.45, 26.0, 3.2, 0.5)
ROOMS = {  # № : (x, y, w, h, название, площадь по эскизу)
    1: (None, None, None, None, "Терраса (открытая, под общей кровлей)", 18.9),
    2: (12.75, 16.647, 1.656, 6.853, "Холл-коридор, вход с террасы", 11.1),
    3: (9.15, 20.856, 3.306, 3.5, "Спальня", 11.6),
    4: (9.15, 17.847, 3.306, 2.912, "Спальня", 9.6),
    5: (9.15, 14.65, 3.306, 3.1, "Спальня", 10.2),
    6: (12.603, 14.65, 2.356, 1.9, "Санузел: душ, унитаз, умывальник", 4.5),
    7: (15.056, 14.65, 2.8, 1.9, "Котельная-постирочная: газовый котёл, бойлер, насосная", 5.3),
    8: (14.5, 16.647, 3.353, 6.709, "Кухня-гостиная", 23.5),
}

# ---------- остальные объекты (без изменений) ----------
BATH = (24.8, 1.5, 5.7, 6.0); BATH_TER = (24.8, 7.5, 3.0, 1.5)
GAZEBO = (4.0, 7.0, 5.0, 4.0); MANGAL = (9.0, 8.2, 0.6, 1.6)
SHED = (1.0, 1.0, 6.0, 2.3)
WELL = (31.0, 21.0)
LOS = (2.0, 29.3, 1.2, 1.2); LOS_IN = (3.2, 29.9)
PARK = (25.5, 25.0, 5.5, 6.5)

# ---------- щиты ----------
VRU = (14.3, 32.0)            # шкаф учёта: перенесён из пролёта 15,6–17,9 в пролёт 13,4–15,6
SHG = (16.875, 32.1)          # газовый шкаф: посередине пролёта 15,62–17,87 (было x = 7,875)
SHRD = (14.3, 22.9)           # ЩР-Д в холле у входа

# ---------- канализация К1 ----------
I = 0.02
KK = {"КК-Б": (22.5, 12.0), "КК-1": (21.0, 20.0), "КК-2": (21.0, 29.0),
      "КК-4": (13.2, 29.5), "КК-3": (4.2, 29.9)}
BATH_OUT = (28.1, 7.5)
HOUSE_OUT = (13.2, YV)         # выход из тёплого подполья под входной дверью, ось В
k1 = {}
k1["bath"] = [BATH_OUT, KK["КК-Б"], KK["КК-1"], KK["КК-2"], KK["КК-4"]]
k1["house"] = [HOUSE_OUT, KK["КК-4"]]
k1["main"] = [KK["КК-4"], KK["КК-3"], LOS_IN]
lv = {}
lv["вып.бани"] = -0.55
lv["КК-Б"] = lv["вып.бани"] - I*L([BATH_OUT, KK["КК-Б"]])
lv["КК-1"] = lv["КК-Б"] - I*L([KK["КК-Б"], KK["КК-1"]])
lv["КК-2"] = lv["КК-1"] - I*L([KK["КК-1"], KK["КК-2"]])
lv["КК-4"] = lv["КК-2"] - I*L([KK["КК-2"], KK["КК-4"]])
lv["вып.дома"] = -0.85
lv["КК-4 (дом)"] = lv["вып.дома"] - I*L(k1["house"])
lv["КК-3"] = lv["КК-4"] - I*L([KK["КК-4"], KK["КК-3"]])
lv["ЛОС"] = lv["КК-3"] - I*L([KK["КК-3"], LOS_IN])
K1_TOTAL = L(k1["bath"]) + L(k1["house"]) + L(k1["main"])

def k1_level_on(pts, start_level, p):
    """отметка лотка в точке p, лежащей на ломаной pts"""
    acc = 0
    for a, b in zip(pts, pts[1:]):
        seg = hypot(b[0]-a[0], b[1]-a[1])
        if seg_dist(p, a, b) < 1e-6:
            return start_level - I*(acc + hypot(p[0]-a[0], p[1]-a[1]))
        acc += seg
    raise ValueError(p)

# ---------- водопровод В1 ----------
V1 = [(30.45, 21.0), (HX1, 21.0)]                # кессон → ввод в подполье у правой стены
V1_UNDER = [(HX1, 21.0), (17.3, 21.0), (17.3, 16.2)]   # по подполью в котельную
V1_BATH = [(31.0, 20.45), (31.0, 6.95), (30.5, 6.95)]
V1_NEIGH = [(31.55, 21.0), (33.2, 21.0)]
V1_DEPTH = -1.80

# ---------- газ Г1 ----------
G1_DEPTH = -1.55                 # верх трубы
G1 = [(SHG[0], 32.1), (SHG[0], 28.0), (20.0, 28.0), (20.0, 23.3), (18.3, 23.3)]
G1_FACADE = [(18.0, 23.3), (18.0, 15.35)]        # по цоколю правой стены на +0,5
G1_ENTRY = (18.0, 15.35)

# ---------- электрика ----------
EL = {
    "ВРУ→ЩР-Д": [(VRU[0], 32.0), (VRU[0], YV)],
    "магистраль": [SHRD, (15.0, SHRD[1]), (15.0, YG), (15.0, 10.4)],  # по подполью, выход у оси Г
    "баня": [(15.0, 10.4), (28.65, 10.4), (28.65, 7.5)],
    "беседка": [(15.0, 10.4), (9.0, 10.4)],
    "хозблок": [(15.0, 10.4), (10.3, 10.4), (10.3, 4.2), (7.0, 4.2), (7.0, 2.2)],
    "насос": [SHRD, (SHRD[0], 21.0), (HX1, 21.0), (30.45, 21.0)],
    "ЛОС": [SHRD, (HX0, SHRD[1]), (2.6, SHRD[1]), (2.6, 29.3)],
}
EXTRA = 6.0   # спуск от щита в подполье и траншею ≈ 2,9 м, подъём в постройке ≈ 2,1 м, запас ≈ 1,0 м
trunk = L(EL["магистраль"])
lines = [  # QD, потребитель, P кВт, фаза, сечение, трасса
    ("QD1", "Баня: свет, розетки, водонагреватель 2 кВт, тёплый пол", 4.5, "L1", 6, trunk + L(EL["баня"])),
    ("QD2", "Беседка: свет, розетки, электрогриль", 3.5, "L2", 2.5, trunk + L(EL["беседка"])),
    ("QD3", "Хозблок: свет, розетки под инструмент", 3.5, "L3", 4, trunk + L(EL["хозблок"])),
    ("QD4", "Насос скважины SQ 5-70 (общий с соседом)", 1.7, "L2", 2.5, L(EL["насос"])),
    ("QD5", "ЛОС: компрессор, насос", 0.2, "L3", 1.5, L(EL["ЛОС"])),
]
RHO = 0.0175
def du(p_kw, l, s):
    i_ = p_kw*1000/230
    return 2*l*i_*RHO/s/230*100

# траншеи кабелей (вне дома и не в траншее В1)
EL_TRENCH = (YA + 6.0 - YV) and (32.0 - YV)  # ВРУ → ось В (под террасой — тоже в грунте)
EL_TRENCH = (32.0 - YV) + (10.4 and (YG - 10.4)) + 13.65 + 2.9 + 6.0 + 6.2 + 3.3 + 2.0 + L(EL["ЛОС"][1:])

if __name__ == "__main__":
    print("K1 lengths bath %.2f house %.2f main %.2f total %.2f" % (L(k1["bath"]), L(k1["house"]), L(k1["main"]), K1_TOTAL))
    for k, v in lv.items(): print(f"  {k:12s} {v:+.3f}")
    print("segments:")
    for a, b in [("вып.бани", "КК-Б"), ("КК-Б", "КК-1"), ("КК-1", "КК-2"), ("КК-2", "КК-4"), ("КК-4", "КК-3")]:
        pa = BATH_OUT if a == "вып.бани" else KK[a]; print(f"  {a}->{b} {L([pa, KK[b]]):.2f}")
    print("  house out -> KK-4 %.2f, KK-3->LOS %.2f" % (L(k1['house']), L([KK['КК-3'], LOS_IN])))
    # checks
    print("K1 bath line to house wall:", min(poly_dist(p, k1['bath']) for p in [(18, y/10) for y in range(145, 261)]))
    print("K1 to well:", min(poly_dist(WELL, k1[k]) for k in k1))
    print("K1 house to well", poly_dist(WELL, k1['house']))
    print("KK-4 to house front", KK['КК-4'][1]-YA)
    print("LOS to house", rect_dist(LOS, (9, 14.5, 9, 11.5)), "LOS-well", rect_dist(LOS, (30.45, 20.45, 1.1, 1.1)), hypot(WELL[0]-2.6, WELL[1]-29.9))
    print("bath-house", rect_dist(BATH, HOUSE), "bath ter-house", rect_dist(BATH_TER, HOUSE))
    print("gazebo-house", rect_dist(GAZEBO, HOUSE), "mangal-house", rect_dist(MANGAL, HOUSE))
    print("G1 underground %.2f facade %.2f" % (L(G1), L(G1_FACADE)))
    for name, (a, b) in {"KK-2": (KK['КК-2'], None)}.items(): print("G1-KK2", poly_dist(KK['КК-2'], G1))
    print("G1 - K1 bath (parallel)", min(poly_dist(p, k1['bath']) for p in [(20.0, 23.3+i*0.1) for i in range(47)]))
    print("G1 - K1 main dist from corner", poly_dist((20, 28), k1['bath']))
    # crossing G1 x=16.875 with K1 KK-2->KK-4
    a, b = KK['КК-2'], KK['КК-4']; t = (a[0]-SHG[0])/(a[0]-b[0]); yc = a[1]+t*(b[1]-a[1])
    lvl = k1_level_on(k1['bath'], lv['вып.бани'], (SHG[0], yc))
    print("G1xK1 at y=%.2f lotok %.3f, outer bottom %.3f, gap to G1 top %.2f" % (yc, lvl, lvl-0.004, (lvl-0.004)-G1_DEPTH))
    print("G1 - V1 min", min(poly_dist(p, V1) for p in G1), "G1-VRU cable", SHG[0]-VRU[0])
    print("SHG-VRU gap", (SHG[0]-0.3)-(VRU[0]+0.4))
    # el crossing K1 main at x=14.3
    t = (a[0]-VRU[0])/(a[0]-b[0]); yc = a[1]+t*(b[1]-a[1]); lvl = k1_level_on(k1['bath'], lv['вып.бани'], (VRU[0], yc))
    print("VRU cable x K1 main: y %.2f lotok %.3f top %.3f gap %.2f" % (yc, lvl, lvl+0.11, -0.7-(lvl+0.11)))
    print("VRU cable to K1 house outlet", VRU[0]-HOUSE_OUT[0])
    print("V1 x K1 bath: K1 level at (21,21)?", k1_level_on(k1['bath'], lv['вып.бани'], (21.0, 21.0)))
    print("trunk", trunk)
    for q, n, p, ph, s, tr in lines:
        l = round(tr + EXTRA); print(q, n[:20], p, s, "trace %.2f -> L %d  dU %.2f%%" % (tr, l, du(p, l, s)))
    print("VRU->SHRD trace", L(EL['ВРУ→ЩР-Д']) + abs(YV-SHRD[1]))
    print("EL trench", EL_TRENCH)
    print("V1 trench", L(V1), "under", L(V1_UNDER))
