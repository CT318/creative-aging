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


# ================= v4：文青線稿風（低彩度、線條細緻） =================
K.update(far='#CBD5D6', mid='#AFC1B6', near='#93AB98', bld1='#EFE5D2', bld2='#E3CFBE', bld3='#D7DBD7', cream='#F3E8D2',
         brick='#C47B62', brick2='#DBA58E', plaster='#EADBBB', win='#A3BAC4', roof='#8F9195', wood='#B8926A',
         trunk='#927660', leaf='#93AD86', leaf2='#B8CAA2', leaf3='#6E9075', grass='#B9C9A0',
         blue='#4F7BAA', black='#3B404A', red='#C7553F', white='#FBF7EE', pink='#DF93A6', pink2='#EFBFC6', mag='#C2647F',
         yellow='#DBA945', teal='#6FA3A0', tyre='#4B4A4D', seat='#7B6453', grey='#B7B3AC', green='#4F8C6C',
         bamboo='#DCC18E', bamboo2='#C6A570', skin='#ECCBA9', cloth='#C7553F', ground='#D8CEBC',
         scoot='#A9C2B4', helmet='#DBA945')


def _arc(x, y, r, a0=20, a1=160, n=8):
    return L(*[(x + r * np.cos(np.radians(a)), y + r * np.sin(np.radians(a))) for a in np.linspace(a0, a1, n)])


def p_backdrop():
    W = UW * 3
    pc = Piece('群山', tabs=[(UW * i + o, 10) for i in range(3) for o in (17, 57)])
    ridge = [(0, 53), (14, 60), (30, 70), (44, 64), (58, 71), (74, 78), (90, 87), (104, 95), (112, 97), (122, 92),
             (134, 84), (148, 79), (160, 84), (172, 75), (186, 66), (200, 70), (212, 59), (W, 54)]
    pc.f(Polygon([(0, 0)] + cr(ridge) + [(W, 0)]), K['far'])
    midr = [(0, 42), (18, 53), (38, 47), (58, 61), (80, 56), (100, 71), (120, 62), (141, 73), (160, 58), (181, 63), (201, 49), (W, 45)]
    pc.f(Polygon([(0, 0)] + cr(midr) + [(W, 0)]), K['mid'])
    nearr = [(0, 27), (24, 35), (50, 29), (76, 39), (100, 32), (126, 41), (150, 31), (176, 37), (200, 29), (W, 31)]
    pc.f(Polygon([(0, 0)] + cr(nearr) + [(W, 0)]), K['near'])
    rng = np.random.default_rng(3)
    for _ in range(46):
        x = float(rng.uniform(6, W - 6)); y = float(rng.uniform(24, 62))
        pc.l(_arc(x, y, 2.2, 30, 150, 5))
    x = 4.0; i = 0
    cols = [K['bld1'], K['bld2'], K['bld3'], K['cream']]
    while x < W - 12:
        w = float(rng.choice([10, 12, 14])); h = float(rng.choice([9, 11, 13, 16]))
        if (x - 2 < UW < x + w + 2) or (x - 2 < 2 * UW < x + w + 2):
            x += 3; continue
        pc.f(R(x, 0, w, h), cols[i % 4])
        if i % 3 == 0:
            pc.f(P((x - 1, h), (x + w + 1, h), (x + w / 2, h + 4.5)), K['brick'])
        else:
            pc.f(R(x - 0.8, h, w + 1.6, 1.6), K['roof'])
        for xx in np.arange(x + 2.6, x + w - 2, 3.4):
            pc.l(L((xx, 4.4), (xx, h - 2.6)))
        x += w + float(rng.choice([2.5, 4, 9])); i += 1
    for xx in (30, 96, 131, 190):
        pc.f(SP([(xx - 4, 3), (xx - 5, 8), (xx - 2, 12), (xx + 2, 12.6), (xx + 5, 9), (xx + 4, 3)]), K['leaf3'])
    pc.f(R(0, 0, W, 3.2), K['ground'])
    clip = box(0, 0, W, 200)
    pc.items = [(k, g.intersection(clip), c) for k, g, c in pc.items]
    return pc


CAN_A = [(-20, 46), (-28, 52), (-30, 62), (-25, 70), (-27, 79), (-19, 87), (-9, 88), (-3, 94), (8, 93), (14, 87), (23, 84),
         (27, 74), (24, 66), (28, 57), (22, 49), (12, 48), (6, 44), (-4, 47), (-12, 44)]
TSLOT = 68


def p_tree_a():
    pc = Piece('藍鵲與樹', tabs=[(-12, 9), (12, 9)], slot=('top', -3, TSLOT))
    pc.f(half(E(0, 0, 20, 4.6), 0), K['grass'])
    pc.f(P((-5, 0), (5, 0), (3.2, 10), (2.9, 34), (9.5, 47), (6.6, 49), (0.8, 40), (-4, 51), (-6.8, 49.5), (-2.9, 36), (-3.2, 10)), K['trunk'])
    pc.f(P((2, 24), (29, 33.6), (29, 36.2), (2, 28.2)), K['trunk'])
    pc.l(SL([(-1.2, 4), (-0.4, 18), (-0.8, 33)])); pc.l(SL([(1.6, 8), (1.4, 20)]))
    pc.f(SP(CAN_A), K['leaf'])
    pc.f(SP([(0, 51), (12, 52), (22, 56), (23, 64), (15, 63), (7, 67), (-1, 61), (-10, 63), (-19, 57), (-13, 51), (-5, 53)]), K['leaf3'])
    pc.f(SP([(-15, 75), (-7, 81), (4, 84), (11, 79), (4, 75), (-4, 77), (-10, 71)]), K['leaf2'])
    for (x, y) in [(-22, 60), (-18, 66), (-20, 78), (-10, 84), (0, 88), (8, 88), (16, 82), (20, 75), (18, 68), (-4, 68), (6, 72), (-12, 56), (12, 58), (2, 56)]:
        pc.l(_arc(x, y, 2.4, 25, 155, 6))
    pc.f(P((15.6, 40.6), (18.4, 38.6), (12.6, 17.6), (9.0, 18.6)), K['blue'])
    pc.f(P((13.7, 21.6), (12.6, 17.6), (9.0, 18.6), (10.1, 22.6)), K['white'])
    pc.f(P((15.3, 27.4), (14.6, 24.8), (10.9, 25.8), (11.7, 28.4)), K['white'])
    pc.f(SP([(14.4, 40.2), (17, 37.3), (21.5, 36.9), (25, 39), (26.6, 42.6), (24, 44.4), (19, 43.8)]), K['blue'])
    pc.l(SL([(16.5, 40.2), (20.5, 39.2), (24, 41)]))
    pc.f(C(26.4, 44.8, 3.0), K['black'])
    pc.f(P((28.7, 45.9), (32.8, 44.4), (28.7, 43.3)), K['red'])
    return pc


def p_tree_b():
    pc = Piece('樹的側片', tabs=[(9, 9)], slot=('bot', -2, TSLOT))
    pc.f(half(E(9, 0, 9.5, 3.6), 0), K['grass'])
    pc.f(P((6.2, 0), (11.8, 0), (10.6, 54), (7.4, 54)), K['trunk'])
    pc.f(SP([(-14, 51), (-18, 61), (-13, 71), (-15, 79), (-6, 85), (4, 83), (12, 77), (11, 67), (15, 59), (10, 51), (0, 48), (-7, 50)]), K['leaf'])
    pc.f(SP([(-10, 54), (0, 52), (9, 55), (10, 62), (2, 60), (-6, 63), (-12, 59)]), K['leaf3'])
    for (x, y) in [(-10, 68), (-4, 76), (4, 76), (6, 68), (-8, 60), (2, 66)]:
        pc.l(_arc(x, y, 2.4, 25, 155, 6))
    return pc


def p_xlb():
    pc = Piece('小籠包', tabs=[(0, 10)])
    pc.f(R(-14, 0, 28, 1.6), K['ground'])
    pc.f(R(-12.5, 1, 3, 5.5), K['wood']); pc.f(R(9.5, 1, 3, 5.5), K['wood'])
    pc.f(R(-14, 6, 28, 2.4), K['wood'])
    for i, (x0, w) in enumerate(((-11.5, 23), (-11, 22))):
        y = 8.4 + i * 5.4
        pc.f(R(x0, y, w, 5.4, 1.2), K['bamboo2'] if i == 0 else K['bamboo'])
        pc.l(L((x0 + 1, y + 1.5), (x0 + w - 1, y + 1.5))); pc.l(L((x0 + 1, y + 3.9), (x0 + w - 1, y + 3.9)))
        for xx in np.arange(x0 + 3, x0 + w - 2, 3.2):
            pc.l(L((xx, y + 1.5), (xx, y + 3.9)))
    for xx in (-6.6, 0, 6.6):
        pc.f(half(E(xx, 19.2, 3.9, 5.2), 19.2), K['white'])
        pc.f(C(xx, 24.6, 1.0), K['white'])
        for dx in (-1.9, -0.6, 0.6, 1.9):
            pc.l(L((xx + dx, 20.2), (xx + dx * 0.25, 23.6)))
    return pc


def p_scooter():
    pc = Piece('機車', tabs=[(-8, 8), (8, 8)])
    B_ = K['scoot']
    pc.f(R(-19, 0, 35, 1.5), K['ground'])
    for cx in (-10.5, 11.5):
        pc.f(C(cx, 4.6, 4.6), K['tyre']); pc.f(C(cx, 4.6, 2.2), K['grey']); pc.f(C(cx, 4.6, 0.8), K['tyre'])
    pc.f(half(C(11.5, 4.6, 6.3), 5.8).difference(C(11.5, 4.6, 4.75)), B_)
    pc.f(P((10.2, 6), (12.7, 6), (13, 11), (11, 11)), K['tyre'])
    pc.f(SP([(-17.4, 8.6), (-17.6, 12.6), (-14, 15), (-4, 15), (-1.4, 12), (0.6, 8.6), (1.2, 5.6), (-4.6, 5.2), (-6.2, 9.4), (-10.5, 10.8), (-15, 9.8)]), B_)
    pc.f(R(-2, 5, 10.5, 2.5, 0.8), B_)
    pc.l(SL([(-15, 12.2), (-9, 12.8), (-3.6, 12.2)]))
    pc.f(SP([(6.6, 5.2), (10, 5.2), (11.4, 10), (13.4, 17), (11.8, 19.2), (9.4, 17.6), (7.6, 11)]), B_)
    pc.f(R(-13.6, 14.6, 12.4, 3.1, 1.4), K['seat'])
    pc.f(R(-20.2, 14.4, 8, 7.8, 1.3), K['cream']); pc.l(L((-19.2, 19.2), (-13.2, 19.2)))
    pc.f(C(-5.2, 20.3, 3.2), K['helmet']); pc.l(SL([(-4.6, 22.4), (-2.8, 21), (-2.6, 18.8)]))
    pc.f(E(12.2, 19.8, 2.7, 2.3), B_); pc.f(C(14.1, 19.6, 1.35), K['cream'])
    pc.f(P((8.6, 21.2), (13.2, 21.2), (13.2, 23), (8.2, 23.4)), K['tyre'])
    pc.f(P((9.8, 22.8), (12.8, 22.8), (13.8, 25.8), (10.8, 26.1)), K['tyre']); pc.f(C(12.4, 27, 2.2), K['grey'])
    pc.items = [(k, AF.scale(g, 0.92, 0.92, origin=(0, 0)), c) for k, g, c in pc.items]
    return pc


def _flower(pc, x, y, i, r=2.1):
    col = (K['pink'], K['pink2'], K['mag'])[i % 3]
    pc.f(unary_union([C(x + r * np.sin(np.radians(a + i * 25)), y + r * np.cos(np.radians(a + i * 25)), r * 0.98) for a in range(0, 360, 72)]), col)
    pc.f(C(x, y, 0.9), K['mag'] if i % 3 != 2 else K['yellow'])


def _hedge(pc, top, flowers, leaves):
    pc.f(Polygon([(top[0][0], 0)] + cr(top) + [(top[-1][0], 0)]).buffer(0), K['leaf3'])
    for (x, y) in leaves:
        pc.f(SP([(x - 3.2, y), (x, y + 1.9), (x + 3.2, y), (x, y - 1.9)]), K['leaf'])
        pc.l(L((x - 2.4, y), (x + 2.4, y)))
    for i, (x, y) in enumerate(flowers):
        _flower(pc, x, y, i)


def p_azalea_a():
    pc = Piece('杜鵑花', tabs=[(-14, 9), (16, 9)], slot=('top', 4, 7.5))
    _hedge(pc, [(-23, 0), (-24, 7), (-20, 12), (-14, 11.5), (-10, 15), (-3, 13.5), (2, 16), (9, 14.5), (14, 17), (20, 12.5), (24, 8), (23, 0)],
           [(-18, 9.5), (-9.5, 13.5), (-1, 9.5), (9.5, 14.2), (17, 9), (9, 6.2), (-10, 5.4)],
           [(-14, 6.5), (-4, 5), (3.6, 11.6), (14.6, 4.6), (-20, 4.4), (1.5, 4.2), (20, 5)])
    return pc


def p_azalea_b():
    pc = Piece('花叢側片', slot=('bot', -2, 7.5))
    _hedge(pc, [(-12, 0), (-12.6, 6), (-8, 11), (-2, 12.5), (4, 14.5), (9, 11), (12, 6), (11.6, 0)],
           [(-7, 7.5), (2, 10.8), (7.5, 6.2)], [(-1, 4.6), (-8, 3.4), (6.5, 2.8)])
    return pc


LAYOUT = [
    (1, '群山', p_backdrop, None, None, 1),
    (2, '老街屋', p_house, 2, 40, 2),
    (3, '夜市攤', p_stall, 34, 6, 2),
    (4, '藍鵲與樹', p_tree_a, -30, 22, 3),
    (5, '小籠包', p_xlb, -8, 2, 3),
    (6, '歪腰郵筒', p_mail, -50, -24, 4),
    (7, '機車', p_scooter, 30, -43, 4),
    (8, '杜鵑花', p_azalea_a, -8, -61, 4),
]
CROSS = {4: p_tree_b, 8: p_azalea_b}
CAPTION = {1: '台北是盆地，四面環山', 2: '紅磚拱廊的老街', 4: '長尾巴的台灣藍鵲，台北市鳥', 3: '天黑以後最熱鬧',
           5: '剛蒸好，小心燙', 6: '被颱風吹歪的一對郵筒', 7: '街頭最常見的風景', 8: '三月盛開，台北市花'}
CAPTION_B = {4: '和大樹十字交叉', 8: '和花叢十字交叉'}


# ================= v4.1：依專業設計師第一輪意見重畫 =================
K.update(far='#B9C8BF', mid='#93AEA3', near='#6F9186', bld1='#F6EFE2', bld2='#E6D5C3', bld3='#D9D2C4', cream='#F6EFE2',
         brick='#B5543C', brick2='#D4927C', plaster='#EADFC8', win='#B9C8BF', roof='#8D857A', wood='#B08F68',
         trunk='#8D7460', leaf='#8FA88B', leaf2='#B1C3A8', leaf3='#55705C', grass='#B1C3A8',
         blue='#3E5C86', blue2='#32507A', black='#33363C', red='#B5543C', white='#F6EFE2', pink='#E2A7A0', pink2='#EBC3BC', mag='#C9756F',
         yellow='#D8A444', teal='#8FA88B', tyre='#4A4540', seat='#6E5A4B', grey='#C9C2B6', green='#55705C',
         bamboo='#DDC79B', bamboo2='#C8AC78', skin='#EAC9A8', cloth='#B5543C', ground='#D9D2C4',
         scoot='#D8A444', helmet='#B5543C')


def _tick(x, y, n=3, a=60, ln=2.0):
    """一組短葉形筆觸。"""
    out = []
    for i in range(n):
        ang = np.radians(a + (i - (n - 1) / 2) * 32)
        out.append(L((x + i * 0.9, y), (x + i * 0.9 + ln * np.cos(ang), y + ln * np.sin(ang))))
    return out


def _clump(cx, cy, Rr, seed):
    rng = np.random.default_rng(seed)
    n = int(rng.integers(7, 10))
    gs = [C(cx, cy, Rr * 0.86)]
    for i in range(n):
        a = 2 * np.pi * i / n + rng.uniform(-0.2, 0.2)
        r = Rr * rng.uniform(0.30, 0.46)
        gs.append(C(cx + (Rr - r * 0.75) * np.cos(a), cy + (Rr - r * 0.75) * np.sin(a) * 0.9, r))
    return unary_union(gs)


def p_backdrop():
    W = UW * 3
    pc = Piece('群山', tabs=[(UW * i + o, 10) for i in range(3) for o in (17, 57)])
    ridge = [(0, 50), (16, 58), (34, 66), (52, 74), (70, 88), (88, 97), (100, 92), (116, 80), (132, 74), (150, 78), (166, 70), (184, 62), (200, 64), (214, 56), (W, 52)]
    midr = [(0, 40), (22, 48), (40, 44), (64, 60), (84, 54), (104, 62), (128, 56), (150, 66), (170, 52), (190, 56), (206, 44), (W, 42)]
    nearr = [(0, 26), (30, 34), (56, 28), (82, 36), (110, 30), (140, 40), (165, 30), (192, 34), (W, 28)]
    for r_, c in ((ridge, 'far'), (midr, 'mid'), (nearr, 'near')):
        pc.f(Polygon([(0, 0)] + cr(r_) + [(W, 0)]), K[c])
    rng = np.random.default_rng(5)
    for _ in range(26):
        x = float(rng.uniform(8, W - 12)); y = float(rng.uniform(18, 70)); w = float(rng.uniform(3, 6))
        pc.l(SL([(x, y), (x + w / 2, y + 0.5), (x + w, y)]))
    x = 6.0; i = 0
    cols = [K['bld1'], K['bld2'], K['bld3']]
    while x < W - 14:
        w = float(rng.choice([11, 13, 15])); h = float(rng.choice([9, 11, 14]))
        if (x - 2 < UW < x + w + 2) or (x - 2 < 2 * UW < x + w + 2):
            x += 3; continue
        pc.f(R(x, 0, w, h), cols[i % 3])
        if i % 2 == 0:
            pc.f(P((x - 1, h), (x + w + 1, h), (x + w / 2, h + 4.6)), K['brick'])
        else:
            pc.f(R(x - 0.8, h, w + 1.6, 1.6), K['roof'])
        for xx in (x + w * 0.3, x + w * 0.7):
            pc.f(R(xx - 1.2, 3.6, 2.4, h - 6.4), K['win'])
        x += w + float(rng.choice([10, 16, 22])); i += 1
    pc.f(R(0, 0, W, 3.0), K['ground'])
    clip = box(0, 0, W, 200)
    pc.items = [(k, g.intersection(clip), c) for k, g, c in pc.items]
    return pc


_h0 = p_house


def p_house():
    pc = _h0()
    for (x0, x1, y0, y1) in [(-42, -16, 26, 42), (-52, -44, 4, 38)]:
        for j, yy in enumerate(np.arange(y0 + 2.5, y1, 3.2)):
            for xx in np.arange(x0 + (1.5 if j % 2 else 4.5), x1 - 3, 9):
                pc.l(L((xx, yy), (xx + 3.2, yy)))
    for xc in (-38, -20, -10, 10, 20, 38):
        pc.f(R(xc - 2.6, 11.6, 5.2, 1.8), K['cream'])
    return pc


TSLOT = 54


def p_tree_a():
    pc = Piece('藍鵲與樹', tabs=[(-10, 9), (10, 9)], slot=('top', -2, TSLOT))
    pc.f(half(E(0, 0, 18, 4.2), 0), K['grass'])
    pc.f(P((-6, 0), (6, 0), (3.8, 8), (3.2, 22), (5.6, 30), (10.4, 38), (7.8, 40), (3, 34), (0.8, 31.4), (-0.2, 41), (-3, 41), (-2.6, 30.5),
           (-6.2, 37.4), (-8.6, 36), (-4.2, 27), (-3.6, 8)), K['trunk'])
    pc.f(P((3, 17.6), (27, 27.4), (27, 30), (3, 22)), K['trunk'])
    pc.l(SL([(-1.4, 3), (-0.6, 14), (-1, 26)])); pc.l(SL([(1.6, 6), (1.2, 16)])); pc.l(SL([(-3.6, 2.4), (-2.6, 8)]))
    for i, (x, y, r, c) in enumerate([(-12, 44, 7.6, 'leaf3'), (9, 46, 8, 'leaf3'), (-2, 51, 8.6, 'leaf'), (16, 56, 6.2, 'leaf'),
                                       (-13, 57, 6.6, 'leaf'), (2, 63, 7.2, 'leaf2'), (-5, 40.5, 5.4, 'leaf3')]):
        pc.f(_clump(x, y, r, 11 + i), K[c])
    for (x, y, a) in [(-14, 44, 70), (8, 46, 100), (-3, 52, 80), (15, 56, 60), (-14, 58, 110), (1, 64, 90), (-6, 46, 60), (11, 50, 120)]:
        for l_ in _tick(x, y, 3, a):
            pc.l(l_)
    # 台灣藍鵲：黑頭胸、紅嘴紅腳、長尾白斑
    la, lb, ra, rb = (14.8, 33.2), (9.8, 12.6), (17.2, 31), (12.6, 12)
    pc.f(P(la, ra, rb, (11, 6.4), lb), K['blue'])
    mix = lambda p, q, t: (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    for t0, t1 in ((0.42, 0.52), (0.64, 0.74), (0.86, 1.0)):
        pc.f(P(mix(la, lb, t0), mix(ra, rb, t0), mix(ra, rb, t1), mix(la, lb, t1)), K['white'])
    pc.f(P(lb, rb, (11, 6.4)), K['white'])
    pc.l(L(mix(la, ra, 0.5), (11.2, 12.3)))
    for x in (18.6, 21.4):
        pc.f(P((x, 30.4), (x + 1.1, 30.4), (x + 0.9, 27.2), (x - 0.1, 27.2)), K['red'])
    pc.f(SP([(14.5, 32.6), (17, 30), (21.5, 29.8), (25, 32), (26.6, 35.4), (24.6, 37.2), (19.5, 36.4)]), K['blue'])
    pc.f(SP([(16, 33.6), (19.5, 31.3), (23.2, 32.4), (20.6, 34.8)]), K['blue2'])
    pc.f(SP([(22.4, 37.2), (25.2, 39.8), (28.2, 38.6), (28.8, 35.6), (26.8, 32.4), (24.2, 32.8), (23, 35)]), K['black'])
    pc.f(P((28.2, 38), (32.2, 36.5), (28.5, 35.6)), K['red'])
    pc.f(C(26.3, 37.5, 0.6), K['yellow'])
    return pc


def p_tree_b():
    pc = Piece('樹的側片', tabs=[(9, 9)], slot=('bot', -2, TSLOT))
    pc.f(half(E(9, 0, 9.5, 3.6), 0), K['grass'])
    pc.f(P((6.2, 0), (11.8, 0), (10.6, 45), (7.4, 45)), K['trunk'])
    for i, (x, y, r, c) in enumerate([(-8, 47, 7, 'leaf3'), (9, 45, 5.8, 'leaf3'), (3, 52, 8, 'leaf'), (-4, 60, 6.6, 'leaf2')]):
        pc.f(_clump(x, y, r, 31 + i), K[c])
    for (x, y, a) in [(-9, 47, 70), (2, 53, 100), (-5, 60, 80)]:
        for l_ in _tick(x, y, 3, a):
            pc.l(l_)
    return pc


def p_xlb():
    pc = Piece('小籠包', tabs=[(0, 9)])
    pc.f(R(-14, 0, 28, 1.6), K['ground'])
    pc.f(R(-12.5, 1, 3, 6.5), K['wood']); pc.f(R(9.5, 1, 3, 6.5), K['wood'])
    pc.f(R(-14, 7, 28, 2.6), K['wood'])
    for i, (x0, w) in enumerate(((-11.5, 23), (-11, 22))):
        y = 9.6 + i * 5.6
        pc.f(R(x0, y, w, 5.6, 1.4), K['bamboo2'] if i == 0 else K['bamboo'])
        pc.l(SL([(x0 + 1.2, y + 1.6), (x0 + w / 2, y + 1.1), (x0 + w - 1.2, y + 1.6)]))
        pc.l(SL([(x0 + 1.2, y + 4.0), (x0 + w / 2, y + 3.5), (x0 + w - 1.2, y + 4.0)]))
    for xx in (-6.8, 0, 6.8):
        pc.f(half(E(xx, 20.8, 4.0, 5.2), 20.8), K['white'])
        pc.f(C(xx, 26.2, 1.0), K['white'])
        for dx in (-1.9, -0.6, 0.6, 1.9):
            pc.l(L((xx + dx, 21.8), (xx + dx * 0.25, 25.2)))
    pc.items = [(k, AF.scale(g, 0.8, 0.8, origin=(0, 0)), c) for k, g, c in pc.items]
    return pc


def p_scooter():
    pc = Piece('機車', tabs=[(-8.5, 8), (8.5, 8)])
    B_ = K['scoot']
    pc.f(R(-19, 0, 36, 1.5), K['ground'])
    for cx in (-10.8, 10.8):
        pc.f(C(cx, 4.6, 4.6), K['tyre']); pc.f(C(cx, 4.6, 2.4), K['grey']); pc.f(C(cx, 4.6, 0.8), K['tyre'])
    pc.f(half(C(10.8, 4.6, 6.4), 6.0).difference(C(10.8, 4.6, 4.8)), B_)
    pc.f(P((9.6, 6), (12.1, 6), (12.2, 11.4), (10.2, 11.4)), K['tyre'])
    pc.f(SP([(7.8, 5.6), (9.4, 10), (11.2, 16.4), (12.6, 20.6), (10.6, 21.8), (8.8, 20), (7.2, 13), (5.4, 8.8), (1, 8), (-1.2, 9.4), (-2.6, 13),
             (-4.4, 15.2), (-15, 15.2), (-18.8, 13), (-19.2, 9.8), (-16.6, 7.2), (-15.4, 9.6), (-10.8, 10.8), (-6.4, 9.4), (-5, 5.8)], 8), B_)
    pc.l(SL([(-17, 12), (-10, 12.8), (-4.2, 12)])); pc.l(SL([(8.4, 10), (9.8, 15), (11, 19.4)]))
    pc.f(SP([(-15.2, 15), (-14.6, 17.6), (-9, 18.2), (-4.8, 17.6), (-3.8, 15)]), K['seat'])
    pc.f(R(-20, 15.4, 5.6, 5.2, 1), K['cream'])
    pc.f(C(12.6, 19.4, 1.7), K['cream'])
    pc.f(P((8.2, 21.4), (13.4, 21.4), (13.4, 23), (7.8, 23.2)), K['tyre'])
    pc.f(P((9.4, 22.8), (12.2, 22.8), (13, 26.2), (10.2, 26.4)), K['tyre']); pc.f(C(11.8, 27.4, 2.1), K['grey'])
    pc.f(C(5.6, 19.4, 3.0), K['helmet']); pc.l(SL([(3.4, 18.4), (5.6, 17.6), (8, 18.4)]))
    return pc


def _flower(pc, x, y, i, r=2.3):
    col = (K['pink'], K['mag'], K['pink2'])[i % 3]
    pet = [rot(E(x, y + r * 0.78, r * 0.55, r * 0.95), a + i * 23, (x, y)) for a in range(0, 360, 72)]
    pc.f(unary_union(pet + [C(x, y, r * 0.5)]), col)
    for a in (-28, 0, 28):
        pc.l(rot(L((x, y), (x, y + r * 1.15)), a + i * 23, (x, y)))
    pc.f(C(x, y, 0.55), K['mag'] if i % 3 != 1 else K['pink2'])


def _mbox(pc, x, col, legh, ang):
    o = (x, 0)
    pc.f(R(x - 4, 0, 8, 1.9), K['roof'])
    pc.f(rot(R(x - 1.7, 0, 3.4, legh), ang, o), K['roof'])
    pc.f(rot(R(x - 5, legh - 0.4, 10, 9.6, 1.6), ang, o), col)
    pc.f(rot(half(E(x, legh + 9, 5, 3.4), legh + 9), ang, o), col)
    pc.f(rot(R(x - 5.7, legh + 7.0, 11.4, 1.4), ang, o), K['black'])
    pc.f(rot(R(x - 2.8, legh + 1.6, 5.6, 2.6), ang, o), K['cream'])
    pc.l(rot(L((x - 3, legh + 5.6), (x + 3, legh + 5.6)), ang, o))


def p_mail():
    pc = Piece('歪腰郵筒', tabs=[(0, 10)])
    pc.f(R(-14, 0, 28, 1.6), K['ground'])
    _mbox(pc, -5.5, K['green'], 9.5, -15)
    _mbox(pc, 6.5, K['red'], 11, -8)
    return pc


_st0 = p_stall


def p_stall():
    pc = Piece('夜市攤', tabs=[(-13, 9), (13, 9)])
    pc.f(R(-25, 0, 50, 1.6), K['ground'])
    pc.f(C(-15, 3.3, 3.3), K['tyre']); pc.f(C(15, 3.3, 3.3), K['tyre']); pc.f(C(-15, 3.3, 1.2), K['grey']); pc.f(C(15, 3.3, 1.2), K['grey'])
    pc.f(R(-22, 3.6, 44, 10.6, 1), K['wood'])
    pc.f(R(-22, 11.6, 44, 2.6), K['cream'])
    for xx in (-11, 0, 11):
        pc.l(L((xx, 4.6), (xx, 11.6)))
    pc.f(R(-22, 14, 4, 17), K['wood']); pc.f(R(18, 14, 4, 17), K['wood'])
    pc.f(R(-17.2, 14, 10.4, 5.6, 1.2), K['grey']); pc.f(half(E(-12, 19.4, 5.8, 2.6), 19.4), K['roof']); pc.f(C(-12, 22.2, 1.1), K['roof'])
    pc.f(P((0.5, 14), (13.5, 14), (12.4, 20.4), (9.8, 22.4), (4.2, 22.4), (1.6, 20.4)), K['teal'])
    pc.l(L((4.6, 14.2), (4.6, 19.5))); pc.l(L((9.4, 14.2), (9.4, 19.5)))
    pc.f(C(7, 24.0, 2.8), K['skin']); pc.f(half(C(7, 24.4, 3.0), 24.6), K['black'])
    xs_b = np.linspace(-26, 26, 6); xs_t = np.linspace(-22.5, 22.5, 6)
    for i in range(5):
        col = K['cloth'] if i % 2 == 0 else K['white']
        pc.f(P((xs_b[i], 30.5), (xs_b[i + 1], 30.5), (xs_t[i + 1], 38.5), (xs_t[i], 38.5)), col)
    sb = np.linspace(-26, 26, 11)
    for i in range(10):
        pc.f(half(C((sb[i] + sb[i + 1]) / 2, 30.6, 2.6), 30.6, up=False), K['cloth'] if (i // 2) % 2 == 0 else K['white'])
    # 招牌：一條繩掛三顆小燈籠
    pc.f(R(-15, 38.5, 30, 9, 1.4), K['cream'])
    pc.l(SL([(-13, 45.2), (-6, 44.4), (0, 44.9), (6, 44.4), (13, 45.2)]))
    for xx in (-8, 0, 8):
        pc.f(E(xx, 42.2, 2.7, 2.3), K['red'])
        pc.l(L((xx, 44.5), (xx, 45)))
    allf = unary_union([g for k, g, c in pc.items if k == 'f'])
    pc.cut(R(-17.6, 14.2, 35.2, 15.6).difference(allf.buffer(0.35)))
    return pc


def _hedge(pc, top, flowers, leaves):
    pc.f(Polygon([(top[0][0], 0)] + cr(top) + [(top[-1][0], 0)]).buffer(0), K['leaf3'])
    for (x, y) in leaves:
        pc.f(SP([(x - 3.2, y), (x, y + 1.8), (x + 3.2, y), (x, y - 1.8)]), K['leaf'])
        pc.l(L((x - 2.4, y), (x + 2.4, y)))
    for i, (x, y) in enumerate(flowers):
        _flower(pc, x, y, i)


LAYOUT = [
    (1, '群山', p_backdrop, None, None, 1),
    (2, '老街屋', p_house, 2, 40, 2),
    (3, '夜市攤', p_stall, 36, 8, 2),
    (4, '藍鵲與樹', p_tree_a, -36, 22, 3),
    (5, '小籠包', p_xlb, 2, -12, 3),
    (6, '歪腰郵筒', p_mail, -46, -22, 4),
    (7, '機車', p_scooter, 34, -45, 4),
    (8, '杜鵑花', p_azalea_a, -8, -61, 4),
]

CROSS = {4: p_tree_b, 8: p_azalea_b}


# ================= v4.2：依專業設計師第二輪意見修改 =================
K.update(plaster='#E3C9A8', bamboo='#E8D9B5', bamboo2='#D9C49A', leafdark='#3F6B55')


def p_backdrop():
    W = UW * 3
    pc = Piece('群山', tabs=[(UW * i + o, 10) for i in range(3) for o in (17, 57)])
    ridge = [(0, 50), (16, 58), (34, 66), (52, 74), (70, 88), (88, 97), (100, 92), (116, 80), (132, 74), (150, 78), (166, 70), (184, 62), (200, 64), (214, 56), (W, 52)]
    midr = [(0, 40), (22, 48), (40, 44), (64, 60), (84, 54), (104, 62), (128, 56), (150, 66), (170, 52), (190, 56), (206, 44), (W, 42)]
    nearr = [(0, 26), (30, 34), (56, 28), (82, 36), (110, 30), (140, 40), (165, 30), (192, 34), (W, 28)]
    for r_, c in ((ridge, 'far'), (midr, 'mid'), (nearr, 'near')):
        pc.f(Polygon([(0, 0)] + cr(r_) + [(W, 0)]), K[c])
    rng = np.random.default_rng(5)
    for _ in range(22):
        x = float(rng.uniform(8, W - 14)); y = float(rng.uniform(22, 70)); w = float(rng.uniform(4, 7))
        pc.l(SL([(x, y), (x + w / 2, y + 0.5), (x + w, y)]))
    # 山腳：一排連續的屋頂剪影
    x = 0.0; i = 0
    cols = [K['bld1'], K['bld2'], K['bld3']]
    while x < W:
        w = float(rng.choice([10, 12, 14])); h = float(rng.choice([8, 10, 12]))
        w = min(w, W - x)
        nearfold = any(x - 1 < f < x + w + 1 for f in (UW, 2 * UW))
        pc.f(R(x, 0, w, h), cols[i % 3])
        if i % 3 == 0 and not nearfold and w >= 10:
            pc.f(P((x, h), (x + w, h), (x + w / 2, h + 4.2)), K['brick'])
        else:
            pc.f(R(x, h, w, 1.5), K['roof'])
        if w >= 10:
            pc.f(R(x + w / 2 - 1.3, 3.4, 2.6, max(2.4, h - 6.4)), K['win'])
        x += w; i += 1
    pc.f(R(0, 0, W, 2.6), K['ground'])
    clip = box(0, 0, W, 200)
    pc.items = [(k, g.intersection(clip), c) for k, g, c in pc.items]
    return pc


TSLOT = 56


def p_tree_a():
    pc = Piece('藍鵲與樹', tabs=[(-10, 9), (10, 9)], slot=('top', -2, TSLOT))
    pc.f(half(E(0, 0, 18, 4.2), 0), K['grass'])
    pc.f(P((-6, 0), (6, 0), (3.8, 8), (3.2, 22), (5.6, 30), (10.4, 40), (7.8, 42), (3, 35), (0.8, 32), (-0.2, 44), (-3, 44), (-2.6, 31),
           (-7.2, 40), (-9.6, 38.6), (-4.2, 27), (-3.6, 8)), K['trunk'])
    pc.f(P((3, 17.6), (27, 27.4), (27, 30), (3, 22)), K['trunk'])
    pc.l(SL([(-1.4, 3), (-0.6, 14), (-1, 26)])); pc.l(SL([(1.6, 6), (1.2, 16)]))
    pc.f(_clump(-11, 48, 10.2, 41), K['leaf3'])
    pc.f(_clump(10, 50, 10.6, 42), K['leaf'])
    pc.f(_clump(-1, 61, 10.4, 43), K['leaf2'])
    la, lb, ra, rb = (14.8, 33.2), (9.4, 13), (17.2, 31), (13.4, 12)
    mix = lambda p, q, t: (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    pc.f(P(la, ra, rb, lb), K['blue'])
    for t0, t1 in ((0.46, 0.58), (0.72, 0.84)):
        pc.f(P(mix(la, lb, t0), mix(ra, rb, t0), mix(ra, rb, t1), mix(la, lb, t1)), K['white'])
    pc.f(C(11.3, 11.4, 2.5), K['white'])
    for x in (18.6, 21.4):
        pc.f(P((x, 30.4), (x + 1.1, 30.4), (x + 0.9, 27.2), (x - 0.1, 27.2)), K['red'])
    pc.f(SP([(14.5, 32.6), (17, 30), (21.5, 29.8), (25, 32), (26.6, 35.4), (24.6, 37.2), (19.5, 36.4)]), K['blue'])
    pc.f(SP([(16, 33.6), (19.5, 31.3), (23.2, 32.4), (20.6, 34.8)]), K['blue2'])
    pc.f(SP([(22.4, 37.2), (25.2, 39.8), (28.2, 38.6), (28.8, 35.6), (26.8, 32.4), (24.2, 32.8), (23, 35)]), K['black'])
    pc.f(P((28.2, 38), (32.2, 36.5), (28.5, 35.6)), K['red'])
    pc.f(C(26.3, 37.5, 0.6), K['yellow'])
    return pc


def p_tree_b():
    pc = Piece('樹的側片', tabs=[(9, 9)], slot=('bot', -2, TSLOT))
    pc.f(half(E(9, 0, 9.5, 3.6), 0), K['grass'])
    pc.f(P((6.2, 0), (11.8, 0), (10.6, 46), (7.4, 46)), K['trunk'])
    pc.f(_clump(6, 50, 9, 51), K['leaf3'])
    pc.f(_clump(-5, 58, 9.6, 52), K['leaf'])
    return pc


def p_xlb():
    pc = Piece('小籠包', tabs=[(0, 9)])
    pc.f(R(-14, 0, 28, 3.0), K['ground'])
    pc.f(R(-12.5, 1, 3, 6.5), K['wood']); pc.f(R(9.5, 1, 3, 6.5), K['wood'])
    pc.f(R(-14, 7, 28, 2.6), K['wood'])
    for i, (x0, w) in enumerate(((-11.5, 23), (-11, 22))):
        y = 9.6 + i * 5.6
        pc.f(R(x0, y, w, 5.6, 1.4), K['bamboo2'] if i == 0 else K['bamboo'])
        pc.l(SL([(x0 + 1.2, y + 1.6), (x0 + w / 2, y + 1.1), (x0 + w - 1.2, y + 1.6)]))
        pc.l(SL([(x0 + 1.2, y + 4.0), (x0 + w / 2, y + 3.5), (x0 + w - 1.2, y + 4.0)]))
    for (x, y, r) in [(7.4, 27.6, 3.0), (10.2, 31.2, 3.4), (7, 34.6, 2.8), (10, 37.4, 2.2)]:
        pc.f(C(x, y, r), K['white'])
    for xx in (-6.8, 0, 6.8):
        pc.f(half(E(xx, 20.8, 4.0, 5.2), 20.8), K['white'])
        pc.f(C(xx, 26.2, 1.0), K['white'])
        for dx in (-1.9, -0.6, 0.6, 1.9):
            pc.l(L((xx + dx, 21.8), (xx + dx * 0.25, 25.2)))
    pc.items = [(k, AF.scale(g, 0.85, 0.85, origin=(0, 0)), c) for k, g, c in pc.items]
    return pc


def p_scooter():
    pc = Piece('機車', tabs=[(-8.5, 8), (8.5, 8)])
    B_ = K['scoot']
    pc.f(R(-19, 0, 36, 2.0), K['ground'])
    for cx in (-10.8, 10.8):
        pc.f(C(cx, 4.8, 4.8), K['tyre']); pc.f(C(cx, 4.8, 2.5), K['grey']); pc.f(C(cx, 4.8, 0.8), K['tyre'])
    pc.f(half(C(10.8, 4.8, 6.6), 6.2).difference(C(10.8, 4.8, 5.0)), B_)
    pc.f(P((9.6, 6), (12.1, 6), (12.2, 11.4), (10.2, 11.4)), K['tyre'])
    pc.f(SP([(7.8, 5.6), (9.4, 10), (11.2, 16.4), (12.4, 19.6), (9, 19.8), (7.2, 13), (5.4, 8.8), (1, 8), (-1.2, 9.4), (-2.6, 13),
             (-4.4, 15.2), (-15, 15.2), (-18.8, 13), (-19.2, 9.8), (-16.6, 7.2), (-15.4, 9.6), (-10.8, 10.8), (-6.4, 9.4), (-5, 5.8)], 8), B_)
    pc.l(SL([(-17, 12), (-10, 12.8), (-4.2, 12)])); pc.l(SL([(8.4, 10), (9.8, 15), (10.8, 18.6)]))
    pc.f(SP([(-15.2, 15), (-14.6, 17.8), (-9, 18.4), (-4.8, 17.8), (-3.8, 15)]), K['seat'])
    pc.f(R(-20, 15.4, 5.6, 5.2, 1), K['cream'])
    # 車頭罩＋圓燈＋握把
    pc.f(SP([(7.6, 20), (8.6, 23.8), (12.6, 24.6), (15, 22.4), (14, 19.6), (10.4, 19)]), B_)
    pc.f(C(13.4, 21.8, 1.7), K['cream'])
    pc.f(P((5.4, 22.6), (9, 22.6), (9, 24.6), (5.2, 24.8)), K['tyre'])
    return pc


def _mbox(pc, x, col, legh, ang):
    o = (x, 0)
    pc.f(R(x - 4, 0, 8, 2.2), K['roof'])
    pc.f(rot(R(x - 1.7, 0, 3.4, legh), ang, o), K['roof'])
    pc.f(rot(R(x - 6, legh - 0.4, 12, 9.6, 1.8), ang, o), col)
    pc.f(rot(half(E(x, legh + 9, 6, 3.6), legh + 9), ang, o), col)
    pc.f(rot(R(x - 6.7, legh + 7.0, 13.4, 1.5), ang, o), K['black'])
    pc.f(rot(R(x - 3.4, legh + 1.6, 6.8, 2.8), ang, o), K['cream'])
    pc.l(rot(L((x - 3.6, legh + 5.6), (x + 3.6, legh + 5.6)), ang, o))


def p_mail():
    pc = Piece('歪腰郵筒', tabs=[(0, 10)])
    pc.f(R(-15, 0, 30, 2.2), K['ground'])
    _mbox(pc, -6.5, K['green'], 9.5, -15)
    _mbox(pc, 7.5, K['red'], 11, -8)
    return pc


_st1 = p_stall


def p_stall():
    pc = _st1()
    its = []
    for k, g, c in pc.items:
        if k == 'f' and c == K['red'] and g.area < 30:          # 招牌上的紅圓 → 燈籠形（上下有提把）
            x, y = g.centroid.x, g.centroid.y
            its.append(('f', E(x, y - 0.4, 2.9, 2.5), K['red']))
            its.append(('f', R(x - 1.2, y + 1.9, 2.4, 1.0), K['yellow'])); its.append(('f', R(x - 1.2, y - 3.8, 2.4, 1.0), K['yellow']))
            its.append(('l', L((x - 1.0, y + 1.6), (x - 1.0, y - 2.6)), None)); its.append(('l', L((x + 1.0, y + 1.6), (x + 1.0, y - 2.6)), None))
        elif k == 'f' and c == K['cream'] and g.bounds[1] > 38:   # 招牌底色與街屋分開
            its.append((k, g, '#F6EFE2'))
        else:
            its.append((k, g, c))
    pc.items = its
    return pc


def _hedge(pc, top, flowers, leaves, buds=()):
    pc.f(Polygon([(top[0][0], 0)] + cr(top) + [(top[-1][0], 0)]).buffer(0), K['leafdark'])
    for (x, y) in leaves:
        pc.f(SP([(x - 3.4, y), (x, y + 1.9), (x + 3.4, y), (x, y - 1.9)]), K['leaf3'])
        pc.l(L((x - 2.6, y), (x + 2.6, y)))
    for (x, y) in buds:
        pc.f(E(x, y, 1.3, 1.9), K['mag'])
    for i, (x, y) in enumerate(flowers):
        _flower(pc, x, y, i, r=3.1)


def p_azalea_a():
    pc = Piece('杜鵑花', tabs=[(-14, 9), (16, 9)], slot=('top', 4, 7.5))
    _hedge(pc, [(-23, 0), (-24, 7), (-20, 12), (-14, 11.5), (-10, 15), (-3, 13.5), (2, 16), (9, 14.5), (14, 17), (20, 12.5), (24, 8), (23, 0)],
           [(-15, 9.6), (-3, 10.4), (12.6, 11.6)],
           [(-8.6, 5), (4, 4.6), (19, 5.4), (-20, 4.4), (10, 4.4)], [(-9.4, 12.6), (3.6, 13.6), (19.4, 9.6), (-20.6, 8.6)])
    return pc


def p_azalea_b():
    pc = Piece('花叢側片', slot=('bot', -2, 7.5))
    _hedge(pc, [(-12, 0), (-12.6, 6), (-8, 11), (-2, 12.5), (4, 14.5), (9, 11), (12, 6), (11.6, 0)],
           [(4, 9.4)], [(-6.4, 4), (6.6, 3.2)], [(-6.6, 8.4), (-1.4, 10)])
    return pc


LAYOUT = [
    (1, '群山', p_backdrop, None, None, 1),
    (2, '老街屋', p_house, 2, 40, 2),
    (3, '夜市攤', p_stall, 36, 8, 2),
    (4, '藍鵲與樹', p_tree_a, -37, 24, 3),
    (5, '小籠包', p_xlb, -20, -8, 3),
    (6, '歪腰郵筒', p_mail, -47, -26, 4),
    (7, '機車', p_scooter, 16, -44, 4),
    (8, '杜鵑花', p_azalea_a, -8, -61, 4),
]
CROSS = {4: p_tree_b, 8: p_azalea_b}


# ================= v4.3：依專業設計師第三輪意見修改 =================
def p_tree_a():
    pc = Piece('藍鵲與樹', tabs=[(-10, 9), (10, 9)], slot=('top', -2, TSLOT))
    pc.f(half(E(0, 0, 18, 4.2), 0), K['grass'])
    pc.f(P((-6, 0), (6, 0), (3.8, 8), (3.2, 22), (5.6, 30), (10.4, 40), (7.8, 42), (3, 35), (0.8, 32), (-0.2, 44), (-3, 44), (-2.6, 31),
           (-7.2, 40), (-9.6, 38.6), (-4.2, 27), (-3.6, 8)), K['trunk'])
    pc.f(P((3, 17.6), (28, 27.8), (28, 30.4), (3, 22)), K['trunk'])
    for pts in ([(-1.6, 3), (-0.8, 12), (-1.2, 22)], [(1.8, 5), (1.4, 14)], [(-3.4, 2.6), (-2.8, 9)], [(0.6, 20), (1.0, 28)]):
        pc.l(SL(pts))
    pc.f(_clump(-11, 48, 10.2, 41), K['leaf3'])
    pc.f(_clump(10, 50, 10.6, 42), K['leaf'])
    pc.f(_clump(-1, 61, 10.4, 43), K['leaf2'])
    for (x, y, a0) in [(-13, 50, 20), (-8, 44, 200), (8, 53, 30), (13, 46, 210), (-3, 64, 25), (2, 57, 205), (-15, 44, 190), (14, 53, 20)]:
        pc.l(_arc(x, y, 3.0, a0, a0 + 120, 6))
    # 台灣藍鵲（放大）：兩根漸細的長尾羽，只有尾端白
    bird = []
    fa = [((14.6, 33.4), (16.8, 31.6), (11.9, 9.4), (10.1, 10.0)), ((16.0, 32.4), (18.0, 30.6), (15.2, 12.6), (13.5, 13.2))]
    mix = lambda p, q, t: (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    for (a, b_, c_, d) in fa:
        bird.append(('f', P(a, b_, c_, d), K['blue']))
        bird.append(('f', P(mix(a, d, 0.8), mix(b_, c_, 0.8), c_, d), K['white']))
    for x in (18.6, 21.4):
        bird.append(('f', P((x, 30.4), (x + 1.1, 30.4), (x + 0.9, 27.2), (x - 0.1, 27.2)), K['red']))
    bird.append(('f', SP([(14.5, 32.6), (17, 30), (21.5, 29.8), (25, 32), (26.6, 35.4), (24.6, 37.2), (19.5, 36.4)]), K['blue']))
    bird.append(('f', SP([(16, 33.6), (19.5, 31.3), (23.2, 32.4), (20.6, 34.8)]), K['blue2']))
    bird.append(('f', SP([(22.4, 37.2), (25.2, 39.8), (28.2, 38.6), (28.8, 35.6), (26.8, 32.4), (24.2, 32.8), (23, 35)]), K['black']))
    bird.append(('f', P((28.2, 38), (32.2, 36.5), (28.5, 35.6)), K['red']))
    bird.append(('f', C(26.3, 37.5, 0.6), K['yellow']))
    for k, g, c in bird:
        pc.items.append((k, AF.scale(g, 1.25, 1.25, origin=(20, 27.4)), c))
    return pc


def p_xlb():
    pc = Piece('小籠包', tabs=[(0, 9)])
    pc.f(R(-14, 0, 28, 3.0), K['ground'])
    pc.f(R(-12.5, 1, 3, 6.5), K['wood']); pc.f(R(9.5, 1, 3, 6.5), K['wood'])
    pc.f(R(-14, 7, 28, 2.6), K['wood'])
    for i, (x0, w) in enumerate(((-11.5, 23), (-11, 22))):
        y = 9.6 + i * 5.6
        pc.f(R(x0, y, w, 5.6, 1.4), K['bamboo2'] if i == 0 else K['bamboo'])
        pc.l(SL([(x0 + 1.2, y + 1.6), (x0 + w / 2, y + 1.1), (x0 + w - 1.2, y + 1.6)]))
        pc.l(SL([(x0 + 1.2, y + 4.0), (x0 + w / 2, y + 3.5), (x0 + w - 1.2, y + 4.0)]))
    # 蒸氣：一條 S 形的煙
    pc.f(LineString(cr([(7, 24), (9.6, 28), (6.6, 32.5), (9.4, 37), (7.6, 40.5)])).buffer(1.7, quad_segs=8), '#E4DCCB')
    for xx in (-6.8, 0, 6.8):
        pc.f(half(E(xx, 20.8, 4.0, 5.2), 20.8), K['white'])
        pc.f(C(xx, 26.2, 1.0), K['white'])
        for dx in (-1.9, -0.6, 0.6, 1.9):
            pc.l(L((xx + dx, 21.8), (xx + dx * 0.25, 25.2)))
    pc.items = [(k, AF.scale(g, 0.85, 0.85, origin=(0, 0)), c) for k, g, c in pc.items]
    return pc


_sc3 = p_scooter


def p_scooter():
    pc = _sc3()
    pc.items = [(k, g, (K['red'] if (k == 'f' and c == K['cream'] and g.bounds[0] < -15) else c)) for k, g, c in pc.items]
    pc.f(P((14.2, 23.4), (16.2, 22.6), (16.2, 20.8), (14.4, 20.2)), K['tyre'])
    return pc


LAYOUT = [
    (1, '群山', p_backdrop, None, None, 1),
    (2, '老街屋', p_house, 2, 40, 2),
    (3, '夜市攤', p_stall, 36, 8, 2),
    (4, '藍鵲與樹', p_tree_a, -37, 24, 3),
    (5, '小籠包', p_xlb, -30, -8, 3),
    (6, '歪腰郵筒', p_mail, -50, -30, 4),
    (7, '機車', p_scooter, 16, -44, 4),
    (8, '杜鵑花', p_azalea_a, -8, -61, 4),
]
CROSS = {4: p_tree_b, 8: p_azalea_b}
