"""Изометрия дома 9,0×11,5 в координатах участка (м)."""
X0, X1, YG, YV, YB, YA = 9.0, 18.0, 14.5, 23.5, 24.5, 26.0
AX2 = 12.6
FL, WT = 0.5, 2.9            # пол, верх стен
def zL(x): return 2.75 + (x-8.5)/4.1*1.15          # левый скат: карниз слева, верх у оси 2 = 3,9
def zR(x): return 4.6 - (x-AX2)/5.9*1.85           # правый скат: верх у оси 2 = 4,6, карниз справа
OV_B, OV_F = 14.0, 26.3

def poly(P, pts, fill, stroke='#1E2528', sw=0.5):
    q = ' '.join('%.1f,%.1f' % P(*p) for p in pts)
    return f'<polygon points="{q}" style="fill: {fill}; stroke: {stroke}; stroke-width: {sw}; stroke-linejoin: round"></polygon>'

def box_faces(P, x0, y0, x1, y1, z0, z1, cl, cf, ct=None, sw=0.4):
    out = [poly(P, [(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)], cl, sw=sw),
           poly(P, [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], cf, sw=sw)]
    if ct: out.append(poly(P, [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], ct, sw=sw))
    return out

def opening_x(P, x, ya, yb, za, zb, fill):   # проём на стене x = const (левая)
    return poly(P, [(x, ya, za), (x, yb, za), (x, yb, zb), (x, ya, zb)], fill, sw=0.4)
def opening_y(P, y, xa, xb, za, zb, fill):   # проём на стене y = const (фасад к улице)
    return poly(P, [(xa, y, za), (xb, y, za), (xb, y, zb), (xa, y, zb)], fill, sw=0.4)

def house(P, sw=0.5, flue=True):
    o = []
    # цоколь
    o.append(poly(P, [(X0, YG, 0), (X0, YA, 0), (X0, YA, FL), (X0, YG, FL)], '#474B4F', sw=sw))
    o.append(poly(P, [(X0, YA, 0), (X1, YA, 0), (X1, YA, FL), (X0, YA, FL)], '#565B60', sw=sw))
    # настил террасы
    o.append(poly(P, [(X0, YB, FL), (AX2, YB, FL), (AX2, YV, FL), (X1, YV, FL), (X1, YA, FL), (X0, YA, FL)], '#B98A5A', sw=sw))
    # стены тёплого контура
    o.append(poly(P, [(AX2, YV, FL), (X1, YV, FL), (X1, YV, WT), (AX2, YV, WT)], '#E9E1D2', sw=sw))
    o.append(opening_y(P, YV, 12.75, 13.61, FL, FL+2.06, '#4B5055'))                   # Д-1 металлическая
    for xa in (14.75, 16.44): o.append(opening_y(P, YV, xa, xa+1.04, FL+0.9, FL+2.07, '#8FB3C9'))
    o.append(poly(P, [(X0, YB, FL), (AX2, YB, FL), (AX2, YB, WT), (X0, YB, WT)], '#E9E1D2', sw=sw))
    o.append(opening_y(P, YB, 10.28, 11.32, FL+0.9, FL+2.07, '#8FB3C9'))
    o.append(poly(P, [(X0, YG, FL), (X0, YB, FL), (X0, YB, WT), (X0, YG, WT)], '#D3CAB8', sw=sw))
    for ya in (15.9, 19.1): o.append(opening_x(P, X0, ya, ya+1.04, FL+0.9, FL+2.07, '#7FA3B9'))
    # стойки террасы
    for (x, y) in [(X1, 24.75), (X0, YA), (10.8, YA), (AX2, YA), (15.3, YA), (X1, YA)]:
        o += box_faces(P, x-0.07, y-0.07, x+0.07, y+0.07, FL, 2.75, '#6E5236', '#80613F', sw=0.3)
    # ступени
    for k in range(3):
        o += box_faces(P, 12.45, YA + 0.17*k, 15.65, YA+0.5, 0, FL - 0.17*k, '#7E5E3E', '#946F49', '#B98A5A', sw=0.3)
    # фронтон над террасой (плоскость y = 26)
    fr = [(X0, YA, 2.75)] + [(x/10, YA, zL(x/10)) for x in (90, 126)] + [(AX2, YA, zR(AX2))] + [(X1, YA, zR(X1)), (X1, YA, 2.75)]
    o.append(poly(P, fr, '#E3DACB', sw=sw))
    # кровля: правый скат, световой фриз, левый скат
    o.append(poly(P, [(AX2, OV_B, zR(AX2)), (18.5, OV_B, zR(18.5)), (18.5, OV_F, zR(18.5)), (AX2, OV_F, zR(AX2))], '#9C4636', sw=sw))
    o.append(poly(P, [(AX2, OV_B, zL(AX2)), (AX2, OV_F, zL(AX2)), (AX2, OV_F, zR(AX2)), (AX2, OV_B, zR(AX2))], '#E3DACB', sw=sw))
    for yv in (15.3, 19.6, 24.0):
        o.append(opening_x(P, AX2, yv, yv+0.6, 4.02, 4.45, '#5C6166'))
    if flue:   # фановый стояк санузла над левым скатом
        o += box_faces(P, 12.2, 15.3, 12.36, 15.46, zL(12.3)-0.2, zL(12.3)+0.55, '#474B4F', '#565B60', '#5C6166', sw=0.3)
    o.append(poly(P, [(8.5, OV_B, zL(8.5)), (AX2, OV_B, zL(AX2)), (AX2, OV_F, zL(AX2)), (8.5, OV_F, zL(8.5))], '#8A3B2E', sw=sw))
    # торцы кровли у улицы
    o.append(poly(P, [(8.5, OV_F, zL(8.5)), (AX2, OV_F, zL(AX2)), (AX2, OV_F, zL(AX2)-0.14), (8.5, OV_F, zL(8.5)-0.14)], '#6E2E24', sw=0.3))
    o.append(poly(P, [(AX2, OV_F, zR(AX2)), (18.5, OV_F, zR(18.5)), (18.5, OV_F, zR(18.5)-0.14), (AX2, OV_F, zR(AX2)-0.14)], '#6E2E24', sw=0.3))
    if flue:   # коаксиальный дымоход котла над правым скатом (котельная, пом. 7)
        o += box_faces(P, 17.2, 15.0, 17.34, 15.14, zR(17.27)-0.2, zR(17.27)+0.6, '#8C9399', '#A5ACB2', '#C9CDD1', sw=0.3)
    return o
