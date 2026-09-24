"""Параметрическая модель хозблока 6,0 x 2,3 м (по крыше).

Единая геометрия для чертежей (drawings/), 3D-визуализации (render/) и
подсчёта объёмов для сметы (smeta/). Все размеры в миллиметрах.

Система координат:
  X — вдоль длинной стороны (0 = левый наружный угол каркаса при взгляде
      на главный фасад), Y — вглубь (0 = наружная грань каркаса главного
      фасада, где дверь), Z — вверх (0 = низ нижней обвязки).
"""
import json
import math
from pathlib import Path

# ---------------------------------------------------------------- параметры
P = dict(
    L=5800,            # длина каркаса
    W=2200,            # ширина каркаса
    roof_L=6000,       # длина по крыше
    roof_W=2300,       # ширина по крыше (в плане)
    wall_t=100,        # толщина каркаса стен (= утеплитель 100)
    osb_wall=9,        # ОСБ-3 внутри (стены, потолок)
    base_h=150,        # нижняя обвязка брус 100x150 / лаги 50x150
    floor_board=25,    # доска пола
    floor_osb=12,      # ОСБ-3 пола
    clear_h=2170,      # высота помещения в чистоте
    top_plate=50,      # верхняя обвязка стен 50x100 (плашмя)
    chord_h=100,       # нижний пояс ферм / балки потолка 50x100
    roof_pitch=20,     # уклон двускатной кровли, град
    block=(400, 200, 200),  # блок бетонный 400x200x200
    door=dict(x_c=2900, w=960, h=2050, leaf_w=900, leaf_h=2000),
    windows=[dict(x_c=1150, w=1000, h=1000), dict(x_c=4650, w=1000, h=1000)],
    win_top=2200,      # верх проёмов окон и двери (от низа обвязки)
    stud_step=600,
    truss_count=11,
)

L, W = P["L"], P["W"]
T = P["wall_t"]
Z_FLOOR = P["base_h"] + P["floor_board"] + P["floor_osb"]          # 187
Z_CEIL = Z_FLOOR + P["clear_h"]                                     # 2357
Z_PLATE_TOP = Z_CEIL + P["osb_wall"]                                # 2366
Z_STUD_TOP = Z_PLATE_TOP - P["top_plate"]
Z_CHORD_TOP = Z_PLATE_TOP + P["chord_h"]
TAN = math.tan(math.radians(P["roof_pitch"]))
COS = math.cos(math.radians(P["roof_pitch"]))
OVH_Y = (P["roof_W"] - W) / 2          # свес по ширине, 50
OVH_X = (P["roof_L"] - L) / 2          # свес по длине, 100
Y_RIDGE = W / 2
PROF_ROOF, BATTEN, RAFTER_H = 20, 25, 100
# отметка верха кровли над наружной гранью стены
Z_ROOF_AT_WALL = Z_CHORD_TOP + RAFTER_H / COS + BATTEN + PROF_ROOF
Z_RIDGE = Z_ROOF_AT_WALL + Y_RIDGE * TAN
IN_X0, IN_X1 = T + P["osb_wall"], L - T - P["osb_wall"]
IN_Y0, IN_Y1 = T + P["osb_wall"], W - T - P["osb_wall"]
GROUND = -P["block"][2]


def roof_z(y):
    """Отметка верха кровельного листа в точке y."""
    return Z_RIDGE - TAN * abs(y - Y_RIDGE)


els = []


def box(id_, group, mat, x0, y0, z0, x1, y1, z1, **kw):
    e = dict(id=id_, group=group, mat=mat, kind="box",
             b=[round(v, 1) for v in (min(x0, x1), min(y0, y1), min(z0, z1),
                                      max(x0, x1), max(y0, y1), max(z0, z1))])
    e.update(kw)
    els.append(e)
    return e


def rbox(id_, group, mat, center, size, rx=0.0, ry=0.0, **kw):
    """Повёрнутый брусок: size=(sx,sy,sz) до поворота, поворот вокруг X, затем Y (град)."""
    e = dict(id=id_, group=group, mat=mat, kind="rbox",
             c=[round(v, 1) for v in center], s=[round(v, 1) for v in size],
             rx=rx, ry=ry)
    e.update(kw)
    els.append(e)
    return e


def item(id_, group, type_, **kw):
    e = dict(id=id_, group=group, kind="item", type=type_)
    e.update(kw)
    els.append(e)
    return e


# ------------------------------------------------------------- фундамент
bx, by, bz = P["block"]
block_x = [220, 1980, 3820, 5580]
for j, yc in enumerate([50, W - 50]):
    for i, xc in enumerate(block_x):
        box(f"block_{j}{i}", "foundation", "concrete",
            xc - bx / 2, yc - by / 2 - 20, -bz, xc + bx / 2, yc + by / 2 + 20, 0,
            pos=1)
        box(f"ruberoid_{j}{i}", "foundation", "ruberoid",
            xc - bx / 2, yc - by / 2 - 20, -1, xc + bx / 2, yc + by / 2 + 20, 0)

# ------------------------------------------------------------- каркас пола
bh = P["base_h"]
box("base_front", "frame", "timber", 0, 0, 0, L, T, bh, pos=2, sec="100x150")
box("base_back", "frame", "timber", 0, W - T, 0, L, W, bh, pos=2, sec="100x150")
box("base_left", "frame", "timber", 0, T, 0, T, W - T, bh, pos=2, sec="100x150")
box("base_right", "frame", "timber", L - T, T, 0, L, W - T, bh, pos=2, sec="100x150")
n_joist = 9
joist_x = [T + (L - 2 * T) * k / (n_joist + 1) for k in range(1, n_joist + 1)]
for k, xc in enumerate(joist_x):
    box(f"joist_{k}", "frame", "timber", xc - 25, T, 0, xc + 25, W - T, bh,
        pos=3, sec="50x150")
# черновой пол на черепных брусках, утеплитель, чистовой пол
box("subfloor", "floor", "board_rough", T, T, 20, L - T, W - T, 45, pos=4, section_only=True)
box("ins_floor", "floor", "insulation", T, T, 45, L - T, W - T, bh, section_only=True)
box("floor_board", "floor", "board", T, T, bh, L - T, W - T, bh + P["floor_board"], pos=5)
box("floor_osb", "floor", "osb", T, T, bh + P["floor_board"], L - T, W - T, Z_FLOOR, pos=6)

# ------------------------------------------------------------- проёмы
d = P["door"]
door_x0, door_x1 = d["x_c"] - d["w"] / 2, d["x_c"] + d["w"] / 2
door_z0, door_z1 = bh, bh + d["h"]
wins = []
for w in P["windows"]:
    x0, x1 = w["x_c"] - w["w"] / 2, w["x_c"] + w["w"] / 2
    wins.append((x0, x1, P["win_top"] - w["h"], P["win_top"]))
openings_front = [(door_x0, door_x1, door_z0, door_z1)] + wins


# ------------------------------------------------------------- стены (каркас)
def stud_positions(a0, a1, openings, step):
    """Центры стоек на отрезке [a0, a1] с учётом проёмов (a — вдоль стены)."""
    fixed = {a0 + 25, a1 - 25}
    for o0, o1, *_ in openings:
        fixed |= {o0 - 25, o1 + 25}
    fixed = sorted(fixed)
    res = []
    for p, q in zip(fixed[:-1], fixed[1:]):
        res.append(p)
        inside = any(o0 - 30 <= p and q <= o1 + 30 for o0, o1, *_ in openings)
        if inside:
            continue
        n = math.ceil((q - p) / step)
        res += [p + (q - p) * k / n for k in range(1, n)]
    res.append(fixed[-1])
    return res


def wall_frame(name, axis, a0, a1, c0, c1, openings):
    """axis='x' — стена вдоль X (толщина по Y от c0 до c1); 'y' — вдоль Y."""
    def B(id_, a_0, a_1, z0, z1, **kw):
        if axis == "x":
            return box(id_, "frame", "timber", a_0, c0, z0, a_1, c1, z1, **kw)
        return box(id_, "frame", "timber", c0, a_0, z0, c1, a_1, z1, **kw)

    for k, s in enumerate(stud_positions(a0, a1, openings, P["stud_step"])):
        in_open = [o for o in openings if o[0] < s < o[1]]
        if in_open:
            o0, o1, z0, z1 = in_open[0]
            if z0 > bh + 1:
                B(f"{name}_cripple_lo{k}", s - 25, s + 25, bh, z0 - 50, pos=7, sec="50x100")
            B(f"{name}_cripple_hi{k}", s - 25, s + 25, z1 + 100, Z_STUD_TOP, pos=7, sec="50x100")
        else:
            B(f"{name}_stud{k}", s - 25, s + 25, bh, Z_STUD_TOP, pos=7, sec="50x100")
    B(f"{name}_plate", a0, a1, Z_STUD_TOP, Z_PLATE_TOP, pos=8, sec="50x100")
    for k, (o0, o1, z0, z1) in enumerate(openings):
        B(f"{name}_lintel{k}", o0 - 50, o1 + 50, z1, z1 + 100, pos=9, sec="2x50x100")
        if z0 > bh + 1:
            B(f"{name}_sill{k}", o0, o1, z0 - 50, z0, pos=9, sec="50x100")


wall_frame("wf", "x", 0, L, 0, T, openings_front)
wall_frame("wb", "x", 0, L, W - T, W, [])
wall_frame("wl", "y", T, W - T, 0, T, [])
wall_frame("wr", "y", T, W - T, L - T, L, [])

# укосины (раскосы жёсткости) в углах стен
brace_len = 1400
ang = 45
for nm, xc, yc, ry, rx in [
    ("br_b1", 700, W - T / 2, ang, 0), ("br_b2", L - 700, W - T / 2, -ang, 0),
    ("br_f1", 330, T / 2, ang, 0), ("br_f2", L - 330, T / 2, -ang, 0),
]:
    rbox(nm, "frame", "timber", (xc, yc, 1250), (brace_len if "b" in nm[3] else 700, 25, 100),
         ry=ry, pos=10, sec="25x100")
for nm, xc, yc, rx in [("br_l1", T / 2, 700, -ang), ("br_l2", T / 2, W - 700, ang),
                       ("br_r1", L - T / 2, 700, -ang), ("br_r2", L - T / 2, W - 700, ang)]:
    rbox(nm, "frame", "timber", (xc, yc, 1250), (25, 1000, 100), rx=rx, pos=10, sec="25x100")

# ------------------------------------------------------------- стропильные фермы
truss_x = [25 + (L - 50) * k / (P["truss_count"] - 1) for k in range(P["truss_count"])]
raf_len = (Y_RIDGE + OVH_Y) / COS
for k, xc in enumerate(truss_x):
    box(f"chord_{k}", "frame", "timber", xc - 25, -OVH_Y + 20, Z_PLATE_TOP,
        xc + 25, W + OVH_Y - 20, Z_CHORD_TOP, pos=11, sec="50x100")
    for side, sgn in (("a", 1), ("b", -1)):
        yc = Y_RIDGE - sgn * (Y_RIDGE + OVH_Y) / 2
        # ось стропила: на 45+50/cos ниже поверхности кровли
        zc = roof_z(yc) - PROF_ROOF - BATTEN - (RAFTER_H / 2) / COS
        rbox(f"rafter_{k}{side}", "frame", "timber", (xc, yc, zc), (50, raf_len, RAFTER_H),
             rx=sgn * P["roof_pitch"], pos=12, sec="50x100")
    kp_top = roof_z(Y_RIDGE) - PROF_ROOF - BATTEN - RAFTER_H / COS
    box(f"kingpost_{k}", "frame", "timber", xc - 25, Y_RIDGE - 50, Z_CHORD_TOP,
        xc + 25, Y_RIDGE + 50, kp_top, pos=13, sec="50x100")

# обрешётка 25x100
slope = (Y_RIDGE + OVH_Y) / COS
for side, sgn in (("a", 1), ("b", -1)):
    for k in range(5):
        s = 60 + k * (slope - 120) / 4                  # по скату от карниза
        y = -OVH_Y + s * COS if sgn > 0 else W + OVH_Y - s * COS
        z = roof_z(y) - PROF_ROOF - BATTEN / 2
        rbox(f"batten_{side}{k}", "roof", "timber", (L / 2, y, z), (P["roof_L"], 100, BATTEN),
             rx=sgn * P["roof_pitch"], pos=14, sec="25x100")

# ------------------------------------------------------------- утепление, отделка
H_IN = Z_CEIL - Z_FLOOR
box("ins_walls_f", "insulation", "insulation", T, 0, bh, L - T, T, Z_STUD_TOP, section_only=True)
box("ins_ceiling", "insulation", "insulation", T, T, Z_PLATE_TOP, L - T, W - T, Z_CHORD_TOP,
    section_only=True)
# ОСБ внутри (для рендера — сплошные панели, проёмы вырезаются в JS)
box("osb_back", "finish", "osb", IN_X0, IN_Y1, Z_FLOOR, IN_X1, W - T, Z_CEIL, pos=16)
box("osb_front", "finish", "osb", IN_X0, T, Z_FLOOR, IN_X1, IN_Y0, Z_CEIL, pos=16,
    holes=[[o[0], o[2] if o[2] > bh + 1 else Z_FLOOR, o[1], o[3]] for o in openings_front])
box("osb_left", "finish", "osb", T, T, Z_FLOOR, IN_X0, W - T, Z_CEIL, pos=16)
box("osb_right", "finish", "osb", IN_X1, T, Z_FLOOR, L - T, W - T, Z_CEIL, pos=16)
box("osb_ceiling", "finish", "osb", T, T, Z_CEIL, L - T, W - T, Z_PLATE_TOP, pos=16)

# наружная обшивка — профлист С8 (цветной); задаём плоскости, рёбра строятся в JS
CLAD = 12   # ветрозащита + профлист
Z_CLAD0 = -40
Z_CLAD_TOP = round(roof_z(-CLAD) - PROF_ROOF - BATTEN, 1)   # до низа обрешётки у стены
item("clad_front", "cladding", "wall_sheet", face="front", x0=-CLAD, x1=L + CLAD, y=-CLAD,
     z0=Z_CLAD0, z1=Z_CLAD_TOP, holes=[[o[0], o[2], o[1], o[3]] for o in openings_front], pos=17)
item("clad_back", "cladding", "wall_sheet", face="back", x0=-CLAD, x1=L + CLAD, y=W + CLAD,
     z0=Z_CLAD0, z1=Z_CLAD_TOP, holes=[], pos=17)
item("clad_left", "cladding", "gable_sheet", face="left", x=-CLAD, y0=-CLAD, y1=W + CLAD,
     z0=Z_CLAD0, z1=Z_CHORD_TOP, pos=17)
item("clad_right", "cladding", "gable_sheet", face="right", x=L + CLAD, y0=-CLAD, y1=W + CLAD,
     z0=Z_CLAD0, z1=Z_CHORD_TOP, pos=17)
item("roof_sheet", "roof", "roof_sheet", x0=-OVH_X, x1=L + OVH_X, y0=-OVH_Y, y1=W + OVH_Y,
     ridge_y=Y_RIDGE, ridge_z=Z_RIDGE, pitch=P["roof_pitch"], t=PROF_ROOF, pos=15)

# окна, дверь
for k, (x0, x1, z0, z1) in enumerate(wins):
    item(f"window_{k}", "opening", "window", x0=x0, x1=x1, z0=z0, z1=z1, y0=-CLAD, y1=T,
         pos=18, name="Окно ПВХ 1000x1000 поворотно-откидное")
item("door", "opening", "door", x0=door_x0, x1=door_x1, z0=door_z0, z1=door_z1, y0=-CLAD, y1=T,
     leaf_w=d["leaf_w"], leaf_h=d["leaf_h"], pos=19, name="Дверь металлическая 2050x960")

# ступени входные (2 подъёма + площадка)
st_x0, st_x1 = P["door"]["x_c"] - 650, P["door"]["x_c"] + 650
rise = (bh - GROUND) / 2
box("step_landing", "site", "deck", st_x0, -CLAD - 450, GROUND, st_x1, -CLAD, bh - 10, pos=20)
box("step_1", "site", "deck", st_x0, -CLAD - 750, GROUND, st_x1, -CLAD - 450, GROUND + rise - 10,
    pos=20)

# ------------------------------------------------------------- наполнение
# 21 Верстак 2000x650, h=900
bx0, bx1, by0, by1 = IN_X0, IN_X0 + 2000, IN_Y0, IN_Y0 + 650
bz = Z_FLOOR + 900
for k, (x, y) in enumerate([(bx0 + 30, by0 + 40), (bx1 - 80, by0 + 40), (bx0 + 30, by1 - 90),
                            (bx1 - 80, by1 - 90), ((bx0 + bx1) / 2 - 25, by1 - 90),
                            ((bx0 + bx1) / 2 - 25, by0 + 40)]):
    box(f"bench_leg{k}", "equip", "wood", x, y, Z_FLOOR, x + 50, y + 50 + 0, bz - 40, pos=21)
box("bench_apron_f", "equip", "wood", bx0 + 30, by1 - 90, bz - 140, bx1 - 30, by1 - 40, bz - 40, pos=21)
box("bench_apron_b", "equip", "wood", bx0 + 30, by0 + 40, bz - 140, bx1 - 30, by0 + 90, bz - 40, pos=21)
box("bench_top", "equip", "plywood", bx0, by0, bz - 40, bx1, by1, bz, pos=21)
box("bench_shelf", "equip", "osb", bx0 + 30, by0 + 40, Z_FLOOR + 180, bx1 - 30, by1 - 40,
    Z_FLOOR + 198, pos=21)
box("bench_backboard", "equip", "plywood", bx0, by0, bz, bx1, by0 + 18, bz + 100, pos=21)
item("vise", "equip", "vise", x=bx1 - 260, y=by1, z=bz, pos=22, name="Тиски слесарные 125 мм")
item("bench_stuff", "equip", "bench_stuff", x0=bx0, x1=bx1, y0=by0, y1=by1, z=bz)
item("bench_drawers", "equip", "drawer_unit", x0=bx0 + 90, x1=bx0 + 590, y0=by0 + 90,
     y1=by1 - 90, z0=Z_FLOOR + 198, z1=bz - 140, pos=23, name="Тумба-кассетница под верстаком")

# 24 Перфопанель на левой торцевой стене
peg = dict(x=IN_X0, y0=IN_Y0 + 700, y1=IN_Y0 + 1450, z0=Z_FLOOR + 950, z1=Z_FLOOR + 1950)
item("pegboard", "equip", "pegboard", **peg, pos=24, name="Перфопанель 750x1000 с крючками")

# 25 Стеллаж вдоль задней стены 3000x500x2100, 5 ярусов
rk_x0, rk_x1, rk_y0, rk_y1 = IN_X0, IN_X0 + 3000, IN_Y1 - 500, IN_Y1
rk_z1 = Z_FLOOR + 2100
shelf_lv = [150, 600, 1050, 1500, 1950]
post_x = [rk_x0, rk_x0 + 975, rk_x0 + 1975, rk_x1 - 50]
for i, x in enumerate(post_x):
    for j, y in enumerate([rk_y0, rk_y1 - 50]):
        box(f"rack_post{i}{j}", "equip", "wood", x, y, Z_FLOOR, x + 50, y + 50, rk_z1, pos=25)
for k, h in enumerate(shelf_lv):
    z = Z_FLOOR + h
    box(f"rack_shelf{k}", "equip", "osb", rk_x0, rk_y0, z, rk_x1, rk_y1, z + 18, pos=25)
    box(f"rack_rail{k}f", "equip", "wood", rk_x0, rk_y0, z - 50, rk_x1, rk_y0 + 25, z, pos=25)
    box(f"rack_rail{k}b", "equip", "wood", rk_x0, rk_y1 - 25, z - 50, rk_x1, rk_y1, z, pos=25)
item("rack_stuff", "equip", "rack_stuff", x0=rk_x0, x1=rk_x1, y0=rk_y0, y1=rk_y1,
     levels=[Z_FLOOR + h + 18 for h in shelf_lv], seps=[p + 25 for p in post_x])

# 26 Инструментальная стена (задняя стена, правая часть) + 27 антресоль
tw_x0, tw_x1 = IN_X0 + 3150, IN_X1 - 60
for k, h in enumerate([1250, 1650]):
    box(f"toolrail{k}", "equip", "wood", tw_x0, IN_Y1 - 25, Z_FLOOR + h, tw_x1, IN_Y1,
        Z_FLOOR + h + 100, pos=26)
tools = ["shovel", "shovel2", "fork", "rake", "rake_fan", "hoe", "broom", "scoop", "pruner",
         "axe", "sledge", "crowbar"]
n = len(tools)
item("tool_wall", "equip", "tool_wall", x0=tw_x0 + 120, x1=tw_x1 - 120, y=IN_Y1 - 25,
     z_hook=Z_FLOOR + 1700, tools=tools, pos=26,
     name="Инструментальная стена: 2 рейки + 12 держателей")
an_z = Z_FLOOR + 1900
box("antresol", "equip", "osb", tw_x0, IN_Y1 - 400, an_z, tw_x1, IN_Y1, an_z + 18, pos=27)
item("antresol_brackets", "equip", "brackets", x0=tw_x0, x1=tw_x1, y0=IN_Y1 - 400, y1=IN_Y1,
     z=an_z, count=5)
item("antresol_stuff", "equip", "shelf_stuff", x0=tw_x0, x1=tw_x1, y0=IN_Y1 - 400, y1=IN_Y1,
     z=an_z + 18, hmax=Z_CEIL - an_z - 60, seed=7)

# 28 Полки для ГСМ и мелочей у двери (фронтальная стена)
gs_x0, gs_x1 = door_x1 + 60, P["windows"][1]["x_c"] - P["windows"][1]["w"] / 2 - 60
for k, h in enumerate([1250, 1650]):
    box(f"gsm_shelf{k}", "equip", "osb", gs_x0, IN_Y0, Z_FLOOR + h, gs_x1, IN_Y0 + 280,
        Z_FLOOR + h + 18, pos=28)
    item(f"gsm_br{k}", "equip", "brackets", x0=gs_x0, x1=gs_x1, y0=IN_Y0, y1=IN_Y0 + 280,
         z=Z_FLOOR + h, count=2, wall="front")
    item(f"gsm_stuff{k}", "equip", "shelf_stuff", x0=gs_x0, x1=gs_x1, y0=IN_Y0, y1=IN_Y0 + 280,
         z=Z_FLOOR + h + 18, hmax=300, seed=11 + k, kind="bottles")

# 29 Крючки/кронштейны на правой торцевой стене
item("hooks_right", "equip", "hook_wall", x=IN_X1, y0=IN_Y0 + 250, y1=IN_Y1 - 450,
     z=Z_FLOOR + 1550, pos=29, name="Крючки для шланга, удлинителя, триммера")

# 30 Садовая техника (зона хранения)
item("mower", "equip", "mower", x=3700, y=IN_Y0 + 80, z=Z_FLOOR, pos=30,
     name="Газонокосилка (место)")
item("tiller", "equip", "tiller", x=4380, y=IN_Y0 + 80, z=Z_FLOOR, pos=31,
     name="Мотоблок / культиватор (место)")
item("barrow", "equip", "barrow", x=5130, y=IN_Y0 + 80, z=Z_FLOOR, pos=32,
     name="Садовая тачка (место)")
item("canisters", "equip", "canisters", x=gs_x0 + 30, y=IN_Y0 + 20, z=Z_FLOOR, pos=28)
item("floor_mat", "equip", "floor_mat", x0=3560, x1=IN_X1, y0=IN_Y0, y1=IN_Y0 + 1350, z=Z_FLOOR,
     pos=33, name="Резиновый коврик под технику")

# 34 Освещение (опция)
for k, xc in enumerate([1400, 4400]):
    item(f"lamp{k}", "equip", "lamp", x=xc, y=W / 2, z=Z_CEIL, pos=34)

model = dict(
    params=P,
    levels=dict(ground=GROUND, floor=Z_FLOOR, ceil=Z_CEIL, plate_top=Z_PLATE_TOP,
                chord_top=Z_CHORD_TOP, roof_at_wall=round(Z_ROOF_AT_WALL, 1),
                ridge=round(Z_RIDGE, 1), clad_bottom=Z_CLAD0, clad=CLAD),
    interior=dict(x0=IN_X0, x1=IN_X1, y0=IN_Y0, y1=IN_Y1),
    elements=els,
)

if __name__ == "__main__":
    out = Path(__file__).with_name("model.json")
    out.write_text(json.dumps(model, ensure_ascii=False, indent=1))
    print(f"{len(els)} элементов, пол {Z_FLOOR}, потолок {Z_CEIL}, конёк {Z_RIDGE:.0f}"
          f" (от земли {Z_RIDGE - GROUND:.0f}), помещение {IN_X1 - IN_X0}x{IN_Y1 - IN_Y0}")
