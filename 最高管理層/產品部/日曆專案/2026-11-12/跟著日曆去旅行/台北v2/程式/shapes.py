"""台北 v2 幾何（單位 mm，y 向上，地面 y=0）。每件＝parts（後蓋前的面）＋lines（額外上色線）。"""
import math
from shapely.geometry import Polygon, Point, box, LineString
from shapely.ops import unary_union, linemerge
from shapely import affinity

TAB_H = 8.0     # 卡榫高
SLOT = 0.6      # 十字插槽寬（紙厚＋約 0.2，試切後調）
GROUND = 1.8    # 每件底部的地面條，讓零件連成一片

def B(x0, y0, x1, y1): return box(x0, y0, x1, y1)
def C(x, y, r): return Point(x, y).buffer(r, quad_segs=24)
def E(x, y, rx, ry, rot=0):
    return affinity.rotate(affinity.scale(Point(x, y).buffer(1, quad_segs=24), rx, ry), rot, origin=(x, y))
def P(*pts): return Polygon(pts)
def RR(x0, y0, x1, y1, r): return box(x0 + r, y0 + r, x1 - r, y1 - r).buffer(r, quad_segs=8)
def cr(pts, closed=False, k=10):
    """Catmull-Rom 平滑曲線取樣點。"""
    n = len(pts); out = []
    idx = range(n) if closed else range(n - 1)
    for i in idx:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1 = pts[i]; p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        for j in range(k):
            t = j / k; t2 = t * t; t3 = t2 * t
            out.append(tuple(0.5 * ((2 * p1[a]) + (-p0[a] + p2[a]) * t + (2 * p0[a] - 5 * p1[a] + 4 * p2[a] - p3[a]) * t2 + (-p0[a] + 3 * p1[a] - 3 * p2[a] + p3[a]) * t3) for a in (0, 1)))
    if not closed: out.append(tuple(pts[-1]))
    return out
def SP(*pts): return Polygon(cr(list(pts), True)).buffer(0)
def SL(*pts): return LineString(cr(list(pts)))
def L(*pts): return LineString(pts)
def ring(g): return LineString(g.exterior.coords)
def arch(x0, y0, x1, y1):
    r = (x1 - x0) / 2
    return unary_union([B(x0, y0, x1, y1 - r), C((x0 + x1) / 2, y1 - r, r)])
def rot(g, a, o): return affinity.rotate(g, a, origin=o)

# ───────── 1 食：小籠包蒸籠 ─────────
def p_xlb():
    def dump(cx, by, s=1.0):
        return SP((cx - 5.2 * s, by), (cx - 5.7 * s, by + 3.2 * s), (cx - 3.6 * s, by + 6.3 * s), (cx - 1.3 * s, by + 7.7 * s), (cx, by + 9.8 * s),
                  (cx + 1.3 * s, by + 7.7 * s), (cx + 3.6 * s, by + 6.3 * s), (cx + 5.7 * s, by + 3.2 * s), (cx + 5.2 * s, by)).union(B(cx - 5 * s, by - 1, cx + 5 * s, by + 2))
    def pleat(cx, by, s=1.0):
        return [SL((cx - 0.5 * s, by + 8.4 * s), (cx - 2.6 * s, by + 5 * s), (cx - 3.5 * s, by + 1.6 * s)), SL((cx, by + 8.2 * s), (cx + 0.2 * s, by + 5 * s), (cx, by + 1.8 * s)),
                SL((cx + 0.5 * s, by + 8.4 * s), (cx + 2.6 * s, by + 5 * s), (cx + 3.5 * s, by + 1.6 * s))]
    parts = [B(0, 0, 42, GROUND), RR(2, 1.6, 40, 11.2, 1.6), RR(4.5, 11, 37.5, 19.6, 1.6),
             dump(11.5, 18.6), dump(30.5, 18.6), dump(21, 18.2, 1.12)]
    lines = [L((2.6, 4.8), (39.4, 4.8)), L((2.6, 8.2), (39.4, 8.2)), L((5.1, 13.9), (36.9, 13.9)), L((5.1, 16.8), (36.9, 16.8)),
             L((9, 4.8), (9, 8.2)), L((10.4, 4.8), (10.4, 8.2)), L((31.6, 4.8), (31.6, 8.2)), L((33, 4.8), (33, 8.2)),
             L((20.3, 13.9), (20.3, 16.8)), L((21.7, 13.9), (21.7, 16.8))]
    lines += pleat(11.5, 18.6) + pleat(30.5, 18.6) + pleat(21, 18.2, 1.12)
    return dict(parts=parts, lines=lines, tab=(21, 20))

# ───────── 4 行：機車（側面，車頭朝左） ─────────
def p_scooter():
    body = SP((24, 7), (24.6, 12.5), (27, 16), (33, 17.4), (40, 17.6), (44, 15.6), (43.4, 11.6), (40, 9.2), (41, 6.4), (33, 5.6), (27, 5.8))
    shield = SP((9.2, 11), (8.4, 17), (9.6, 22.4), (12.2, 24.6), (14.8, 23), (15.4, 16), (17.6, 10.4), (19.4, 7.4), (13, 7.2))
    seat = SP((23.6, 17), (25.6, 19.8), (31, 20.6), (39.4, 20.8), (41, 18.8), (39.6, 17.2), (31, 16.6))
    parts = [B(0, 0, 46, GROUND), C(8, 5.6, 5.6), C(37, 5.6, 5.6),
             C(8, 5.6, 7.4).intersection(B(0, 7.6, 16, 14)), body, RR(15, 6.2, 27.6, 9.4, 1.2), shield, seat,
             RR(38.4, 20.4, 46, 27.4, 1.3),                                    # 置物箱
             C(29.4, 22.4, 3.5).intersection(B(20, 20.2, 40, 30)),             # 安全帽
             P((11.4, 23.6), (13.8, 23.6), (15, 28.2), (12.8, 28.8)), RR(9.4, 27.2, 17, 29.6, 1.1),
             P((15.4, 29), (17.2, 28.6), (18.8, 30.8), (17.2, 31.4)), E(18.6, 32.2, 2.4, 1.8, 20)]
    lines = [ring(C(8, 5.6, 2.2)), ring(C(37, 5.6, 2.2)), ring(C(10, 19.8, 1.7)), SL((26.4, 11), (33, 12.6), (42.6, 13)),
             L((39.8, 23.8), (44.6, 23.8)), SL((27, 22), (29.6, 22.8), (32.4, 21.6))]
    return dict(parts=parts, lines=lines, tab=(23, 22))

# ───────── 6 物：歪腰郵筒（一綠一紅） ─────────
def p_mail():
    def mb(x, a, h=15):
        ps = [B(x - 1.7, 0, x + 1.7, h + 1), RR(x - 5.6, h, x + 5.6, h + 13, 1),
              E(x, h + 13, 6.4, 4.4).intersection(B(x - 8, h + 13, x + 8, h + 19)), RR(x - 6.5, h + 12.3, x + 6.5, h + 13.9, .7)]
        ls = [ring(RR(x - 3.5, h + 8.2, x + 3.5, h + 10.2, 0.95)), ring(B(x - 3, h + 2, x + 3, h + 6.2)), L((x - 3, h + 4.1), (x + 3, h + 4.1))]
        return [rot(p, a, (x, 0)) for p in ps], [rot(l, a, (x, 0)) for l in ls]
    p1, l1 = mb(9, -17, 14); p2, l2 = mb(23, -9, 16)
    grass = [SP((0.5, 1.6), (1.2, 5.4), (2.4, 2.6), (3.4, 6.4), (4.6, 2.6), (5.8, 4.8), (6.4, 1.6))]
    parts = [B(0, 0, 37, GROUND)] + grass + p1 + p2
    return dict(parts=parts, lines=l1 + l2, tab=(18, 18))

# ───────── 5 樂：夜市攤 ─────────
def p_stall():
    scal = unary_union([C(8.5 + 5 * i, 35, 2.5) for i in range(10)])
    awn = unary_union([P((6, 35), (56, 35), (51, 43.4), (11, 43.4)), scal])
    parts = [B(4, 0, 60, GROUND), C(16, 4.2, 4.2), C(46, 4.2, 4.2),
             B(13, 19, 49, 35.5),                                             # 背布
             RR(11, 5, 51, 19, 1), RR(9.5, 18, 52.5, 20.6, .9),
             RR(15, 20.4, 27, 24.6, .7), RR(15, 24.4, 27, 28.6, .7), E(21, 28.4, 6.2, 3).intersection(B(14, 28.4, 28, 32)), C(21, 31.4, 1),   # 蒸籠
             RR(33, 20.4, 45, 27.4, 1.6), RR(31.6, 24.6, 46.4, 26.2, .7),      # 湯鍋
             awn, RR(18, 42.4, 44, 50, 1.3),
             E(8.2, 29.4, 3.1, 3.6), E(8.2, 23.2, 3.1, 3.6), B(7.4, 18.6, 9, 20.4),   # 燈籠串
             RR(53, 1.6, 59.4, 13.4, 2.6), B(55.2, 13, 57.2, 15.6), B(54.2, 15.2, 58.2, 16.8)]  # 瓦斯桶
    lines = [L((11 + 5 * i, 43.4), (6 + 6.25 * i, 35.6)) for i in range(1, 8)]
    lines += [ring(RR(20, 44.2, 42, 48.2, .8)), ring(C(25.5, 46.2, 1.3)), ring(C(31, 46.2, 1.3)), ring(C(36.5, 46.2, 1.3)),
              L((24.3, 5.2), (24.3, 18)), L((37.7, 5.2), (37.7, 18)), ring(RR(27.4, 9, 34.6, 15, .8)),
              ring(C(16, 4.2, 1.6)), ring(C(46, 4.2, 1.6)),
              L((5.2, 30.4), (11.2, 30.4)), L((5.2, 28.4), (11.2, 28.4)), L((5.2, 24.2), (11.2, 24.2)), L((5.2, 22.2), (11.2, 22.2)),
              SL((36, 27.4), (37.4, 30.4), (36.2, 32.6)), SL((40.4, 27.4), (41.8, 30), (40.6, 32)),   # 熱氣
              L((53.4, 9.6), (59, 9.6))]
    lines += [ring(C(18 + 6.5 * i, 33, 1)) for i in range(5)]
    return dict(parts=parts, lines=lines, tab=(31, 26))

# ───────── 3 植物：杜鵑花叢（十字兩片，不對稱） ─────────
def flower(cx, cy, r=3.3, a0=90):
    pet = unary_union([C(cx + r * .55 * math.cos(math.radians(a0 + 72 * i)), cy + r * .55 * math.sin(math.radians(a0 + 72 * i)), r * .52) for i in range(5)])
    return pet, [ring(C(cx, cy, .75))]
def leaf(cx, cy, a, s=1.0):
    return rot(SP((cx - 2.6 * s, cy), (cx, cy + 1.25 * s), (cx + 2.6 * s, cy), (cx, cy - 1.25 * s)), a, (cx, cy))
def _bush(circles, base, flowers, leaves):
    parts = [B(base[0], 0, base[1], GROUND), unary_union([C(*c) for c in circles] + [B(base[0] + 2, 0, base[1] - 2, 7)])]
    lines = []
    for lf in leaves:
        g = leaf(*lf); lines += [ring(g), rot(L((lf[0] - 2, lf[1]), (lf[0] + 2, lf[1])), lf[2], (lf[0], lf[1]))]
    for f in flowers:
        g, ls = flower(*f); parts.append(g); lines += ls
    return parts, lines
def p_azalea_a():
    parts, lines = _bush([(8, 9, 7.6), (15, 13.5, 8.6), (23.5, 12, 8), (29.5, 8, 6.6), (11.5, 20, 6.2), (19, 21.5, 5.6)], (1.5, 35),
                         [(5.4, 17.4, 3.4, 60), (13.5, 26, 3.5, 90), (24.5, 20, 3.4, 110), (31.6, 13.6, 3.2, 80), (17.6, 13, 3.3, 90), (9.6, 8, 3.1, 70), (26, 7, 3, 100)],
                         [(11.5, 15.6, 35), (22.4, 14.2, -25), (16.6, 6.6, 10), (29, 9.4, -40), (6, 11.4, 70), (18.4, 20.4, 55)])
    return dict(parts=parts, lines=lines, tab=(11, 12), slot=(22, 'top', 13))
def p_azalea_b():
    parts, lines = _bush([(7, 8.5, 6.6), (14, 11.5, 7.6), (21.5, 8, 6.2), (8.6, 17.6, 5.2), (7.4, 23.6, 3.8)], (1, 27),
                         [(6.6, 26.6, 3.3, 90), (15.4, 18.4, 3.3, 100), (23.2, 12.6, 3.1, 70), (3.4, 13, 3.1, 60), (12.6, 9, 3.2, 90), (19.6, 5.6, 2.9, 80)],
                         [(9.4, 14, 60), (18, 11.6, -20), (8, 20.4, 80), (6.4, 5.8, 15)])
    return dict(parts=parts, lines=lines, tab=None, slot=(15.6, 'bottom', 13))

# ───────── 2 動物：台灣藍鵲與樹（十字兩片） ─────────
def mirror(d, xc):
    f = lambda g: affinity.scale(g, -1, 1, origin=(xc, 0))
    d['parts'] = [f(p) for p in d['parts']]; d['lines'] = [f(l) for l in d['lines']]
    if d.get('tab'): d['tab'] = (2 * xc - d['tab'][0], d['tab'][1])
    if d.get('slot'): d['slot'] = (2 * xc - d['slot'][0],) + d['slot'][1:]
    return d
def p_magpie_a():
    trunk = P((11, 0), (14.6, 6), (15, 20), (14.4, 34), (15, 48), (15.4, 60), (22.6, 60), (22.8, 48), (22.2, 34), (22.6, 20), (23.4, 6), (27, 0))
    branch = P((21, 35), (28, 40.4), (37, 43), (46.5, 43.4), (46.5, 46.4), (36.4, 46.4), (27, 44), (21, 41.6))
    stub = P((16, 23), (9.4, 28.4), (7.6, 31), (9.8, 32.6), (16, 28.6))
    canopy = unary_union([C(14, 61, 8.4), C(22, 67, 7.8), C(8.4, 67.6, 5.8), C(28.4, 61, 5.4), C(15, 71, 4.6)])
    body = E(33.4, 49.8, 6.8, 4, -14); head = C(27.4, 53.8, 3.2)
    tail = P((38.4, 50.4), (41.2, 49), (47.6, 40.5), (49.6, 34.4), (47, 33.6), (44.2, 38.8), (37.6, 46.6))
    beak = P((25.2, 55.4), (20.2, 53.4), (25.2, 51.6))
    parts = [B(7, 0, 31, GROUND), trunk, stub, unary_union([C(5.6, 34, 4.8), C(2.4, 30, 3.5), C(9.4, 37.6, 3.5)]), canopy, branch, tail, body, head, beak]
    lines = [SL((29.4, 51.4), (34, 48.6), (39.6, 48.8)), SL((31, 50.2), (35, 47.4), (39.4, 47)), L((40.6, 48.2), (47.6, 36.4)),
             L((44.6, 37.4), (47.4, 38.6)), L((45.6, 35.6), (48.6, 36.6)), ring(C(26.6, 54.4, .65)),
             L((31.4, 46.4), (31.8, 45.2)), L((34.4, 46.4), (34.8, 45.2)),
             SL((17.6, 8), (18.4, 16), (17.4, 24)), SL((19.6, 30), (19, 38), (19.8, 46)),
             SL((9, 60), (11.4, 62.4), (14, 60.6)), SL((17, 66.4), (19.6, 68.6), (22.4, 66.6)), SL((23, 59.4), (25.4, 61.4), (28, 59.6)), SL((5.4, 66.6), (7.6, 68.6), (10, 67)),
             SL((2.4, 31.4), (4.4, 33.2), (6.6, 31.8))]
    return mirror(dict(parts=parts, lines=lines, tab=(19, 14), slot=(19, 'top', 56)), 25)
def p_magpie_b():
    canopy = unary_union([C(10, 12, 9), C(20.5, 16.4, 10), C(31, 12.4, 8), C(15.6, 22.6, 7), C(25.6, 23.6, 6), C(3.6, 8.4, 4.2)])
    lines = [SL((5, 11), (7.6, 13.4), (10.4, 11.4)), SL((13, 20.6), (15.6, 22.8), (18.4, 21)), SL((22, 13.6), (24.6, 15.8), (27.4, 14)),
             SL((27, 22), (29, 23.8), (31.2, 22.4)), SL((30, 8.4), (32.4, 10.4), (35, 8.8)), SL((11.4, 5.6), (14, 7.6), (16.6, 6))]
    return dict(parts=[canopy], lines=lines, tab=None, slot=(19, 'bottom', 12))

# ───────── 7 住：老街屋（紅磚拱廊，不指定哪一棟） ─────────
def p_house():
    ped = SP((24, 47), (24.4, 52), (27.4, 53.6), (28.6, 57), (31.6, 59.6), (34.4, 63.6), (37, 66), (39.6, 63.6), (42.4, 59.6), (45.4, 57), (46.6, 53.6), (49.6, 52), (50, 47))
    parts = [B(0, 0, 74, GROUND), B(2, 0, 72, 46)]
    parts += [arch(7.4, 0, 21.6, 18.6), arch(29.9, 0, 44.1, 18.6), arch(52.4, 0, 66.6, 18.6)]
    parts += [B(1, 22, 73, 25.2)]
    for cx in (14.5, 37, 59.5):
        parts += [arch(cx - 4.6, 29.4, cx + 4.6, 41.6), B(cx - 6, 26.4, cx + 6, 29.4)]
    parts += [B(0.4, 44, 73.6, 47.2), B(3, 47, 71, 51), B(3.6, 47, 7.4, 52), C(5.5, 53.6, 2.3), B(66.6, 47, 70.4, 52), C(68.5, 53.6, 2.3),
              ped.union(B(24, 46.8, 50, 50)), C(37, 56.6, 3.5),
              B(71, 38.4, 74.4, 40.2), RR(73.4, 26.6, 80, 42, .9),                                   # 直式招牌
              P((-0.4, 1.8), (5.4, 1.8), (6.2, 6.4), (-1.2, 6.4)), unary_union([C(2.5, 9.6, 3.4), C(-0.6, 8, 2.2), C(5.6, 8.4, 2.2)])]   # 盆栽
    lines = []
    for cx in (14.5, 37, 59.5):
        lines += [L((cx, 29.4), (cx, 41.4)), L((cx - 4.6, 35), (cx + 4.6, 35)), L((cx - 3, 26.4), (cx - 3, 29.4)), L((cx, 26.4), (cx, 29.4)), L((cx + 3, 26.4), (cx + 3, 29.4))]
    lines += [L((a, y), (a + 3, y)) for a, y in ((22, 33), (25.6, 37), (21.6, 40.6), (47.4, 34.4), (44.6, 38.4), (48, 41.4), (4, 36), (66.6, 33), (5, 31))]
    lines += [ring(C(37, 56.6, 1.6)), ring(C(37, 12.6, 2.5)), L((37, 15.1), (37, 18.4)), L((34.5, 12.6), (39.5, 12.6)),
              ring(RR(74.8, 28.2, 78.6, 40.4, .5))]
    return dict(parts=parts, lines=lines, tab=(37, 40))

# ───────── 8 景：盆地群山背板（沿底座後三邊，折兩折） ─────────
def p_backdrop(U):
    W = 3 * U
    top = cr([(0, 40), (8, 53), (18, 71), (29, 85), (41, 77), (53, 63), (65, 58), (U, 62), (86, 82), (98, 100), (109, 112), (118, 117), (128, 109), (138, 91),
              (2 * U, 75), (158, 73), (170, 82), (183, 91), (195, 83), (207, 65), (216, 51), (W, 45)])
    far = Polygon([(0, 0)] + top + [(W, 0)])
    near = Polygon([(0, 0)] + cr([(0, 24), (15, 34), (32, 30), (50, 41), (70, 35), (90, 47), (108, 41), (125, 51), (145, 39), (165, 47), (185, 37), (205, 43), (W, 31)]) + [(W, 0)])
    parts = [C(57, 71, 9.5), far, near]
    for x0, x1, h in ((79, 85, 17), (85, 93, 25), (93, 99, 19), (99, 106, 30), (106, 113, 21), (113, 119, 34), (119, 126, 23), (126, 132, 28), (132, 140, 18), (140, 145, 23)):
        parts.append(B(x0, 0, x1, h))
    for (x, y, r) in ((11, 8, 6.4), (24, 10, 7.4), (38, 7, 5.4), (52, 9, 6.6), (65, 7, 5), (159, 8, 6), (172, 10, 7.4), (186, 7, 5.6), (200, 9, 6.8), (213, 7, 5)):
        parts.append(C(x, y, r).union(B(x - 1, 0, x + 1, y)))
    lines = [SL((19, 60), (29, 71), (40, 65)), SL((24, 50), (34, 58), (46, 54)), SL((98, 86), (110, 97), (123, 99)), SL((93, 71), (109, 81), (131, 83)),
             SL((100, 58), (116, 66), (134, 64)), SL((171, 70), (183, 79), (196, 71)), SL((176, 56), (188, 63), (202, 55))]
    for x0, x1, h in ((85, 93, 25), (99, 106, 30), (113, 119, 34), (126, 132, 28)):
        for yy in range(6, h - 3, 6):
            lines.append(L((x0 + 1.6, yy), (x1 - 1.6, yy)))
    return dict(parts=parts, lines=lines, tabs=[(U / 2, 30), (1.5 * U, 30), (2.5 * U, 30)], folds=[U, 2 * U])

# ───────── 合成 ─────────
def build(d):
    parts = [p.buffer(0) for p in d['parts']]
    body = unary_union(parts)
    body = body.buffer(0.5, quad_segs=6).buffer(-1.0, quad_segs=6).buffer(0.5, quad_segs=6)      # 去掉太細的部位、內外角帶小圓角
    if body.geom_type != 'Polygon':
        body = max(body.geoms, key=lambda g: g.area)
    body = Polygon(body.exterior)                                   # 不留內孔
    minx, miny, maxx, maxy = body.bounds
    shape = body
    tabs = d.get('tabs') or ([d['tab']] if d.get('tab') else [])
    for (tx, tw) in tabs:
        shape = shape.union(B(tx - tw / 2, -TAB_H, tx + tw / 2, 0.05))
    slot = d.get('slot'); slot_geom = None
    if slot:
        sx, side, yy = slot
        slot_geom = B(sx - SLOT / 2, yy, sx + SLOT / 2, maxy + 5) if side == 'top' else B(sx - SLOT / 2, miny - TAB_H - 5, sx + SLOT / 2, yy)
        shape = shape.difference(slot_geom)
        if shape.geom_type != 'Polygon': shape = max(shape.geoms, key=lambda g: g.area)
    vis = []
    for i, p in enumerate(parts):
        later = unary_union(parts[i + 1:]) if i + 1 < len(parts) else None
        vis.append(p.difference(later) if later is not None else p)
    bounds = unary_union([v.boundary for v in vis if not v.is_empty] + list(d.get('lines', [])))
    inner = bounds.intersection(body.buffer(-0.7))
    if slot_geom is not None: inner = inner.difference(slot_geom.buffer(0.6))
    if inner.geom_type == 'MultiLineString': inner = linemerge(inner)
    return dict(shape=shape, body=body, inner=inner, w=maxx - minx, h=maxy - miny, minx=minx, maxx=maxx, miny=miny, maxy=maxy,
                xc=(minx + maxx) / 2, tabs=tabs, slot=slot, folds=d.get('folds', []))
