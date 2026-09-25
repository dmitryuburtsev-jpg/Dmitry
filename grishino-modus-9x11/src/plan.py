"""Базовый план дома 9,0×11,5 (местные координаты: x от оси 1, y от оси Г)."""
from calc import TERRACE
T = 0.147
ROOMS_L = {5: (T, T, 3.306, 3.1), 4: (T, 3.344, 3.306, 2.912), 3: (T, 6.353, 3.306, 3.5), 6: (3.6, T, 2.356, 1.9),
           7: (6.053, T, 2.8, 1.9), 2: (3.6, 2.144, 1.656, 6.709), 8: (5.353, 2.144, 3.5, 6.709)}
PLAN_CSS = '''
.wallf{fill:#1E2528} .partf{fill:#1E2528} .roomf{fill:#FFFFFF} .terf{fill:#EFE5D2;stroke:#1E2528;stroke-width:.03}
.wetf{fill:#E3EEF5} .boilf{fill:#FBEFC8} .stepf{fill:#ECE4D2;stroke:#1E2528;stroke-width:.03}
.winw{fill:#FFFFFF;stroke:#1E2528;stroke-width:.02} .winnew{fill:#FFFFFF;stroke:#1D5FA0;stroke-width:.05}
.dsw{fill:none;stroke:#565C61;stroke-width:.02} .dnew{fill:none;stroke:#1D5FA0;stroke-width:.035}
.fx{fill:#FFFFFF;stroke:#1E2528;stroke-width:.025} .post2{fill:#1E2528}
'''
def base(s, fixtures=True, room_cls=None):
    room_cls = room_cls or {6: 'wetf', 7: 'boilf'}
    s.pg([(p[0]-9, p[1]-14.5) for p in TERRACE], 'terf')
    for (x, y) in [(0, 11.5), (1.8, 11.5), (3.6, 11.5), (6.3, 11.5), (9, 11.5), (9, 10.25)]:
        s.rect(x-0.08, y-0.08, 0.16, 0.16, 'post2')
    s.rect(3.45, 11.5, 3.2, 0.5, 'stepf'); s.line(3.45, 11.67, 6.65, 11.67, 'dsw'); s.line(3.45, 11.84, 6.65, 11.84, 'dsw')
    s.pg([(0, 0), (9, 0), (9, 9), (3.6, 9), (3.6, 10), (0, 10)], 'wallf')
    for k, (x, y, w, h) in ROOMS_L.items(): s.rect(x, y, w, h, room_cls.get(k, 'roomf'))
    s.rect(3.6, 2.047, 5.253, 0.097, 'roomf')
    s.rect(3.6, 2.047, 2.356, 0.097, 'partf'); s.rect(6.053, 2.047, 2.8, 0.097, 'partf')
    s.rect(5.256, 2.144, 0.097, 2.0, 'partf'); s.rect(5.256, 6.344, 0.097, 2.509, 'partf')
    s.rect(5.956, T, 0.097, 1.9, 'partf')
    def door_v(x, ya, yb, into_left=True, c='dsw'):
        s.rect(x-0.08, ya, 0.16, yb-ya, 'roomf'); w = yb-ya; sx = x - w if into_left else x + w
        s.add(f'<path class="{c}" d="M {x:.3f} {ya:.3f} L {sx:.3f} {ya:.3f} A {w:.3f} {w:.3f} 0 0 {0 if into_left else 1} {x:.3f} {yb:.3f}"></path>')
    def door_h(y, xa, xb, down=True, c='dsw', hinge_left=True):
        s.rect(xa, y-0.08, xb-xa, 0.16, 'roomf'); w = xb-xa
        hx, ox = (xa, xb) if hinge_left else (xb, xa); ey = y + w if down else y - w
        sweep = (1 if down else 0) if hinge_left else (0 if down else 1)
        s.add(f'<path class="{c}" d="M {hx:.3f} {y:.3f} L {hx:.3f} {ey:.3f} A {w:.3f} {w:.3f} 0 0 {sweep} {ox:.3f} {y:.3f}"></path>')
    for ya, yb in [(2.267, 3.147), (5.226, 6.106), (6.503, 7.383)]: door_v(3.527, ya, yb)
    door_h(2.096, 4.376, 5.056, down=False)
    door_h(2.096, 7.843, 8.703, down=True, c='dnew', hinge_left=False)
    door_h(8.927, 3.65, 4.51, down=True)
    def win_v(x, ya, yb, c='winw'): s.rect(x-0.075, ya, 0.15, yb-ya, c); s.line(x, ya, x, yb, 'dsw')
    def win_h(y, xa, xb, c='winw'): s.rect(xa, y-0.075, xb-xa, 0.15, c); s.line(xa, y, xb, y, 'dsw')
    win_v(0.074, 1.4, 2.44); win_v(0.074, 4.6, 5.64); win_v(8.926, 4.6, 5.64); win_h(9.926, 1.28, 2.32)
    win_h(8.926, 5.75, 6.79); win_h(8.926, 7.44, 8.48); win_h(0.074, 5.216, 5.756); win_h(0.074, 6.75, 7.35, 'winnew')
    if fixtures:
        s.rect(3.65, 0.2, 0.85, 0.85, 'fx'); s.line(3.65, 0.2, 4.5, 1.05, 'dsw')
        s.add('<ellipse class="fx" cx="3.93" cy="1.62" rx=".2" ry=".27"></ellipse>'); s.rect(3.75, 1.84, 0.36, 0.17, 'fx')
        s.rect(5.5, 0.55, 0.4, 0.55, 'fx')
        s.rect(5.45, 2.19, 2.25, 0.6, 'fx'); s.rect(6.0, 2.29, 0.55, 0.4, 'fx'); s.rect(6.9, 2.29, 0.6, 0.4, 'fx')
        s.rect(6.15, 1.3, 0.6, 0.6, 'fx'); s.circ(6.5, 0.55, 0.28, 'fx'); s.circ(8.5, 1.5, 0.3, 'fx')
        s.rect(8.43, 0.35, 0.36, 0.44, 'fx', 'fill: #F6E3A6')
