"""Лист 07: беседка 5×4 — в одном ряду с хозблоком у тыльной границы, ближе к бане; мангальная зона между беседкой и баней.
Мангал из беседки убран (открытый огонь — не ближе 5 м к постройкам), вынесен на площадку из брусчатки."""
from common import *
from calc import *
import re
s = src('Gazebo.dc.html').replace('Дизайн-проект участка · д. Гришино · КН 50:31:0010104:5239', KICKER)
def rep(a, b):
    global s
    assert s.count(a) == 1, a
    s = s.replace(a, b)
N = lambda v: fmt(v, 1)

rep('>Беседка 5×4 м на винтовых сваях</h1>', '>Беседка 5×4 м и мангальная зона</h1>')
rep('двускатная кровля 25°, зона мангала.', 'двускатная кровля 25°. Стоит в одном ряду с хозблоком у тыльной границы; мангал — на отдельной площадке между беседкой и баней.')
# мангал внутри беседки убран: план пола и аксонометрия
for a in ['<rect class="steel" x="0.5" y="0.4" width="1.5" height="1"></rect>', '<rect class="mang" x="0.9" y="0.7" width="0.7" height="0.4"></rect>',
          '<text class="gt" x="0.55" y="1.7">мангал</text>']:
    rep(a, '')
iso = re.search(r'<svg width="640" height="560".*?</svg>', s, flags=re.S).group(0)
iso2 = re.sub(r'<polygon [^>]*fill: #(?:8E9296|1F2122|2A2D2F|2E3133);[^>]*></polygon>', '', iso)
assert iso.count('<polygon') - iso2.count('<polygon') == 8   # в исходнике слой мангала продублирован
s = s.replace(iso, iso2)
rep('<div>Вход с востока, со стороны дорожки к дому. Стол со скамьями на 6 человек, мангал в заднем левом углу.</div>',
    '<div>Вход с востока — ступени смотрят на мангальную зону. Стол со скамьями на 6 человек; мангала внутри нет.</div>')
rep('<div>4. Мангал ставится только на стальной лист 1,5×1,0 м, не ближе 1 м к стойкам. Для кирпичной печи-барбекю нужен отдельный фундамент рядом с беседкой (опция).</div>',
    f'<div>4. Мангал в беседке не ставится: открытый огонь допускается не ближе 5 м к постройкам (ППР РФ, прил. 4), а беседка деревянная. '
    f'Мангал вынесен на площадку из брусчатки — {N(MG["беседка ступени"])} м от ступеней беседки и {N(MG["баня стена"])} м от бани (ниже).</div>')
rep('<div>5. Электрика — от ЩР-Д отдельной линией (лист 05): 3 светильника и 3 розетки IP54.</div>',
    '<div>5. Электрика — от ЩР-Д отдельной линией (лист 05): кабель поднимается по правой передней стойке к щиту IP65, 3 светильника и 3 розетки IP54; '
    'один светильник — прожектор на восточной стойке, светит на мангальную зону.</div>\n'
    f'<div>6. Посадка: в одном ряду с хозблоком — {N(GAZEBO[1])} м до тыльной границы (СП 53.13330, п. 6.7), {N(MG["беседка-хозблок"])} м до хозблока, '
    f'{N(GAZEBO[0])} м до левой границы, {N(MG["беседка-баня"])} м до бани. Конёк вдоль ряда; на тыльном скате (свес 0,4 м) — желоб и водосток, вода уходит на свой участок.</div>')

# спецификация беседки: без листа под мангал, с водостоком тыльного ската
def num(t): return float(t.replace(' ', '').replace(' ', '').replace(',', '.'))
m = re.search(r'(<h2[^>]*>Спецификация и стоимость</h2>\s*)<table class="tb">.*?</table>', s, flags=re.S)
rows = re.findall(r'<tr><td>\d+</td><td>(.*?)</td><td>(.*?)</td><td class="r">(.*?)</td><td class="r">(.*?)</td><td class="r">(.*?)</td></tr>', m.group(0))
assert len(rows) == 22 and fmt(sum(num(r[4]) for r in rows)) == '399 270'
items = [(n, u, num(q), num(p)) for n, u, q, p, _ in rows if 'под мангал' not in n]
k = next(i for i, it in enumerate(items) if it[0].startswith('Крепёж'))
items.insert(k, ('Водосток тыльного ската: желоб 5,5 м, кронштейны, воронка, труба', 'компл', 1, 6500))
tbl, gz_total = spec_table(items, 'Итого беседка')
s = s.replace(m.group(0), m.group(1) + tbl)

# ---------- мангальная зона ----------
x0, x1, y0, y1 = 10.9, 27.3, -1.3, 9.4
v = Svg()
v.rect(x0, y0, x1 - x0, -y0, '', 'fill: #EDE7DA')                                        # соседний участок
v.line(x0, 0, x1, 0, 'mzg'); v.text(x0 + 0.2, -0.35, 'тыльная граница · забор', 'mt mu')
v.text(x1 - 0.2, -0.35, 'соседний участок', 'mt mu end')
for r in GARDEN_PATHS + [(18.9, 7.6, 1.2, 1.8), (20.1, 7.6, 6.2, 1.2)]:
    v.rect(*r, 'mzw')
px, py, pw, ph = MANGAL_PAD
v.rect(px, py, pw, ph, 'mzp')
for i in range(1, int(ph / 0.2)): v.line(px, py + i*0.2, px + pw, py + i*0.2, 'mzh')
for i in range(1, int(pw / 0.4) + 1):
    for j in range(int(ph / 0.2)):
        xx = px + i*0.4 - (0.2 if j % 2 else 0)
        if px < xx < px + pw: v.line(xx, py + j*0.2, xx, py + (j + 1)*0.2, 'mzh')
v.rect(*GAZEBO, 'mzb'); v.rect(*GAZ_STEPS, 'mzb', 'fill: #E6D2B2')
for (qx, qy) in GAZ_PILES: v.circ(qx, qy, 0.1, '', 'fill: #1E2528')
v.rect(*BATH, 'mzb'); v.rect(*BATH_TER, 'mzb', 'fill: #E6D2B2')
mx, my, mw, mh = MANGAL
v.add(f'<rect class="mzf" x="{mx-FIRE:.3f}" y="{my-FIRE:.3f}" width="{mw+2*FIRE:.3f}" height="{mh+2*FIRE:.3f}" rx="{FIRE}" ry="{FIRE}"></rect>')
v.rect(*MANGAL, 'mzm'); v.rect(*MANGAL_TABLE, 'mzt')
v.circ(mx - 0.55, my + mh/2, 0.22, '', 'fill: none; stroke: #565C61; stroke-width: .04'); v.text(mx - 0.55, my + mh/2 + 0.6, 'повар', 'mt mid mu')
v.rect(px + 0.25, py + ph - 0.75, 0.5, 0.5, '', 'fill: #D8E6F2; stroke: #1D5FA0; stroke-width: .04'); v.text(px + 0.9, py + ph - 0.4, 'вода 200 л, ОП-4', 'mt')
v.text(GAZEBO[0] + GAZEBO[2] - 0.35, 3.0, 'беседка', 'ml end'); v.text(GAZEBO[0] + GAZEBO[2] - 0.35, 3.45, 'сваи, пол +0,58', 'mt end mu')
v.text(BATH[0] + 0.35, 3.0, 'баня', 'ml'); v.text(BATH[0] + 0.35, 3.45, 'брус, УШП', 'mt mu'); v.text(BATH_TER[0] + 0.15, 8.4, 'терраса бани', 'mt')
v.text(mx + mw/2, my - 0.25, 'мангал', 'mt mid'); v.text(MANGAL_TABLE[0] + 0.75, MANGAL_TABLE[1] + 0.55, 'стол', 'mt')
v.text(mx + mw/2, my + mh + FIRE - 0.3, 'граница 5 м от очага (ППР)', 'mt mid mr')
v.text(px + pw/2, py + ph - 0.3 + 1.05, 'дорожка сада', 'mt mid mu')
v.text(15.6, 2.25, 'дорожка', 'mt mid mu')
v.chain([GAZ_STEPS[0] + GAZ_STEPS[2], px, mx, mx + mw, px + pw, BATH[0]], 1.35, cls='md')
v.dim(GAZ_STEPS[0] + GAZ_STEPS[2], 0.75, mx, 0.75, f'{N(mx - GAZ_STEPS[0] - GAZ_STEPS[2])} — до ступеней беседки', cls='md')
v.dim(mx + mw, 0.75, BATH[0], 0.75, f'{N(MG["баня стена"])} — до стены бани', cls='md')
v.chain([py, my, my + mh, py + ph], 22.3, horizontal=False, cls='md')
v.dim(24.2, 0, 24.2, my, f'{fmt(round(my*1000))} — до границы', cls='md')
MZ_CSS = ('.mzp{fill:#D9D2C4;stroke:#8C857A;stroke-width:.05} .mzh{stroke:#C4BBAA;stroke-width:.015} .mzb{fill:#ECE6D8;stroke:#1E2528;stroke-width:.05} '
          '.mzw{fill:#E4DDCF} .mzm{fill:#2E3133} .mzt{fill:#B7BBBF;stroke:#5C6166;stroke-width:.03} '
          '.mzf{fill:none;stroke:#B3261E;stroke-width:.05;stroke-dasharray:.3 .18} .mzg{stroke:#1E2528;stroke-width:.07;stroke-dasharray:.5 .15} '
          'svg .mt{font-size:.3px} svg .ml{font-size:.4px;font-weight:600} svg .md{font-size:.27px;font-family:\'IBM Plex Mono\',monospace} svg .mr{fill:#B3261E}')
plan = v.svg(690, round(690 * (y1 - y0) / (x1 - x0)), f'{x0} {y0} {x1 - x0} {y1 - y0}')

mitems = [
    ('Разбивка, выемка грунта 0,25 м, вывоз', 'м²', 24, 700),
    ('Геотекстиль 150 г/м²', 'м²', 26, 60),
    ('Щебень гранитный 20–40, слой 150 мм с уплотнением', 'м³', 3.6, 3200),
    ('Пескоцементная смесь 1:5, слой 40 мм', 'м³', 1, 4500),
    ('Брусчатка бетонная 200×100×60 (24 м² + 4 %)', 'м²', 25, 1100),
    ('Бордюр садовый 500×200×80 на бетоне', 'м', 20, 650),
    ('Мангал стальной 4 мм, очаг 1000×400, на ножках, с крышкой', 'шт', 1, 28000),
    ('Стол разделочный металлический 1000×600 с полкой', 'шт', 1, 12000),
    ('Огнетушитель ОП-4 с кронштейном, бочка 200 л с водой, ведро', 'компл', 1, 5500),
    ('Работы: основание, укладка брусчатки и бордюра', 'м²', 24, 1500),
    ('Работы: установка и анкеровка мангала и стола', 'компл', 1, 4000),
]
mtbl, mz_total = spec_table(mitems, 'Итого мангальная зона')
dist_rows = [('Очаг — ступени / стойки беседки', f'{N(MG["беседка ступени"])} / {N(MG["беседка"])}'),
             ('Очаг — стена / терраса бани', f'{N(MG["баня стена"])} / {N(near(MANGAL, [BATH_TER]))}'),
             ('Очаг — дом / хозблок', f'{N(MG["дом"])} / {N(MG["хозблок"])}'),
             ('Очаг — тыльная граница', N(MG['граница'])),
             ('Негорючее покрытие вокруг очага', f'{N(MG["очистка"])} и более')]
dist_html = ('<table class="tb"><thead><tr><th>Расстояние, м</th><th class="r">Норма</th><th class="r">Факт</th></tr></thead><tbody>' +
             ''.join(f'<tr><td>{a}</td><td class="r">{"≥ 2,0" if "покрытие" in a else "≥ 4,0" if "граница" in a else "≥ 5,0"}</td><td class="r">{b}</td></tr>' for a, b in dist_rows) + '</tbody></table>')
mz_notes = [
    f'1. Место — между беседкой и баней, в одном ряду с ними. От очага до любой постройки не меньше 5 м (ППР РФ, ПП № 1479, прил. 4): это и задаёт '
    f'расстояние между беседкой и баней — {N(MG["беседка-баня"])} м. Очаг в {N(MG["граница"])} м от тыльной границы — до построек соседа при их отступе 1 м тоже ≥ 5 м.',
    f'2. Площадка {fmt(pw, 1)}×{fmt(ph, 1)} м из бетонной брусчатки 60 мм: пескоцементная смесь 40 мм, щебень 150 мм, геотекстиль, бордюр по периметру; '
    'уклон 1–2 % к дорожке сада. Негорючее покрытие на 2 м вокруг очага — это зона очистки: без травы, дров и деревянной мебели.',
    '3. Мангал стальной, очаг 1000×400, длинной стороной поперёк ряда построек; повар стоит со стороны беседки, стол — в линию с мангалом. '
    'Дрова и уголь — в хозблоке, на площадке не хранить.',
    '4. У стола — огнетушитель ОП-4 и бочка с водой 200 л с ведром. В особый противопожарный режим и при сильном ветре мангал не разжигают.',
    '5. Под площадкой сетей нет: кабели беседки и хозблока — в 3,8 м западнее, кабель бани — в 2,8 м со стороны сада, К1 бани — за баней.',
]
block = f'''<div style="display: flex; gap: 28px; align-items: flex-start; border-top: 2px solid #1E2528; padding-top: 14px">
<div style="display: flex; flex-direction: column; gap: 8px; width: 690px; flex-shrink: 0">
{h2('Мангальная зона · план, размеры в мм')}
{plan}
<div style="font-size: 12px; line-height: 1.45; color: #565C61">Пунктир — граница 5 м от очага: в неё не попадают ни беседка со ступенями, ни баня с террасой. Штриховка — брусчатка.</div>
</div>
<div style="display: flex; flex-direction: column; gap: 10px; flex-grow: 1; min-width: 0">
{h2('Мангальная зона: решения')}
{notes(mz_notes)}
{dist_html}
{h2('Спецификация и стоимость: мангальная зона', '6px 0 0')}
{mtbl}
</div>
</div>'''
i = s.rfind('</div>\n</x-dc>')
s = s[:i] + block + '\n' + s[i:]
s = s.replace('</style>', MZ_CSS + '\n</style>', 1)
H = 2680
s = s.replace('height: 1700px', f'height: {H}px').replace('"height": 1700', f'"height": {H}')
assert f'"height": {H}' in s
write('Gazebo.dc.html', s)
open('gazebo_total.txt', 'w').write(str(gz_total)); open('mangal_total.txt', 'w').write(str(mz_total))
print('gazebo', gz_total, 'mangal', mz_total)
