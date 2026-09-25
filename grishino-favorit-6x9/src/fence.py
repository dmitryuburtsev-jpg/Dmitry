"""Лист 02 «Забор из профлиста»: расчёт из скрипта исходного листа перенесён сюда, чтобы на листе
(и в PNG/PDF) стояли готовые числа, а не шаблоны {{…}}. Параметры — те же, что были по умолчанию в «Tweaks»."""
import math, re

W, D = 32.0, 32.0            # участок, м
H, S = 2.0, 2.5              # высота забора, шаг столбов, м
SHEET_PRICE, WORK_PRICE = 690, 1250
PLANK = True
COLOR = '#3E5B3A'            # RAL 6005, зелёный мох


def rnd(v, d=0):             # округление «от нуля», как Math.round в исходном листе
    k = 10 ** d
    return math.floor(v * k + 0.5) / k


def nf(v, d):
    s = f'{v:,.{d}f}'.replace(',', ' ').replace('.', ',')
    return s


def rub(v):
    return nf(rnd(v), 0)


def qf(v):                   # количество: целое — без дробной части, иначе столько знаков, сколько вошло в сумму
    if float(v).is_integer(): return str(int(v))
    return nf(v, 1) if rnd(v, 1) == v else nf(v, 2)


def calc():
    gx1 = W - 1.5; gx0 = gx1 - 4; wx1 = gx0 - 7.5; wx0 = max(wx1 - 1, 0)
    runs_in = [('Улица: до калитки', wx0), ('Улица: зона отката ворот', 7.5), ('Улица: за воротами', W - gx1),
               ('Тыльная граница', W), ('Левая граница', D), ('Правая граница', D)]
    inner = sheets = 0; L = 0.0; runs = []
    for name, ln in runs_in:
        sp = math.ceil(ln / S - 1e-9); sh = math.ceil(ln / 1.1 - 1e-9); ip = max(sp - 1, 0)
        inner += ip; sheets += sh; L += ln
        runs.append((name, nf(ln, 2), str(ip), str(sh)))
    posts = inner + 4; allp = posts + 4
    post_len = math.ceil((H + 1.15) * 10 - 1e-9) / 10
    rows = 3 if H > 2.05 else 2
    area = rnd(sheets * 1.15 * H, 1)
    mats = [
        (f'Профлист С20 0,45 мм, полимер с одной стороны, лист {nf(H, 1)} м', 'м²', area, SHEET_PRICE),
        (f'Столбы — труба 60×60×2, L = {nf(post_len, 1)} м ({posts} шт)', 'м', rnd(posts * post_len, 1), 330),
        ('Столбы ворот и калитки — труба 80×80×3, L = 3,5 м (4 шт)', 'м', 14, 720),
        (f'Лаги — труба 40×20×2, {rows} ряда', 'м', rnd(rows * L * 1.05, 1), 125),
        ('Саморез 5,5×19 по металлу с EPDM, в цвет', 'шт', sheets * rows * 6, 3.2),
        ('Заглушка на столб', 'шт', allp, 60),
    ]
    if PLANK:
        mats.append(('Планка П-образная на верх забора, 2 м', 'шт', math.ceil(L / 1.95), 380))
    mats += [
        ('Бетон М250 — бетонирование столбов на всю глубину (Ø250 / Ø300 у ворот)', 'м³',
         rnd((posts * math.pi * 0.125 ** 2 * 1.05 + 4 * math.pi * 0.15 ** 2 * 1.15) * 1.1, 2), 7800),
        ('Щебень 20–40 — подушка 150 мм на дне скважин', 'м³', rnd(allp * math.pi * 0.125 ** 2 * 0.15 * 1.2, 2), 3200),
        ('Рубероид РКП-350 — рукав-опалубка скважины (защита от пучения), рулон 10 м²', 'рул', math.ceil(allp * 0.82 / 10), 650),
        ('Грунт-эмаль по металлу 3 в 1, 2,7 кг', 'банка', math.ceil(allp / 25), 1450),
        ('Электроды 3 мм, 2,5 кг', 'пачка', math.ceil(allp / 30), 950),
        (f'Ворота откатные 4,0×{nf(H, 1)} м: рама из профтрубы, обшивка профлистом С20 в цвет забора, фурнитура, закладная 16П', 'компл', 1, 82000),
        (f'Калитка 1,0×{nf(H, 1)} м: рама из профтрубы, обшивка профлистом С20, петли, замок', 'компл', 1, 13500),
    ]
    works = [
        ('Монтаж забора: бурение Ø250 на 1,2 м, бетонирование столбов, сварка лаг, окраска, профлист', 'м', rnd(L, 1), WORK_PRICE),
        ('Монтаж откатных ворот с фундаментом под закладную', 'компл', 1, 28000),
        ('Монтаж калитки', 'компл', 1, 6000),
        ('Доставка материалов', 'рейс', 2, 6000),
    ]
    n = 0
    def mk(arr):
        nonlocal n
        out = []
        for name, unit, q, price in arr:
            n += 1; sm = rnd(q * price)
            out.append((str(n), name, unit, qf(q), rub(price) if float(price).is_integer() else nf(price, 1), rub(sm), sm))
        return out
    mat_rows, work_rows = mk(mats), mk(works)
    m = sum(r[6] for r in mat_rows); w = sum(r[6] for r in work_rows)
    return dict(runs=runs, mat_rows=mat_rows, work_rows=work_rows, kL=nf(L, 1), kPosts=str(allp), kSheets=str(sheets),
                kArea=nf(area, 1), mSum=rub(m), wSum=rub(w), total=rub(m + w), total_v=int(m + w), perM=rub((m + w) / L),
                hLabel=nf(H, 1), sLabel=nf(S, 1), rowsLabel=f'{rows} ряда лаг', plotLabel=f'{nf(W, 2)} × {nf(D, 2)} м',
                plankOp='1' if PLANK else '0', color=COLOR)


def static(html):
    """Подставляет расчёт в исходный лист и убирает скрипт пересчёта."""
    v = calc()
    def expand(list_name, var, rows, keys):
        nonlocal html
        m = re.search(r'<sc-for list="\{\{' + list_name + r'\}\}" as="' + var + r'"[^>]*>(.*?)</sc-for>', html, flags=re.S)
        assert m, list_name
        body = ''
        for r in rows:
            t = m.group(1)
            for k, val in zip(keys, r): t = t.replace('{{' + var + '.' + k + '}}', val)
            body += t
        html = html[:m.start()] + body + html[m.end():]
    expand('runs', 'r', v['runs'], ('name', 'len', 'posts', 'sheets'))
    expand('matRows', 'i', v['mat_rows'], ('n', 'name', 'unit', 'qty', 'price', 'sum'))
    expand('workRows', 'i', v['work_rows'], ('n', 'name', 'unit', 'qty', 'price', 'sum'))
    html = html.replace('{{{{plotLabel}}}}', v['plotLabel'])
    html = html.replace(' Количество и стоимость пересчитываются от параметров в «Tweaks».',
                        f' Высота {v["hLabel"]} м, шаг столбов {v["sLabel"]} м, профлист RAL 6005.')
    for k in ('kL', 'kPosts', 'kSheets', 'kArea', 'mSum', 'wSum', 'total', 'perM', 'hLabel', 'sLabel', 'rowsLabel', 'plankOp', 'color'):
        html = html.replace('{{' + k + '}}', v[k])
    h = re.search(r'"\$preview": \{"width": (\d+), "height": (\d+)\}', html)
    html = re.sub(r'<script type="text/x-dc" data-dc-script.*?</script>',
                  '<script type="text/x-dc" data-dc-script data-props=\'{"$preview": {"width": %s, "height": %s}}\'>\n'
                  'class Component extends DCLogic {\nrenderVals() { return {}; }\n}\n</script>' % h.groups(), html, count=1, flags=re.S)
    html = html.replace('</style>', 'svg .ct{paint-order:stroke;stroke:#FBF9F4;stroke-width:3.5px;stroke-linejoin:round}\n</style>', 1)   # подписи читаются на тёмном профлисте
    assert '{{' not in html, re.findall(r'.{30}\{\{.{30}', html)
    return html, v['total_v']
