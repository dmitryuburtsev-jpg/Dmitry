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
    """Дом 6×9, 2 этажа, двускатная кровля с коньком вдоль участка; терраса — к саду (y 15–17), уличный торец — y = 26."""
    X0, X1, Y2, Y3, XB = 12.0, 18.0, 17.0, 26.0, 14.85
    FL, EV, RG, XR = 0.5, 4.0, 7.45, 15.0
    zr = lambda x: EV + (RG - EV) * (1 - abs(x - XR) / 3.0)
    o = []
    # крыльцо входа у правой стены (со стороны калитки) — за домом, рисуется первым
    o += box_faces(P, 18.0, 17.0, 19.0, 18.6, 0, FL, '#7E5E3E', '#946F49', '#B98A5A', sw=0.3)
    o += box_faces(P, 18.0, 18.6, 19.0, 19.2, 0, 0.25, '#7E5E3E', '#946F49', '#B98A5A', sw=0.3)
    o += box_faces(P, 18.0, 16.9, 19.1, 18.7, 2.55, 2.65, '#4B5055', '#565C61', '#5A626B', sw=0.3)
    # терраса в сад: ступени, настил, стойки, односкатный навес
    o += box_faces(P, 15.6, 14.4, 17.0, 15.0, 0, 0.25, '#7E5E3E', '#946F49', '#B98A5A', sw=0.3)
    o.append(poly(P, [(XB, 15.0, FL), (X1, 15.0, FL), (X1, Y2, FL), (XB, Y2, FL)], '#B98A5A', sw=sw))
    o.append(poly(P, [(XB, 15.0, 0), (XB, Y2, 0), (XB, Y2, FL), (XB, 15.0, FL)], '#7E5E3E', sw=sw))
    for (x, y) in [(XB, 15.0), (16.35, 15.0), (X1, 15.0)]:
        o += box_faces(P, x-0.07, y-0.07, x+0.07, y+0.07, FL, 2.8, '#6E5236', '#80613F', sw=0.3)
    o.append(poly(P, [(XB-0.2, 14.8, 2.85), (X1+0.2, 14.8, 2.85), (X1+0.2, Y2, 3.2), (XB-0.2, Y2, 3.2)], '#9C4636', sw=sw))
    # цоколь
    o.append(poly(P, [(X0, Y2, 0), (X0, Y3, 0), (X0, Y3, FL), (X0, Y2, FL)], '#474B4F', sw=sw))
    o.append(poly(P, [(X0, Y3, 0), (X1, Y3, 0), (X1, Y3, FL), (X0, Y3, FL)], '#565B60', sw=sw))
    # левая стена (ось А): окно холла, окно лестницы, окно кухни-гостиной
    o.append(poly(P, [(X0, Y2, FL), (X0, Y3, FL), (X0, Y3, EV), (X0, Y2, EV)], '#D3CAB8', sw=sw))
    o.append(opening_x(P, X0, 23.66, 24.68, FL+0.9, FL+2.07, '#7FA3B9'))
    o.append(opening_x(P, X0, 20.99, 22.01, 2.4, 3.6, '#7FA3B9'))
    # уличный торец с фронтоном: окна кухни-гостиной и спален 2 этажа, продух
    o.append(poly(P, [(X0, Y3, FL), (X1, Y3, FL), (X1, Y3, EV), (XR, Y3, RG), (X0, Y3, EV)], '#E9E1D2', sw=sw))
    for xa in (13.04, 15.94): o.append(opening_y(P, Y3, xa, xa+1.02, FL+0.9, FL+2.07, '#8FB3C9'))
    for xa in (13.5, 15.48): o.append(opening_y(P, Y3, xa, xa+1.02, 4.25, 5.42, '#8FB3C9'))
    o.append(opening_y(P, Y3, 14.7, 15.3, 6.1, 6.6, '#5C6166'))
    # кровля: правый скат не виден, левый скат и торцевой свес
    o.append(poly(P, [(11.6, Y2-0.4, EV-0.2), (XR, Y2-0.4, RG), (XR, Y3+0.4, RG), (11.6, Y3+0.4, EV-0.2)], '#8A3B2E', sw=sw))
    o.append(poly(P, [(11.6, Y3+0.4, EV-0.2), (XR, Y3+0.4, RG), (XR, Y3+0.4, RG-0.16), (11.6, Y3+0.4, EV-0.36)], '#6E2E24', sw=0.3))
    o.append(poly(P, [(XR, Y3+0.4, RG), (18.4, Y3+0.4, EV-0.2), (18.4, Y3+0.4, EV-0.36), (XR, Y3+0.4, RG-0.16)], '#6E2E24', sw=0.3))
    return o
