from common import *
from calc import *
import fence, re
# Лист 10 — газоснабжение первого проекта: ШГ слева, Г1 к левой стене, ввод прямо в бойлерную. Бойлерная, разрез, нагрузка,
# порядок подключения и спецификация — без изменений; трасса на участке и проверки пересчитаны под новые сети и забор.
s = src('Gas.dc.html').replace('Дизайн-проект участка · д. Гришино · КН 50:31:0010104:5239', KICKER)
def rep(a, b):
    global s
    assert s.count(a) == 1, a
    s = s.replace(a, b)
N = lambda v: fmt(v, 1); N2 = lambda v: fmt(v, 2)
gas_fence = next(r[2] for r in fence.util_checks() if r[0].startswith('Газопровод'))

# ---------- трасса на участке (в координатах участка, классы — из исходного листа) ----------
t = Svg()
t.rect(-1.5, 32.9, 22.2, 2.9, 'road'); t.rect(-1.5, 32.6, 22.2, 0.4, 'ditch'); t.text(-1.3, 32.5, 'кювет', 'ts mu'); t.text(11.0, 35.45, 'улица / проезд', 'tl mu')
t.pl([(-1.5, 34.1), (20.7, 34.1)], 'g1gro'); t.text(-1.3, 33.75, 'сеть ГРО вдоль улицы — место врезки и давление по ТУ', 'ts gac')
t.pl([(SHG[0], 34.1), (SHG[0], 32.42)], 'g1gro')
t.rect(*HOUSE, 'bld'); x, y, w, h, *_ = ROOMS[6]; t.rect(HX0, y, 1.2, YG - y, 'boil')
t.line(10.2, y, 10.2, YG, 'part'); t.line(HX0, y, 12.3, y, 'part'); t.line(12.3, y, 12.3, YG, 'part'); t.line(10.2, 22.2, 12.3, 22.2, 'part')
t.line(HX0, BOIL_DOOR[0], HX0, BOIL_DOOR[1], 'gap'); t.line(HX0, 23.7, HX0, 24.3, 'win')
t.text(14.9, 20.0, '1 · Жилой дом', 'tb3 mid'); t.text(9.6, 23.8, 'бойлерная', 'ts mid', rot=-90)
t.text(11.25, 24.3, 'санузел', 'ts mid mu'); t.text(13.3, 25.4, 'прихожая', 'ts mid mu')
t.rect(*PORCH, 'porch'); t.text(14.4, 26.95, 'крыльцо', 'ts mid mu')
for r in [(16.7, 26.2, 1.3, 1.1), (18, 26.2, 1, 5.8), (18.9, 17.2, 1.2, 9.8)]: t.rect(*r, 'path')
t.rect(*LOS, 'los'); t.text(1.9, 28.95, 'ЛОС', 'ts')
t.pl(k1['main'], 'k1'); t.pl(k1['house'], 'k1'); t.pl([p for p in k1['bath'] if p[0] < 21] , 'k1'); t.pl([(2.6, 30.5), (2.6, 32.6)], 'k1n')
for k in ('КК-3', 'КК-4', 'КК-5'):
    px, py = KK[k]
    if py > 17: t.circ(px, py, 0.22, 'kk'); t.text(px + 0.35, py + 0.65, k, 'ts')
t.text(KK['КК-4'][0] + 1.3, 28.85, 'К1 дома → ЛОС', 'ts k1c'); t.text(4.35, 21.5, 'К1 бани → КК-3', 'ts k1c', rot=-86)
t.pl(EL['ВРУ→ЩР-Д'], 'el'); t.pl(EL['ЛОС'][1:], 'el'); t.pl(EL['ЛОС'][:2], 'el', 'stroke-width: .05')
t.rect(VRU[0] - 0.4, 31.75, 0.8, 0.5, 'vru'); t.text(VRU[0] - 0.55, 31.5, 'ВРУ', 'ts end')
t.rect(SHRD[0] - 0.2, SHRD[1] - 0.2, 0.4, 0.4, 'shd'); t.text(SHRD[0] + 0.35, SHRD[1] + 0.25, 'ЩР-Д', 'ts elc')
t.text(0.2, SHRD[1] - 0.25, 'кабель ЛОС −0,7', 'ts elc')
t.pl([(0, 17.2), (0, 32), (18, 32)], 'fnc'); t.pl([(19, 32), (20.7, 32)], 'fnc')
t.add('<path class="arc" d="M 18 32 L 18 31 A 1 1 0 0 1 19 32"></path>')
for p in fence.SUP:
    if (p['side'] == 'street' and p['x'] < 20.7) or (p['side'] == 'left' and p['y'] > 17.2) or p['n'] == 1:
        t.rect(p['x'] - 0.13, p['y'] - 0.13, 0.26, 0.26, 'post')
t.pl([(0, 17.2), (0, 32), (20.7, 32)], 'bnd'); t.text(18.5, 30.8, 'калитка', 'ts mid')
t.pl(G1 + G1_FACADE[1:], 'g1'); t.rect(SHG[0] - 0.3, 32.1, 0.6, 0.32, 'shg'); t.circ(*G1[-1], 0.15, 'riser')
t.circ(9.6, 25.66, 0.12, 'flue'); t.rect(9.85, 24.5, 0.2, 0.2, 'vent')
t.text(SHG[0] - 0.42, 31.6, 'Г1 Ø32 · верх −1,55', 'ts gac', rot=-90)
def chk(a, b, txt, tx, ty):
    t.line(*a, *b, 'chk'); t.circ(*a, 0.07, 'chkc'); t.circ(*b, 0.07, 'chkc'); t.text(tx, ty, txt, 'td chkt mid')
chk((SHG[0], 28.3), (KK['КК-4'][0], 28.3), N(KK['КК-4'][0] - SHG[0]), (SHG[0] + KK['КК-4'][0]) / 2, 28.12)
chk((SHG[0] + 0.3, 32.8), (VRU[0] - 0.4, 32.8), N(CH['ШГ-ВРУ']), (SHG[0] + VRU[0]) / 2, 33.2)
_xk = cross_y(k1['bath'][2:], 27.4)[0]
chk((_xk, 27.4), (SHG[0], 27.4), N(SHG[0] - _xk), (_xk + SHG[0]) / 2, 27.22)
chk((SHG[0], SHRD[1]), (SHG[0], G1_Y), N(CH['G1-кабель ЛОС']), SHG[0] - 0.5, 25.1)
for n, x, y in [(1, SHG[0] - 1.0, 32.3), (2, SHG[0] + 0.5, 30.9), (3, SHG[0] + 0.7, 29.2), (4, 8.35, 26.4), (5, 9.6, 21.1)]:
    t.circ(x, y, 0.34, 'tagc'); t.text(x, y + 0.14, str(n), 'tagt mid')
site_svg = t.svg(700, 586, '-1.5 17.2 22.2 18.6', 'flex-shrink: 0; background: #FBF9F4; border: 1px solid #D6CEBF')
i = s.find('<svg width="700" height="586"'); j = s.find('</svg>', i) + 6
s = s[:i] + site_svg + s[j:]

rep('Посередине пролёта забора, в 7,9 м от ВРУ, доступ ГРО с улицы.',
    f'Посередине пролёта забора {fmt(fence.BYN[4]["x"], 2)}–{fmt(fence.BYN[5]["x"], 2)} (опоры 4–5), в {N(CH["ШГ-ВРУ"])} м от ВРУ, доступ ГРО с улицы.')
rep('так газопровод проходит под канализацией и кабелем к ЛОС.', 'так газопровод проходит под магистралью канализации КК-4 → КК-3.')
rep('— с магистралью К1 КК-4 → КК-3 — Г1 ниже на 0,26 м; с кабелем к ЛОС — ниже на 0,85 м.',
    f'— с магистралью К1 КК-4 → КК-3 — Г1 ниже на {N2(G1X_GAP)} м. Кабель к ЛОС идёт у левой стены дома и Г1 не пересекает ({N(CH["G1-кабель ЛОС"])} м); линия канализации бани — левее, параллельно в {N(CH["G1-K1"])} м.')
rep('Г1 −1,55: у улицы проходит под К1 с зазором 0,26 м и под кабелем ЛОС — 0,85 м', f'Г1 −1,55: у улицы проходит под К1 с зазором {N2(G1X_GAP)} м')
def row(label, val, why_old=None, why=None, label_new=None, norm_new=None):
    """заменить значение (и при необходимости подпись, норму, основание) строки проверки"""
    global s
    m = re.search(re.escape(label) + r'</td><td class="r">([^<]*)</td><td class="r">([^<]*)</td>', s)
    assert m, label
    old = m.group(0); new = old.replace(f'<td class="r">{m.group(2)}</td>', f'<td class="r">{val}</td>')
    if norm_new: new = new.replace(f'<td class="r">{m.group(1)}</td>', f'<td class="r">{norm_new}</td>', 1)
    if label_new: new = new.replace(label, label_new)
    s = s.replace(old, new)
    if why_old: rep(why_old, why)
row('Г1 — канализация К1, параллельно (выпуск дома)', f'{N(CH["G1-K1"])} / {N(CH["G1-выпуск"])}', label_new='Г1 — канализация К1, параллельно (линия бани / выпуск дома)')
row('Г1 — К1 на пересечении, по вертикали в свету', N2(G1X_GAP))
row('Г1 — кабель к ЛОС на пересечении, по вертикали', N(CH['G1-кабель ЛОС']), 'ПУЭ, гл. 2.3 · кабель в гофре выше газа', 'ПУЭ, гл. 2.3 · кабель у левой стены дома, пересечения нет',
    label_new='Г1 — кабель к ЛОС, параллельно', norm_new='≥ 1,0')
row('Г1 — стенки колодца КК-3 и ЛОС', N2(CH['G1-КК-3']))
row('Г1 — фундаменты столбов забора', N2(gas_fence), 'СП 62.13330, прил. В · ось Г1 посередине пролёта 2,25 м',
    f'СП 62.13330, прил. В · ось Г1 посередине пролёта {fmt(fence.BYN[5]["x"] - fence.BYN[4]["x"], 2)} м, лунки столбов Ø200')
row('ШГ (кран, счётчик) — шкаф учёта ВРУ', N2(CH['ШГ-ВРУ']))
write('Gas.dc.html', s)
total = 326160
assert fmt(total).replace(' ', ' ') in s or fmt(total) in s
open('gas_total.txt', 'w').write(str(total)); print('gas', total)
