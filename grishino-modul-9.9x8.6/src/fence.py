"""Забор из профлиста С8: разбивка опор, расчёт и листы 02, 02.1, 02.2, 02.3.
Рядовые и угловые столбы — забивка в пробуренную лунку со щебнем; винтовые сваи — только под калиткой и откатными воротами.

Координаты участка — как в calc.py: x от левой границы, y от тыльной границы (н2); улица — y = 32.
Отметки z — от уровня земли у опоры (±0,000), вверх плюс."""
from common import *
from calc import *
import math

# ---------------- исходные данные ----------------
AX = 0.10                                   # ось опор — на 0,1 м внутрь участка от границы
FS, FR, FB, FL = 32 - AX, 32 - AX, AX, AX   # линии осей: улица (y), правая (x), тыльная (y), левая (x)
WICKET = (18.0, 19.0)                       # оси столбов калитки
GATE = (26.5, 30.5)                         # оси столбов ворот: В1 (с верхними роликами) и В2 (улавливатель)
ROLL = (19.0, 26.5)                         # зона отката — вдоль уличного забора до калитки
LEAF_BODY, CWT = 4.1, 1.6                   # полотно ворот (проём + 0,1 в улавливатель) и противовес
LEAF_Y = FS - 0.15                          # плоскость полотна — 150 мм внутрь от оси забора
LEAF_CLOSED = (GATE[1] - LEAF_BODY - CWT, GATE[1])
LEAF_OPEN = (LEAF_CLOSED[0] - LEAF_BODY, LEAF_CLOSED[1] - LEAF_BODY)
EMB = (24.4, 26.4)                          # закладная — швеллер 16П 2,0 м полками вниз
EMB_PILES = (24.7, 25.9)                    # сваи под закладной
CARR = (24.95, 26.2)                        # роликовые опоры (тележки) на закладной
VRU_BOX = (VRU[0] - 0.40, VRU[0] + 0.40, 0.90, 1.55, 0.25)    # x0, x1, низ, верх, глубина — шкаф учёта в нише
SHG_BOX = (SHG[0] - 0.30, SHG[0] + 0.30, 0.60, 1.40, 0.30)    # газовый шкаф в нише
Z_HEAD, Z_EMB = 0.10, -0.16                 # верх оголовков свай столбов; оголовки свай закладной
Z_S0, Z_S1 = 0.15, 2.15                     # низ и верх профлиста (лист 2,0 м, зазор до земли 150 мм)
Z_LAG = (0.45, 1.85)                        # оси лаг 40×20 — по 300 мм от краёв листа
Z_TOP = 2.20                                # верх столбов (заглушка)
Z_TOPV = 2.35                               # верх столбов ворот (кронштейн верхних роликов)
Z_FRZ = -1.40                               # нормативная глубина промерзания суглинков
SHEET_W, SHEET_USE = 1.20, 1.15             # профлист С8: ширина и полезная ширина
WAVE = 0.115                                # шаг волны С8
HOLE_D, Z_HOLE, Z_DRV = 0.20, -0.80, -1.50  # рядовые и угловые столбы: лунка Ø200 на 0,8 м, столб забит до −1,5 м (ниже промерзания), щебень с трамбовкой

PILES = {   # свая: диаметр ствола, лопасть, длина, оголовок, толщина оголовка, цена
    '89':  dict(name='СВС-89×2500', d=0.089, wall='3,5', blade=0.25, L=2.5, plate=0.15, pt=0.008, price=3100),
    '108': dict(name='СВС-108×2500', d=0.108, wall='4,0', blade=0.30, L=2.5, plate=0.20, pt=0.008, price=4200),
}
DRV = 'drv'                                 # основание «забивка в лунку со щебнем» вместо сваи
TYPES = {   # тип: назначение, сечение столба, размер, верх столба, основание (свая или DRV), цвет на планах
    'А':  ('промежуточная', '60×60×2', 0.06, Z_TOP, DRV, '#3A4045'),
    'У':  ('угловая', '60×60×2', 0.06, Z_TOP, DRV, '#3A4045'),
    'К':  ('калитки', '80×80×3', 0.08, Z_TOP, '89', '#1D5FA0'),
    'В1': ('ворот, верхние ролики', '80×80×3', 0.08, Z_TOPV, '108', '#9A5B00'),
    'В2': ('ворот, улавливатели', '80×80×3', 0.08, Z_TOPV, '108', '#9A5B00'),
}
STREET_X = [FL, 2.0, 4.3, 6.6, 8.9, 11.2, 13.5, 15.75, WICKET[0], WICKET[1], 21.5, 24.0, GATE[0], GATE[1], FR]
N_SIDE = 13                                 # пролётов на боковых и тыльной сторонах


def rnd(v, d=0):
    k = 10 ** d
    return math.floor(v * k + 0.5) / k


def nf(v, d):
    return f'{v:,.{d}f}'.replace(',', ' ').replace('.', ',')


def mm(v):
    return nf(rnd(v * 1000), 0)


def zf(z):
    """Отметка в метрах со знаком: +2,200 / ±0,000 / −1,400."""
    if abs(z) < 5e-4: return '±0,000'
    return ('+' if z > 0 else '−') + nf(abs(z), 3)


def driven(t):
    return t in TYPES and TYPES[t][4] == DRV


def post_len(t):
    if driven(t): return TYPES[t][3] - Z_DRV
    p = PILES[TYPES[t][4]]
    return TYPES[t][3] - Z_HEAD - p['pt']


def base_name(t):
    return f'лунка Ø{mm(HOLE_D)} на {nf(-Z_HOLE, 1)} м, щебень, забивка' if driven(t) else PILES[TYPES[t][4]]['name']


def base_bottom(t):
    return Z_DRV if driven(t) else Z_HEAD - PILES[TYPES[t][4]]['L']


# ---------------- разбивка опор ----------------
def supports():
    """Все опоры по кругу от угла н1 против часовой стрелки на плане: улица → правая → тыльная → левая."""
    P = []
    for x in STREET_X: P.append(dict(x=x, y=FS, side='street', s=x))
    st = (FS - FB) / N_SIDE
    for k in range(1, N_SIDE + 1): P.append(dict(x=FR, y=FS - k * st, side='right', s=FS - k * st))
    for k in range(1, N_SIDE + 1): P.append(dict(x=FR - k * st, y=FB, side='back', s=FR - k * st))
    for k in range(1, N_SIDE): P.append(dict(x=FL, y=FB + k * st, side='left', s=FB + k * st))
    corners = {1: 'угол н1', 15: 'угол н4', 28: 'угол н3', 41: 'угол н2'}
    for i, p in enumerate(P, 1):
        p['n'] = i
        p['t'] = 'У' if i in corners else 'К' if p['side'] == 'street' and p['x'] in WICKET else \
                 'В1' if p['side'] == 'street' and p['x'] == GATE[0] else 'В2' if p['side'] == 'street' and p['x'] == GATE[1] else 'А'
        p['note'] = [corners[i]] if i in corners else []
    assert len(P) == 53 and P[-1]['y'] < FS
    return P


SUP = supports()
BYN = {p['n']: p for p in SUP}


def seg_dist(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    t = 0 if dx == dy == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def poly_d(p, pts):
    return min(seg_dist(p, a, b) for a, b in zip(pts, pts[1:]))


def rect_pts(r):
    x, y, w, h = r[:4]
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]


# подземные сети и сооружения рядом с забором: название, трасса, глубина, норма в свету от лунки или лопасти, основание
K1N = {'bath': 'линия бани', 'house': 'выпуск дома', 'main': 'магистраль'}
UTIL = [   # название, коротко, трасса, глубина, норма в свету от лунки или лопасти, основание
    ('Напорный выпуск ЛОС в кювет, ПНД Ø32', 'выпуск ЛОС', [(2.6, 30.5), (2.6, 32.6)], -0.8, 0.5, 'принято: труба вне зоны бурения'),
    ('Кабель ВРУ → ЩР-Д и ввод от сети в шкаф ВРУ', 'кабель ВРУ', [(VRU[0], 32.6)] + EL['ВРУ→ЩР-Д'][:2], -0.7, 0.6, 'ПУЭ, п. 2.3.86 · до фундаментов'),
    ('Газопровод: ввод в ШГ и Г1', 'газ', [(SHG[0], 32.6)] + G1, G1_DEPTH, 1.0, 'СП 62.13330, прил. В · до фундаментов опор'),
    ('Отвод В1 к соседу, ПНД Ø32 в гильзе', 'В1 к соседу', V1_NEIGH, -1.8, 0.5, 'принято: гильза вне зоны бурения и забивки'),
    ('В1 в баню вдоль правой границы', 'В1 в баню', V1_BATH, -0.6, 0.5, 'принято'),
    ('Кессон скважины', 'кессон', rect_pts((30.45, 20.45, 1.1, 1.1)), -2.0, 0.5, 'принято'),
    ('ЛОС', 'ЛОС', rect_pts(LOS), -2.0, 0.5, 'принято'),
] + [(f'Кабель 0,4 кВ: {k}', f'кабель {k}', EL[k], -0.7, 0.6, 'ПУЭ, п. 2.3.86') for k in ('ЛОС', 'хозблок', 'баня')] \
  + [(f'Канализация К1: {K1N.get(k, k)}', f'К1 {K1N.get(k, k)}', k1[k], -1.0, 0.5, 'принято') for k in k1]


def blade(p):
    """Диаметр зоны, занятой опорой в грунте: лунка (забивка) или лопасть сваи."""
    return HOLE_D if driven(p['t']) else PILES[TYPES[p['t']][4]]['blade']


def util_checks():
    """Для каждой сети — ближайшая опора и расстояние в свету от края лунки или лопасти."""
    rows = []
    for name, short, pts, z, need, why in UTIL:
        best = min(((poly_d((p['x'], p['y']), pts) - blade(p) / 2, p) for p in SUP), key=lambda a: a[0])
        emb = min(poly_d((x, LEAF_Y), pts) - PILES['108']['blade'] / 2 for x in EMB_PILES)
        d, p = best
        who = f"опора {p['n']}"
        if emb < d: d, who = emb, 'свая закладной'
        rows.append((name, who, d, need, why))
    return rows


for p in SUP:   # примечания о сетях рядом с опорой (в свету от лунки или лопасти менее 1,5 м)
    for name, short, pts, z, need, why in UTIL:
        d = poly_d((p['x'], p['y']), pts) - blade(p) / 2
        if d < 1.5:
            p['note'].append(f'{short} — {nf(d, 2)} м')
def niche_span(box):
    """номера опор пролёта, в котором стоит ниша шкафа"""
    st = [p for p in SUP if p['side'] == 'street']
    for a, b in zip(st, st[1:]):
        if a['x'] < box[0] and box[1] < b['x']: return a['n'], b['n']
    raise ValueError(box)


NICHES = sorted([('ВРУ', VRU_BOX, niche_span(VRU_BOX)), ('ШГ', SHG_BOX, niche_span(SHG_BOX))], key=lambda v: v[1][0])
ADJ = NICHES[0][2][1] == NICHES[1][2][0]                   # ниши в соседних пролётах (общая опора между ними)
NICHE_GAP = NICHES[1][1][0] - NICHES[0][1][1]              # между шкафами в свету, м
SPECIAL = {9, 10, 11, 12, 13, 14}                          # опоры калитки и ворот — у них свои примечания
WICKET_NICHE = max((v for v in NICHES if v[1][1] < WICKET[0]), key=lambda v: v[1][1])   # ближайший шкаф левее калитки
_reach = (WICKET[0] + 0.07) - (WICKET[1] - WICKET[0] - 0.14)                             # полотно, распахнутое на 180°
WICKET_HITS = _reach - WICKET_NICHE[1][1] < 0.10                                         # без упора ударит в шкаф
_nn = []
for k, (s_, box, (a, b)) in enumerate(NICHES):
    _nn.append((a, f'ниши {NICHES[k - 1][0]} и {s_} по сторонам' if ADJ and k == 1 else f'ниша {s_} в пролёте {a}–{b}'))
    if not (ADJ and k == 0) and b not in SPECIAL: _nn.append((b, f'ниша {s_} в пролёте {a}–{b}'))
for n, t in _nn + [(9, 'калитка: петли, ограничитель 90°'),
             (10, 'калитка: замок, упор'), (11, 'зона отката: полотно проходит с внутренней стороны'),
             (12, 'зона отката: полотно проходит с внутренней стороны'), (13, 'верхние направляющие ролики'),
             (14, 'нижний и верхний улавливатели')]:
    BYN[n]['note'].insert(0, t)


# ---------------- участки забора ----------------
def runs():
    """Участки между столбами калитки, ворот и углами: лаги непрерывны внутри участка, профлист — по участку."""
    st = SUP
    def seg(a, b, name):
        pa, pb = BYN[a], BYN[b]
        ln = math.hypot(pa['x'] - pb['x'], pa['y'] - pb['y'])
        corner_ext = 0.07 * sum(1 for q in (pa, pb) if q['t'] == 'У')   # лист заходит на угол до внешней плоскости
        sheets = math.ceil((ln + corner_ext) / SHEET_USE - 1e-9)
        spans = (b - a) if b > a else (b + 53 - a)
        return dict(name=name, a=a, b=b, len=ln, spans=spans, sheets=sheets)
    return [seg(1, 9, 'Улица: угол н1 — калитка (ниши ВРУ и ШГ)'), seg(10, 13, 'Улица: зона отката ворот'),
            seg(14, 15, 'Улица: за воротами — угол н4'), seg(15, 28, 'Правая граница'), seg(28, 41, 'Тыльная граница'),
            seg(41, 1, 'Левая граница')]


RUNS = runs()


def spans(side):
    ps = [p for p in SUP if p['side'] == side]
    if side == 'right': ps = [BYN[15]] + ps
    if side == 'back': ps = [BYN[28]] + ps
    if side == 'left': ps = [BYN[41]] + ps + [BYN[1]]
    return ps


# ---------------- расчёт ----------------
def calc():
    L = sum(r['len'] for r in RUNS)
    sheets = sum(r['sheets'] for r in RUNS)
    area = rnd(sheets * SHEET_W * (Z_S1 - Z_S0), 1)
    cnt = {t: sum(1 for p in SUP if p['t'] == t) for t in TYPES}
    n60 = cnt['А'] + cnt['У']; n80 = cnt['К'] + cnt['В1'] + cnt['В2']
    len60 = n60 * rnd(post_len('А'), 2); len80 = 2 * rnd(post_len('К'), 2) + 2 * rnd(post_len('В1'), 2)
    sticks60 = math.ceil(n60 / math.floor(12 / rnd(post_len('А'), 2)))
    lag = rnd(2 * L * 1.05, 1); sticks_lag = math.ceil(lag / 6)
    p89, p108 = cnt['К'], cnt['В1'] + cnt['В2'] + len(EMB_PILES)
    # щебень: лунка Ø200 × 0,8 м минус столб, коэффициент уплотнения 1,3; заказ — кратно 0,5 м³
    stone = math.ceil(n60 * (math.pi * HOLE_D ** 2 / 4 - 0.06 ** 2) * -Z_HOLE * 1.3 * 2 - 1e-9) / 2
    mats = [
        (f'Сваи винтовые {PILES["89"]["name"]}, лопасть Ø250, оголовок 150×150×8 — под столбы калитки', 'шт', p89, PILES['89']['price']),
        (f'Сваи винтовые {PILES["108"]["name"]}, лопасть Ø300, оголовок 200×200×8 — под столбы ворот и закладную', 'шт', p108, PILES['108']['price']),
        (f'Столбы — труба 60×60×2, {sticks60} хлыстов по 12 м, нарезка {n60} × {mm(post_len("А"))} мм ({mm(-Z_DRV)} в грунте)', 'м', sticks60 * 12, 330),
        (f'Щебень гранитный фр. 20–40 для трамбовки лунок ({n60} × Ø200 × 0,8 м, с уплотнением)', 'м³', stone, 3200),
        (f'Мастика битумная, 18 кг — подземная часть столбов 60×60 ({nf(Z_S0 - Z_DRV, 2)} м) до +0,150, 2 слоя', 'ведро', 2, 2600),
        ('Столбы калитки и ворот — труба 80×80×3, 2 хлыста по 6 м (2 × 2 090 + 2 × 2 240 мм)', 'м', 12, 720),
        (f'Лаги — труба 40×20×1,5, 2 ряда, {sticks_lag} хлыстов по 6 м', 'м', sticks_lag * 6, 100),
        ('Обрамление ниш ВРУ и ШГ — труба 40×40×2', 'м', 8, 190),
        (f'Профлист С8 0,4 мм RAL 6005, лист 1 200 × 2 000, {sheets} шт', 'м²', area, 540),
        ('Саморез 5,5×19 по металлу с EPDM, в цвет (6 шт на лист на ряд лаг)', 'шт', sheets * 2 * 6, 3.2),
        ('Планка П-образная на верх забора, 2 м', 'шт', math.ceil(L / 1.95 - 1e-9), 380),
        ('Уголок-планка на углы забора и края ниш, 2 м', 'шт', 8, 290),
        ('Заглушки на столбы 60×60 / 80×80', 'шт', n60 + n80, 60),
        ('Грунт-эмаль по металлу 3 в 1 RAL 6005, 2,7 кг (столбы, лаги, оголовки, 2 слоя)', 'банка', 6, 1450),
        ('Электроды 3 мм, 2,5 кг', 'пачка', 3, 950),
        ('Ворота откатные 4,0 × 2,0 м: полотно 4,1 м + противовес 1,6 м, обшивка С8 0,4 в цвет забора, комплект фурнитуры (2 роликовые опоры, концевой ролик, нижний и верхний улавливатели, верхние ролики), швеллер 16П 2,0 м', 'компл', 1, 82000),
        ('Калитка 0,86 × 2,0 м: рама 40×40, обшивка С8 0,4, 2 петли, замок, ограничитель открывания', 'компл', 1, 13500),
    ]
    works = [
        ('Геодезическая разбивка осей и опор, поиск подземных сетей трассоискателем, вешки', 'компл', 1, 12000),
        (f'Столбы А и У: бурение лунки Ø200 на 0,8 м, забивка столба до {zf(Z_DRV)}, засыпка щебнем с трамбовкой слоями по 0,2 м, выверка', 'шт', n60, 1300),
        ('Закручивание свай СВС-89 и СВС-108 (калитка, ворота, закладная)', 'шт', p89 + p108, 2000),
        ('Монтаж лаг (сварка к столбам), окраска, профлист, планка; столбы калитки и ворот — на оголовки свай', 'м', rnd(L, 1), 850),
        ('Ниши ВРУ и ШГ в линии забора: обрамление, вырезка листа, окантовка', 'компл', 1, 7000),
        ('Монтаж откатных ворот: закладная на сваях, роликовые опоры, улавливатели, регулировка', 'компл', 1, 26000),
        ('Монтаж калитки', 'компл', 1, 6000),
        ('Доставка материалов и свай', 'рейс', 2, 6000),
    ]
    return dict(L=L, sheets=sheets, area=area, cnt=cnt, mats=mats, works=works, p89=p89, p108=p108,
                n60=n60, n80=n80, len60=len60, len80=len80, lag=lag, stone=stone)


def cost():
    c = calc()
    m = sum(rnd(q * p) for _, _, q, p in c['mats']); w = sum(rnd(q * p) for _, _, q, p in c['works'])
    return m, w, m + w


def total():
    return int(cost()[2])


def wind():
    """Проверка столба и сваи на ветер: I ветровой район, местность B (СП 20.13330)."""
    w0, k, cx, gf = 0.23, 0.5, 1.4, 1.4
    w = w0 * k * cx * gf                                     # кПа
    step = max(math.hypot(a['x'] - b['x'], a['y'] - b['y']) for a, b in zip(SUP, SUP[1:] + SUP[:1])
               if {a['t'], b['t']} not in ({'К'}, {'В1', 'В2'}))          # пролёты с обшивкой, без проёмов
    F = w * step * (Z_S1 - Z_S0)                             # кН на столб
    arm = (Z_S0 + Z_S1) / 2                                  # плечо от уровня земли (забитый столб)
    M = F * arm                                              # кН·м у земли
    I60 = (60 ** 4 - 56 ** 4) / 12; W60 = I60 / 30          # мм³
    # столб в грунте: короткая жёсткая свая в глинистом грунте (Broms), свободная голова; cu = 40 кПа (суглинок тугопластичный),
    # ширина — только столб 60 мм, щебень в лунке в запас не учитывается
    cu, b, Lg = 40.0, 0.06, -Z_DRV
    def lhs(H):
        f = H / (9 * cu * b); g = Lg - 1.5 * b - f
        return H * (arm + 1.5 * b + 0.5 * f) - 2.25 * b * cu * max(g, 0) ** 2
    lo, hi = 0.0, 20.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if lhs(mid) < 0 else (lo, mid)
    Hu = lo
    # лага 40×20×1,5 (узкой стороной поперёк забора): неразрезная по столбам, грузовая полоса — половина листа
    ql = w * (Z_S1 - Z_S0) / 2; Ml = ql * step ** 2 / 10
    Il = (40 * 20 ** 3 - 37 * 17 ** 3) / 12; Wl = Il / 10
    return dict(w=w, step=step, F=F, arm=arm, M=M, s60=M * 1e6 / W60, W60=W60 / 1000, Hu=Hu, kH=Hu / F, cu=cu,
                Ml=Ml, sl=Ml * 1e6 / Wl, Wl=Wl / 1000)


# ================= рисование =================
C = dict(ink='#1E2528', mu='#565C61', post='#3A4045', pile='#7C858C', blade='#4E575E', lag='#8C9399', sheet='#3E5B3A',
         soil='#E7DFCF', frz='#1D5FA0', gas='#C28E00', k1='#7A3E1D', v1='#1D5FA0', el='#C45F08', gate='#9A5B00', wick='#1D5FA0', paper='#FBF9F4')


class D(Svg):
    """SVG в метрах: толщина линий и размер текста — в пикселях при масштабе sc (px на метр)."""
    def __init__(self, sc): super().__init__(); self.sc = sc
    def ln(self, x1, y1, x2, y2, w=1.0, c=C['ink'], dash=''):
        return self.line(x1, y1, x2, y2, '', f'stroke:{c};stroke-width:{w}px;vector-effect:non-scaling-stroke' + (f';stroke-dasharray:{dash}' if dash else ''))
    def pln(self, pts, w=1.0, c=C['ink'], dash='', fill='none'):
        return self.pl(pts, '', f'fill:{fill};stroke:{c};stroke-width:{w}px;vector-effect:non-scaling-stroke' + (f';stroke-dasharray:{dash}' if dash else ''))
    def box(self, x, y, w, h, fill='none', c=None, sw=0.8, dash='', op=None):
        st = f'fill:{fill}' + (f';stroke:{c};stroke-width:{sw}px;vector-effect:non-scaling-stroke' if c else '') + (f';stroke-dasharray:{dash}' if dash else '') + (f';opacity:{op}' if op is not None else '')
        return self.rect(x, y, w, h, '', st)
    def poly(self, pts, fill='none', c=None, sw=0.8, dash='', op=None):
        st = f'fill:{fill}' + (f';stroke:{c};stroke-width:{sw}px;vector-effect:non-scaling-stroke' if c else '') + (f';stroke-dasharray:{dash}' if dash else '') + (f';opacity:{op}' if op is not None else '')
        return self.pg(pts, '', st)
    def dot(self, x, y, r_px, fill=C['ink'], c=None, sw=0.8):
        st = f'fill:{fill}' + (f';stroke:{c};stroke-width:{sw}px;vector-effect:non-scaling-stroke' if c else '')
        return self.circ(x, y, r_px / self.sc, '', st)
    def ring(self, x, y, r, c=C['ink'], sw=0.8, fill='none', dash=''):
        return self.circ(x, y, r, '', f'fill:{fill};stroke:{c};stroke-width:{sw}px;vector-effect:non-scaling-stroke' + (f';stroke-dasharray:{dash}' if dash else ''))
    def t(self, x, y, s, px=11, a='', c=C['ink'], b=False, mono=False, rot=None, halo=False):
        st = f'font-size:{px / self.sc:.5f}px;fill:{c}' + (';font-weight:600' if b else '') + (";font-family:'IBM Plex Mono',monospace" if mono else '')
        if halo: st += f';paint-order:stroke;stroke:{C["paper"]};stroke-width:{3 / self.sc:.5f}px;stroke-linejoin:round'
        return self.text(x, y, s, {'m': 'mid', 'e': 'end', '': ''}[a], rot, st)
    def tag(self, x, y, s, r_px=8, fill=C['ink'], px=9):
        self.dot(x, y, r_px, fill); return self.t(x, y + px * 0.36 / self.sc, s, px, 'm', '#FFFFFF', True)
    def dimh(self, x1, x2, y, s=None, px=9.5, tick=4, above=True, c=C['mu']):
        self.ln(x1, y, x2, y, 0.7, c)
        for x in (x1, x2): self.ln(x - tick / self.sc, y + tick / self.sc, x + tick / self.sc, y - tick / self.sc, 1.1, C['ink'])
        if s is None: s = mm(abs(x2 - x1))
        self.t((x1 + x2) / 2, y - (3 / self.sc if above else -px * 1.05 / self.sc), s, px, 'm', C['ink'], mono=True)
    def dimv(self, x, y1, y2, s=None, px=9.5, tick=4, left=True, c=C['mu']):
        self.ln(x, y1, x, y2, 0.7, c)
        for y in (y1, y2): self.ln(x - tick / self.sc, y + tick / self.sc, x + tick / self.sc, y - tick / self.sc, 1.1, C['ink'])
        if s is None: s = mm(abs(y2 - y1))
        xx = x - 3 / self.sc if left else x + px * 1.05 / self.sc
        self.t(xx, (y1 + y2) / 2, s, px, 'm', C['ink'], mono=True, rot=-90)
    def chainh(self, xs, y, px=9, min_px=26, above=True):
        xs = sorted(xs); self.ln(xs[0], y, xs[-1], y, 0.7, C['mu'])
        for x in xs: self.ln(x - 4 / self.sc, y + 4 / self.sc, x + 4 / self.sc, y - 4 / self.sc, 1.1, C['ink'])
        for a, b in zip(xs, xs[1:]):
            if (b - a) * self.sc >= min_px: self.t((a + b) / 2, y - (3 / self.sc if above else -px * 1.05 / self.sc), mm(b - a), px, 'm', C['ink'], mono=True)
    def chainv(self, ys, x, px=9, min_px=26, left=True):
        ys = sorted(ys); self.ln(x, ys[0], x, ys[-1], 0.7, C['mu'])
        for y in ys: self.ln(x - 4 / self.sc, y + 4 / self.sc, x + 4 / self.sc, y - 4 / self.sc, 1.1, C['ink'])
        for a, b in zip(ys, ys[1:]):
            if (b - a) * self.sc >= min_px: self.t(x - 3 / self.sc if left else x + px * 1.05 / self.sc, (a + b) / 2, mm(b - a), px, 'm', C['ink'], mono=True, rot=-90)
    def mark(self, x, z, label, px=9, right=False):
        """Высотная отметка: треугольник и подпись (z — отметка, по оси Y — минус z)."""
        y = -z; h = 5 / self.sc
        self.poly([(x, y), (x - h, y - h), (x + h, y - h)], C['ink'])
        self.ln(x - 2.2 * h, y, x + 2.2 * h, y, 0.8)
        self.t(x + (2.6 * h if right else -2.6 * h), y - 1.5 / self.sc, label, px, '' if right else 'e', C['ink'], mono=True)
    def out(self, x0, y0, w, h, width_px, style='background: #FBF9F4; border: 1px solid #D6CEBF'):
        return self.svg(width_px, round(width_px * h / w), f'{x0:.3f} {y0:.3f} {w:.3f} {h:.3f}', style)


STONE, BITUM = '#C9C1AF', '#2B2F31'


def draw_driven(d, X, t, top=None):
    """Забитый столб: лунка Ø200 на 0,8 м со щебнем, столб до Z_DRV, битум до +0,15, заглушка. Y = −z."""
    w = TYPES[t][2]; top = top or TYPES[t][3]
    d.box(X - HOLE_D / 2, 0, HOLE_D, -Z_HOLE, STONE, C['ink'], 0.5, '3 2')                   # лунка со щебнем
    if d.sc >= 60:
        for k in range(int(-Z_HOLE / 0.1)):
            for j, dx in enumerate((-0.065, 0.065) if k % 2 else (-0.045, 0.045)):
                d.dot(X + dx, 0.05 + k * 0.1, 1.2 if d.sc < 120 else 1.8, '#8C8373')
    d.box(X - w / 2, -top, w, top - Z_S0 + 0.0, C['post'], C['ink'], 0.5)                    # столб над землёй
    d.box(X - w / 2, -Z_S0, w, Z_S0 - Z_DRV, BITUM, C['ink'], 0.5)                           # подземная часть в мастике
    d.box(X - w / 2 - 0.004, -(top + max(0.006, 1.5 / d.sc)), w + 0.008, max(0.006, 1.5 / d.sc), C['ink'])   # заглушка


def draw_support(d, X, t, head=Z_HEAD, top=None, pile_only=False, face=None):
    """Опора в фасаде: свая (ствол, лопасть, наконечник), оголовок, столб, заглушка. Y = −z."""
    if driven(t): return draw_driven(d, X, t, top)
    P = PILES[TYPES[t][4]] if t in TYPES else PILES[t]
    L, pd, bl = P['L'], P['d'], P['blade']
    tip = head - L
    d.box(X - pd / 2, -head, pd, L - 0.10, C['pile'], C['ink'], 0.5)                    # ствол
    d.poly([(X - pd / 2, -(tip + 0.10)), (X + pd / 2, -(tip + 0.10)), (X, -tip)], C['pile'], C['ink'], 0.5)   # наконечник
    zb = tip + 0.22                                                                     # лопасть (виток)
    d.poly([(X - bl / 2, -(zb - 0.02)), (X + bl / 2, -(zb + 0.03)), (X + bl / 2, -(zb + 0.045)), (X - bl / 2, -(zb - 0.005))], C['blade'], C['ink'], 0.5)
    pt = max(P['pt'], 1.6 / d.sc)
    d.box(X - P['plate'] / 2, -(head + pt), P['plate'], pt, C['ink'])                   # оголовок
    if pile_only: return
    w = TYPES[t][2]; top = top or TYPES[t][3]
    d.box(X - w / 2, -top, w, top - head - pt, C['post'], C['ink'], 0.5)               # столб
    d.box(X - w / 2 - 0.004, -(top + max(0.006, 1.5 / d.sc)), w + 0.008, max(0.006, 1.5 / d.sc), C['ink'])   # заглушка


def draw_ground(d, x0, x1, zmin=-3.05):
    d.box(x0, 0, x1 - x0, -zmin, C['soil'])
    d.ln(x0, 0, x1, 0, 1.3, C['ink'])
    d.ln(x0, -Z_FRZ, x1, -Z_FRZ, 0.9, C['frz'], '6 4')


def draw_frame(d, a, b, lag=True, sheet=True, cut=()):
    """Лаги и профлист между осями a и b (в фасаде). cut — вырезы (x0, x1, z0, z1) под ниши."""
    if lag:
        for z in Z_LAG: d.box(a, -(z + 0.02), b - a, 0.04, C['lag'], C['ink'], 0.4)
    if sheet:
        d.box(a, -Z_S1, b - a, Z_S1 - Z_S0, C['sheet'], op=0.16)
        x = a + WAVE / 2
        while x < b - 0.02:
            d.ln(x, -Z_S1, x, -Z_S0, 0.35, C['sheet']); x += WAVE
        d.ln(a, -Z_S1, b, -Z_S1, 2.2, C['sheet'])                                        # П-планка
        d.ln(a, -Z_S0, b, -Z_S0, 0.8, C['sheet'])
        for (x0, x1, z0, z1) in cut:
            d.box(x0, -z1, x1 - x0, z1 - z0, C['paper'], C['ink'], 0.9)


SIDE_POSTS = {'street': list(range(1, 16)), 'right': list(range(15, 29)), 'back': list(range(28, 42)), 'left': list(range(41, 54)) + [1]}
SIDE_X = {'street': lambda p: p['x'], 'right': lambda p: 32 - p['y'], 'back': lambda p: 32 - p['x'], 'left': lambda p: p['y']}
SIDE_NAME = {'street': 'Уличный забор — вид с улицы', 'right': 'Правая граница — вид снаружи (от соседа справа)',
             'back': 'Тыльная граница — вид снаружи', 'left': 'Левая граница — вид снаружи (от соседа слева)'}


def elevation(side, xa, xb, sc, zmax=3.25, zmin=-3.35, marks=True, width=None):
    d = D(sc); X = SIDE_X[side]
    ps = [BYN[n] for n in SIDE_POSTS[side]]
    draw_ground(d, xa, xb, zmin)
    # обшивка и лаги по участкам (без проёмов калитки и ворот)
    xs = [X(p) for p in ps]
    groups = []; cur = [xs[0]]
    for p, q, xp, xq in zip(ps, ps[1:], xs, xs[1:]):
        if side == 'street' and {p['t'], q['t']} in ({'К'}, {'В1', 'В2'}):
            groups.append(cur); cur = [xq]
        else: cur.append(xq)
    groups.append(cur)
    cut = [(VRU_BOX[0], VRU_BOX[1], VRU_BOX[2], VRU_BOX[3]), (SHG_BOX[0], SHG_BOX[1], SHG_BOX[2], SHG_BOX[3])] if side == 'street' else []
    for p, xp in zip(ps, xs): draw_support(d, xp, p['t'])
    if side == 'street':                                  # закладная ворот на сваях (за линией забора, показана пунктиром)
        for x in EMB_PILES: draw_support(d, x, '108', head=Z_EMB, pile_only=True)
        d.box(EMB[0], 0, EMB[1] - EMB[0], -Z_EMB, '#9AA0A4', C['ink'], 0.8)
    for g in groups: draw_frame(d, min(g), max(g), cut=[c for c in cut if min(g) < c[0] < max(g)])
    if side == 'street':
        # шкафы в нишах
        x0, x1, z0, z1, _ = VRU_BOX
        d.box(x0 + 0.02, -z1 + 0.02, x1 - x0 - 0.04, z1 - z0 - 0.04, '#E8E3D6', C['ink'], 1)
        d.box((x0 + x1) / 2 - 0.12, -(z0 + 0.42), 0.24, 0.13, '#FFFFFF', C['ink'], 0.7)
        d.t((x0 + x1) / 2, -(z0 + 0.16), 'ВРУ', 10, 'm', C['ink'], True)
        d.ln(VRU[0], -z0, VRU[0], 0.7, 1.6, C['el'], '5 3'); d.dot(VRU[0], 0.7, 3.5, C['el'])
        x0, x1, z0, z1, _ = SHG_BOX
        d.box(x0 + 0.02, -z1 + 0.02, x1 - x0 - 0.04, z1 - z0 - 0.04, '#F2C230', C['ink'], 1)
        for k in range(4): d.ln(x0 + 0.12, -(z1 - 0.12 - k * 0.05), x1 - 0.12, -(z1 - 0.12 - k * 0.05), 0.7)
        d.t((x0 + x1) / 2, -(z0 + 0.2), 'ШГ', 10, 'm', C['ink'], True)
        for dx in (-0.09, 0.09): d.ln(SHG[0] + dx, -z0, SHG[0] + dx, -G1_DEPTH, 1.8, C['gas'])
        d.dot(SHG[0], -G1_DEPTH, 4, C['gas'])
        # калитка
        a, b = WICKET[0] + 0.07, WICKET[1] - 0.07
        d.box(a, -Z_S1, b - a, Z_S1 - Z_S0, C['sheet'], op=0.22); d.box(a, -Z_S1, b - a, Z_S1 - Z_S0, 'none', C['wick'], 1.6)
        d.ln(a, -(Z_S0 + 1.0), b, -(Z_S0 + 1.0), 1, C['wick'])
        for z in (0.40, 1.90): d.box(WICKET[0] + 0.04, -(z + 0.06), 0.04, 0.12, C['ink'])
        d.box(b - 0.07, -1.08, 0.05, 0.16, C['ink'])
        # ворота (закрыты): полотно в проёме, противовес за забором — пунктир
        a, b = GATE[0] - 0.1, GATE[1]
        d.box(a, -Z_S1, b - a, Z_S1 - Z_S0, C['sheet'], op=0.22); d.box(a, -Z_S1, b - a, Z_S1 - Z_S0, 'none', C['gate'], 1.6)
        d.pln([(LEAF_CLOSED[0], -0.13), (a, -0.13), (a, -Z_S1), (LEAF_CLOSED[0] + 0.3, -(Z_S0 + 0.1)), (LEAF_CLOSED[0], -0.13)], 1.2, C['gate'], '5 3')
        d.ln(LEAF_CLOSED[0], -0.13, b, -0.13, 2.4, C['gate'])
        for x in CARR: d.box(x - 0.12, -0.12, 0.24, 0.12, C['gate'])
        d.box(GATE[0] - 0.16, -(Z_TOPV - 0.02), 0.12, 0.14, C['gate'])                         # верхние ролики
        d.box(GATE[1] - 0.02, -0.33, 0.1, 0.2, C['gate']); d.box(GATE[1] - 0.02, -(Z_S1 + 0.02), 0.1, 0.16, C['gate'])   # улавливатели
    # сети на пересечении с линией забора
    cross = []
    if side == 'street': cross = [(2.6, -0.8, 'выпуск ЛОС −0,80', C['k1']), (VRU[0], -0.7, 'кабель ВРУ −0,70', C['el']), (SHG[0], G1_DEPTH, 'газ −1,55', C['gas'])]
    if side == 'right': cross = [(32 - V1_NEIGH[0][1], -1.8, 'В1 к соседу в гильзе −1,80', C['v1'])]
    for x, z, s, c in cross:
        d.ring(x, -z, 0.07, c, 1.6, '#FFFFFF'); d.t(x + 0.14, -z + 0.30, s, 9.5, '', c, True, halo=True)
    # номера опор и цепочка размеров
    for p, xp in zip(ps, xs):
        d.tag(xp, -(Z_TOPV + 0.35), str(p['n']), 9 if sc > 50 else 7.5, TYPES[p['t']][5], 9 if sc > 50 else 7.5)
    ych = -(zmin + 0.35)
    d.chainh(xs, ych, 9 if sc > 50 else 8, 22, above=True)
    if side == 'street':
        d.dimh(ROLL[0], ROLL[1], -(Z_TOPV + 0.78), f'зона отката {mm(ROLL[1] - ROLL[0])}', 9.5)
        d.dimh(GATE[0], GATE[1], -(Z_TOPV + 0.78), f'проём ворот {mm(GATE[1] - GATE[0])}', 9.5)
        d.dimh(WICKET[0], WICKET[1], -(Z_TOPV + 0.78), 'калитка 1 000', 9.5)
    if marks:
        xm = xa + 60 / sc
        zs = [Z_TOP, Z_LAG[1], Z_LAG[0], 0, Z_HOLE, Z_DRV] + ([Z_TOPV, Z_S0, Z_HEAD - 2.5, Z_EMB - 2.5] if side == 'street' else [])
        for z in zs: d.mark(xm, z, zf(z), 8.5 if sc > 50 else 8)
    return d.out(xa, -zmax, xb - xa, zmax - zmin, width or round((xb - xa) * sc), 'flex-shrink: 0; background: #FBF9F4; border: 1px solid #D6CEBF')


def site_plan(sc=22.9, x0=-3.4, y0=-3.3, w=38.8, h=39.4):
    d = D(sc)
    d.box(0, 0, 32, 32, '#F4F0E4', '#B3261E', 0.9, '8 4')                              # граница участка
    for pg in (HEATED, TERRACE): d.poly(pg, '#E2D6BE', C['mu'], 0.6)
    for r in (BATH, GAZEBO, SHED, PARK): d.box(*r, '#ECE6D8', C['mu'], 0.6)
    d.box(*LOS, '#FFFFFF', C['k1'], 0.8); d.box(30.45, 20.45, 1.1, 1.1, '#FFFFFF', C['v1'], 0.8); d.ring(*WELL, 0.3, C['v1'], 1.2)
    for tx, ty, s in [(13.5, 21.5, 'дом'), (27.6, 4.6, 'баня'), (GAZEBO[0] + GAZEBO[2]/2, GAZEBO[1] + GAZEBO[3]/2 + 0.3, 'беседка'), (4.0, 2.3, 'хозблок'), (28.2, 28.4, 'стоянка'), (2.6, 29.0, 'ЛОС'), (29.9, 20.1, 'скважина')]:
        d.t(tx, ty, s, 10, 'm', C['mu'])
    for name, short, pts, z, need, why in UTIL:                                          # сети
        c = C['gas'] if 'газ' in short else C['v1'] if 'В1' in short else C['el'] if 'кабель' in short else C['k1']
        if 'кессон' in short or short == 'ЛОС': continue
        d.pln(pts, 1.4, c, '6 3' if 'К1' in short or 'ЛОС' in short else '')
    # линия профлиста (с наружной стороны опор) и проёмы
    o = 0.06
    segs = [((FL, FS + o), (WICKET[0], FS + o)), ((WICKET[1], FS + o), (GATE[0], FS + o)), ((GATE[1], FS + o), (FR + o, FS + o)),
            ((FR + o, FS + o), (FR + o, FB - o)), ((FR + o, FB - o), (FL - o, FB - o)), ((FL - o, FB - o), (FL - o, FS + o)), ((FL - o, FS + o), (FL, FS + o))]
    for a, b in segs: d.ln(*a, *b, 3.2, C['sheet'])
    # ниши
    for (bx0, bx1, z0, z1, dep), c, s in [(VRU_BOX, '#E8E3D6', 'ВРУ'), (SHG_BOX, '#F2C230', 'ШГ')]:
        d.box(bx0, FS + 0.07 - dep, bx1 - bx0, dep, c, C['ink'], 0.9); d.t((bx0 + bx1) / 2, FS - 0.55, s, 9, 'm', C['ink'], True)
    # калитка
    r = WICKET[1] - WICKET[0] - 0.14
    hx = WICKET[0] + 0.07
    d.ln(hx, FS, hx + r, FS, 2.2, C['wick'])
    d.add(f'<path d="M {hx + r:.3f} {FS:.3f} A {r:.3f} {r:.3f} 0 0 0 {hx:.3f} {FS - r:.3f}" style="fill:none;stroke:{C["wick"]};stroke-width:1px;vector-effect:non-scaling-stroke;stroke-dasharray:4 3"></path>')
    d.ln(hx, FS, hx, FS - r, 1.4, C['wick'])
    # ворота: полотно закрыто, открыто (пунктир), закладная и сваи
    d.ln(LEAF_CLOSED[0], LEAF_Y, LEAF_CLOSED[1], LEAF_Y, 3.2, C['gate'])
    d.ln(LEAF_OPEN[0], LEAF_Y - 0.28, LEAF_OPEN[1], LEAF_Y - 0.28, 1.6, C['gate'], '6 3')
    d.box(EMB[0], LEAF_Y - 0.08, EMB[1] - EMB[0], 0.16, '#9AA0A4', C['ink'], 0.6)
    for x in EMB_PILES: d.ring(x, LEAF_Y, 0.15, C['ink'], 1, '#FFFFFF')
    # опоры
    lab = {'street': (0, 0.95), 'right': (0.95, 0), 'back': (0, -0.95), 'left': (-0.95, 0)}
    for p in SUP:
        c = TYPES[p['t']][5]; bl = blade(p)
        d.ring(p['x'], p['y'], bl / 2, c, 0.7, 'none', '2 1.5')
        q = 0.30 if p['t'] in ('А', 'У') else 0.38
        d.box(p['x'] - q / 2, p['y'] - q / 2, q, q, c)
        side = p['side'] if p['t'] != 'У' else {1: 'street', 15: 'street', 28: 'back', 41: 'back'}[p['n']]
        dx, dy = lab[side]
        d.tag(p['x'] + dx, p['y'] + dy, str(p['n']), 7.8, c, 8)
    # цепочки пролётов по осям опор и общие размеры
    xs = [p['x'] for p in SUP if p['side'] == 'street']
    d.chainh(xs, 33.55, 7.8, 21, above=True); d.dimh(FL, FR, 34.55, '31 800 по осям опор', 8.5)
    ys = [FS] + [p['y'] for p in SUP if p['side'] == 'right']
    d.chainv(ys, 33.55, 7.8, 21, left=False); d.dimv(34.55, FB, FS, '31 800', 8.5, left=False)
    xs = [FR] + [p['x'] for p in SUP if p['side'] == 'back']
    d.chainh(xs, -1.75, 7.8, 21); d.dimh(FL, FR, -2.75, '31 800', 8.5)
    ys = [FB] + [p['y'] for p in SUP if p['side'] == 'left'] + [FS]
    d.chainv(ys, -1.75, 7.8, 21); d.dimv(-2.6, FB, FS, '31 800', 8.5)
    for (px, py, t, a) in [(0, 32, 'н1', 'e'), (0, 0, 'н2', 'e'), (32, 0, 'н3', ''), (32, 32, 'н4', '')]:
        d.t(px + (-0.35 if a == 'e' else 0.35), py + (0.6 if py else -0.3), t, 10, a, '#B3261E', True)
    d.t(16, 35.2, 'улица', 11, 'm', C['mu'], True); d.t(-3.05, 22, 'сосед слева', 10, 'm', C['mu'], rot=-90); d.t(35.0, 22, 'сосед справа', 10, 'm', C['mu'], rot=90)
    return d.out(x0, y0, w, h, round(w * sc), 'flex-shrink: 0; background: #FBF9F4; border: 1px solid #D6CEBF')


EMB_N = (54, 55)                            # номера свай закладной в общей ведомости


def street_plan(x0, x1, sc=71.1, y0=29.75, y1=34.35):
    """Уличный забор в плане крупно: опоры с лопастями, ниши, калитка, ворота, закладная, сети."""
    d = D(sc)
    d.box(x0, y0, x1 - x0, 32 - y0, '#F4F0E4'); d.box(x0, 32, x1 - x0, y1 - 32, '#E9E4D8')
    d.ln(x0, 32, x1, 32, 1, '#B3261E', '8 4'); d.t(x1 - 0.2, 32.35, 'граница участка', 9, 'e', '#B3261E')
    d.ln(FL, FS, FR, FS, 0.6, C['mu'], '10 3 2 3'); d.t(x0 + 0.1, FS - 0.08, 'ось опор', 8.5, '', C['mu'])
    d.box(WICKET[0] + 0.06, FS - 1.9, WICKET[1] - WICKET[0] - 0.12, 1.9 - 0.1, '#DCD3C1')      # дорожка от калитки
    d.t(sum(WICKET) / 2, FS - 1.35, 'дорожка', 8.5, 'm', C['mu'])
    o = 0.06
    for a, b in [(FL, WICKET[0]), (WICKET[1], GATE[0]), (GATE[1], FR)]: d.ln(a, FS + o, b, FS + o, 3.4, C['sheet'])
    d.ln(FL - o, FS + o, FL - o, y0, 3.4, C['sheet']); d.ln(FR + o, FS + o, FR + o, y0, 3.4, C['sheet'])
    for (bx0, bx1, z0, z1, dep), c, s in [(VRU_BOX, '#E8E3D6', 'ВРУ 800×650×250'), (SHG_BOX, '#F2C230', 'ШГ 600×800×300')]:
        d.box(bx0, FS + 0.07 - dep, bx1 - bx0, dep, c, C['ink'], 1); d.t((bx0 + bx1) / 2, FS - 1.25, s, 9, 'm', C['ink'], True, halo=True)
        d.ln((bx0 + bx1) / 2, FS - 1.18, (bx0 + bx1) / 2, FS + 0.07 - dep, 0.6, C['ink'])
    # сети, пересекающие линию забора
    for x, c, s, z in [(2.6, C['k1'], 'выпуск ЛОС в кювет, −0,80', -0.8), (VRU[0], C['el'], 'кабель ВРУ, −0,70', -0.7), (SHG[0], C['gas'], 'газ: ввод в ШГ и Г1, −1,55', -1.55)]:
        d.ln(x, y0, x, y1, 1.6, c, '7 3'); d.t(x + 0.08, y0 + 0.25, s, 9, '', c, True, halo=True)
    # калитка
    r = WICKET[1] - WICKET[0] - 0.14; hx = WICKET[0] + 0.07
    d.ln(hx, FS, hx + r, FS, 2.4, C['wick'])
    d.add(f'<path d="M {hx + r:.3f} {FS:.3f} A {r:.3f} {r:.3f} 0 0 0 {hx:.3f} {FS - r:.3f}" style="fill:none;stroke:{C["wick"]};stroke-width:1px;vector-effect:non-scaling-stroke;stroke-dasharray:4 3"></path>')
    d.ln(hx, FS, hx, FS - r, 1.4, C['wick']); d.box(hx - 0.05, FS - r - 0.08, 0.1, 0.08, C['wick'])
    d.t(hx - 0.1, FS - r + 0.05, 'упор 90°', 8.5, 'e', C['wick'], halo=True)
    # ворота
    d.ln(LEAF_CLOSED[0], LEAF_Y, LEAF_CLOSED[1], LEAF_Y, 3.4, C['gate'])
    d.ln(LEAF_OPEN[0], LEAF_Y - 0.35, LEAF_OPEN[1], LEAF_Y - 0.35, 1.8, C['gate'], '7 3')
    d.t(LEAF_CLOSED[0] + CWT / 2, LEAF_Y - 0.12, 'противовес 1 600', 8.5, 'm', C['gate'], halo=True)
    d.t(GATE[0] + LEAF_BODY / 2, LEAF_Y - 0.12, 'полотно 4 100 (закрыто)', 8.5, 'm', C['gate'], halo=True)
    d.t(LEAF_OPEN[0] + 0.1, LEAF_Y - 0.47, 'полотно в открытом положении', 9, '', C['gate'], halo=True)
    d.box(EMB[0], LEAF_Y - 0.08, EMB[1] - EMB[0], 0.16, '#9AA0A4', C['ink'], 0.7)
    for x in CARR: d.box(x - 0.14, LEAF_Y - 0.09, 0.28, 0.18, C['gate'])
    for n, x in zip(EMB_N, EMB_PILES):
        d.ring(x, LEAF_Y, PILES['108']['blade'] / 2, C['gate'], 0.8, 'none', '2 1.5'); d.dot(x, LEAF_Y, 3, C['ink'])
        d.tag(x, FS - 1.45, str(n), 8.5, C['gate'], 8.5); d.ln(x, FS - 1.33, x, LEAF_Y - 0.1, 0.6, C['gate'])
    # опоры: сечение столба; лунка со щебнем или оголовок и лопасть сваи — в масштабе
    for p in [q for q in SUP if q['side'] == 'street']:
        tp = TYPES[p['t']]; c = tp[5]
        if driven(p['t']):
            d.ring(p['x'], p['y'], HOLE_D / 2, c, 0.8, STONE, '2 1.5')
        else:
            P = PILES[tp[4]]
            d.ring(p['x'], p['y'], P['blade'] / 2, c, 0.8, 'none', '2 1.5')
            d.box(p['x'] - P['plate'] / 2, p['y'] - P['plate'] / 2, P['plate'], P['plate'], 'none', C['ink'], 0.6)
        d.box(p['x'] - tp[2] / 2, p['y'] - tp[2] / 2, tp[2], tp[2], c)
        d.tag(p['x'], FS - 0.75, str(p['n']), 8.5, c, 8.5)
    xs = [p['x'] for p in SUP if p['side'] == 'street']
    d.chainh(xs, 32.95, 9, 20)
    d.dimh(ROLL[0], ROLL[1], 30.05, f'зона отката {mm(ROLL[1] - ROLL[0])}', 9)
    d.chainh([EMB[0], EMB_PILES[0], EMB_PILES[1], EMB[1], GATE[0]], 33.55, 9, 18)
    d.t(EMB[0] - 0.1, 33.5, 'закладная 16П 2 000, сваи 54, 55', 9, 'e', C['ink'])
    d.chainh([VRU_BOX[0], VRU_BOX[1], SHG_BOX[0], SHG_BOX[1]], 33.55, 9, 18)
    for s_, box, (a, b) in NICHES:                  # привязка шкафов к осям опор своего пролёта
        d.chainh([BYN[a]['x'], (box[0] + box[1]) / 2, BYN[b]['x']], 34.05, 9, 18)
    return d.out(x0, y0, x1 - x0, y1 - y0, round((x1 - x0) * sc), 'flex-shrink: 0; background: #FBF9F4; border: 1px solid #D6CEBF')


def leader(d, x, y, tx, ty, s, px=10, a=''):
    d.ln(x, y, tx, ty, 0.7); d.dot(x, y, 2.2)
    d.t(tx + (0.03 if a == '' else -0.03) * 150 / d.sc, ty + 3.5 / d.sc, s, px, a, C['ink'], halo=True)


def callout(d, x, y, tx, ty, n, c=C['ink']):
    d.ln(x, y, tx, ty, 0.7); d.dot(x, y, 2.2); d.tag(tx, ty, str(n), 8.5, c, 9)


def node_post(sc=150):
    """У1: опора типа А — фасад со стороны участка и разрез 1–1 поперёк забора: лунка со щебнем, забитый столб."""
    d = D(sc)
    X0, X1 = -1.12, 3.95
    d.box(X0, 0, X1 - X0, 2.12, C['soil']); d.ln(X0, 0, X1, 0, 1.3); d.ln(X0, -Z_FRZ, X1, -Z_FRZ, 0.9, C['frz'], '6 4')
    # фасад: столб, обрезки лаг, лист за ними
    d.box(-0.45, -Z_S1, 0.9, Z_S1 - Z_S0, C['sheet'], op=0.14)
    x = -0.45 + WAVE / 2
    while x < 0.45: d.ln(x, -Z_S1, x, -Z_S0, 0.4, C['sheet']); x += WAVE
    draw_support(d, 0, 'А')
    for z in Z_LAG: d.box(-0.45, -(z + 0.02), 0.9, 0.04, C['lag'], C['ink'], 0.5)
    d.ln(-0.45, -Z_S1, 0.45, -Z_S1, 2.6, C['sheet'])
    d.t(0, -2.52, 'фасад со стороны участка', 10, 'm', C['mu'], True)
    for z in (Z_TOP, Z_S1, Z_LAG[1], Z_LAG[0], Z_S0, 0, Z_HOLE, Z_DRV, Z_FRZ):
        d.mark(-0.55, z, zf(z), 9)
    # разрез 1–1: ось опоры в X = 1.7; улица справа
    c = 1.7
    d.ln(c + AX, -2.35, c + AX, 2.1, 1, '#B3261E', '8 4'); d.t(c + AX + 0.03, -2.25, 'граница участка', 9, '', '#B3261E')
    d.ln(c, -2.45, c, 2.1, 0.6, C['mu'], '10 3 2 3'); d.t(c - 0.03, -2.38, 'ось опор', 9, 'e', C['mu'])
    draw_driven(d, c, 'А')
    for z in Z_LAG: d.box(c + 0.03, -(z + 0.02), 0.02, 0.04, C['lag'], C['ink'], 0.6)
    zz = [Z_S0 + i * 0.0 for i in range(1)]
    d.pln([(c + 0.05, -Z_S0), (c + 0.05, -Z_S1)], 1.4, C['sheet']); d.pln([(c + 0.07, -Z_S0), (c + 0.07, -Z_S1)], 1.4, C['sheet'])
    for z in (Z_S0 + 0.05, Z_S1 - 0.05): d.ln(c + 0.05, -z, c + 0.07, -z, 0.8, C['sheet'])
    d.pln([(c + 0.035, -(Z_S1 - 0.03)), (c + 0.035, -(Z_S1 + 0.02)), (c + 0.085, -(Z_S1 + 0.02)), (c + 0.085, -(Z_S1 - 0.05))], 1.6, C['sheet'])   # П-планка
    for z in Z_LAG: d.ln(c + 0.03, -z, c + 0.09, -z, 1.2, C['ink'])                                                      # саморез
    d.t(c, -2.52, 'разрез 1–1 поперёк забора', 10, 'm', C['mu'], True)
    L = [(c + 0.06, -(Z_S1 + 0.02), 'П-планка на верх листа', -2.2), (c, -(Z_TOP + 0.003), 'заглушка 60×60', -2.33),
         (c + 0.07, -1.5, 'профлист С8 0,4 RAL 6005, лист 2 000', -1.6), (c + 0.04, -Z_LAG[1], 'лага 40×20×1,5 (2 ряда), к столбу — сварка', -1.3),
         (c + 0.09, -Z_LAG[0], 'саморез 5,5×19 с EPDM, 6 шт на лист на лагу', -0.72), (c, -1.0, f'столб 60×60×2, L = {mm(post_len("А"))}', -1.0),
         (c + 0.03, -0.05, 'мастика битумная 2 слоя: от низа до +0,150', -0.2), (c + 0.07, 0.3, 'лунка Ø200 мотобуром на 0,8 м', 0.3),
         (c - 0.05, 0.62, 'щебень 20–40, трамбовка слоями по 0,2 м', 0.72), (c, 1.1, f'столб забит на {nf(Z_HOLE - Z_DRV, 1)} м ниже дна лунки', 1.15),
         (c, -Z_DRV, f'низ столба {zf(Z_DRV)} — ниже промерзания', 1.62)]
    for x, y, s, ty in L: leader(d, x, y, c + 0.42, ty, s, 10)
    d.dimh(c, c + AX, -2.1, '100', 9); d.dimh(c + 0.03, c + 0.07, -1.93, '', 9)
    d.t(c + 0.05, -1.97, '30 + 20 + 20', 9, 'e', C['ink'], mono=True, halo=True)
    d.dimv(c - 0.18, 0, -Z_HOLE, f'{mm(-Z_HOLE)} лунка', 9); d.dimv(c - 0.3, 0, -Z_DRV, f'{mm(-Z_DRV)} в грунте', 9)
    d.dimv(c - 0.18, -Z_TOP, 0, mm(Z_TOP), 9); d.dimh(c - HOLE_D / 2, c + HOLE_D / 2, 0.86, f'Ø{mm(HOLE_D)}', 9, above=False)
    return d.out(X0, -2.72, X1 - X0, 4.9, round((X1 - X0) * sc), 'flex-shrink: 0; background: #FBF9F4; border: 1px solid #D6CEBF')


def node_corner(sc=820):
    """У2: угловая опора н1 в плане."""
    d = D(sc); cx, cy = FL, FS
    x0, y0, w, h = -0.14, 31.52, 0.62, 0.64
    d.box(x0, y0, w, h, '#F4F0E4'); d.box(x0, 32, w, y0 + h - 32, '#E9E4D8'); d.box(x0, y0, 0 - x0, 32 - y0, '#E9E4D8')
    d.ln(0, y0, 0, y0 + h, 1, '#B3261E', '8 4'); d.ln(x0, 32, x0 + w, 32, 1, '#B3261E', '8 4')
    d.ring(cx, cy, HOLE_D / 2, C['ink'], 0.8, STONE, '4 3')                                  # лунка Ø200 со щебнем
    d.box(cx - 0.03, cy - 0.03, 0.06, 0.06, C['post'], C['ink'], 0.8); d.box(cx - 0.028, cy - 0.028, 0.056, 0.056, '#FBF9F4')
    d.box(cx - 0.03, cy + 0.03, x0 + w - cx + 0.03, 0.02, C['lag'], C['ink'], 0.7)         # лага уличного забора
    d.box(cx - 0.05, y0, 0.02, cy - 0.03 - y0 + 0.05, C['lag'], C['ink'], 0.7)             # лага левого забора
    zig = [(cx - 0.07 + (0 if i % 2 == 0 else 0), 0) for i in range(1)]
    d.pln([(cx - 0.07, cy + 0.07), (x0 + w, cy + 0.07)], 2, C['sheet']); d.pln([(cx - 0.07, cy + 0.05), (x0 + w, cy + 0.05)], 1, C['sheet'], '3 3')
    d.pln([(cx - 0.07, y0), (cx - 0.07, cy + 0.07)], 2, C['sheet']); d.pln([(cx - 0.05, y0), (cx - 0.05, cy + 0.05)], 1, C['sheet'], '3 3')
    d.pln([(cx - 0.07 + 0.10, cy + 0.08), (cx - 0.08, cy + 0.08), (cx - 0.08, cy + 0.07 - 0.10)], 2.6, C['ink'])     # уголок
    d.dimh(0, cx, 32.1, '100', 9); d.dimv(0.4, cy, 32, '100', 9, left=False)
    for x, y, s, tx, ty in [(cx, cy, f'столб 60×60×2 (тип У), забит до {zf(Z_DRV)}', 0.12, 31.62), (cx + 0.06, cy - 0.06, 'лунка Ø200 на 0,8 м', 0.2, 31.7),
                            (cx + 0.085, cy - 0.02, 'щебень 20–40 с трамбовкой', 0.25, 31.78), (cx + 0.2, cy + 0.04, 'лага улицы', 0.3, 31.86),
                            (cx - 0.04, 31.6, 'лага левой границы', 0.08, 31.555), (cx - 0.08, cy + 0.02, 'уголок 100×100 на угол', -0.1, 32.12),
                            (0.3, cy + 0.07, 'профлист', 0.3, 32.08)]:
        d.ln(x, y, tx, ty, 0.6); d.dot(x, y, 2); d.t(tx + 0.005, ty - 0.005, s, 9.5, '', C['ink'], halo=True)
    d.t(x0 + 0.01, y0 + h - 0.015, 'улица', 9, '', C['mu']); d.t(x0 + 0.01, y0 + 0.03, 'сосед', 9, '', C['mu'])
    return d.out(x0, y0, w, h, round(w * sc), 'flex-shrink: 0; background: #FBF9F4; border: 1px solid #D6CEBF')


def node_wicket(sc=150):
    """У3: калитка — фасад со стороны участка (x зеркально) и план открывания."""
    d = D(sc)
    X = lambda x: 36.0 - x                                   # вид со стороны участка: x растёт влево
    xa, xb = X(19.95), X(15.35)
    d.box(xa, 0, xb - xa, 2.62, C['soil']); d.ln(xa, 0, xb, 0, 1.3); d.ln(xa, -Z_FRZ, xb, -Z_FRZ, 0.9, C['frz'], '6 4')
    for n in (9, 10): draw_support(d, X(BYN[n]['x']), 'К')
    draw_support(d, X(15.75), 'А')
    for a, b in [(15.4, WICKET[0]), (WICKET[1], 19.95)]:
        for z in Z_LAG: d.box(X(b), -(z + 0.02), X(a) - X(b), 0.04, C['lag'], C['ink'], 0.5)
        d.box(X(b), -Z_S1, X(a) - X(b), Z_S1 - Z_S0, C['sheet'], op=0.12)
    for s_, (x0, x1, z0, z1, _), _ab in NICHES:                   # шкафы в нишах, попавшие в вид
        if 15.35 < x0 and x1 < 19.95:
            d.box(X(x1), -z1, x1 - x0, z1 - z0, '#F2C230' if s_ == 'ШГ' else '#E8E3D6', C['ink'], 0.8); d.t(X((x0 + x1) / 2), -(z0 + 0.35), s_, 10, 'm', C['ink'], True)
    a, b = WICKET[0] + 0.07, WICKET[1] - 0.07                   # полотно 860 × 2 000, рама 40×40
    d.box(X(b), -Z_S1, b - a, Z_S1 - Z_S0, C['sheet'], op=0.2)
    d.box(X(b), -Z_S1, b - a, Z_S1 - Z_S0, 'none', C['wick'], 2.4)
    d.ln(X(b), -(Z_S0 + 1.0), X(a), -(Z_S0 + 1.0), 1.6, C['wick']); d.ln(X(b), -Z_S0, X(a), -(Z_S0 + 1.0), 1.2, C['wick'])
    for z in (0.40, 1.90):                                      # петли на столбе 9
        d.box(X(WICKET[0]) - 0.07, -(z + 0.08), 0.05, 0.16, C['ink'])
    d.box(X(b) + 0.02, -1.25, 0.08, 0.22, C['ink'])             # замок
    d.box(X(WICKET[1]) - 0.045, -1.21, 0.03, 0.14, '#9AA0A4', C['ink'], 0.6)   # ответная планка
    d.box(X(WICKET[1]) + 0.04, -(Z_S0 + 0.3), 0.05, 0.3, C['ink'])             # упор-притвор
    for n, (x, y, tx, ty) in enumerate([(X(WICKET[0]) - 0.045, -1.9, X(WICKET[0]) + 0.3, -2.02), (X(b) + 0.06, -1.14, X(b) + 0.33, -1.3),
                                         (X(WICKET[1]) - 0.03, -1.14, X(WICKET[1]) - 0.3, -1.35), (X(WICKET[1]) + 0.065, -(Z_S0 + 0.15), X(WICKET[1]) - 0.3, -0.35),
                                         ((X(a) + X(b)) / 2, -(Z_S0 + 1.5), (X(a) + X(b)) / 2 + 0.28, -1.75), (X(WICKET[0]), 0.9, X(WICKET[0]) + 0.35, 1.05)], 1):
        callout(d, x, y, tx, ty, n, C['wick'])
    d.chainh([X(WICKET[1]), X(b), X(a), X(WICKET[0]), X(15.75)], -(Z_TOP + 0.3), 9, 18)
    d.dimh(X(WICKET[1]) + 0.04, X(WICKET[0]) - 0.04, -(Z_TOP + 0.55), 'в свету 920', 9)
    for n in (9, 10): d.tag(X(BYN[n]['x']), -(Z_TOP + 0.85), str(n), 9, C['wick'], 9)
    d.tag(X(15.75), -(Z_TOP + 0.85), '8', 9, C['post'], 9)
    for z in (Z_TOP, Z_S1, Z_S0, 0, Z_FRZ, Z_HEAD - 2.5): d.mark(xa + 0.5, z, zf(z), 9)
    d.t(X(18.5), 2.5, 'вид со стороны участка', 10, 'm', C['mu'], True)
    return d.out(xa, -(Z_TOP + 1.1), xb - xa, Z_TOP + 1.1 + 2.62, round((xb - xa) * sc), 'flex-shrink: 0; background: #FBF9F4; border: 1px solid #D6CEBF')


def node_wicket_plan(sc=150):
    d = D(sc); x0, x1, y0, y1 = 15.4, 19.9, FS - 1.35, 32.35
    d.box(x0, y0, x1 - x0, y1 - y0, '#F4F0E4'); d.box(x0, 32, x1 - x0, y1 - 32, '#E9E4D8')
    d.ln(x0, 32, x1, 32, 1, '#B3261E', '8 4')
    d.box(WICKET[0] + 0.06, y0, WICKET[1] - WICKET[0] - 0.12, FS - 0.1 - y0, '#DCD3C1')
    for a, b in [(x0, WICKET[0]), (WICKET[1], x1)]: d.ln(a, FS + 0.06, b, FS + 0.06, 3, C['sheet'])
    for p in (BYN[8], BYN[9], BYN[10]):
        tp = TYPES[p['t']]
        d.ring(p['x'], FS, blade(p) / 2, tp[5], 0.8, STONE if driven(p['t']) else 'none', '3 2'); d.box(p['x'] - tp[2] / 2, FS - tp[2] / 2, tp[2], tp[2], tp[5])
    kind, (x0b, x1b, _, _, dep), _ab = WICKET_NICHE
    d.box(x0b, FS + 0.07 - dep, x1b - x0b, dep, '#F2C230' if kind == 'ШГ' else '#E8E3D6', C['ink'], 0.9); d.t((x0b + x1b) / 2, FS - 0.32, kind, 9.5, 'm', C['ink'], True)
    r = WICKET[1] - WICKET[0] - 0.14; hx = WICKET[0] + 0.07
    d.ln(hx, FS, hx, FS - r, 2.4, C['wick'])
    d.add(f'<path d="M {hx + r:.3f} {FS:.3f} A {r:.3f} {r:.3f} 0 0 0 {hx:.3f} {FS - r:.3f}" style="fill:none;stroke:{C["wick"]};stroke-width:1px;vector-effect:non-scaling-stroke;stroke-dasharray:4 3"></path>')
    d.add(f'<path d="M {hx:.3f} {FS - r:.3f} A {r:.3f} {r:.3f} 0 0 0 {hx - r:.3f} {FS:.3f}" style="fill:none;stroke:#B3261E;stroke-width:1px;vector-effect:non-scaling-stroke;stroke-dasharray:2 3"></path>')
    d.box(hx - 0.05, FS - r - 0.1, 0.1, 0.06, C['ink'])
    d.t(hx + 0.08, FS - r - 0.02, 'ограничитель 90° (упор в дорожку)', 9, '', C['ink'], halo=True)
    d.t(hx - r + 0.05, FS - 0.1, f'без упора полотно ударит в {kind}' if WICKET_HITS else f'полотно не достаёт до {kind}', 9, '', '#B3261E' if WICKET_HITS else C['mu'], halo=True)
    d.dimh(x1b, hx, FS + 0.2, mm(hx - x1b), 9, above=False)
    d.t(x0 + 0.05, y0 + 0.2, 'план, калитка открывается внутрь участка', 10, '', C['mu'], True)
    return d.out(x0, y0, x1 - x0, y1 - y0, round((x1 - x0) * sc), 'flex-shrink: 0; background: #FBF9F4; border: 1px solid #D6CEBF')


def node_gate(sc=112):
    """У4: откатные ворота — вид со стороны участка (x зеркально)."""
    d = D(sc); X = lambda x: 52.0 - x
    xa, xb = X(32.2), X(20.1)
    d.box(xa, 0, xb - xa, 2.95, C['soil']); d.ln(xa, 0, xb, 0, 1.3); d.ln(xa, -Z_FRZ, xb, -Z_FRZ, 0.9, C['frz'], '6 4')
    for n in (11, 12, 13, 14, 15): draw_support(d, X(BYN[n]['x']), BYN[n]['t'])
    for x in EMB_PILES: draw_support(d, X(x), '108', head=Z_EMB, pile_only=True)
    d.box(X(EMB[1]), 0, EMB[1] - EMB[0], -Z_EMB, '#9AA0A4', C['ink'], 0.8)
    for a, b in [(20.1, GATE[0]), (GATE[1], FR)]:
        for z in Z_LAG: d.box(X(b), -(z + 0.02), b - a, 0.04, C['lag'], C['ink'], 0.4)
        d.box(X(b), -Z_S1, b - a, Z_S1 - Z_S0, C['sheet'], op=0.10)
    # полотно (закрыто): рама, противовес-ферма, нижняя балка
    L0, L1 = LEAF_CLOSED; B0 = GATE[0] - 0.1
    d.box(X(L1), -Z_S1, L1 - B0, Z_S1 - Z_S0, C['sheet'], op=0.25)
    d.box(X(L1), -Z_S1, L1 - B0, Z_S1 - Z_S0, 'none', C['gate'], 2.4)
    for k in range(1, 3): d.ln(X(B0 + k * (L1 - B0) / 3), -Z_S1, X(B0 + k * (L1 - B0) / 3), -Z_S0, 1.2, C['gate'])
    d.ln(X(L1), -1.15, X(B0), -1.15, 1.2, C['gate'])
    d.pln([(X(L0), -0.14), (X(B0), -0.14), (X(B0), -Z_S1), (X(L0 + 0.25), -0.3), (X(L0), -0.14)], 2, C['gate'])
    d.ln(X(L0), -0.13, X(L1), -0.13, 3.2, C['gate'])
    for x in CARR: d.box(X(x) - 0.13, -0.12, 0.26, 0.12, C['gate'], C['ink'], 0.6)
    d.box(X(L0) - 0.05, -0.2, 0.1, 0.1, C['ink'])                                           # концевой ролик
    d.box(X(GATE[0]) - 0.06, -(Z_TOPV - 0.02), 0.2, 0.16, C['gate'], C['ink'], 0.6)         # верхние ролики
    d.box(X(GATE[1]) - 0.1, -0.3, 0.12, 0.2, C['gate'], C['ink'], 0.6)                      # нижний улавливатель
    d.box(X(GATE[1]) - 0.1, -(Z_S1 + 0.02), 0.12, 0.16, C['gate'], C['ink'], 0.6)           # верхний улавливатель
    d.ln(X(L0), -0.26, X(L1), -0.26, 1, C['gate'], '2 2')                                   # зубчатая рейка (опция)
    for n, (x, y, tx, ty) in enumerate([(X(CARR[0]), -0.06, X(CARR[0]) + 0.35, -0.5), (X(L0), -0.15, X(L0) + 0.35, -0.55),
                                         (X(GATE[1]) - 0.04, -0.2, X(GATE[1]) - 0.4, -0.55), (X(GATE[1]) - 0.04, -(Z_S1 + 0.06), X(GATE[1]) - 0.4, -2.5),
                                         (X(GATE[0]) + 0.1, -(Z_TOPV + 0.06), X(GATE[0]) + 0.45, -2.62), (X(sum(EMB) / 2), 0.08, X(sum(EMB) / 2) + 0.3, 0.55),
                                         (X(L0 + 0.8), -0.62, X(L0 + 0.8) + 0.3, -1.0), (X(L0 + 2.5), -0.26, X(L0 + 2.5) + 0.3, -0.62)], 1):
        callout(d, x, y, tx, ty, n, C['gate'])
    for n in (11, 12, 13, 14, 15):
        p = BYN[n]; d.tag(X(p['x']), -(Z_TOPV + 0.62), str(n), 9, TYPES[p['t']][5], 9)
    for n, x in zip(EMB_N, EMB_PILES): d.tag(X(x), 0.62, str(n), 9, C['gate'], 9)
    xs = [X(BYN[n]['x']) for n in (11, 12, 13, 14, 15)]
    d.chainh(xs, -(Z_TOPV + 0.95), 9, 18)
    d.chainh([X(EMB[1]), X(EMB_PILES[1]), X(EMB_PILES[0]), X(EMB[0])], 2.85, 9, 18, above=False)
    d.chainh([X(GATE[1]), X(GATE[0]), X(L0)], -(Z_TOPV + 0.3), 9, 18)
    for z in (Z_TOPV, Z_S1, 0, Z_EMB, Z_FRZ, Z_HEAD - 2.5, Z_EMB - 2.5): d.mark(xa + 0.55, z, zf(z), 9)
    d.t(X(26.2), 2.8, 'вид со стороны участка, ворота закрыты', 10, 'm', C['mu'], True)
    return d.out(xa, -(Z_TOPV + 1.25), xb - xa, Z_TOPV + 1.25 + 3.1, round((xb - xa) * sc), 'flex-shrink: 0; background: #FBF9F4; border: 1px solid #D6CEBF')

WICKET_ITEMS = ['Петли усиленные, 2 шт, на столбе 9 (+0,400 и +1,900)', 'Замок накладной, ручка +1,000', 'Ответная планка на столбе 10',
                'Упор-притвор на столбе 10 — полотно открывается только внутрь', 'Рама 40×40×2, ригель и раскос 40×20, обшивка С8 0,4', 'Свая СВС-89×2500 под каждым столбом калитки']
GATE_ITEMS = ['Роликовые опоры, 2 шт, на закладной', 'Концевой ролик нижней балки', 'Нижний улавливатель на столбе 14', 'Верхний улавливатель на столбе 14',
              'Верхние направляющие ролики на столбе 13', 'Закладная — швеллер 16П 2 000 полками вниз на сваях 54 и 55, верх ±0,000',
              'Противовес 1 600 (ферма из трубы 60×40)', 'Зубчатая рейка — под привод (опция)']


def node_niches(sc=130, which=None):
    """У5: ниши шкафов ВРУ и ШГ в линии забора — вид с улицы. which — ниши на одном виде (по умолчанию все)."""
    ns = [v for v in NICHES if which is None or v[0] in which]
    posts = sorted({n for v in ns for n in v[2]})
    last = BYN[posts[-1]]
    d = D(sc); xa, xb = BYN[posts[0]]['x'] - 0.75, last['x'] + 0.55
    d.box(xa, 0, xb - xa, 2.2, C['soil']); d.ln(xa, 0, xb, 0, 1.3); d.ln(xa, -Z_FRZ, xb, -Z_FRZ, 0.9, C['frz'], '6 4')
    for n in posts: draw_support(d, BYN[n]['x'], BYN[n]['t'])
    draw_frame(d, xa, last['x'] if last['n'] in SPECIAL else xb, cut=[v[1][:4] for v in ns])
    for s_, (x0, x1, z0, z1, dep), _ab in ns:
        fill = '#F2C230' if s_ == 'ШГ' else '#E8E3D6'
        for x in (x0 - 0.02, x1 + 0.02): d.box(x - 0.02, -(Z_LAG[1] - 0.02), 0.04, Z_LAG[1] - Z_LAG[0] - 0.04, '#9AA0A4', C['ink'], 0.6)   # стойки 40×40
        for z in (z0 - 0.02, z1 + 0.02): d.box(x0 - 0.04, -(z + 0.02), x1 - x0 + 0.08, 0.04, '#9AA0A4', C['ink'], 0.6)                    # ригели 40×40
        d.box(x0 + 0.01, -z1 + 0.01, x1 - x0 - 0.02, z1 - z0 - 0.02, fill, C['ink'], 1.2)
        d.t((x0 + x1) / 2, -(z0 + 0.12), s_, 11, 'm', C['ink'], True)
        if s_ == 'ВРУ':
            d.box(VRU[0] - 0.14, -(z0 + 0.45), 0.28, 0.14, '#FFFFFF', C['ink'], 0.8); d.t(VRU[0], -(z0 + 0.35), 'окно счётчика', 8.5, 'm', C['mu'])
            d.ln(VRU[0], -z0, VRU[0], 0.7, 2.2, C['el'], '6 3'); d.ring(VRU[0], 0.7, 0.05, C['el'], 1.6, '#FFFFFF')
            d.t(VRU[0] + 0.1, 0.62, 'кабель в гофре Ø63 до −0,70: с улицы — ввод, в участок — к ЩР-Д' if len(ns) > 1 else 'кабель в гофре Ø63 до −0,70', 9, '', C['el'], halo=True)
            d.dimv(x0 - 0.12, -z1, -z0, '650', 9); d.dimv(x0 - 0.12, -z0, 0, '900', 9)
        else:
            for k in range(5): d.ln(x0 + 0.12, -(z1 - 0.12 - k * 0.05), x1 - 0.12, -(z1 - 0.12 - k * 0.05), 0.8)
            for dx in (-0.1, 0.1):
                d.ln(SHG[0] + dx, -z0, SHG[0] + dx, -G1_DEPTH, 2.4, C['gas']); d.box(SHG[0] + dx - 0.03, -0.25, 0.06, 0.5, 'none', C['ink'], 0.8)
            d.ring(SHG[0], -G1_DEPTH, 0.05, C['gas'], 1.6, '#FFFFFF')
            d.t(SHG[0] + 0.18, -G1_DEPTH - 0.1, 'ввод от сети ГРО и выход Г1 на −1,55; футляры на выходе из земли' if len(ns) > 1 else 'ввод ГРО и Г1, −1,55', 9, '', C['gas'], halo=True)
            d.dimv(x1 + 0.12, -z1, -z0, '800', 9, left=False); d.dimv(x1 + 0.12, -z0, 0, '600', 9, left=False)
    d.chainh(sorted([BYN[n]['x'] for n in posts] + [e for v in ns for e in v[1][:2]]), -(Z_TOP + 0.25), 9, 18)
    if len(ns) > 1 and ADJ:
        d.dimh(ns[0][1][1], ns[1][1][0], -(Z_TOP + 0.55), f'между шкафами {mm(ns[1][1][0] - ns[0][1][1])}', 9)
    for n in posts: d.tag(BYN[n]['x'], -(Z_TOP + 0.85), str(n), 9, TYPES[BYN[n]['t']][5], 9)
    zs = [Z_TOP, Z_LAG[1]] + [v[1][3] for v in ns] + [v[1][2] for v in ns] + [Z_LAG[0], 0]
    if len(ns) > 1: zs = [Z_TOP, Z_LAG[1], VRU_BOX[3], SHG_BOX[3], VRU_BOX[2], SHG_BOX[2], Z_LAG[0], 0]
    for z in zs: d.mark(xa + 0.48, z, zf(z), 9)
    d.t((xa + xb) / 2, 2.1, 'вид с улицы · шкафы дверцами на улицу, корпус — внутри участка' if len(ns) > 1 else 'вид с улицы · дверцей на улицу', 10, 'm', C['mu'], True)
    return d.out(xa, -(Z_TOP + 1.12), xb - xa, Z_TOP + 1.12 + 2.25, round((xb - xa) * sc), 'flex-shrink: 0; background: #FBF9F4; border: 1px solid #D6CEBF')


def node_piles(sc=112):
    """У6: основания опор — столб в лунке со щебнем (А, У) и винтовые сваи калитки и ворот."""
    d = D(sc); keys = ['89', '108']
    xs = [1.75, 2.95]
    d.box(-0.1, 0, 3.75, 3.05, C['soil']); d.ln(-0.1, 0, 3.65, 0, 1.3); d.ln(-0.1, -Z_FRZ, 3.65, -Z_FRZ, 0.9, C['frz'], '6 4')
    x = 0.55                                                     # столб А, У: только подземная часть
    d.box(x - HOLE_D / 2, 0, HOLE_D, -Z_HOLE, STONE, C['ink'], 0.6, '3 2')
    for k in range(int(-Z_HOLE / 0.1)):
        for dx in ((-0.065, 0.065) if k % 2 else (-0.045, 0.045)): d.dot(x + dx, 0.05 + k * 0.1, 1.4, '#8C8373')
    d.box(x - 0.03, -0.12, 0.06, 0.12 - Z_DRV, BITUM, C['ink'], 0.6)
    d.t(x, -0.28, 'столб 60×60×2 (А, У)', 10, 'm', C['ink'], True)
    d.t(x, -0.12 - 0.02, 'забивка в лунку со щебнем', 9, 'm', C['mu'])
    d.dimv(x - 0.2, 0, -Z_HOLE, mm(-Z_HOLE), 9); d.dimv(x - 0.33, 0, -Z_DRV, mm(-Z_DRV), 9)
    d.dimh(x - HOLE_D / 2, x + HOLE_D / 2, -Z_DRV + 0.12, f'лунка Ø{mm(HOLE_D)}', 9, above=False)
    d.t(1.15, -Z_FRZ - 0.05, 'промерзание −1,400', 8.5, 'm', C['frz'])
    for k, x in zip(keys, xs):
        P = PILES[k]; tip = -P['L']
        d.box(x - P['d'] / 2, 0, P['d'], P['L'] - 0.1, C['pile'], C['ink'], 0.6)
        d.poly([(x - P['d'] / 2, -(tip + 0.1)), (x + P['d'] / 2, -(tip + 0.1)), (x, -tip)], C['pile'], C['ink'], 0.6)
        d.poly([(x - P['blade'] / 2, -(tip + 0.2)), (x + P['blade'] / 2, -(tip + 0.26)), (x + P['blade'] / 2, -(tip + 0.28)), (x - P['blade'] / 2, -(tip + 0.22))], C['blade'], C['ink'], 0.6)
        d.box(x - P['plate'] / 2, -0.01, P['plate'], 0.01, C['ink'])
        d.t(x, -0.28, P['name'], 10, 'm', C['ink'], True)
        d.t(x, -0.12, f'оголовок {mm(P["plate"])}×{mm(P["plate"])}×{mm(P["pt"])}', 9, 'm', C['mu'])
        d.dimv(x - 0.2, 0, -tip, mm(P['L']), 9)
        d.dimh(x - P['blade'] / 2, x + P['blade'] / 2, -tip + 0.12, f'Ø{mm(P["blade"])}', 9, above=False)
        d.t(x + 0.08, 1.0, f'Ø{mm(P["d"])}×{P["wall"]}', 9, '', C['ink'], mono=True, halo=True)
    d.t(2.35, 2.98, 'сваи калитки и ворот: длина — от верха оголовка до острия', 9, 'm', C['mu'])
    return d.out(-0.1, -0.45, 3.75, 3.5, round(3.75 * sc), 'flex-shrink: 0; background: #FBF9F4; border: 1px solid #D6CEBF')


def typical_section(sc=101):
    """Типовая секция: 2 пролёта боковой стороны, вид со стороны участка."""
    d = D(sc); st = (FS - FB) / N_SIDE
    xs = [0, st, 2 * st]; xa, xb = -1.05, 2 * st + 0.9
    draw_ground(d, xa, xb, -2.3)
    for x in xs: draw_support(d, x, 'А')
    draw_frame(d, xs[0], xs[-1])
    d.chainh(xs, -(Z_TOP + 0.3), 9.5, 20)
    for n, (x, y, tx, ty) in enumerate([(xs[1], -1.2, xs[1] + 0.35, -1.45), (xs[1] + 0.8, -Z_LAG[1], xs[1] + 1.1, -2.05),
                                         (0.6, -1.0, 0.95, -1.3), (xs[1] + 0.07, 0.35, xs[1] + 0.45, 0.35), (xs[1], 1.0, xs[1] + 0.4, 1.0),
                                         (xs[1] + 0.03, -0.06, xs[1] + 0.4, -0.55), (xs[2], -(Z_TOP + 0.005), xs[2] - 0.35, -2.5)], 1):
        callout(d, x, y, tx, ty, n)
    for z in (Z_TOP, Z_S1, Z_LAG[1], Z_LAG[0], Z_S0, 0, Z_HOLE, Z_DRV): d.mark(xa + 0.55, z, zf(z), 9)   # промерзание — подписанная линия
    d.t(xs[2] + 0.5, -Z_FRZ - 0.06, 'промерзание', 9, 'm', C['frz'])
    return d.out(xa, -(Z_TOP + 0.55), xb - xa, Z_TOP + 0.55 + 2.3, round((xb - xa) * sc), 'flex-shrink: 0; background: #FBF9F4; border: 1px solid #D6CEBF')


SECTION_ITEMS = [f'Столб 60×60×2, L = {mm(post_len("А"))}: верх +2,200 с заглушкой, низ {zf(Z_DRV)}', 'Лаги 40×20×1,5 в 2 ряда (+0,450 и +1,850), сварка к столбам с уличной стороны',
                 'Профлист С8 0,4 RAL 6005, лист 1 200 × 2 000, низ +0,150, П-планка сверху', 'Лунка Ø200 мотобуром на 0,8 м, засыпка щебнем 20–40 с трамбовкой слоями по 0,2 м',
                 f'Столб забит ещё на {nf(Z_HOLE - Z_DRV, 1)} м ниже дна лунки — в нетронутый грунт, до {zf(Z_DRV)}, ниже промерзания', 'Подземная часть столба — битумная мастика в 2 слоя до +0,150', 'Шаг опор по осям — 2 446 (улица — 1 900…2 500)']


def legend_list(items, c=C['ink'], start=1):
    return '<div style="display: flex; flex-direction: column; gap: 5px">' + ''.join(
        f'<div style="display: flex; gap: 8px; align-items: flex-start"><div class="mono" style="flex-shrink: 0; width: 18px; height: 18px; border-radius: 9px; background: {c}; color: #FFFFFF; font-size: 10.5px; font-weight: 600; display: flex; align-items: center; justify-content: center">{i}</div><div style="font-size: 12px; line-height: 1.4">{t}</div></div>'
        for i, t in enumerate(items, start)) + '</div>'


def types_table():
    rows = []
    for t, (what, sec, w, top, pk, col_) in TYPES.items():
        n = sum(1 for p in SUP if p['t'] == t)
        nums = ', '.join(str(p['n']) for p in SUP if p['t'] == t) if n <= 4 else 'остальные'
        sw = f'<span style="display: inline-block; width: 10px; height: 10px; background: {col_}; margin-right: 6px"></span>'
        rows.append(f'<tr><td>{sw}{t}</td><td>{what}<br><span style="color: #565C61">{nums}</span></td><td class="r">{n}</td><td>{base_name(t)}</td><td class="r">{zf(base_bottom(t))}</td><td>{sec}, L {mm(post_len(t))}</td><td class="r">{zf(top)}</td></tr>')
    P = PILES['108']
    rows.append(f'<tr><td>закл.</td><td>сваи закладной ворот<br><span style="color: #565C61">54, 55</span></td><td class="r">2</td><td>{P["name"]}</td><td class="r">{zf(Z_EMB - P["L"])}</td><td>швеллер 16П 2 000</td><td class="r">{zf(0)}</td></tr>')
    return ('<table class="tb"><thead><tr><th>Тип</th><th>Опора</th><th class="r">Шт</th><th>Основание</th><th class="r">Низ</th><th>Столб</th><th class="r">Верх</th></tr></thead><tbody>'
            + ''.join(rows) + f'<tr class="sum"><td></td><td>Всего опор и свай</td><td class="r">{len(SUP) + len(EMB_PILES)}</td><td colspan="4"></td></tr></tbody></table>')


def schedule(rows_):
    out = ['<table class="tb"><thead><tr><th class="r">№</th><th>Тип</th><th class="r">x, м</th><th class="r">y, м</th><th>Основание</th><th class="r">Низ</th><th>Примечание</th></tr></thead><tbody>']
    for p in rows_:
        if p['t'] in TYPES:
            name, bot = ('лунка Ø200, щебень' if driven(p['t']) else base_name(p['t'])), base_bottom(p['t'])
        else:
            name, bot = PILES['108']['name'], Z_EMB - PILES['108']['L']
        out.append(f'<tr><td class="r">{p["n"]}</td><td>{p["t"]}</td><td class="r">{nf(p["x"], 3)}</td><td class="r">{nf(p["y"], 3)}</td><td>{name}</td><td class="r">{zf(bot)}</td><td style="font-size: 11.5px">{"; ".join(p["note"])}</td></tr>')
    return ''.join(out) + '</tbody></table>'


def all_rows():
    return SUP + [dict(n=n, t='закл.', x=x, y=LEAF_Y, note=['свая закладной ворот', 'швеллер 16П полками вниз, верх ±0,000']) for n, x in zip(EMB_N, EMB_PILES)]


def crossings_table():
    groups = [(None, [(f'{name}: {who}', f'≥ {nf(need, 1)}', nf(dd, 2), dd >= need - 1e-6, why) for name, who, dd, need, why in util_checks()])]
    return check_table(groups, 'Сеть — ближайшая опора (в свету от лунки или лопасти), м')


def runs_table():
    rows = ''.join(f'<tr><td>{r["name"]}</td><td class="r">{nf(r["len"], 2)}</td><td class="r">{r["spans"]}</td><td class="r">{r["sheets"]}</td></tr>' for r in RUNS)
    c = calc()
    return ('<table class="tb"><thead><tr><th>Участок (опоры)</th><th class="r">По осям, м</th><th class="r">Пролётов</th><th class="r">Листов</th></tr></thead><tbody>'
            + rows + f'<tr class="sum"><td>Итого</td><td class="r">{nf(c["L"], 2)}</td><td class="r">{sum(r["spans"] for r in RUNS)}</td><td class="r">{c["sheets"]}</td></tr></tbody></table>')


def spec_html():
    c = calc(); out = ['<table class="tb"><thead><tr><th>№</th><th>Наименование</th><th>Ед.</th><th class="r">Кол-во</th><th class="r">Цена, ₽</th><th class="r">Сумма, ₽</th></tr></thead><tbody>']
    n = 0; tot = 0
    def qf(v): return str(int(v)) if float(v).is_integer() else (nf(v, 1) if rnd(v, 1) == v else nf(v, 2))
    for g, items in [('Материалы', c['mats']), ('Работы', c['works'])]:
        out.append(f'<tr class="grp"><td colspan="6">{g}</td></tr>'); sub = 0
        for name, unit, q, price in items:
            n += 1; sm = rnd(q * price); sub += sm
            out.append(f'<tr><td>{n}</td><td>{name}</td><td>{unit}</td><td class="r">{qf(q)}</td><td class="r">{fmt(price) if float(price).is_integer() else nf(price, 1)}</td><td class="r">{fmt(sm)}</td></tr>')
        out.append(f'<tr class="sum"><td></td><td>Итого {g.lower()}</td><td></td><td></td><td></td><td class="r">{fmt(sub)}</td></tr>'); tot += sub
    out.append(f'<tr class="tot"><td></td><td>Всего по забору</td><td></td><td></td><td></td><td class="r">{fmt(tot)}</td></tr></tbody></table>')
    return ''.join(out)


def wind_table():
    w = wind()
    rows = [('Ветровое давление на глухой забор (I район, местность B, c = 1,4, γf = 1,4)', f'{nf(w["w"], 3)} кПа'),
            (f'Нагрузка на столб: пролёт {mm(w["step"])} × лист 2,0 м', f'{nf(w["F"], 2)} кН'),
            (f'Момент у земли, плечо {nf(w["arm"], 2)} м', f'{nf(w["M"], 2)} кН·м'),
            (f'Столб 60×60×2 (W = {nf(w["W60"], 2)} см³): напряжение ≤ 230 МПа', f'{nf(w["s60"], 0)} МПа'),
            (f'Столб в грунте, {nf(-Z_DRV, 1)} м: предельная горизонтальная сила (Broms, cu = {nf(w["cu"], 0)} кПа, щебень в запас)', f'{nf(w["Hu"], 1)} кН · запас {nf(w["kH"], 1)}'),
            (f'Лага 40×20×1,5 (W = {nf(w["Wl"], 2)} см³), пролёт {mm(w["step"])}: напряжение ≤ 230 МПа', f'{nf(w["sl"], 0)} МПа')]
    return '<table class="tb"><tbody>' + ''.join(f'<tr><td>{a}</td><td class="r">{b}</td></tr>' for a, b in rows) + '</tbody></table>'


def _clear(p):
    return min(poly_d((p['x'], p['y']), pts) - blade(p) / 2 for name, short, pts, z, need, why in UTIL)


NEAR_DRV = [p['n'] for p in SUP if driven(p['t']) and _clear(p) < 1.1]      # лунки — ручным ямобуром после шурфа
NEAR_PILE = [p['n'] for p in SUP if not driven(p['t']) and _clear(p) < 1.1]  # сваи — вручную после шурфа
def ranges(ns):
    """[2, 4, 5, 19, 20, 21] → «2, 4, 5, 19–21»"""
    out, run = [], []
    for n in ns + [None]:
        if run and (n is None or n != run[-1] + 1):
            out.append(f'{run[0]}–{run[-1]}' if len(run) > 2 else ', '.join(map(str, run))); run = []
        if n is not None: run.append(n)
    return ', '.join(out)


_ut = {r[0]: r[2] for r in util_checks()}
_cl = [v for k, v in _ut.items() if k.startswith('Кабель ВРУ') or k.startswith('Газопровод')]
MONTAGE = [
    f'<b>Разбивка.</b> Вызвать трассоискатель, отметить вешками сети у забора: выпуск ЛОС (x = 2,6), кабель ВРУ (x = {nf(VRU[0], 1 if round(VRU[0], 1) == VRU[0] else 3)}), газ (x = {nf(SHG[0], 3 if round(SHG[0], 2) != SHG[0] else 2)}), В1 к соседу (y = 21,0), В1 в баню (0,9 м от правой линии). Вынести ось забора в 0,1 м от границы и все 55 точек по ведомости (лист 02.1).',
    f'<b>Столбы А и У (49 шт).</b> Подземную часть ({nf(Z_S0 - Z_DRV, 2)} м от низа) заранее покрыть битумной мастикой в 2 слоя. Лунка Ø200 мотобуром на 0,8 м; у сетей (опоры {ranges(NEAR_DRV)}) — ручным ямобуром после шурфа до сети.',
    f'<b>Забивка.</b> Столб поставить в лунку, забить гидромолотом (или кувалдой) через оголовник ещё на {nf(Z_HOLE - Z_DRV, 1)} м — до {zf(Z_DRV)} (верх +2,200 по шнуру). Вертикаль — 3 мм на 2 м, ось вдоль линии ±20 мм, поперёк ±10 мм.',
    '<b>Щебень</b> 20–40 засыпать слоями по 0,2 м, каждый слой трамбовать ручной трамбовкой до отказа, выверяя столб; верх засыпки — вровень с землёй, с уклоном от столба.',
    f'<b>Калитка и ворота (6 свай).</b> Пробное закручивание: момент — по паспорту сваи; вертикальность ±1°. Обрезка по нивелиру: оголовки +0,100, у закладной −0,160; столбы 80×80 — на оголовки, сварка по контуру, верх ворот +2,350. {("Сваи " + ranges(NEAR_PILE) + " и у закладной") if NEAR_PILE else "Сваи у закладной"} — вручную после шурфа.',
    '<b>Лаги</b> 40×20×1,5 в 2 ряда (+0,450 и +1,850) с уличной стороны столбов, стыки лаг — только на столбах; сварка короткими швами (стенка 1,5 мм — без прожогов), окраска 2 слоя.',
    '<b>Ниши ВРУ и ШГ:</b> обрамление 40×40, шкафы дверцами на улицу; газовый шкаф и врезку делает организация с допуском по ТУ.',
    '<b>Профлист</b> С8 0,4 — саморезами по 6 шт на лист на лагу (через волну, в нижнюю полку), нахлёст в одну волну, П-планка сверху, уголки на углах и по краям ниш.',
    '<b>Ворота:</b> закладную 16П приварить к оголовкам свай 54, 55 (горизонт ±2 мм, верх ±0,000), роликовые опоры, полотно, улавливатели, регулировка. <b>Калитка:</b> петли на столбе 9, замок, упор, ограничитель 90°.',
]


# ================= листы =================
BOX = 'display: flex; flex-direction: column; gap: 2px; padding: 12px 14px; background: #FBF9F4; border: 1px solid #D6CEBF'


def kpi(v, s):
    return f'<div style="{BOX}"><div class="mono" style="font-size: 24px; font-weight: 500">{v}</div><div style="font-size: 12px; color: #565C61">{s}</div></div>'


def small(t):
    return f'<div style="font-size: 12px; line-height: 1.45; color: #565C61">{t}</div>'


H = {'Fence.dc.html': 2220, 'FencePlan.dc.html': 3270, 'FenceElev.dc.html': 2280, 'FenceNodes.dc.html': 3710}


def boards():
    c = calc(); m, w, tot = cost(); n_all = len(SUP) + len(EMB_PILES)
    out = {}
    # ---------- 02 ----------
    wd = wind()
    body = header('Забор из профлиста С8',
                  f'Периметр участка 32 × 32 м, ось опор — в 0,1 м внутрь от границы. {c["n60"]} рядовых и угловых столбов — забивка в пробуренную лунку со щебнем, без бетона; винтовые сваи — только под калиткой и откатными воротами. Лаги 40×20×1,5, профлист С8 0,4. Ниши под ВРУ и газовый шкаф. Сборочные чертежи — листы 02.1–02.3.', '02')
    body += '<div style="display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px">' + kpi(f'{nf(c["L"], 1)} м', 'длина забора по осям опор, без проёмов') + \
        kpi(f'{c["n60"]} + {c["p89"] + c["p108"]}', f'столбов в лунках со щебнем + винтовых свай (СВС-89 — {c["p89"]}, СВС-108 — {c["p108"]})') + \
        kpi(str(c['sheets']), f'листов профнастила, {nf(c["area"], 1)} м²') + kpi(f'{fmt(tot / c["L"])} ₽', 'за погонный метр, всё включено') + \
        kpi(f'{fmt(tot)} ₽', 'итого: материалы и работы') + '</div>'
    left = h2('Типовая секция · вид со стороны участка') + typical_section() + legend_list(SECTION_ITEMS) + \
        h2('Участки забора', '6px 0 0') + runs_table() + h2('Типы опор', '6px 0 0') + types_table() + \
        h2('Проверка столба и лаги на ветер', '6px 0 0') + wind_table() + \
        small(f'СП 20.13330.2016: w₀ = 0,23 кПа, k(z ≤ 5 м, B) = 0,5. Запас по напряжениям в столбе — {nf(230 / wd["s60"], 1)} раза, в лаге 40×20×1,5 — {nf(230 / wd["sl"], 1)} раза. '
              'Столб в грунте — по Бромсу для короткой сваи в суглинке, без учёта щебня; сваи калитки и ворот проверяются пробным закручиванием.')
    right = h2('Решения') + notes([
        f'1. <b>Рядовые и угловые столбы ({c["n60"]} шт)</b> — без бетона: лунка Ø200 мотобуром на 0,8 м, столб 60×60×2 длиной {mm(post_len("А"))} забивается ещё на {nf(Z_HOLE - Z_DRV, 1)} м в нетронутый грунт (низ {zf(Z_DRV)}), лунка засыпается щебнем 20–40 с трамбовкой слоями. Подземная часть — битумная мастика в 2 слоя.',
        f'2. <b>Ниже промерзания.</b> Низ столбов {zf(Z_DRV)} — на {nf(Z_FRZ - Z_DRV, 1)} м ниже нормативной глубины промерзания 1,4 м: столб опирается на непромерзающий грунт, морозное пучение его не выталкивает. Щебень дренирует лунку и снижает касательные силы пучения, мастика — сцепление мёрзлого грунта со столбом. Столб {mm(post_len("А"))} — из хлыста 12 м их выходит 3 шт, как и при 3 400.',
        f'3. <b>Винтовые сваи — только калитка и ворота:</b> СВС-89×2500 под столбы калитки 80×80×3, СВС-108×2500 под столбы ворот и закладную — там нагрузка от полотна и движения. Оголовки на +0,100, у закладной — на −0,160.',
        '4. <b>Лаги 40×20×1,5 и профлист С8 0,4</b> — легче прежних 40×20×2 и С20 0,45; на ветер проходят с запасом (таблица слева). Лист С8 — 1 200 × 2 000, полезная ширина 1,15 м.',
        '5. <b>Разбивка опор</b> — по ведомости с координатами (лист 02.1): на улице пролёты подобраны так, чтобы лунки и сваи не попадали на выпуск ЛОС, кабель ВРУ и газ; на боковых и тыльной сторонах — по 13 пролётов 2 446 мм.',
        '6. <b>Калитка</b> — между воротами и газовым шкафом (оси 18,0–19,0), напротив дорожки к крыльцу; открывается внутрь, ограничитель 90° не даёт полотну ударить в ШГ.' if WICKET_HITS and WICKET_NICHE[0] == 'ШГ' else
        f'6. <b>Калитка</b> — оси 18,0–19,0, правее ниши {WICKET_NICHE[0]}, напротив дорожки к крыльцу; открывается внутрь, ограничитель 90° держит полотно у дорожки.',
        '7. <b>Откатные ворота</b> 4,0 м (оси 26,5–30,5): полотно 4,1 м с противовесом 1,6 м откатывается влево по участку, зона отката 7,5 м до калитки свободна; закладная — на двух сваях, без бетонного ростверка.',
        f'8. <b>ВРУ и ШГ</b> встроены в линию забора: шкафы дверцами на улицу, корпус внутри участка, между шкафами {nf(NICHE_GAP, 1)} м. Кабель и газ выходят в пролётах, в {nf(min(_cl), 1)}–{nf(max(_cl), 1)} м от лунок и лопастей свай.',
        '9. Глухой забор 2 м по границам с соседями — по ПЗЗ Чеховского г. о. и согласованию с соседями (проверить допустимую высоту).',
    ]) + h2('Спецификация и стоимость', '6px 0 0') + spec_html() + small('Цены ориентировочные: розница Московской обл., сентябрь 2026. Лист С8 — ширина 1,20 м, полезная 1,15 м. Сваи калитки и ворот — с заводским антикоррозийным покрытием и оголовком. Обшивка ворот и калитки — тем же С8 0,4, цена комплектов прежняя.')
    body += row(col(left, 12, 'width: 700px; flex-shrink: 0') + col(right, 12, 'flex-grow: 1; min-width: 0'))
    out['Fence.dc.html'] = page('Забор из профлиста', 1440, H['Fence.dc.html'], body)
    # ---------- 02.1 ----------
    body = header('Забор · план опор и ведомость', f'Разбивка всех {n_all} опор и свай с координатами, привязки к сетям и сооружениям. x — от левой границы, y — от тыльной границы (угол н2), м.', '02.1')
    lg = ''.join(f'<div style="display: flex; gap: 8px; align-items: center; font-size: 12px"><span style="width: 14px; height: 14px; background: {c_}; flex-shrink: 0"></span>{t}</div>'
                 for c_, t in [(TYPES['А'][5], f'опоры типов А и У: столб 60×60×2 в лунке Ø200 со щебнем, забит до {zf(Z_DRV)}'), (TYPES['К'][5], 'опоры калитки К: столб 80×80×3 на СВС-89'),
                               (TYPES['В1'][5], 'опоры ворот В1, В2 и сваи закладной 54, 55: СВС-108'), (C['sheet'], 'линия профлиста — с уличной (наружной) стороны опор'),
                               ('#B3261E', 'граница участка (пунктир)')])
    right = h2('Обозначения') + col(lg, 6) + small('Кружок пунктиром — лунка Ø200 (А, У) или лопасть сваи (К, В) в масштабе. Номер опоры — снаружи линии забора. Цепочки размеров — между осями опор, мм.') + \
        h2('Расстояния до сетей и сооружений', '6px 0 0') + crossings_table() + \
        small('Проверено для каждой из 55 опор и свай; в таблице — ближайшая к каждой сети. Лунки и сваи рядом с сетями — бурить и закручивать вручную после шурфа.')
    body += row(col(h2('План забора') + site_plan(), 10, 'width: 890px; flex-shrink: 0') + col(right, 10, 'flex-grow: 1; min-width: 0'))
    body += col(h2('Уличный забор крупно · опоры 1–9') + street_plan(-0.9, 18.2) + h2('Уличный забор крупно · опоры 8–15, ворота и калитка') + street_plan(13.9, 33.0), 10)
    rows_ = all_rows(); half = 27
    body += col(h2('Ведомость опор и свай') + row(col(schedule(rows_[:half]), 0, 'flex: 1; min-width: 0') + col(schedule(rows_[half:]), 0, 'flex: 1; min-width: 0'), 20) +
                small('Отметки — от уровня земли у опоры. Низ: для столбов А и У — низ забитого столба, для свай — острие наконечника. Примечание к опоре — ближайшие сети в свету от лунки или лопасти, м.'), 10)
    out['FencePlan.dc.html'] = page('Забор: план опор', 1440, H['FencePlan.dc.html'], body)
    # ---------- 02.2 ----------
    body = header('Забор · развёртки по сторонам', 'Каждая опора в масштабе: столб в лунке со щебнем или свая с оголовком (калитка, ворота), лаги; профлист показан условно, полупрозрачным. Отметки от уровня земли, размеры между осями опор, мм.', '02.2')
    body += h2('Уличный забор · вид с улицы · опоры 1–8') + elevation('street', -1.9, 17.2, 71.1, zmax=3.75, zmin=-3.35)
    body += h2('Уличный забор · опоры 8–15: калитка, зона отката, ворота (противовес за забором — пунктир)') + elevation('street', 14.75, 33.0, 71.1, zmax=3.75, zmin=-3.35)
    for side in ('right', 'back', 'left'):
        body += h2(SIDE_NAME[side]) + elevation(side, -2.1, 33.9, 37.7, zmax=2.95, zmin=-2.75)
    body += small(f'Столбы А и У: лунка Ø200 до −0,800 со щебнем (штриховка), столб забит до {zf(Z_DRV)} — ниже промерзания, подземная часть в мастике (тёмная); СВС-89×2500 и СВС-108×2500 у калитки и ворот — низ −2,400; сваи закладной 54, 55 — низ −2,660. Промерзание −1,400 (синий пунктир). Сети, пересекающие линию забора, — кружками на своей глубине.')
    out['FenceElev.dc.html'] = page('Забор: развёртки', 1440, H['FenceElev.dc.html'], body)
    # ---------- 02.3 ----------
    body = header('Забор · узлы', 'Опора в лунке со щебнем, угол, калитка и откатные ворота на винтовых сваях, закладная без бетона, ниши ВРУ и ШГ, основания опор. Порядок монтажа и допуски.', '02.3')
    body += row(col(h2('Узел 1 · опора типа А: лунка со щебнем, забивка') + node_post(), 10, 'flex-shrink: 0') + col(h2('Узел 2 · угловая опора (н1), план') + node_corner(), 10, 'flex-shrink: 0'), 24)
    body += row(col(h2('Узел 3 · калитка') + node_wicket(125), 10, 'flex-shrink: 0') + col(h2('Калитка в плане') + node_wicket_plan() + legend_list(WICKET_ITEMS, C['wick']), 10, 'flex-grow: 1; min-width: 0'), 24)
    body += col(h2('Узел 4 · откатные ворота на закладной и сваях') + node_gate() +
                '<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 24px">' + legend_list(GATE_ITEMS[:4], C['gate']) +
                legend_list(GATE_ITEMS[4:], C['gate'], 5) + '</div>', 10)
    if ADJ:
        body += row(col(h2('Узел 5 · ниши ВРУ и ШГ') + node_niches(), 10, 'flex-shrink: 0') + col(h2('Узел 6 · основания опор') + node_piles(), 10, 'flex-shrink: 0'), 24)
    else:
        body += row(''.join(col(h2(f'Узел 5{"а" if k else ""} · ниша {v[0]}, пролёт {v[2][0]}–{v[2][1]}') + node_niches(which=(v[0],)), 10, 'flex-shrink: 0') for k, v in enumerate(NICHES)) +
                    col(h2('Узел 6 · основания опор') + node_piles(), 10, 'flex-shrink: 0'), 24)
    body += col(h2('Порядок монтажа и допуски') + '<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px 24px; font-size: 12.5px; line-height: 1.45">' +
                ''.join(f'<div>{i}. {t}</div>' for i, t in enumerate(MONTAGE, 1)) + '</div>', 10)
    out['FenceNodes.dc.html'] = page('Забор: узлы', 1440, H['FenceNodes.dc.html'], body)
    return out
