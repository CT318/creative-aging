# -*- coding: utf-8 -*-
"""台北 v3 八件零件。每件原點在底邊中央附近，y=0 是底座頂面。"""
from geo import *

K = dict(
    far='#A9C1D6', mid='#8FB5A6', near='#7FAE7C', sky='#F3E7D0', bld1='#EFE0C8', bld2='#E3C9B8', bld3='#C9D3DA',
    brick='#C8705A', brick2='#DC9B7C', plaster='#EFDDB6', cream='#F6EBD3', roof='#8A8F9A', win='#8DB7C7',
    wood='#B98A5E', trunk='#94735A', leaf='#78A96C', leaf2='#A3C987', leaf3='#5A9068',
    blue='#3F7CC4', black='#353944', red='#D9503F', white='#F7F3EA', pink='#E77BA2', pink2='#F3A8C1',
    mag='#D2527F', yellow='#EDBE4F', teal='#4FA5A6', tyre='#45474F', seat='#6B564B', grey='#A9AEB3',
    green='#3F9469', bamboo='#DDBB7B', bamboo2='#C39A5E', steam='#E4EBEF', skin='#F0C9A4', cloth='#D9584B',
    ground='#CFC3AE', grass='#A9CC8A',
)

UW = 73.9   # 背板每片寬


def p_backdrop():
    W = UW * 3
    pc = Piece('群山', tabs=[(UW * i + o, 10) for i in range(3) for o in (17, 57)])
    ridge = [(0, 60), (14, 68), (30, 80), (44, 73), (58, 81), (74, 89), (90, 99), (104, 108), (112, 110), (122, 104),
             (134, 96), (148, 90), (160, 95), (172, 85), (186, 75), (200, 79), (212, 67), (W, 61)]
    pc.f(Polygon([(0, 0)] + cr(ridge) + [(W, 0)]), K['far'])
    # 雲
    for (cx, cy, k) in [(52, 70, 1.0), (150, 80, 0.85), (108, 92, 0.7)]:
        pc.f(unary_union([E(cx - 9 * k, cy, 7 * k, 2.6 * k), E(cx, cy + 1.6 * k, 8 * k, 3.6 * k), E(cx + 9 * k, cy + 0.2, 7.5 * k, 2.8 * k)]), '#F4F1EA')
    midr = [(0, 42), (18, 53), (38, 47), (58, 61), (80, 56), (100, 71), (120, 62), (141, 73), (160, 58), (181, 63), (201, 49), (W, 45)]
    pc.f(Polygon([(0, 0)] + cr(midr) + [(W, 0)]), K['mid'])
    nearr = [(0, 27), (24, 35), (50, 29), (76, 39), (100, 32), (126, 41), (150, 31), (176, 37), (200, 29), (W, 31)]
    pc.f(Polygon([(0, 0)] + cr(nearr) + [(W, 0)]), K['near'])
    # 一般樓房（不是地標）
    rng = np.random.default_rng(7)
    x = 3.0
    cols = [K['bld1'], K['bld2'], K['bld3'], K['cream']]
    i = 0
    while x < W - 8:
        w = float(rng.choice([7, 8, 9, 10, 12]))
        h = float(rng.choice([11, 13, 15, 17, 19, 22, 25]))
        if abs(x + w / 2 - UW) < 2.5 or abs(x + w / 2 - 2 * UW) < 2.5:
            h = min(h, 13)
        pc.f(R(x, 0, w, h), cols[i % 4])
        if h >= 17:
            for yy in np.arange(5.5, h - 2, 4.2):
                pc.l(L((x + 1.6, yy), (x + w - 1.6, yy)))
        else:
            pc.l(L((x + w / 2, 4), (x + w / 2, h - 2.5)))
        x += w + float(rng.choice([0, 0, 1.5, 3]))
        i += 1
    # 前排樹
    for i, xx in enumerate(np.arange(4, W - 2, 9.3)):
        r = 3.6 + 1.2 * ((i * 7) % 3) / 2
        pc.f(C(xx + ((i * 5) % 3 - 1), 3.2 + r * 0.55, r), K['leaf3'] if i % 2 else K['leaf'])
    pc.f(R(0, 0, W, 3.2), K['ground'])
    clip = box(0, 0, W, 200)
    pc.items = [(k, g.intersection(clip), c) for k, g, c in pc.items]
    return pc


def p_house():
    pc = Piece('老街屋', tabs=[(-15, 9), (15, 9)])
    # 一樓騎樓
    pc.f(R(-43, 0, 28, 24), K['brick']); pc.f(R(-15, 0, 30, 24), K['brick2']); pc.f(R(15, 0, 28, 24), K['plaster'])
    pc.f(R(-43, 0, 86, 3.5), K['grey'])
    pc.f(R(-53, 0, 10, 40), K['brick']); pc.f(R(43, 0, 10, 40), K['plaster'])
    pc.f(R(-43, 22, 86, 3), K['cream'])
    # 二樓
    pc.f(R(-43, 25, 28, 18), K['brick']); pc.f(R(-15, 25, 30, 18), K['brick2']); pc.f(R(15, 25, 28, 18), K['plaster'])
    for xc in (-35, -23):
        pc.f(arch(xc, 28, 6, 36), K['win']); pc.l(L((xc, 28), (xc, 39)))
        pc.f(R(xc - 4, 26.6, 8, 1.4), K['cream'])
    for xc in (-8.5, 0, 8.5):
        pc.f(arch(xc, 28, 5, 37), K['win'])
    pc.f(R(-12.5, 26.6, 25, 1.4), K['cream'])
    pc.f(R(19.5, 28, 19, 11), K['win'])
    for xx in (25.8, 32.2):
        pc.l(L((xx, 28), (xx, 39)))
    pc.l(L((19.5, 35.5), (38.5, 35.5)))
    pc.f(R(18.5, 26.6, 21, 1.4), K['cream'])
    pc.f(R(-43, 43, 86, 2.2), K['cream'])
    # 女兒牆：三戶各不相同
    pc.f(R(-43, 45.2, 28, 4.6), K['brick']); pc.f(R(-38, 49.8, 18, 4.4), K['brick']); pc.f(R(-34, 54.2, 10, 3), K['brick'])
    pc.f(C(-29, 57.6, 3.4), K['cream'])
    pc.f(R(-15, 45.2, 30, 3.4), K['brick2'])
    pc.f(half(E(0, 48.6, 13.2, 11.2), 48.6), K['brick2'])
    pc.f(C(-13, 49.6, 2.6), K['cream']); pc.f(C(13, 49.6, 2.6), K['cream'])
    pc.f(C(0, 53, 3.6), K['cream']); pc.f(C(0, 61, 2.3), K['cream'])
    pc.f(R(15, 45.2, 28, 5), K['plaster'])
    pc.f(P((19.5, 50.2), (38.5, 50.2), (29, 57.5)), K['cream'])
    pc.f(R(15.4, 50.2, 3.2, 3.6), K['cream']); pc.f(R(39.4, 50.2, 3.2, 3.6), K['cream'])
    for xx in (20, 24.5, 29, 33.5, 38):
        pc.l(L((xx, 46.2), (xx, 49.2)))
    # 磚紋
    for (x0, y0) in [(-41, 30), (-30.5, 33), (-41, 37), (-19, 30.5), (-19, 40), (-41, 47)]:
        pc.l(L((x0, y0), (x0 + 3, y0)))
    # 騎樓拱：鏤空，看得到後面
    for xc, w in ((-29, 18), (0, 20), (29, 18)):
        pc.cut(arch(xc, 3.5, w, 12.5))
        pc.l(L((xc - w / 2 - 2.2, 12.5), (xc - w / 2 - 0.2, 12.5))); pc.l(L((xc + w / 2 + 0.2, 12.5), (xc + w / 2 + 2.2, 12.5)))
    return pc


def p_tree_a():
    pc = Piece('藍鵲與樹', tabs=[(-12, 9), (12, 9)], slot=('top', -3, 55))
    pc.f(half(E(0, 0, 21, 5.2), 0), K['grass'])
    pc.f(P((-5.5, 0), (5.5, 0), (3.2, 12), (2.7, 41), (-2.7, 41), (-3.2, 12)), K['trunk'])
    pc.f(P((1.5, 19), (27, 26.5), (27, 29.2), (1.5, 23.4)), K['trunk'])
    pc.l(L((-1, 6), (-0.6, 30))); pc.l(L((1.4, 10), (1.2, 18)))
    for (x, y, r, c) in [(-14, 50, 12, 'leaf'), (0, 58, 14, 'leaf'), (13, 53, 11, 'leaf3'), (-4, 43.5, 9, 'leaf3'),
                         (-21, 41, 7.5, 'leaf'), (8, 68, 9, 'leaf2'), (-8, 68, 9, 'leaf'), (19, 63, 6.5, 'leaf'),
                         (-25, 52, 6, 'leaf3'), (-12, 56, 7, 'leaf2'), (4, 60, 6.5, 'leaf2'), (14, 50, 4.8, 'leaf')]:
        pc.f(C(x, y, r), K[c])
    # 藍鵲：長尾巴垂在樹枝下面
    pc.f(P((13.4, 31.6), (15.9, 29), (10.6, 9), (7.4, 9.7)), K['blue'])
    pc.f(P((11.5, 12.6), (10.6, 9), (7.4, 9.7), (8.3, 13.4)), K['white'])
    pc.l(L((14.4, 30), (9.6, 13.2)))
    pc.f(E(19, 32.3, 6.9, 4.4, 22), K['blue'])
    pc.l(SL([(14.5, 31.2), (18.5, 30.2), (23, 32.6)]))
    pc.f(C(24.6, 36, 3.4), K['black'])
    pc.f(P((27.2, 37.4), (31.8, 35.6), (27.2, 34.4)), K['red'])
    pc.l(L((18, 28.3), (18, 26.8))); pc.l(L((20.5, 28.6), (20.5, 27.4)))
    return pc


def p_tree_b():
    pc = Piece('樹（側片）', slot=('bot', -2, 55))
    for (x, y, r, c) in [(-8, 50, 10, 'leaf3'), (5, 58, 11, 'leaf'), (11, 46.5, 7, 'leaf2'), (-3, 67, 7.5, 'leaf2'),
                         (-13, 60, 5.5, 'leaf'), (2, 50, 5, 'leaf')]:
        pc.f(C(x, y, r), K[c])
    return pc


def p_stall():
    pc = Piece('夜市攤', tabs=[(-13, 9), (13, 9)])
    pc.f(R(-25, 0, 50, 1.6), K['ground'])
    pc.f(C(-15, 3.3, 3.3), K['tyre']); pc.f(C(15, 3.3, 3.3), K['tyre'])
    pc.f(R(-22, 3.6, 44, 10.6, 1), K['wood'])
    pc.f(R(-22, 11.6, 44, 2.6), K['cream'])
    for xx in (-11, 0, 11):
        pc.l(L((xx, 4.6), (xx, 11.6)))
    pc.f(R(-22, 14, 4, 17), K['wood']); pc.f(R(18, 14, 4, 17), K['wood'])
    # 攤上的東西：湯鍋、老闆
    pc.f(R(-17.2, 14, 10.4, 5.6, 1.2), K['grey']); pc.f(half(E(-12, 19.4, 5.8, 2.6), 19.4), K['roof']); pc.f(C(-12, 22.2, 1.1), K['roof'])
    pc.f(P((0.5, 14), (13.5, 14), (12.4, 20.4), (9.8, 22.4), (4.2, 22.4), (1.6, 20.4)), K['teal'])
    pc.l(L((4.6, 14.2), (4.6, 19.5))); pc.l(L((9.4, 14.2), (9.4, 19.5)))
    pc.f(C(7, 24.0, 2.8), K['skin']); pc.f(half(C(7, 24.4, 3.0), 24.6), K['black'])
    # 遮雨棚：紅白條
    xs_b = np.linspace(-26, 26, 10); xs_t = np.linspace(-22.5, 22.5, 10)
    for i in range(9):
        pc.f(P((xs_b[i], 30.5), (xs_b[i + 1], 30.5), (xs_t[i + 1], 38.5), (xs_t[i], 38.5)), K['cloth'] if i % 2 == 0 else K['white'])
    for i in range(9):
        pc.f(half(C((xs_b[i] + xs_b[i + 1]) / 2, 30.6, 2.85), 30.6, up=False), K['cloth'] if i % 2 == 0 else K['white'])
    # 燈籠
    pc.f(R(-17, 38.5, 34, 2.2), K['wood'])
    for xx, yy in ((-11.5, 43.4), (0, 44.2), (11.5, 43.4)):
        pc.f(E(xx, yy, 4.2, 3.6), K['red'])
        pc.f(R(xx - 1.6, yy + 3.0, 3.2, 1.3), K['yellow']); pc.f(R(xx - 1.6, yy - 4.3, 3.2, 1.3), K['yellow'])
        pc.l(SL([(xx - 2, yy + 3), (xx - 2.9, yy), (xx - 2, yy - 3)])); pc.l(SL([(xx + 2, yy + 3), (xx + 2.9, yy), (xx + 2, yy - 3)]))
    allf = unary_union([g for k, g, c in pc.items if k == 'f'])
    pc.cut(R(-17.6, 14.2, 35.2, 15.6).difference(allf.buffer(0.35)))
    return pc


def p_xlb():
    pc = Piece('小籠包', tabs=[(0, 10)])
    pc.f(R(-17, 0, 34, 1.6), K['ground'])
    pc.f(P((-15, 1), (15, 1), (14, 11.2), (-14, 11.2)), K['cloth'])
    for xx in (-9.5, -4.8, 0, 4.8, 9.5):
        pc.l(L((xx * 1.04, 1.6), (xx, 11)))
    pc.l(L((-14.4, 6.2), (14.4, 6.2)))
    pc.f(R(-16, 11, 32, 2.2), K['wood'])
    for i, dx in enumerate((-0.6, 0.8, 0)):
        y = 13.2 + i * 5.2
        pc.f(R(-11 + dx, y, 22, 5.2, 1), K['bamboo'] if i != 1 else K['bamboo2'])
        pc.l(L((-10 + dx, y + 2.6), (10 + dx, y + 2.6)))
    # 最上層打開：看得到三顆小籠包
    for xx in (-6.2, 0.4, 6.8):
        pc.f(half(E(xx, 28.6, 3.7, 3.9), 28.6), K['white'])
        pc.l(L((xx - 1.4, 30.4), (xx, 32.2))); pc.l(L((xx + 1.4, 30.4), (xx, 32.2)))
    # 蒸氣
    for (x, y, r) in [(-9.5, 33.4, 3.0), (-12.6, 36.6, 3.3), (-9.6, 39.8, 2.8), (-12.4, 42.6, 2.2)]:
        pc.f(C(x, y, r), K['steam'])
    pc.items = [(k, AF.scale(g, 0.82, 0.82, origin=(0, 0)), c) for k, g, c in pc.items]
    return pc


def _box(x, col, legh, ang):
    g = []
    g.append((R(x - 2, 0, 4, legh), K['grey']))
    g.append((R(x - 5, legh - 0.4, 10, 9.6, 1.6), col))
    g.append((half(E(x, legh + 9, 5, 3.4), legh + 9), col))
    ls = [L((x - 3, legh + 6.6), (x + 3, legh + 6.6)), L((x - 2.6, legh + 1.6), (x + 2.6, legh + 1.6)),
          L((x - 2.6, legh + 3.8), (x + 2.6, legh + 3.8)), L((x - 2.6, legh + 1.6), (x - 2.6, legh + 3.8)), L((x + 2.6, legh + 1.6), (x + 2.6, legh + 3.8))]
    return [(rot(a, ang, (x, 0)), c) for a, c in g], [rot(a, ang, (x, 0)) for a in ls]


def p_mail():
    pc = Piece('歪腰郵筒', tabs=[(0, 10)])
    pc.f(R(-14, 0, 28, 1.6), K['ground'])
    pc.f(half(E(-10.5, 1.2, 4, 3), 1.2), K['grass']); pc.f(half(E(12, 1.2, 3, 2.4), 1.2), K['grass'])
    for x, col, lh, ang in ((-5, K['green'], 9.5, -15), (6.5, K['red'], 11, -8)):
        fs, ls = _box(x, col, lh, ang)
        for g, c in fs:
            pc.f(g, c)
        for l_ in ls:
            pc.l(l_)
    return pc


def p_scooter():
    pc = Piece('機車', tabs=[(-9, 8), (8.5, 8)])
    pc.f(R(-19, 0, 35, 1.5), K['ground'])
    pc.f(C(-10, 4.5, 4.5), K['tyre']); pc.f(C(-10, 4.5, 1.7), K['grey'])
    pc.f(C(11, 4.5, 4.5), K['tyre']); pc.f(C(11, 4.5, 1.7), K['grey'])
    pc.f(half(C(11, 4.5, 6.1), 5.6).difference(C(11, 4.5, 4.6)), K['teal'])
    pc.f(P((9.4, 5.6), (12.1, 5.6), (12.7, 11.4), (10.6, 11.4)), K['tyre'])
    pc.f(P((-16.8, 9.6), (-15.9, 13.8), (-3.4, 13.8), (-1.4, 10), (0.6, 7.3), (6.6, 7.3), (6.6, 4.8), (-4.4, 4.8),
           (-5, 7.6), (-7, 9.8), (-13, 9.8)), K['teal'])
    pc.l(L((-13.5, 11.6), (-4, 11.6)))
    pc.f(P((6, 5), (9.3, 5), (12.8, 16.8), (10.3, 18.2), (8, 10.2)), K['teal'])
    pc.f(R(-13.6, 13.5, 11.4, 2.9, 1.2), K['seat'])
    pc.f(R(-19.5, 13.6, 8, 7.6, 1), K['cream']); pc.l(L((-18.2, 18.6), (-13.2, 18.6)))
    pc.f(C(-5.6, 18.7, 3.1), K['yellow']); pc.l(SL([(-5.2, 20.6), (-3.4, 19.4), (-3.2, 17.4)]))
    pc.f(E(11.4, 18.4, 2.8, 2.4), K['teal']); pc.f(C(13.4, 18.2, 1.3), K['yellow'])
    pc.f(P((8.4, 19.8), (12.6, 19.8), (12.6, 21.5), (7.8, 21.9)), K['tyre'])
    pc.f(P((9.6, 21.2), (12.6, 21.2), (13.6, 24.4), (10.6, 24.7)), K['tyre']); pc.f(C(12.2, 25.6, 2.2), K['grey'])
    return pc


def _azalea(pc, base, bumps, flowers):
    pc.f(base, K['leaf3'])
    for i, (x, y, r) in enumerate(bumps):
        pc.f(C(x, y, r), K['leaf'] if i % 2 else K['leaf3'])
    for i, (x, y) in enumerate(flowers):
        pc.f(C(x, y, 2.9), (K['pink'], K['pink2'], K['mag'])[i % 3])
        pc.f(C(x, y, 0.95), K['yellow'])
        for a in range(0, 360, 72):
            pc.l(rot(L((x, y + 1.3), (x, y + 2.6)), a + i * 20, (x, y)))


def p_azalea_a():
    pc = Piece('杜鵑花', tabs=[(-14, 9), (16, 9)], slot=('top', 6, 7.5))
    _azalea(pc, R(-23, 0, 46, 6), [(-18, 7, 6.5), (-9, 9, 7.5), (1, 8, 7), (10, 10, 7.5), (18, 7.5, 6)],
            [(-19, 11.5), (-12, 15), (-5, 12), (1, 15), (9, 16.4), (15, 12.5), (20.5, 10), (-1.5, 6.5), (12, 6.5), (-13, 6)])
    return pc


def p_azalea_b():
    pc = Piece('杜鵑花（側片）', slot=('bot', -2, 7.5))
    _azalea(pc, R(-12, 0, 24, 5), [(-7, 7, 6), (1, 9, 7), (8, 6.5, 5.5)], [(-8, 11), (-0.5, 14.6), (5.5, 11.6), (10, 8), (-3.5, 6.5)])
    return pc


# 編號＝組裝順序（由後往前）；(名稱, 函式, 中心 x, 深度 y, 第幾週)
LAYOUT = [
    (1, '群山', p_backdrop, None, None, 1),
    (2, '老街屋', p_house, 0, 46, 2),
    (3, '藍鵲與樹', p_tree_a, -29, 26, 2),
    (4, '夜市攤', p_stall, 33, 5, 3),
    (5, '小籠包', p_xlb, -23, 3, 3),
    (6, '歪腰郵筒', p_mail, -46, -15, 3),
    (7, '機車', p_scooter, 22, -32, 4),
    (8, '杜鵑花', p_azalea_a, -12, -56, 4),
]
CROSS = {3: p_tree_b, 8: p_azalea_b}


# ================= 第 2 版修正（平面設計師審查後） =================
K.update(far='#C9D6E2', mid='#A9C6C0', near='#8FB894', leaf='#5F9C54', leaf2='#93C26C', leaf3='#3F7F50',
         scoot='#E9A63A', helmet='#D9503F')
_bd0 = p_backdrop


def p_backdrop():
    pc = _bd0()
    its = []
    for k, g, c in pc.items:
        if c == '#F4F1EA':
            continue                       # 拿掉雲
        if c == K['far'] and k == 'f':
            g = AF.scale(g, 1, 0.88, origin=(0, 0))
        its.append((k, g, c))
    pc.items = its
    return pc


def _ty(y):
    return 47 + (y - 41) * 1.25


def p_tree_a():
    pc = Piece('藍鵲與樹', tabs=[(-12, 9), (12, 9)], slot=('top', -3, _ty(55)))
    pc.f(half(E(0, 0, 21, 5.2), 0), K['grass'])
    pc.f(P((-5.5, 0), (5.5, 0), (3.3, 12), (2.8, 48), (-2.8, 48), (-3.3, 12)), K['trunk'])
    pc.f(P((1.5, 27), (31, 37.5), (31, 40.3), (1.5, 31.6)), K['trunk'])
    pc.l(L((-1, 6), (-0.6, 36)))
    for (x, y, r, c) in [(-14, 50, 12, 'leaf'), (0, 58, 14, 'leaf'), (13, 53, 11, 'leaf3'), (-4, 43.5, 9, 'leaf3'),
                         (-21, 41, 7.5, 'leaf'), (8, 68, 9, 'leaf2'), (-8, 68, 9, 'leaf'), (19, 63, 6.5, 'leaf'),
                         (-25, 52, 6, 'leaf3'), (-12, 56, 7, 'leaf2'), (4, 60, 6.5, 'leaf2')]:
        pc.f(C(x, _ty(y), r), K[c])
    # 台灣藍鵲：長尾、尾端白斑、紅嘴
    pc.f(P((16.6, 44.4), (20.2, 41.2), (13.3, 19.3), (8.6, 20.5)), K['blue'])
    pc.f(P((14.5, 23), (13.3, 19.3), (8.6, 20.5), (9.8, 24.2)), K['white'])
    pc.f(P((15.2, 30), (14.2, 27), (10.9, 27.9), (11.9, 31)), K['white'])
    pc.f(E(23, 44.6, 6.9, 4.4, 22), K['blue'])
    pc.l(SL([(18.5, 43.5), (22.5, 42.5), (27, 44.9)]))
    pc.f(C(28.6, 48.3, 3.4), K['black'])
    pc.f(P((31.2, 49.7), (35.8, 47.9), (31.2, 46.7)), K['red'])
    return pc


def p_tree_b():
    pc = Piece('樹（側片）', tabs=[(9, 9)], slot=('bot', -2, _ty(55)))
    pc.f(half(E(9, 0, 9.5, 3.6), 0), K['grass'])
    pc.f(P((6.2, 0), (11.8, 0), (10.6, 52), (7.4, 52)), K['trunk'])
    for (x, y, r, c) in [(-8, 50, 10, 'leaf3'), (5, 58, 11, 'leaf'), (11, 46.5, 7, 'leaf2'), (-3, 67, 7.5, 'leaf2'),
                         (-13, 60, 5.5, 'leaf'), (2, 50, 5, 'leaf')]:
        pc.f(C(x, _ty(y), r), K[c])
    return pc


def p_xlb():
    """兩層蒸籠開蓋，三顆有摺子的大包子，放在小木桌上。"""
    pc = Piece('小籠包', tabs=[(0, 10)])
    pc.f(R(-14, 0, 28, 1.6), K['ground'])
    pc.f(R(-12.5, 1, 3, 5.5), K['wood']); pc.f(R(9.5, 1, 3, 5.5), K['wood'])
    pc.f(R(-14, 6, 28, 2.4), K['wood'])
    pc.f(R(-11.5, 8.4, 23, 5.4, 1), K['bamboo2']); pc.l(L((-10.5, 11.1), (10.5, 11.1)))
    pc.f(R(-11, 13.8, 22, 5.4, 1), K['bamboo']); pc.l(L((-10, 16.5), (10, 16.5)))
    for xx in (-6.6, 0, 6.6):
        pc.f(half(E(xx, 19.2, 3.9, 4.6), 19.2), K['white'])
        for dx in (-1.6, 0, 1.6):
            pc.l(L((xx + dx, 20.6), (xx + dx * 0.3, 23.2)))
    pc.f(rot(E(-14.6, 15.5, 2.3, 8), 16, (-14.6, 8.4)), K['bamboo2']); pc.f(C(-18.6, 16.5, 1.6), K['wood'])
    for (x, y, r) in [(9.6, 24.2, 2.6), (12, 27.2, 2.9), (9.4, 30, 2.3)]:
        pc.f(C(x, y, r), K['steam'])
    return pc


_sc0 = p_scooter


def p_scooter():
    pc = _sc0()
    its = []
    for k, g, c in pc.items:
        if c == K['teal']:
            c = K['scoot']
        elif c == K['yellow'] and k == 'f' and g.area > 20:
            c = K['helmet']
        its.append((k, AF.scale(g, 0.9, 0.9, origin=(0, 0)), c))
    pc.items = its
    pc.tabs = [(-8, 8), (7.5, 8)]
    return pc


def _azalea(pc, base, bumps, flowers):
    pc.f(base, K['leaf3'])
    for i, (x, y, r) in enumerate(bumps):
        pc.f(C(x, y, r), K['leaf'] if i % 2 else K['leaf3'])
    for i, (x, y) in enumerate(flowers):
        col = (K['pink'], K['pink2'], K['mag'])[i % 3]
        pc.f(unary_union([C(x + 2.0 * np.sin(np.radians(a + i * 25)), y + 2.0 * np.cos(np.radians(a + i * 25)), 1.9) for a in range(0, 360, 72)]), col)
        pc.f(C(x, y, 1.0), K['mag'] if i % 3 != 2 else K['pink2'])


def p_azalea_a():
    pc = Piece('杜鵑花', tabs=[(-14, 9), (16, 9)], slot=('top', 4, 7.5))
    _azalea(pc, R(-23, 0, 46, 6), [(-18, 7, 6.5), (-9, 9, 7.5), (1, 8, 7), (10, 10, 7.5), (18, 7.5, 6)],
            [(-18.5, 11.5), (-10.5, 15), (-2.5, 12.5), (10.5, 16), (17.5, 11), (0, 5.5), (12.5, 7), (-11, 6.5)])
    return pc


def p_azalea_b():
    pc = Piece('杜鵑花（側片）', slot=('bot', -2, 7.5))
    _azalea(pc, R(-12, 0, 24, 5), [(-7, 7, 6), (1, 9, 7), (8, 6.5, 5.5)], [(-7.5, 10.5), (1.5, 14), (8, 9), (-1, 6)])
    return pc


LAYOUT = [
    (1, '群山', p_backdrop, None, None, 1),
    (2, '老街屋', p_house, 2, 40, 2),
    (3, '藍鵲與樹', p_tree_a, -30, 22, 2),
    (4, '夜市攤', p_stall, 34, 6, 3),
    (5, '小籠包', p_xlb, -8, 2, 3),
    (6, '歪腰郵筒', p_mail, -50, -24, 3),
    (7, '機車', p_scooter, 30, -43, 4),
    (8, '杜鵑花', p_azalea_a, -8, -61, 4),
]
CROSS = {3: p_tree_b, 8: p_azalea_b}
