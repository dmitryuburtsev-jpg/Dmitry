"""План дома 9,0×11,5 в развёрнутом положении. Координаты u = x − 9, v = y − 14,5 (м):
v = 0 — ось А (терраса, сад, вверху), v = 11,5 — ось Г (улица, внизу); u = 0 — ось 1 (слева), u = 9 — ось 3 (справа, калитка)."""
from calc import TERRACE, HEATED, ROOMS, STEPS, PORCH, PORCH_STEPS, DOOR_IN
def U(p): return (p[0]-9, p[1]-14.5)
def R(r): return (r[0]-9, r[1]-14.5, r[2], r[3])
PLAN_CSS = '''
.wallf{fill:#1E2528} .partf{fill:#1E2528} .roomf{fill:#FFFFFF} .terf{fill:#EFE5D2;stroke:#1E2528;stroke-width:.03}
.wetf{fill:#E3EEF5} .boilf{fill:#FBEFC8} .entf{fill:#EEF3E4} .stepf{fill:#ECE4D2;stroke:#1E2528;stroke-width:.03}
.winw{fill:#FFFFFF;stroke:#1E2528;stroke-width:.02} .winnew{fill:#FFFFFF;stroke:#1D5FA0;stroke-width:.05}
.dsw{fill:none;stroke:#565C61;stroke-width:.02} .dnew{fill:none;stroke:#1D5FA0;stroke-width:.035} .partn{fill:#1D5FA0}
.fx{fill:#FFFFFF;stroke:#1E2528;stroke-width:.025} .post2{fill:#1E2528}
.dim{stroke:#565C61;stroke-width:.015} .dimt{stroke:#1E2528;stroke-width:.025}
svg .tdc{font-size:.19px;font-family:'IBM Plex Mono',monospace;fill:#1E2528} svg .tdk{font-size:.19px;font-family:'IBM Plex Mono',monospace;fill:#7A3E1D;font-weight:600}
'''
def base(s, fixtures=True, porch=True):
    s.pg([U(p) for p in TERRACE], 'terf')
    for (x, y) in [(0, 0), (1.8, 0), (3.6, 0), (6.3, 0), (9, 0), (9, 1.25)]:
        s.rect(x-0.08, y-0.08, 0.16, 0.16, 'post2')
    x, y, w, h = R(STEPS); s.rect(x, y, w, h, 'stepf'); s.line(x, y+0.17, x+w, y+0.17, 'dsw'); s.line(x, y+0.33, x+w, y+0.33, 'dsw')
    if porch:
        x, y, w, h = R(PORCH); s.rect(x, y, w, h, 'stepf')
        x, y, w, h = R(PORCH_STEPS); s.rect(x, y, w, h, 'stepf'); s.line(x, y+0.3, x+w, y+0.3, 'dsw')
    s.pg([U(p) for p in HEATED], 'wallf')
    cls = {6: 'wetf', 7: 'boilf', 9: 'entf'}
    for k in (2, 3, 4, 5, 6, 7, 8, 9):
        x, y, w, h = R(ROOMS[k][:4]); s.rect(x, y, w, h, cls.get(k, 'roomf'))
    s.rect(3.6, 9.356, 5.253, 0.097, 'partf')                        # перегородка 6/7 — холл/прихожая
    s.rect(5.956, 9.453, 0.097, 1.9, 'partf')                         # 6 | 7
    s.rect(5.256, 2.647, 0.097, 2.509, 'partf'); s.rect(5.256, 7.356, 0.097, 2.0, 'partf')   # П-1, проём 2,2 м
    s.rect(5.353, 7.659, 3.5, 0.097, 'partn')                         # новая перегородка прихожей
    def door_v(x, ya, yb, right=True, c='dsw', hinge_top=True):       # проём в вертикальной стене, створка в сторону right
        s.rect(x-0.08, ya, 0.16, yb-ya, 'roomf'); w = yb-ya
        hy, oy = (ya, yb) if hinge_top else (yb, ya); ex = x + w if right else x - w
        sweep = (0 if right else 1) if hinge_top else (1 if right else 0)
        s.add(f'<path class="{c}" d="M {x:.3f} {hy:.3f} L {ex:.3f} {hy:.3f} A {w:.3f} {w:.3f} 0 0 {sweep} {x:.3f} {oy:.3f}"></path>')
    def door_h(y, xa, xb, down=True, c='dsw', hinge_left=True):
        s.rect(xa, y-0.08, xb-xa, 0.16, 'roomf'); w = xb-xa
        hx, ox = (xa, xb) if hinge_left else (xb, xa); ey = y + w if down else y - w
        sweep = (1 if down else 0) if hinge_left else (0 if down else 1)
        s.add(f'<path class="{c}" d="M {hx:.3f} {y:.3f} L {hx:.3f} {ey:.3f} A {w:.3f} {w:.3f} 0 0 {sweep} {ox:.3f} {y:.3f}"></path>')
    for ya, yb in [(8.353, 9.233), (5.394, 6.274), (4.117, 4.997)]: door_v(3.527, ya, yb, right=False)   # двери спален из холла
    door_h(9.405, 4.376, 5.056, down=True)                               # санузел
    door_h(9.405, 7.9, 8.76, down=False, c='dnew', hinge_left=False)    # котельная → прихожая
    door_v(5.305, 8.4, 9.2, right=True, c='dnew')                        # прихожая ↔ холл (новая)
    door_v(9.0, DOOR_IN[0]-14.5, DOOR_IN[1]-14.5, right=True, c='dnew') # входная дверь, наружу к калитке
    door_h(2.573, 3.75, 4.65, down=False)                                # выход на террасу (по эскизу: 150 + 900 от оси 2)
    def win_v(x, ya, yb, c='winw'): s.rect(x-0.075, ya, 0.15, yb-ya, c); s.line(x, ya, x, yb, 'dsw')
    def win_h(y, xa, xb, c='winw'): s.rect(xa, y-0.075, xb-xa, 0.15, c); s.line(xa, y, xb, y, 'dsw')
    win_v(0.074, 9.06, 10.1); win_v(0.074, 5.86, 6.9); win_v(8.926, 5.86, 6.9); win_h(1.574, 1.28, 2.32)
    win_h(2.574, 5.75, 6.79); win_h(2.574, 7.44, 8.48); win_h(11.426, 5.216, 5.756); win_h(11.426, 6.3, 6.9, 'winnew')
    if fixtures:
        s.rect(3.65, 10.5, 0.85, 0.85, 'fx'); s.line(3.65, 11.35, 4.5, 10.5, 'dsw')          # душ
        s.add('<ellipse class="fx" cx="3.93" cy="9.95" rx=".2" ry=".27"></ellipse>'); s.rect(3.75, 9.5, 0.36, 0.17, 'fx')  # унитаз
        s.rect(5.5, 10.4, 0.4, 0.55, 'fx')                                                     # умывальник
        s.rect(6.0, 6.95, 2.8, 0.6, 'fx'); s.rect(6.35, 7.05, 0.55, 0.4, 'fx'); s.rect(7.7, 7.05, 0.6, 0.4, 'fx')  # кухня
        s.rect(6.15, 9.55, 0.6, 0.6, 'fx'); s.circ(6.5, 11.0, 0.28, 'fx'); s.circ(8.5, 9.95, 0.3, 'fx')        # СМ, ГА, бойлер
        s.rect(8.43, 10.6, 0.36, 0.44, 'fx', 'fill: #F6E3A6')                                   # котёл
