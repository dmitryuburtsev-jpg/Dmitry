"""Изометрия дома 9,0×11,5 в координатах участка (м)."""
X0, X1 = 9.0, 18.0
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
    """Дом развёрнут: терраса (ось А) к саду при y = 14,5, уличный фасад (ось Г) при y = 26, вход — справа."""
    o = []
    # крыльцо входа у правой стены (почти не видно с этой стороны — рисуется первым)
    o += box_faces(P, 18.0, 22.2, 19.0, 23.8, 0, FL, '#7E5E3E', '#946F49', '#B98A5A', sw=0.3)
    o += box_faces(P, 18.0, 23.8, 19.0, 24.4, 0, 0.25, '#7E5E3E', '#946F49', '#B98A5A', sw=0.3)
    o += box_faces(P, 18.0, 22.1, 19.1, 23.9, 2.55, 2.65, '#4B5055', '#565C61', '#5A626B', sw=0.3)
    # ступени террасы в сад (за домом)
    for k in range(3):
        o += box_faces(P, 12.45, 14.0, 15.65, 14.5 - 0.17*k, 0, FL - 0.17*k, '#7E5E3E', '#946F49', '#B98A5A', sw=0.3)
    # цоколь
    o.append(poly(P, [(X0, 14.5, 0), (X0, 26.0, 0), (X0, 26.0, FL), (X0, 14.5, FL)], '#474B4F', sw=sw))
    o.append(poly(P, [(X0, 26.0, 0), (X1, 26.0, 0), (X1, 26.0, FL), (X0, 26.0, FL)], '#565B60', sw=sw))
    # настил террасы
    o.append(poly(P, [(X0, 14.5, FL), (X1, 14.5, FL), (X1, 17.0, FL), (AX2, 17.0, FL), (AX2, 16.0, FL), (X0, 16.0, FL)], '#B98A5A', sw=sw))
    # стойки террасы (дальние — до стен)
    for (x, y) in [(X0, 14.5), (10.8, 14.5), (AX2, 14.5), (15.3, 14.5), (X1, 14.5), (X1, 15.75)]:
        o += box_faces(P, x-0.07, y-0.07, x+0.07, y+0.07, FL, 2.75, '#6E5236', '#80613F', sw=0.3)
    # стены: левая (спальни) и уличный фасад
    o.append(poly(P, [(X0, 16.0, FL), (X0, 26.0, FL), (X0, 26.0, WT), (X0, 16.0, WT)], '#D3CAB8', sw=sw))
    for ya in (20.36, 23.56): o.append(opening_x(P, X0, ya, ya+1.04, FL+0.9, FL+2.07, '#7FA3B9'))
    o.append(poly(P, [(X0, 26.0, FL), (X1, 26.0, FL), (X1, 26.0, WT), (X0, 26.0, WT)], '#E9E1D2', sw=sw))
    o.append(opening_y(P, 26.0, 14.216, 14.756, FL+1.5, FL+2.0, '#8FB3C9'))      # О-2 санузла
    o.append(opening_y(P, 26.0, 15.3, 15.9, FL+1.1, FL+1.9, '#8FB3C9'))          # окно котельной
    # фронтон уличного фасада
    fr = [(X0, 26.0, WT)] + [(x/10, 26.0, zL(x/10)) for x in (90, 126)] + [(AX2, 26.0, zR(AX2)), (X1, 26.0, zR(X1)), (X1, 26.0, WT)]
    o.append(poly(P, fr, '#E3DACB', sw=sw))
    # газовый стояк на фасаде
    o.append(poly(P, [(16.85, 26.02, 0), (16.9, 26.02, 0), (16.9, 26.02, FL+0.4), (16.85, 26.02, FL+0.4)], '#C28E00', stroke='#C28E00', sw=0.8))
    # кровля: правый скат, световой фриз, левый скат
    o.append(poly(P, [(AX2, OV_B, zR(AX2)), (18.5, OV_B, zR(18.5)), (18.5, OV_F, zR(18.5)), (AX2, OV_F, zR(AX2))], '#9C4636', sw=sw))
    o.append(poly(P, [(AX2, OV_B, zL(AX2)), (AX2, OV_F, zL(AX2)), (AX2, OV_F, zR(AX2)), (AX2, OV_B, zR(AX2))], '#E3DACB', sw=sw))
    for yv in (15.3, 19.6, 24.0):
        o.append(opening_x(P, AX2, yv, yv+0.6, 4.02, 4.45, '#5C6166'))
    if flue:   # фановый стояк санузла над левым скатом
        o += box_faces(P, 12.2, 24.4, 12.36, 24.56, zL(12.3)-0.2, zL(12.3)+0.55, '#474B4F', '#565B60', '#5C6166', sw=0.3)
    o.append(poly(P, [(8.5, OV_B, zL(8.5)), (AX2, OV_B, zL(AX2)), (AX2, OV_F, zL(AX2)), (8.5, OV_F, zL(8.5))], '#8A3B2E', sw=sw))
    o.append(poly(P, [(8.5, OV_F, zL(8.5)), (AX2, OV_F, zL(AX2)), (AX2, OV_F, zL(AX2)-0.14), (8.5, OV_F, zL(8.5)-0.14)], '#6E2E24', sw=0.3))
    o.append(poly(P, [(AX2, OV_F, zR(AX2)), (18.5, OV_F, zR(18.5)), (18.5, OV_F, zR(18.5)-0.14), (AX2, OV_F, zR(AX2)-0.14)], '#6E2E24', sw=0.3))
    if flue:   # коаксиальный дымоход котла (котельная у уличного угла справа)
        o += box_faces(P, 17.2, 25.2, 17.34, 25.34, zR(17.27)-0.2, zR(17.27)+0.6, '#8C9399', '#A5ACB2', '#C9CDD1', sw=0.3)
    return o
