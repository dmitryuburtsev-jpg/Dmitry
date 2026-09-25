"""Планы дома 6×9 «Планировка 6» в положении на участке. Координаты u = x − 12, v = y − 15 (м):
v = 0 — край террасы (ось 1, сад, вверху), v = 11 — уличный торец (ось 3, внизу); u = 0 — ось А (слева), u = 6 — ось В (справа, калитка)."""
from calc import ROOMS, STEPS, PORCH, PORCH_STEPS, DOOR_IN
def R(r): return (r[0]-12, r[1]-15, r[2], r[3])
def L2U(lx, ly): return (6 - ly, lx)
PLAN_CSS = '''
.wallf{fill:#1E2528} .partf{fill:#1E2528} .roomf{fill:#FFFFFF} .terf{fill:#EFE5D2;stroke:#1E2528;stroke-width:.03}
.wetf{fill:#E3EEF5} .boilf{fill:#FBEFC8} .entf{fill:#EEF3E4} .stepf{fill:#ECE4D2;stroke:#1E2528;stroke-width:.03}
.winw{fill:#FFFFFF;stroke:#1E2528;stroke-width:.02} .winnew{fill:#FFFFFF;stroke:#1D5FA0;stroke-width:.05}
.dsw{fill:none;stroke:#565C61;stroke-width:.02} .dnew{fill:none;stroke:#1D5FA0;stroke-width:.035} .partn{fill:#1D5FA0}
.fx{fill:#FFFFFF;stroke:#1E2528;stroke-width:.025} .post2{fill:#1E2528} .stair{fill:none;stroke:#565C61;stroke-width:.02}
'''
def _doors(s):
    def door_v(x, ya, yb, right=True, c='dsw', hinge_top=True):
        s.rect(x-0.08, ya, 0.16, yb-ya, 'roomf'); w = yb-ya
        hy, oy = (ya, yb) if hinge_top else (yb, ya); ex = x + w if right else x - w
        sweep = (0 if right else 1) if hinge_top else (1 if right else 0)
        s.add(f'<path class="{c}" d="M {x:.3f} {hy:.3f} L {ex:.3f} {hy:.3f} A {w:.3f} {w:.3f} 0 0 {sweep} {x:.3f} {oy:.3f}"></path>')
    def door_h(y, xa, xb, down=True, c='dsw', hinge_left=True):
        s.rect(xa, y-0.08, xb-xa, 0.16, 'roomf'); w = xb-xa
        hx, ox = (xa, xb) if hinge_left else (xb, xa); ey = y + w if down else y - w
        sweep = (1 if down else 0) if hinge_left else (0 if down else 1)
        s.add(f'<path class="{c}" d="M {hx:.3f} {y:.3f} L {hx:.3f} {ey:.3f} A {w:.3f} {w:.3f} 0 0 {sweep} {ox:.3f} {y:.3f}"></path>')
    return door_v, door_h
def _win(s):
    def win_v(x, ya, yb, c='winw'): s.rect(x-0.075, ya, 0.15, yb-ya, c); s.line(x, ya, x, yb, 'dsw')
    def win_h(y, xa, xb, c='winw'): s.rect(xa, y-0.075, xb-xa, 0.15, c); s.line(xa, y, xb, y, 'dsw')
    return win_v, win_h
def stairs(s, u0, u1, v0, v1, n=10):
    s.rect(u0, v0, u1-u0, v1-v0, 'stair')
    for i in range(1, n): s.line(u0, v0 + (v1-v0)*i/n, u1, v0 + (v1-v0)*i/n, 'stair')
    s.line((u0+u1)/2, v1-0.1, (u0+u1)/2, v0+0.2, 'stair')
def floor1(s, fixtures=True, porch=True):
    s.rect(2.85, 0, 3.15, 2.0, 'terf')
    for (x, y) in [(2.85, 0), (4.35, 0), (6, 0), (6, 1.0), (2.85, 2.0)]:
        s.rect(x-0.08, y-0.08, 0.16, 0.16, 'post2')
    x, y, w, h = R(STEPS); s.rect(x, y, w, h, 'stepf'); s.line(x, y+0.3, x+w, y+0.3, 'dsw')
    if porch:
        x, y, w, h = R(PORCH); s.rect(x, y, w, h, 'stepf')
        x, y, w, h = R(PORCH_STEPS); s.rect(x, y, w, h, 'stepf'); s.line(x, y+0.3, x+w, y+0.3, 'dsw')
    s.rect(0, 2, 6, 9, 'wallf')
    cls = {3: 'wetf', 6: 'boilf', 2: 'entf'}
    for k in range(2, 9):
        x, y, w, h = R(ROOMS[k][:4]); s.rect(x, y, w, h, cls.get(k, 'roomf'))
    door_v, door_h = _doors(s); win_v, win_h = _win(s)
    door_h(2.073, 3.15, 4.05, down=False)                              # Д-1 с террасы
    door_v(5.927, DOOR_IN[0]-15, DOOR_IN[1]-15, right=True, c='dnew')  # новая входная дверь к калитке
    door_h(3.548, 3.22, 4.1, down=True)                                # прихожая → холл 4
    door_v(4.468, 4.47, 5.25, right=True)                              # санузел
    door_h(5.5, 3.08, 3.96, down=True)                                 # холл 4 → холл 7
    door_h(5.5, 1.87, 2.75, down=False)                                # спальня 5
    door_v(4.205, 6.47, 7.35, right=False)                             # котельная → холл 7
    s.rect(2.5, 7.40, 1.0, 0.2, 'roomf')                               # проём П-1
    stairs(s, 0.25, 2.05, 5.6, 7.4)
    win_v(5.926, 4.265, 4.785); win_v(5.926, 5.74, 6.26)               # О-2 санузла, О-3 котельной
    win_h(10.926, 3.94, 4.96); win_h(10.926, 1.04, 2.06)               # кухня-гостиная на улицу
    win_v(0.074, 5.99, 7.01); win_v(0.074, 8.66, 9.68); win_h(2.074, 0.99, 2.01)
    if fixtures:
        s.rect(5.05, 3.62, 0.78, 0.78, 'fx'); s.line(5.05, 3.62, 5.83, 4.4, 'dsw')                 # душ
        s.add('<ellipse class="fx" cx="4.78" cy="4.0" rx=".2" ry=".26"></ellipse>'); s.rect(4.6, 3.62, 0.36, 0.15, 'fx')
        s.rect(5.45, 4.85, 0.38, 0.45, 'fx')                                                        # умывальник
        s.rect(5.25, 7.65, 0.6, 3.15, 'fx'); s.rect(5.35, 7.8, 0.4, 0.5, 'fx'); s.rect(5.3, 9.3, 0.5, 0.6, 'fx')   # кухня
        s.circ(5.45, 5.95, 0.28, 'fx'); s.circ(4.6, 5.85, 0.22, 'fx')                                # бойлер, ГА
        s.rect(5.49, 6.6, 0.36, 0.44, 'fx', 'fill: #F6E3A6')                                         # котёл
def floor2(s):
    s.rect(0, 2, 6, 9, 'wallf')
    cls = {10: 'wetf'}
    for k in range(9, 14):
        x, y, w, h = R(ROOMS[k][:4]); s.rect(x, y, w, h, cls.get(k, 'roomf'))
    door_v, door_h = _doors(s); win_v, win_h = _win(s)
    door_h(5.5, 2.52, 3.4, down=False)                                 # спальня 9
    door_v(4.205, 5.98, 6.86, right=True)                              # санузел 10
    door_h(7.5, 3.02, 3.9, down=True); door_h(7.5, 2.07, 2.95, down=True)   # спальни 12, 13
    s.rect(3.0, 7.451, 0.1, 0.097, 'partf')
    stairs(s, 0.15, 2.05, 5.6, 7.4)
    win_h(2.05, 3.48, 4.5); win_h(2.05, 1.5, 2.52); win_h(10.95, 3.48, 4.5); win_h(10.95, 1.5, 2.52); win_v(0.05, 5.99, 7.01)
    s.rect(5.3, 5.62, 0.5, 0.5, 'fx'); s.add('<ellipse class="fx" cx="4.75" cy="5.9" rx=".2" ry=".26"></ellipse>'); s.rect(4.45, 6.95, 0.7, 0.45, 'fx')
