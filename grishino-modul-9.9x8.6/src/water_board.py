from common import *
from calc import *
import re, math
s = src('Water.dc.html').replace('Дизайн-проект участка · д. Гришино · КН 50:31:0010104:5239', KICKER)
def rep(a, b):
    global s
    assert s.count(a) == 1, a
    s = s.replace(a, b)
rep('<div>3. Ввод в подполье дома — у правой стены, дальше труба идёт по утеплённому подполью к бойлерной в левом углу у улицы. Автоматика и гидроаккумулятор — в бойлерной.',
    f'<div>3. Траншея В1 от кессона идёт прямо к правой стене дома ({fmt(L(V1), 2)} м, верх трубы −1,8), ввод в подполье — в {fmt(YG - V1[0][1], 1)} м от уличного фасада; '
    f'дальше ПНД Ø32 в утеплении с греющим кабелем {fmt(L(V1_FLOOR), 1)} м по подполью до бойлерной в левом углу у улицы. Канализацию В1 не пересекает: линия бани обходит дом со стороны сада — футляр не нужен. '
    'Автоматика и гидроаккумулятор — в бойлерной.')
rep('лоток -1,38', f'лоток {fmt(lv["ЛОС"], 2)}'.replace('-', '−'))
rep('До скважины — 29,0 м, до фундамента дома — 6,7 м.', f'До скважины — {fmt(CH["скважина-ЛОС"], 1)} м, до фундамента дома — {fmt(CH["ЛОС-дом"], 1)} м.')

# план трассы В1 с привязками
w = Svg()
W_CSS = """
.wf{fill:none;stroke:#3E5B3A;stroke-width:.12} .wh{fill:#E2D6BE;stroke:#1E2528;stroke-width:.08} .wb{fill:#ECE4D2;stroke:#1E2528;stroke-width:.05}
.wv{fill:none;stroke:#1D5FA0;stroke-width:.14} .wvu{fill:none;stroke:#1D5FA0;stroke-width:.1;stroke-dasharray:.3 .12} .wvb{fill:none;stroke:#1D5FA0;stroke-width:.08;stroke-dasharray:.5 .15}
.wk{fill:none;stroke:#7A3E1D;stroke-width:.12;stroke-dasharray:.4 .15} .wkk{fill:#FFFFFF;stroke:#7A3E1D;stroke-width:.06}
.wwell{fill:#FFFFFF;stroke:#1D5FA0;stroke-width:.1} .dim{stroke:#565C61;stroke-width:.03} .dimt{stroke:#1E2528;stroke-width:.05} .wboil{fill:#F6E3A6}
svg .wt{font-size:.5px;fill:#1E2528} svg .wtb{font-size:.5px;fill:#1D5FA0;font-weight:600} svg .wtk{font-size:.5px;fill:#7A3E1D}
svg .tdc{font-size:.5px;font-family:'IBM Plex Mono',monospace;fill:#1E2528}
"""
w.pl([(8, 32), (18, 32)], 'wf'); w.pl([(19, 32), (32, 32), (32, 5.5)], 'wf'); w.text(13.0, 32.7, 'улица', 'wt mid')
w.pg(HEATED, 'wh'); w.pg(TERRACE, 'wb'); w.rect(*PORCH, 'wb')
x, y, ww, h, *_ = ROOMS[6]; w.rect(x, y, ww, h, 'wboil'); w.text(9.7, 23.9, 'бойл.', 'wt mid', style='font-size: .4px')
w.text(14.5, 24.0, 'дом', 'wt mid', style='font-size: .7px')
w.rect(24.8, 1.5, 5.7, 6.0, 'wb'); w.text(27.6, 6.3, 'баня', 'wt mid', style='font-size: .7px')
w.pl(k1['bath'][:3], 'wk'); w.pl(k1['house'], 'wk')
for k in ('КК-Б', 'КК-4'):
    w.circ(*KK[k], 0.25, 'wkk'); w.text(KK[k][0]+0.35, KK[k][1]-0.3, k, 'wtk')
w.text(12.0, 11.6, 'К1 бани — за домом', 'wtk')
w.pl(V1, 'wv'); w.pl(V1_FLOOR, 'wvu'); w.pl(V1_BATH, 'wvb'); w.pl(V1_NEIGH, 'wv')
w.circ(*WELL, 0.55, 'wwell'); w.text(30.3, 22.3, 'скважина', 'wtb end')
w.circ(*V1_FLOOR[-1], 0.12, '', 'fill: #1D5FA0'); w.text(10.1, 24.9, 'ГА', 'wtb')
w.text(24.2, 20.6, 'В1 ПНД Ø32, −1,8', 'wtb'); w.text(13.2, 20.8, f'по подполью {fmt(L(V1_FLOOR), 1)} м', 'wtb')
w.text(31.4, 14.0, 'В1 в баню', 'wtb', rot=-90)
def d(x1, y1, x2, y2, t, off=0.2):
    w.dim(x1, y1, x2, y2, t, off=off, tick=0.2, cls='tdc')
d(31.0, 23.0, 32.0, 23.0, '1,0'); d(32.9, 21.0, 32.9, 32.0, fmt(32 - WELL[1], 1), off=-0.45)
d(HX1, 19.6, 30.45, 19.6, fmt(L(V1), 2)); d(19.4, 21.0, 19.4, YG, fmt(YG - 21.0, 1), off=-0.45)
d(9.7, 20.3, HX1, 20.3, fmt(HX1 - 9.7, 1)); d(8.6, 21.0, 8.6, V1_FLOOR[-1][1], fmt(V1_FLOOR[-1][1] - 21.0, 1))
d(33.0, 6.95, 33.0, 20.45, f'{fmt(L(V1_BATH[:2]), 1)}', off=-0.45)
water_svg = w.svg(440, 535, '7.8 5.5 26.1 31.7', 'background: #FBF9F4; border: 1px solid #D6CEBF')
bind = [('Скважина (ось)', f'1,0 м от правой границы (x = {fmt(WELL[0], 1)}), {fmt(32 - WELL[1], 1)} м от уличного забора'),
        ('Траншея В1 кессон → дом', f'{fmt(L(V1), 2)} м по линии {fmt(32 - V1[0][1], 1)} м от улицы, верх трубы −1,8'),
        ('Ввод в подполье', f'правая стена, {fmt(YG - V1[0][1], 1)} м от уличного фасада; гильза в утеплённом цоколе'),
        ('По подполью до бойлерной', f'{fmt(L(V1_FLOOR), 1)} м: {fmt(HX1 - 9.7, 1)} м вдоль той же линии + {fmt(V1_FLOOR[-1][1] - 21.0, 1)} м к гидроаккумулятору; утепление, греющий кабель'),
        ('Пересечения с К1', 'нет — линия канализации бани идёт за домом и по левой стороне'),
        ('В1 в баню', f'{fmt(L(V1_BATH), 1)} м вдоль правой границы (1,0 м от забора), −0,6 с греющим кабелем'),
        ('К соседу', 'ПНД Ø32 из кессона через правую границу в гильзе')]
bind_html = '<table class="tb"><thead><tr><th>Участок</th><th>Привязка и длина</th></tr></thead><tbody>' + ''.join(f'<tr><td>{a}</td><td>{b}</td></tr>' for a, b in bind) + '</tbody></table>'
s = s.replace('в итог она не включена.</div>', 'в итог она не включена.</div>\n<h2 class="hd" style="margin: 8px 0 0; font-size: 17px; font-weight: 600">Трасса В1 · привязки, м</h2>' + water_svg + bind_html, 1)
s = s.replace('</style>', W_CSS + '</style>', 1)

items = [
    ('Бурение скважины на известняк ≈ 55 м с обсадкой сталь Ø133 [метраж по факту]', 'м', 55, 3700),
    ('Кессон пластиковый 1,0×2,0 м с горловиной', 'шт', 1, 42000),
    ('Обустройство: монтаж кессона, оголовок, запорная арматура, выход трубы', 'компл', 1, 38000),
    ('Насос скважинный Grundfos SQ 5-70 (или аналог), 5 м³/ч — на два дома', 'шт', 1, 128000),
    ('Отвод к соседу: тройник и кран в кессоне, счётчик воды, ПНД Ø32 в гильзе под забором', 'компл', 1, 9500),
    ('Кабель насоса 4×1,5, трос из нержавеющей стали, хомуты, 60 м', 'компл', 1, 12000),
    ('Гидроаккумулятор 100 л, реле давления, манометр, пятивыводник, фильтр', 'компл', 1, 18500),
    (f'Труба ПНД Ø32 PN16: кессон → ввод в подполье ({math.ceil(L(V1))} м) + по подполью до бойлерной ({math.ceil(L(V1_FLOOR))} м) в утеплении с греющим кабелем', 'компл', 1, 14500),
    (f'Траншея В1 глубиной 1,8 м, {math.ceil(L(V1))} м', 'м', math.ceil(L(V1)), 1400),
    ('В1 в баню: ПНД Ø25 в скорлупе ППУ + саморегулирующийся кабель 16 Вт/м, 17 м', 'компл', 1, 35000),
    ('Траншея В1 в баню глубиной 0,6 м, 14 м, с монтажом', 'м', 14, 900),
    ('Анализ воды: химический и микробиологический', 'шт', 1, 6500),
]
tbl, total = spec_table(items, 'Итого скважина и водоснабжение')
s = re.sub(r'(Спецификация: вода</h2>\n)<table class="tb">.*?</table>', lambda m: m.group(1) + tbl, s, flags=re.S)
assert fmt(total) in s
s = s.replace('height: 1600px', 'height: 1840px').replace('"height": 1600', '"height": 1840')
write('Water.dc.html', s); open('water_total.txt', 'w').write(str(total)); print('water', total)
