"""Индекс холста: раскладка листов 3 в ряд, размеры — из $preview каждого листа."""
import json, re, os, datetime
HERE = os.path.dirname(__file__); PRJ = os.path.join(HERE, '..', 'canvas', 'project')
c = json.load(open(os.path.join(HERE, 'original', 'canvas.json')))
H = {}
for f in os.listdir(PRJ):
    if f.endswith('.dc.html'):
        m = re.search(r'"\$preview": \{"width": (\d+), "height": (\d+)', open(os.path.join(PRJ, f)).read())
        if m: H[f] = (int(m.group(1)), int(m.group(2)))
rows = [(['Main.dc.html', 'Visual.dc.html', 'Fence.dc.html'], [-400, 1520, 3040]),
        (['Sewer.dc.html', 'Water.dc.html', 'Power.dc.html'], [0, 1520, 3040]),
        (['Budget.dc.html', 'Gazebo.dc.html', 'House.dc.html'], [0, 1520, 3040]),
        (['Bath.dc.html', 'Gas.dc.html', 'Check.dc.html'], [0, 1520, 3040])]
titles = {k: v.get('title') for k, v in c['boards'].items()}
titles['House.dc.html'] = 'Дом каркасный 9,0×11,5'; titles['Check.dc.html'] = 'Проверка сетей'
boards = {}; y = 0
for names, xs in rows:
    for n, x in zip(names, xs):
        w, h = H[n]; boards[n] = {'x': x, 'y': y, 'w': w, 'h': h, 'title': titles[n]}
    y += max(H[n][1] for n in names) + 120
cur = os.path.join(PRJ, 'canvas.json')
if os.path.exists(cur):   # холст уже есть: сохраняем его ключи и чужие рамки, меняем только раскладку листов
    new = json.load(open(cur))
    for n, e in boards.items(): new['boards'].setdefault(n, {}).update(e)
    json.dump(new, open(cur, 'w'), ensure_ascii=False, indent=2); raise SystemExit
new = {'v': 3, 'createdOnFiles': {'v': 1, 'at': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')},
       'title': 'Гришино-Фаворит 6х9', 'launch': {'view': 'canvas'}, 'pages': [], 'boards': boards,
       'order': c['order'] + ['Check.dc.html'],
       'notes': {'title': {'kind': 'title1', 'maxW': 4480, 'text': 'Гришино-Фаворит 6х9: двухэтажный дом 6×9 с террасой в сад и входом от калитки; баня, генплан, сети, газ, смета', 'w': 240, 'x': -400, 'y': -300}},
       'designSystems': []}
json.dump(new, open(os.path.join(PRJ, 'canvas.json'), 'w'), ensure_ascii=False)
