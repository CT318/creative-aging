"""台北八件＋底座十字插件的向量幾何（單位 mm，y 向上，基線 y=0）。
每件由多個「部件」多邊形組成，後面的部件蓋住前面的；輸出時自動合成：
外輪廓（割線）一條、內部線（上色分區線）每條只畫一次、不重疊。"""
import math
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union, linemerge

def B(x0, y0, x1, y1):
    return box(x0, y0, x1, y1)

def C(x, y, r):
    return Point(x, y).buffer(r, quad_segs=24)

def P(*pts):
    return Polygon(pts)

def arch(x0, y0, x1, y1):
    """拱窗：下方長方形＋上方半圓，總高 y1。"""
    r = (x1 - x0) / 2
    return unary_union([B(x0, y0, x1, y1 - r), C((x0 + x1) / 2, y1 - r, r).intersection(B(x0, y1 - r, x1, y1))])

def trap(xc, y0, wb, wt, h):
    return P((xc - wb / 2, y0), (xc + wb / 2, y0), (xc + wt / 2, y0 + h), (xc - wt / 2, y0 + h))

TAB_H = 8.0   # 卡榫高（插進底座、正面看不到）

# ───────── 各件 ─────────
def p_night():          # 1 夜市小吃攤 42 × 27
    parts = [C(9, 3.4, 3.4), C(33, 3.4, 3.4), B(3, 6.4, 39, 15), B(3, 6.4, 21, 15) ,
             B(5, 15, 7.5, 21), B(34.5, 15, 37, 21), B(11, 15, 18, 19.5), B(24, 15, 28, 19.5)]
    xb = [1 + 8 * i for i in range(6)]; xt = [4 + 6.8 * i for i in range(6)]
    for i in range(5):
        parts.append(P((xb[i], 21), (xb[i + 1], 21), (xt[i + 1], 27), (xt[i], 27)))
    return parts, 18

def p_mrt():            # 2 捷運列車（側面）52 × 24
    parts = [B(5, 0.6, 15, 3.2), B(37, 0.6, 47, 3.2),
             P((1, 3), (46, 3), (51, 9), (51, 20), (47, 24), (1, 24)),
             B(1, 7.5, 51, 10.5).intersection(P((1, 3), (46, 3), (51, 9), (51, 20), (47, 24), (1, 24))),
             B(4, 13, 11, 20), B(20, 13, 27, 20), B(34, 13, 40, 20),
             B(13, 3, 18, 21.5), B(28.5, 3, 32.5, 21.5), B(42.5, 13, 47.5, 20)]
    return parts, 24

def p_redhouse():       # 3 西門紅樓（八角樓正面）44 × 42
    parts = [B(4, 0, 40, 24), B(4, 0, 15, 24), B(29, 0, 40, 24),
             arch(7, 7, 12, 17), arch(18.5, 0, 25.5, 15), arch(32, 7, 37, 17),
             B(2, 24, 42, 27.5), B(8, 27.5, 36, 33.5),
             B(11.5, 29, 15.5, 32), B(20, 29, 24, 32), B(28.5, 29, 32.5, 32),
             P((5, 33.5), (39, 33.5), (30, 39), (14, 39)), B(19.5, 39, 24.5, 42)]
    return parts, 16

def p_dihua():          # 4 迪化街街屋（兩間）48 × 約 40
    parts = []
    for x0, r in ((0, 5.5), (24, 7)):
        parts += [B(x0, 0, x0 + 24, 13), arch(x0 + 5, 0, x0 + 19, 10.5),
                  B(x0, 13, x0 + 24, 27), arch(x0 + 4, 16, x0 + 10, 24.5), arch(x0 + 14, 16, x0 + 20, 24.5),
                  B(x0, 27, x0 + 24, 29.5)]
        gable = unary_union([B(x0 + 2, 29.5, x0 + 22, 33), C(x0 + 12, 33, r).intersection(B(x0, 33, x0 + 24, 60))])
        parts += [gable, C(x0 + 12, 34.3, 2.1)]
    return parts, 34

def p_temple():         # 5 龍山寺 64 × 約 62
    parts = [B(2, 0, 62, 4), B(8, 4, 56, 20), B(26, 4, 38, 16), B(12, 4, 20, 13), B(44, 4, 52, 13),
             P((0, 24), (5, 20), (59, 20), (64, 24), (57, 27), (7, 27)),
             B(14, 27, 50, 34), B(18, 28.5, 28, 32.5), B(30, 28.5, 34, 32.5), B(36, 28.5, 46, 32.5),
             P((8, 41), (14, 34), (50, 34), (56, 41), (48, 39.5), (16, 39.5)),
             B(20, 39.5, 44, 42.5), P((16, 39.5), (20, 39.5), (20, 42.5), (15, 45)), P((44, 39.5), (48, 39.5), (49, 45), (44, 42.5)),
             P((29, 42.5), (35, 42.5), (34, 48), (30, 48)), C(32, 50.4, 2.6)]
    from shapely import affinity
    return [affinity.scale(p, 1, 1.16, origin=(0, 0)) for p in parts], 24

def p_office():         # 6 總統府 60 × 73
    parts = [B(0, 0, 60, 22)]
    for x in (3, 10, 17, 39, 46, 53):
        parts += [B(x, 4, x + 4, 10), B(x, 13, x + 4, 19)]
    parts += [arch(25, 0, 35, 13), B(0, 22, 23, 24.5), B(37, 22, 60, 24.5),
              B(0, 24.5, 8, 29), B(52, 24.5, 60, 29), P((-0.5, 29), (8.5, 29), (4, 33)), P((51.5, 29), (60.5, 29), (56, 33)),
              B(23, 22, 37, 44), arch(27.5, 27, 32.5, 39), B(22, 44, 38, 47),
              B(25, 47, 35, 62), C(30, 54.5, 3.2),
              P((23.5, 62), (36.5, 62), (34, 67), (26, 67)), P((28.4, 67), (31.6, 67), (30, 73))]
    return parts, 14

def p_101():            # 7 台北 101  30 × 128
    parts = [P((8, 0), (22, 0), (23.5, 16), (6.5, 16)), C(15, 9, 2.8)]
    y = 16.0
    for i in range(8):
        parts.append(trap(15, y, 10, 16, 11)); y += 11
    parts += [P((11, y), (19, y), (18, y + 7), (12, y + 7)), P((13.9, y + 7), (16.1, y + 7), (15.4, 128), (14.6, 128))]
    return parts, 9

def p_mountain():       # 8 象山（背景山，緩坡雙峰）100 × 約 87
    ridge = [(0, 0), (100, 0), (100, 24), (92, 32), (84, 42), (76, 50), (68, 56), (60, 60), (54, 62), (48, 60),
             (42, 55), (36, 51), (30, 50), (24, 46), (16, 38), (8, 30), (0, 22)]
    m = P(*ridge)
    shade = P((54, 62), (60, 60), (68, 56), (76, 50), (84, 42), (92, 32), (100, 24), (100, 0), (78, 0), (70, 22), (62, 42)).intersection(m)
    parts = [m, shade,
             P((38, 44), (45, 42), (49, 47), (46, 52), (40, 51)),          # 巨石（象山六巨石）
             P((50, 47), (55, 45), (58, 50), (54, 54), (50, 52)),
             P((8, 4), (18, 4), (13, 19)), P((20, 4), (32, 4), (26, 22)), P((34, 4), (44, 4), (39, 17)),   # 山腳樹林
             P((84, 4), (94, 4), (89, 18))]
    from shapely import affinity
    return [affinity.scale(p, 1, 1.4, origin=(0, 0)) for p in parts], 30

def p_tree():           # 底座十字插件：行道樹 22 × 29（兩片一組）
    parts = [B(9.4, 0, 12.6, 14), unary_union([C(11, 20.5, 8.3), C(5, 15.5, 5), C(17, 15.5, 5)])]
    return parts, 0

PIECES = [  # 名稱, 函式, 排位深度(mm，離底座前緣), 中心 x(mm，底座中心=0)
    ('夜市', p_night, 18, -24), ('捷運', p_mrt, 18, 24),
    ('迪化街', p_dihua, 44, -14), ('西門紅樓', p_redhouse, 44, 27),
    ('龍山寺', p_temple, 70, -33), ('總統府', p_office, 70, 31),
    ('台北101', p_101, 96, 6), ('象山', p_mountain, 122, -1),
]
TREES = [(30, -50), (58, 61)]   # 十字行道樹的位置（深度, x）

def build(fn):
    parts, tab_w = fn()
    parts = [p.buffer(0) for p in parts]
    body = unary_union(parts)
    minx, miny, maxx, maxy = body.bounds
    # 卡榫：置中於本體最寬實心處下方
    xc = (minx + maxx) / 2
    shape = body
    if tab_w:
        shape = unary_union([body, B(xc - tab_w / 2, -TAB_H, xc + tab_w / 2, 0.01)])
    # 內部線：每個部件可見部分的邊界，扣掉外輪廓
    vis = []
    for i, p in enumerate(parts):
        later = unary_union(parts[i + 1:]) if i + 1 < len(parts) else None
        vis.append(p.difference(later) if later is not None else p)
    bounds = unary_union([v.boundary for v in vis if not v.is_empty])
    inner = bounds.difference(body.exterior.buffer(0.02))
    inner = linemerge(inner) if inner.geom_type in ('MultiLineString',) else inner
    return dict(shape=shape, body=body, inner=inner, w=maxx - minx, h=maxy - miny, minx=minx, xc=xc, tab_w=tab_w)
