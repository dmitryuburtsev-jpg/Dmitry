from common import *
from calc import *
import iso, re
s = src('Visual.dc.html').replace('Дизайн-проект участка · д. Гришино', 'Гришино-Модус 9х11 · терраса в сад · д. Гришино')
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
out = full[0:3] + [rect_g((11.5, 1, 11, 10.8), style(3)), full[4]]
for r in [(18, 24.4, 1, 7.6), (18.9, 7.6, 1.2, 18.9), (20.1, 7.6, 6.2, 1.2), (9.7, 12.3, 9.2, 1.2), (9.7, 3.6, 1.2, 8.7), (3.4, 3.6, 6.3, 1.2), (12.45, 13.5, 3.2, 0.5)]:
    out.append(rect_g(r, st_path))
for k in k1: out.append(pl(k1[k], st_k1))
out.append(pl([(2.6, 30.5), (2.6, 32.6)], st_k1n))
out += [pl(V1 + V1_UNDER[1:], st_v1), pl(V1_NEIGH, st_v1), pl(V1_BATH, st_v1b)]
for k in ('ВРУ→ЩР-Д', 'магистраль', 'баня', 'беседка', 'хозблок', 'ЛОС'): out.append(pl(EL[k], st_el))
out.append(pl(EL['насос'][:3], st_el))
out.append(pl(G1, st_g)); out.append(pl(G1_FACADE, st_g.replace('stroke-width: 2.6', 'stroke-width: 1.6; stroke-dasharray: 5 3')))
for (cx, cy) in KK.values():
    X, Y = P(cx, cy)
    out.append(f'<polygon points="{X-9.4:.1f},{Y:.1f} {X:.1f},{Y-5.4:.1f} {X+9.4:.1f},{Y:.1f} {X:.1f},{Y+5.4:.1f}" style="{st_kk}"></polygon>')
out += full[30:97] + full[103:157]
out += iso.house(P, sw=0.5)
out += [shift(e, -2.2) for e in full[200:203]] + [shift(e, 9.0) for e in full[203:206]] + full[206:246]
mk = full[246:270]
def mv(el, x, y):
    el = re.sub(r'cx="[^"]+" cy="[^"]+"', f'cx="{x:.1f}" cy="{y:.1f}"', el)
    return re.sub(r'x="[^"]+" y="[^"]+"', f'x="{x:.1f}" y="{y+4:.1f}"', el)
pos = {0: (552.0, 400.0), 7: (748.0, 566.0), 11: (795.0, 545.0)}
for n, (x, y) in pos.items():
    mk[2*n] = mv(mk[2*n], x, y); mk[2*n+1] = mv(mk[2*n+1], x, y)
out += mk
s = s[:i] + head + ''.join(out) + '</svg>' + s[j:]
tot = int(open('site_total.txt').read())
for a, b in [('Дом 85 м²: вход и крыльцо со стороны калитки, терраса в сад', 'Дом каркасный 9,0×11,5 м, 94,7 м²: терраса в сад, вход со стороны калитки'),
             ('153,1 м²', '171,5 м²'), ('12\u00a0444\u00a0556 ₽', fmt(tot).replace(' ', '\u00a0') + ' ₽')]:
    assert a in s, a
    s = s.replace(a, b)
write('Visual.dc.html', s); print('ok')
