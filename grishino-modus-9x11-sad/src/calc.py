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

# ---------- дом 9,0 × 11,5 (эскиз заказчика), развёрнут: терраса в сад, вход со стороны калитки ----------
# План эскиза повёрнут на 180° и отзеркален: ось А (терраса) — к саду (y = 14,5), ось Г — к улице (y = 26),
# ось 1 (спальни) — слева (x = 9), ось 3 (кухня, прихожая, котельная) — справа (x = 18), к дорожке от калитки.
HX0, HX1 = 9.0, 18.0          # оси 1 и 3
AX2 = HX0 + 3.6               # ось 2
YA, YB, YV, YG = 14.5, 16.0, 17.0, 26.0   # оси А (сад), Б, В, Г (улица)
HOUSE = (HX0, YA, 9.0, 11.5)
HEATED = [(9, 16), (12.6, 16), (12.6, 17), (18, 17), (18, 26), (9, 26)]
TERRACE = [(9, 14.5), (18, 14.5), (18, 17), (12.6, 17), (12.6, 16), (9, 16)]
STEPS = (12.45, 14.0, 3.2, 0.5)                # ступени террасы в сад
PORCH = (18.0, 22.2, 1.0, 1.6)                 # площадка входа у правой стены
PORCH_STEPS = (18.0, 23.8, 1.0, 0.6)           # ступени к дорожке от калитки
DOOR_IN = (22.7, 23.56)                        # входная дверь в правой стене (y)
ROOMS = {  # № : (x, y, w, h, название, площадь)
    1: (None, None, None, None, "Терраса в сад (открытая, под общей кровлей)", 18.9),
    2: (12.6, 17.147, 1.656, 6.709, "Холл-коридор, выход на террасу", 11.1),
    3: (9.147, 16.147, 3.306, 3.5, "Спальня", 11.6),
    4: (9.147, 19.744, 3.306, 2.912, "Спальня", 9.6),
    5: (9.147, 22.753, 3.306, 3.1, "Спальня", 10.2),
    6: (12.6, 23.953, 2.356, 1.9, "Санузел: душ, унитаз, умывальник", 4.5),
    7: (15.053, 23.953, 2.8, 1.9, "Котельная-постирочная: газовый котёл, бойлер, насосная", 5.3),
    9: (14.353, 22.256, 3.5, 1.6, "Прихожая — вход со стороны калитки (выгорожена из пом. 8)", 5.6),
    8: (14.353, 17.147, 3.5, 5.012, "Кухня-гостиная", 17.5),
}

# ---------- остальные объекты (без изменений) ----------
BATH = (24.8, 1.5, 5.7, 6.0); BATH_TER = (24.8, 7.5, 3.0, 1.5)
GAZEBO = (4.0, 7.0, 5.0, 4.0); MANGAL = (9.0, 8.2, 0.6, 1.6)
SHED = (1.0, 1.0, 6.0, 2.3)
WELL = (31.0, 21.0)
LOS = (2.0, 29.3, 1.2, 1.2); LOS_IN = (3.2, 29.9)
PARK = (25.5, 25.0, 5.5, 6.5)

# ---------- щиты ----------
VRU = (14.3, 32.0)            # шкаф учёта: в пролёте 13,5–15,75
SHG = (16.875, 32.1)          # газовый шкаф: посередине пролёта 15,75–18,0, левее калитки
SHRD = (14.45, 22.55)         # ЩР-Д в прихожей на перегородке П-1

# ---------- канализация К1 ----------
I = 0.02
KK = {"КК-Б": (22.5, 12.0), "КК-1": (21.0, 20.0), "КК-2": (21.0, 29.0),
      "КК-4": (13.2, 29.5), "КК-3": (4.2, 29.9)}
BATH_OUT = (28.1, 7.5)
HOUSE_OUT = (13.2, YG)         # выпуск через уличную стену (ось Г) под санузлом
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
V1_UNDER = [(HX1, 21.0), (17.3, 21.0), (17.3, 24.6)]   # по подполью в котельную
V1_BATH = [(31.0, 20.45), (31.0, 6.95), (30.5, 6.95)]
V1_NEIGH = [(31.55, 21.0), (33.2, 21.0)]
V1_DEPTH = -1.80

# ---------- газ Г1 ----------
G1_DEPTH = -1.55                 # верх трубы (под магистралью К1)
G1 = [(SHG[0], 32.1), (SHG[0], YG + 0.3)]        # от ШГ по прямой к уличной стене, подход под прямым углом
G1_FACADE = [(SHG[0], YG + 0.3), (SHG[0], YG)]   # стояк по фасаду до ввода на +0,9
G1_ENTRY = (SHG[0], YG)

# ---------- электрика ----------
TRX = 16.0   # магистраль кабелей к постройкам: по подполью, выход под террасу у оси В
EL = {
    "ВРУ→ЩР-Д": [(VRU[0], 32.0), (VRU[0], YG), (VRU[0], SHRD[1]), SHRD],
    "магистраль": [SHRD, (TRX, SHRD[1]), (TRX, YV), (TRX, 10.4)],
    "баня": [(TRX, 10.4), (28.65, 10.4), (28.65, 7.5)],
    "беседка": [(TRX, 10.4), (9.0, 10.4)],
    "хозблок": [(TRX, 10.4), (10.3, 10.4), (10.3, 4.2), (7.0, 4.2), (7.0, 2.2)],
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

# траншеи кабелей в грунте (под домом — по подполью; кабель насоса — в траншее В1)
EL_TRENCH = (32.0 - YG) + (YV - 10.4) + L(EL["баня"]) + L(EL["хозблок"][1:]) + (10.3 - 9.0) + L(EL["ЛОС"][1:])
# пересечение кабеля бани с К1 бани (y = 10,4)
_a, _b = BATH_OUT, KK["КК-Б"]; _t = (10.4 - _a[1])/(_b[1]-_a[1]); XCR = _a[0] + _t*(_b[0]-_a[0])
K1_AT_CABLE = lv["вып.бани"] - I*_t*L([_a, _b])

if __name__ == "__main__":
    print("K1 lengths bath %.2f house %.2f main %.2f total %.2f" % (L(k1["bath"]), L(k1["house"]), L(k1["main"]), K1_TOTAL))
    for k, v in lv.items(): print(f"  {k:12s} {v:+.3f}")
    print("segments:")
    for a, b in [("вып.бани", "КК-Б"), ("КК-Б", "КК-1"), ("КК-1", "КК-2"), ("КК-2", "КК-4"), ("КК-4", "КК-3")]:
        pa = BATH_OUT if a == "вып.бани" else KK[a]; print(f"  {a}->{b} {L([pa, KK[b]]):.2f}")
    print("  house out -> KK-4 %.2f, KK-3->LOS %.2f" % (L(k1['house']), L([KK['КК-3'], LOS_IN])))
    # checks
    print("K1 bath line to house wall:", min(poly_dist(p, k1['bath']) for p in [(18, y/10) for y in range(145, 261)]))
    print("K1 bath to porch:", min(poly_dist(p, k1['bath']) for p in [(19.0, y/10) for y in range(222, 245)]))
    print("cable x K1 bath at x=%.2f: lotok %.3f -> pipe bottom %.3f" % (XCR, K1_AT_CABLE, K1_AT_CABLE-0.004))
    print("K1 to well:", min(poly_dist(WELL, k1[k]) for k in k1))
    print("K1 house to well", poly_dist(WELL, k1['house']))
    print("KK-4 to house front", KK['КК-4'][1]-YG)
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
    print("VRU->SHRD trace", L(EL['ВРУ→ЩР-Д']))
    print("EL trench", EL_TRENCH)
    print("V1 trench", L(V1), "under", L(V1_UNDER))
