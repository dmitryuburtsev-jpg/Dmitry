import re, os
SRC = os.path.join(os.path.dirname(__file__), 'original')
OUT = os.path.join(os.path.dirname(__file__), '..', 'canvas', 'project')
os.makedirs(OUT, exist_ok=True)

def src(name):
    return open(os.path.join(SRC, name), encoding='utf-8').read()

_base = src('Main.dc.html')
BASE_CSS = _base[_base.find('<style>')+7:_base.find('svg .b{font-weight:600}')+len('svg .b{font-weight:600}')]
FONTS = '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&amp;family=IBM+Plex+Sans+Condensed:wght@400;500;600;700&amp;family=IBM+Plex+Sans:wght@400;500;600&amp;display=swap" rel="stylesheet">'
KICKER = 'Гришино-Модус 9х11 · терраса в сад · д. Гришино · КН 50:31:0010104:5239'

def page(title, w, h, body, css=''):
    return f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
{FONTS}
<style>
{BASE_CSS}

{css}
</style>
</helmet>
<div style="width: {w}px; height: {h}px; box-sizing: border-box; padding: 36px 40px; display: flex; flex-direction: column; gap: 20px; background: #F3EFE6">
{body}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview": {{"width": {w}, "height": {h}}}}}'>
class Component extends DCLogic {{
renderVals() {{ return {{}}; }}
}}
</script>
</body>
</html>
'''

def header(title, sub, num):
    return f'''<div style="display: flex; justify-content: space-between; align-items: flex-end; gap: 24px; border-bottom: 2px solid #1E2528; padding-bottom: 12px">
<div style="display: flex; flex-direction: column; gap: 4px">
<div class="hd" style="font-size: 12px; font-weight: 600; letter-spacing: .12em; text-transform: uppercase; color: #565C61">{KICKER}</div>
<h1 class="hd" style="margin: 0; font-size: 34px; font-weight: 700; line-height: 1.05">{title}</h1>
<div style="font-size: 13.5px; color: #565C61">{sub}</div>
</div>
<div class="hd" style="font-size: 44px; font-weight: 700; color: #1E2528; line-height: 1">{num}</div>
</div>'''

def h2(t, extra=''):
    return f'<h2 class="hd" style="margin: {extra or "0"}; font-size: 17px; font-weight: 600">{t}</h2>'

def col(inner, gap=12, style=''):
    return f'<div style="display: flex; flex-direction: column; gap: {gap}px{"; "+style if style else ""}">{inner}</div>'

def row(inner, gap=28, style=''):
    return f'<div style="display: flex; gap: {gap}px{"; "+style if style else ""}">{inner}</div>'

def notes(items, size=12.5):
    return '<div style="display: flex; flex-direction: column; gap: 6px; font-size: %spx; line-height: 1.45">' % size + ''.join(f'<div>{t}</div>' for t in items) + '</div>'

def fmt(v, d=0):
    if isinstance(v, str): return v
    if d == 0: return f"{int(round(v)):,}".replace(",", " ")
    return f"{v:,.{d}f}".replace(",", " ").replace(".", ",")

def spec_table(items, total_label):
    """items: (name, unit, qty, price) — сумма считается здесь"""
    rows = []; tot = 0
    for i, (n, u, q, p) in enumerate(items, 1):
        s = round(q*p); tot += s
        qd = fmt(q, 0) if float(q).is_integer() else fmt(q, 1)
        pd = fmt(p, 0) if float(p).is_integer() else fmt(p, 1)
        rows.append(f'<tr><td>{i}</td><td>{n}</td><td>{u}</td><td class="r">{qd}</td><td class="r">{pd}</td><td class="r">{fmt(s)}</td></tr>')
    rows.append(f'<tr class="tot"><td></td><td>{total_label}</td><td></td><td class="r"></td><td class="r"></td><td class="r">{fmt(tot)}</td></tr>')
    return ('<table class="tb"><thead><tr><th>№</th><th>Наименование</th><th>Ед.</th><th class="r">Кол-во</th>'
            '<th class="r">Цена, ₽</th><th class="r">Сумма, ₽</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table>'), tot

def check_table(groups, first='Расстояние, м'):
    """groups: [(group_title|None, [(что, норма, факт, ok(bool|'warn'|'fix'), основание)])]"""
    out = [f'<table class="tb"><thead><tr><th>{first}</th><th class="r">Норма</th><th class="r">Факт</th><th></th><th>Основание</th></tr></thead><tbody>']
    for g, rows in groups:
        if g: out.append(f'<tr class="grp"><td colspan="5">{g}</td></tr>')
        for what, nm, fact, ok, why in rows:
            tag = {True: '<span class="ok">норма</span>', False: '<span class="bad">не норма</span>',
                   'warn': '<span class="warn">уточнить</span>', 'fix': '<span class="ok">исправлено</span>', 'todo': '<span class="warn">доработать</span>'}[ok]
            out.append(f'<tr><td>{what}</td><td class="r">{nm}</td><td class="r">{fact}</td><td>{tag}</td><td><span style="color: #565C61">{why}</span></td></tr>')
    out.append('</tbody></table>')
    return ''.join(out)

BAD_CSS = '.bad{color:#B3261E;font-weight:600}'

def tag_list(items, cls=''):
    """нумерованные метки (как на исходных листах)"""
    return ''.join(f'<div style="display: flex; gap: 8px; align-items: flex-start"><div class="mono" style="flex-shrink: 0; width: 20px; height: 20px; border-radius: 10px; background: #1E2528; color: #F3EFE6; font-size: 11px; display: flex; align-items: center; justify-content: center">{i}</div><div style="font-size: 12px; line-height: 1.4">{t}</div></div>' for i, t in items)

def write(name, html):
    open(os.path.join(OUT, name), 'w', encoding='utf-8').write(html)

class Svg:
    def __init__(self): self.e = []
    def add(self, s): self.e.append(s); return self
    def rect(self, x, y, w, h, cls='', style=''):
        return self.add(f'<rect class="{cls}" x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}"{f" style={chr(34)}{style}{chr(34)}" if style else ""}></rect>')
    def pl(self, pts, cls='', style=''):
        p = ' '.join(f'{x:.3f},{y:.3f}' for x, y in pts)
        return self.add(f'<polyline class="{cls}" points="{p}"{f" style={chr(34)}{style}{chr(34)}" if style else ""}></polyline>')
    def pg(self, pts, cls='', style=''):
        p = ' '.join(f'{x:.2f},{y:.2f}' for x, y in pts)
        return self.add(f'<polygon class="{cls}" points="{p}"{f" style={chr(34)}{style}{chr(34)}" if style else ""}></polygon>')
    def line(self, x1, y1, x2, y2, cls='', style=''):
        return self.add(f'<line class="{cls}" x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}"{f" style={chr(34)}{style}{chr(34)}" if style else ""}></line>')
    def circ(self, x, y, r, cls='', style=''):
        return self.add(f'<circle class="{cls}" cx="{x:.3f}" cy="{y:.3f}" r="{r:.3f}"{f" style={chr(34)}{style}{chr(34)}" if style else ""}></circle>')
    def text(self, x, y, t, cls='', rot=None, style=''):
        tr = f' transform="rotate({rot} {x:.3f} {y:.3f})"' if rot is not None else ''
        st = f' style="{style}"' if style else ''
        return self.add(f'<text class="{cls}" x="{x:.3f}" y="{y:.3f}"{tr}{st}>{t}</text>')
    def dim(self, x1, y1, x2, y2, label, off=0.22, tick=0.22, vertical=None, cls='td'):
        self.line(x1, y1, x2, y2, 'dim')
        for (x, y) in ((x1, y1), (x2, y2)):
            self.line(x-tick, y+tick, x+tick, y-tick, 'dimt')
        mx, my = (x1+x2)/2, (y1+y2)/2
        if abs(x1-x2) < 1e-6:
            self.text(x1-off, my, label, cls+' mid', rot=-90)
        else:
            self.text(mx, my-off, label, cls+' mid')
    def svg(self, w, h, vb, style='background: #FBF9F4; border: 1px solid #D6CEBF'):
        return f'<svg width="{w}" height="{h}" viewBox="{vb}" style="{style}">' + ''.join(self.e) + '</svg>'
