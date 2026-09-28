from common import *
from calc import *
import iso, re, fence
s = src('Visual.dc.html').replace('Дизайн-проект участка · д. Гришино', 'Гришино-Фаворит 6х9 · д. Гришино')
i = s.find('<svg'); j = s.find('</svg>')+6
svg = s[i:j]
head = svg[:svg.find('>')+1]
full = [m.group(0) for m in re.finditer(r'<(\w+)\b[^>]*>[^<]*</\1>', svg)]
assert len(full) == 270
def P(x, y, z=0): return (25.7+15.6*(x+y), 456.6+9*(y-x)-18*z)
def style(k): return re.search(r'style="([^"]+)"', full[k]).group(1)
def rect_g(r, st):
    x, y, w, h = r
    q = ' '.join('%.1f,%.1f' % P(*p) for p in [(x, y), (x+w, y), (x+w, y+h), (x, y+h)])
    return f'<polygon points="{q}" style="{st}"></polygon>'
def pl(pts, st):
    return '<polyline points="' + ' '.join('%.1f,%.1f' % P(*p) for p in pts) + f'" style="{st}"></polyline>'
def shift(el, dx):
    DX, DY = 15.6*dx, -9*dx
    return re.sub(r'points="([^"]+)"', lambda m: 'points="' + ' '.join('%.1f,%.1f' % (float(a)+DX, float(b)+DY) for a, b in (p.split(',') for p in m.group(1).split())) + '"', el)
st_path = style(5); st_k1 = style(12); st_k1n = style(15); st_v1 = style(16); st_v1b = style(18); st_el = style(19); st_g = style(24); st_kk = style(25)
out = full[0:3] + [rect_g(GARDEN, style(3)), full[4]]
for r in [(18, 19.2, 1, 12.8), (18.9, 7.6, 1.2, 18.9), (20.1, 7.6, 6.2, 1.2), (9.7, 12.3, 9.2, 1.2), (15.6, 13.5, 1.4, 0.9)] + GARDEN_PATHS:
    out.append(rect_g(r, st_path))
out.append(rect_g(MANGAL_PAD, re.sub(r'fill: #[0-9A-Fa-f]+', 'fill: #CBC2B1', st_path)))   # мангальная зона: брусчатка
for k in k1: out.append(pl(k1[k], st_k1))
out.append(pl([(2.6, 30.5), (2.6, 32.6)], st_k1n))
out += [pl(V1 + V1_UNDER[1:], st_v1), pl(V1_NEIGH, st_v1), pl(V1_BATH, st_v1b)]
for k in ('ВРУ→ЩР-Д', 'магистраль', 'баня', 'беседка', 'хозблок', 'ЛОС'): out.append(pl(EL[k], st_el))
out.append(pl(EL['насос'][:3], st_el))
out.append(pl(G1, st_g)); out.append(pl(G1_FACADE, st_g.replace('stroke-width: 2.6', 'stroke-width: 1.6; stroke-dasharray: 5 3')))
for (cx, cy) in KK.values():
    X, Y = P(cx, cy)
    out.append(f'<polygon points="{X-9.4:.1f},{Y:.1f} {X:.1f},{Y-5.4:.1f} {X+9.4:.1f},{Y:.1f} {X:.1f},{Y+5.4:.1f}" style="{st_kk}"></polygon>')
# беседка исходного рисунка (full[103:157]) перенесена на новое место, мангал внутри неё (full[151:154]) убран;
# рисуется до хозблока — она дальше от зрителя. Мангал и стол на площадке — между баней и беседкой.
GDX, GDY = GAZEBO[0] - 4.0, GAZEBO[1] - 7.0
def shift2(el, dx, dy):
    DX, DY = 15.6*(dx + dy), 9*(dy - dx)
    return re.sub(r'points="([^"]+)"', lambda m: 'points="' + ' '.join('%.1f,%.1f' % (float(a)+DX, float(b)+DY) for a, b in (p.split(',') for p in m.group(1).split())) + '"', el)
gz = [shift2(e, GDX, GDY) for e in full[103:151] + full[154:157]]
mx, my, mw, mh = MANGAL; tx, ty, tw, th = MANGAL_TABLE
mg = iso.box_faces(P, mx, my, mx + mw, my + mh, 0, 0.85, '#1F2122', '#2A2D2F', '#3E4246', sw=0.3) + \
     iso.box_faces(P, tx, ty, tx + tw, ty + th, 0, 0.9, '#8E9296', '#A5ACB2', '#C9CDD1', sw=0.3)
out += full[30:87] + mg + gz + full[87:97]
out += iso.house(P, sw=0.5)
out += [shift(e, -2.2) for e in full[200:203]] + [shift(e, 9.0) for e in full[203:206]] + full[206:246]
mk = full[246:270]
def mv(el, x, y):
    el = re.sub(r'cx="[^"]+" cy="[^"]+"', f'cx="{x:.1f}" cy="{y:.1f}"', el)
    return re.sub(r'x="[^"]+" y="[^"]+"', f'x="{x:.1f}" y="{y+4:.1f}"', el)
pos = {2: (268.0 + 15.6*(GDX + GDY), 402.0 + 9*(GDY - GDX)), 0: (595.0, 360.0), 7: (748.0, 566.0), 11: (795.0, 545.0)}
for n, (x, y) in pos.items():
    mk[2*n] = mv(mk[2*n], x, y); mk[2*n+1] = mv(mk[2*n+1], x, y)
X13, Y13 = P(MANGAL[0] + MANGAL[2] / 2, MANGAL[1] + MANGAL[3] / 2, 1.9)   # 13 — мангальная зона, над мангалом
mk += [mv(mk[0], X13, Y13), mv(mk[1], X13, Y13).replace('>1</text>', '>13</text>')]
assert '>13</text>' in mk[-1]
out += mk
s = s[:i] + head + ''.join(out) + '</svg>' + s[j:]
tot = int(open('site_total.txt').read())
for a, b in [('Беседка 5×4 м на винтовых сваях', 'Беседка 5×4 м в ряд с хозблоком (лист 07)'), ('>Газовый шкаф ШГ, газопровод Г1</div></div>', '>Газовый шкаф ШГ, газопровод Г1</div></div><div style="display: flex; gap: 10px; align-items: center"><div class="mono" style="width: 24px; height: 24px; border-radius: 12px; background: #1E2528; color: #F3EFE6; display: flex; align-items: center; justify-content: center; font-size: 11px; flex-shrink: 0">13</div><div style="font-size: 13px">Мангальная зона между беседкой и баней (лист 07)</div></div>'), ('Дом 85 м²: вход и крыльцо со стороны калитки, терраса в сад', 'Дом 6×9, 2 этажа, 99,9 м²: терраса в сад, вход со стороны калитки'),
             ('153,1 м²', '128,3 м²'), ('12\u00a0444\u00a0556 ₽', fmt(tot).replace(' ', '\u00a0') + ' ₽')]:
    assert a in s, a
    s = s.replace(a, b)
# узел забора: опора на винтовой свае вместо забетонированного столба
i = s.find('<h2 class="hd" style="margin: 0; font-size: 17px; font-weight: 600">Узел забора'); j = s.find('</svg>', i) + 6
s = s[:i] + h2('Узел забора: столб в лунке со щебнем, без бетона') + fence.typical_section(96) + s[j:]
i = s.find('<h2 class="hd" style="margin: 0; font-size: 17px; font-weight: 600">Как ставится столб</h2>'); j = s.find('</div>\n</div>', i)
steps = ['Разбивка по ведомости опор (лист 02.1), поиск сетей трассоискателем, вешки на трассах.',
         'Лунка Ø200 мотобуром на 0,8 м; столб 60×60×2 длиной 3 700, подземная часть в битумной мастике.',
         'Столб забивается ещё на 0,7 м — до −1,500, ниже промерзания; верх +2,200 по шнуру; лунка — щебень 20–40 с трамбовкой слоями по 0,2 м.',
         'Калитка и ворота — на винтовых сваях СВС-89 и СВС-108 с оголовками, закладная ворот — на двух сваях.',
         'Лаги 40×20×1,5 в 2 ряда, грунт-эмаль, профлист С8 0,4 на саморезы с EPDM, П-планка и заглушки — сразу, выдержка не нужна.']
s = s[:i] + h2('Как ставится опора') + ''.join(f'<div>{k}. {t}</div>' for k, t in enumerate(steps, 1)) + s[j:]
s = s.replace('забор: 53 столбов, все забетонированы', 'забор С8: 49 столбов в лунках со щебнем, 4 на сваях')
assert 'забетонир' not in s
s = s.replace('height: 1560px', 'height: 1600px').replace('"height": 1560', '"height": 1600')
write('Visual.dc.html', s); print('ok')
