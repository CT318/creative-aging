# -*- coding: utf-8 -*-
"""台北 v5：濃縮的城市——高樓林立＋古蹟，垂直方向誇張，小而密。全部是線稿（不上色）。
每件原點在底邊中央，y=0 是底座頂面。底座六角對邊 120 mm。"""
import os, sys, math
from geo import *

AFLAT = 120.0
RH = AFLAT / math.sqrt(3)
INSET = 5.0
UW = RH - INSET * 2 / math.sqrt(3)      # 背板每片寬 63.5

# 借用 v4 已畫好的幾件，縮小後當配角
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '台北v4', '程式'))
import importlib.util
_spec = importlib.util.spec_from_file_location('v4pieces', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '台北v4', '程式', 'pieces.py'))
V4 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(V4)


def take(pc, src, s=1.0, dx=0.0, dy=0.0, flip=False):
    """把另一件的圖形縮放、平移後併進來。"""
    def T(g):
        g = AF.scale(g, -s if flip else s, s, origin=(0, 0))
        return AF.translate(g, dx, dy)
    for k, g, c in src.items:
        pc.items.append((k, T(g), c))
    for g in src.cuts:
        pc.cuts.append(T(g))


def win(pc, x, y, w, h, cross=True):
    pc.l(L((x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)))
    if cross:
        pc.l(L((x + w / 2, y), (x + w / 2, y + h)))


def tank(pc, xc, y, w=6.0):
    """屋頂水塔：台北公寓的標準配備。"""
    pc.f(R(xc - w / 2 + 0.6, y, 1.6, 2.6), 'a'); pc.f(R(xc + w / 2 - 2.2, y, 1.6, 2.6), 'a')
    pc.f(R(xc - w / 2, y + 2.4, w, 4.6, 1.0), 'b')
    pc.f(half(E(xc, y + 7.0, w / 2, 1.5), y + 7.0), 'a')
    pc.l(L((xc - w / 2 + 0.6, y + 4.7), (xc + w / 2 - 0.6, y + 4.7)))


def mast(pc, xc, y, h=6.0):
    pc.f(R(xc - 1.2, y, 2.4, h), 'a')
    pc.f(R(xc - 3.2, y + h - 2.2, 6.4, 2.2), 'a')


def tower(pc, x, w, h, kind, top=None):
    pc.f(R(x, 0, w, h), 'a')
    pc.f(R(x - 0.5, h - 1.8, w + 1.0, 1.8), 'b')
    if kind == 'grid':
        for xx in np.arange(x + 2.4, x + w - 1.4, 2.6):
            pc.l(L((xx, 7), (xx, h - 3)))
        for yy in np.arange(7, h - 2.5, 3.1):
            pc.l(L((x + 1, yy), (x + w - 1, yy)))
    elif kind == 'cells':
        n = max(2, int((w - 2.4) // 3.2)); cw = (w - 2.4 - (n - 1) * 1.0) / n
        for yy in np.arange(7, h - 5.5, 4.4):
            for i in range(n):
                win(pc, x + 1.2 + i * (cw + 1.0), yy, cw, 2.8, cross=False)
    elif kind == 'bands':
        for yy in np.arange(7, h - 5, 4.2):
            pc.l(L((x + 1.2, yy), (x + w - 1.2, yy))); pc.l(L((x + 1.2, yy + 2.2), (x + w - 1.2, yy + 2.2)))
            for xx in np.arange(x + 3.4, x + w - 2, 3.0):
                pc.l(L((xx, yy), (xx, yy + 2.2)))
    # 一樓：騎樓與店面
    pc.l(L((x + 0.8, 5.4), (x + w - 0.8, 5.4)))
    win(pc, x + w / 2 - 1.8, 0.6, 3.6, 4.0)
    xc = x + w / 2
    if top == 'pent':                     # 屋突＋女兒牆欄杆
        pc.f(R(x + 1.2, h, w - 2.4, 2.2), 'b'); pc.f(R(xc - 3, h + 2.2, 6, 5.4), 'a')
        win(pc, xc - 1.6, h + 3.4, 3.2, 2.8)
    elif top == 'tank':
        tank(pc, xc - 1.5, h)
    elif top == 'tanks':
        tank(pc, xc - 3.4, h, 5.0); tank(pc, xc + 3.0, h, 5.0)
    elif top == 'mast':
        pc.f(R(x + 1.5, h, w - 3, 2.6), 'b'); mast(pc, xc + 1.5, h + 2.6, 6)
    elif top == 'frame':                  # 屋頂廣告看板：鏤空的框
        pc.f(R(x + 1.0, h, 2.2, 3.4), 'a'); pc.f(R(x + w - 3.2, h, 2.2, 3.4), 'a')
        pc.f(R(x + 0.4, h + 3.2, w - 0.8, 8.4), 'b')
        pc.cut(R(x + 2.8, h + 5.6, w - 5.6, 3.6))
    elif top == 'slope':                  # 斜切的玻璃頂
        pc.f(P((x, h), (x + w, h), (x + w, h + 3), (x, h + 8)), 'b')
        pc.l(L((x + 1, h + 1.6), (x + w - 1, h + 1.6)))
    elif top == 'board':
        pc.f(R(x + 1.6, h, 2.2, 3), 'a'); pc.f(R(x + w - 3.8, h, 2.2, 3), 'a')
        pc.f(R(x + 0.8, h + 2.8, w - 1.6, 6.2), 'b')
        pc.l(L((x + 2.4, h + 4.4), (x + w - 2.4, h + 4.4), (x + w - 2.4, h + 7.4), (x + 2.4, h + 7.4), (x + 2.4, h + 4.4)))


def p_towers():
    pc = Piece('高樓', tabs=[(-20, 9), (20, 9)])
    pc.f(R(-38, 0, 76, 3), 'g')
    tower(pc, -38, 11, 58, 'cells', 'tank')
    tower(pc, -27, 13, 80, 'grid', 'frame')
    tower(pc, -14, 12, 64, 'bands', 'board')
    tower(pc, -2, 14, 92, 'grid', 'slope')
    pc.cut(R(2, 44, 6, 5)); pc.cut(R(2, 68, 6, 5)); pc.cut(R(-23.5, 52, 6, 5))
    tower(pc, 12, 12, 70, 'cells', 'pent')
    tower(pc, 24, 14, 52, 'bands', 'mast')
    return pc


def flat(pc, x, w, floors, fh=8.6, shop=True, sign=None, roof=None):
    """公寓：每層有陽台欄杆、窗、冷氣。"""
    h = 5.5 + floors * fh
    pc.f(R(x, 0, w, h), 'a')
    n = max(2, int(w // 7.5)); bw = (w - 1.6) / n
    for f in range(floors):
        y = 5.5 + f * fh
        pc.l(L((x + 0.8, y), (x + w - 0.8, y)))
        for i in range(n):
            x0 = x + 0.8 + i * bw
            win(pc, x0 + 1.0, y + 3.3, bw - 2.0, 4.0)
            pc.l(L((x0 + 0.5, y + 2.6), (x0 + bw - 0.5, y + 2.6)))                 # 欄杆扶手
            for xx in np.arange(x0 + 1.6, x0 + bw - 1.0, 2.2):
                pc.l(L((xx, y + 0.4), (xx, y + 2.6)))
            if (f + i) % 3 == 0:
                pc.l(L((x0 + bw - 2.6, y + 0.6), (x0 + bw - 0.9, y + 0.6), (x0 + bw - 0.9, y + 2.0), (x0 + bw - 2.6, y + 2.0), (x0 + bw - 2.6, y + 0.6)))
    if shop:      # 一樓鐵捲門與遮雨棚
        for i in range(n):
            x0 = x + 0.8 + i * bw
            for yy in (1.2, 2.2, 3.2):
                pc.l(L((x0 + 0.9, yy), (x0 + bw - 0.9, yy)))
            pc.l(L((x0 + 0.5, 0.4), (x0 + 0.5, 4.4), (x0 + bw - 0.5, 4.4), (x0 + bw - 0.5, 0.4)))
    if sign is not None:          # 直式招牌
        sx, sy, sh = sign
        pc.f(R(x + sx, sy, 3.4, sh, 0.6), 'b')
        for yy in np.arange(sy + 2.2, sy + sh - 1, 3.2):
            pc.l(L((x + sx + 0.8, yy), (x + sx + 2.6, yy)))
    xc = x + w / 2
    pc.f(R(x - 0.4, h, w + 0.8, 1.6), 'b')
    if roof == 'tank':
        tank(pc, xc - 2, h + 1.6)
    elif roof == 'shed':          # 鐵皮加蓋
        pc.f(P((x + 1, h + 1.6), (x + w - 1, h + 1.6), (x + w - 1, h + 5.2), (x + 1, h + 8.2)), 'a')
        for xx in np.arange(x + 2.6, x + w - 1.4, 2.4):
            pc.l(L((xx, h + 2.2), (xx, h + 5.0)))
    elif roof == 'mast':
        tank(pc, xc - 4.5, h + 1.6, 5.2); mast(pc, xc + 3.5, h + 1.6, 8)
    return h


def p_flats():
    pc = Piece('公寓', tabs=[(-24, 9), (24, 9)])
    pc.f(R(-46, 0, 92, 3), 'g')
    flat(pc, -46, 18, 4, roof='shed')
    flat(pc, -28, 20, 5, sign=(16.4, 14, 18), roof='tank')
    flat(pc, -8, 17, 3, roof='shed', sign=(-0.2, 10, 14))
    flat(pc, 9, 21, 5, roof='mast')
    flat(pc, 30, 16, 4, sign=(-0.4, 16, 16), roof='tank')
    return pc


def _roof(pc, hw, y, rise, th):
    """燕尾屋頂：屋簷兩端往上翹。"""
    eave = cr([(-hw - 6.4, y + rise + 4.8), (-hw - 0.5, y + rise * 0.5), (-hw * 0.55, y), (hw * 0.55, y), (hw + 0.5, y + rise * 0.5), (hw + 6.4, y + rise + 4.8)])
    pc.f(Polygon(eave + [(hw + 4.6, y + rise + 4.9), (hw * 0.72, y + th), (-hw * 0.72, y + th), (-hw - 4.6, y + rise + 4.9)]).buffer(0), 'b')
    for xx in np.arange(-hw * 0.7, hw * 0.71, 2.0):
        pc.l(L((xx * 1.16, y + 0.7), (xx, y + th - 0.4)))


def p_temple():
    pc = Piece('廟', tabs=[(-12, 8), (12, 8)])
    pc.f(R(-24, 0, 48, 2.6), 'g'); pc.f(R(-21.5, 2.6, 43, 2.0), 'a')
    pc.f(R(-19, 4.6, 38, 15), 'a')
    for xc in (-18, -8.4, 8.4, 18):
        pc.f(R(xc - 1.1, 4.6, 2.2, 15), 'b')
    pc.cut(arch(0, 4.9, 7.6, 12.2))
    for xc in (-13.2, 13.2):
        pc.f(R(xc - 3.2, 4.6, 6.4, 10.6), 'c'); pc.l(L((xc, 4.6), (xc, 15.2)))
        pc.f(E(xc, 17.2, 1.5, 1.9), 'b')                         # 燈籠
    pc.f(R(-4.4, 17.2, 8.8, 2.2), 'b')                           # 匾額
    _roof(pc, 22.5, 19.6, 4.2, 7.6)
    pc.f(R(-13.5, 27.2, 27, 6.6), 'a')
    for xc in (-9, -3, 3, 9):
        win(pc, xc - 2, 28.4, 4, 3.6)
    _roof(pc, 17.5, 33.8, 4.0, 7.2)
    pc.f(R(-12.6, 40.6, 25.2, 2.0), 'a')
    pc.f(R(-2.6, 42.4, 5.2, 1.8), 'b'); pc.f(R(-1.9, 44.2, 3.8, 1.8), 'b'); pc.f(P((-1.6, 46), (1.6, 46), (0, 49)), 'b')
    for sg in (-1, 1):
        pc.f(P((sg * 9, 40.6), (sg * 12.6, 40.6), (sg * 19.6, 46.6), (sg * 17.8, 46.6), (sg * 11.6, 42.6), (sg * 9, 42.6)), 'b')
    return pc


def p_shophouse():
    pc = Piece('老街屋', tabs=[(-8.4, 8), (8.4, 8)])
    src = V4.p_house()
    src.items = [(k, g, c) for k, g, c in src.items if g.bounds[0] > -44.5 and g.bounds[2] < 44.5]      # 去掉兩端折翼
    take(pc, src, 0.56)
    return pc


def p_tree():
    pc = Piece('大樹與藍鵲', tabs=[(0, 10)])
    src = V4.p_tree_a()
    bird = src.items[-11:]; src.items = src.items[:-11]
    src.items += [(k, AF.scale(g, 0.6, 0.6, origin=(20, 27.6)), c) for k, g, c in bird]      # 鳥縮小，讓長尾懸空
    take(pc, src, 0.64)
    return pc


def p_stall():
    pc = Piece('夜市攤', tabs=[(-7, 8), (7, 8)])
    take(pc, V4.p_stall(), 0.62)
    return pc


def p_street():
    pc = Piece('街角', tabs=[(-26, 9), (24, 9)])
    pc.f(R(-43, 0, 86, 2.6), 'g')
    take(pc, V4.p_mail(), 0.9, dx=-28)
    take(pc, V4.p_azalea_b(), 1.0, dx=0)
    take(pc, V4.p_scooter(), 0.86, dx=26)
    return pc


def p_backdrop():
    W = UW * 3
    k = W / 221.7
    pc = Piece('群山', tabs=[(UW * i + o, 10) for i in range(3) for o in (15, UW - 15)])
    ridge = [(0, 50), (16, 58), (34, 66), (52, 74), (70, 88), (88, 97), (100, 92), (116, 80), (132, 74), (150, 78), (166, 70), (184, 62), (200, 64), (214, 56), (221.7, 52)]
    midr = [(0, 40), (22, 48), (40, 44), (64, 60), (84, 54), (104, 62), (128, 56), (150, 66), (170, 52), (190, 56), (206, 44), (221.7, 42)]
    nearr = [(0, 26), (30, 34), (56, 28), (82, 36), (110, 30), (140, 40), (165, 30), (192, 34), (221.7, 28)]
    for r_, c in ((ridge, 'a'), (midr, 'b'), (nearr, 'c')):
        pc.f(Polygon([(0, 0)] + cr([(x * k, y * 1.08) for x, y in r_]) + [(W, 0)]), c)
    # 山的紋理：順著稜線往下平移的等高線，每層兩道
    for r_, steps in ((ridge, (7, 15)), (midr, (6, 13)), (nearr, (6, 12))):
        for dy in steps:
            pc.l(LineString(cr([(x * k, y * 1.08 - dy) for x, y in r_])))
    pc.f(R(0, 0, W, 2.6), 'g')
    clip = box(0, 0, W, 200)
    pc.items = [(k_, g.intersection(clip), c) for k_, g, c in pc.items]
    return pc


# (編號, 名稱, 函式, 中心 x, 深度 y, 第幾週)；編號＝由後往前的組裝順序
LAYOUT = [
    (1, '群山', p_backdrop, None, None, 1),
    (2, '高樓', p_towers, 0, 40, 2),
    (3, '公寓', p_flats, 0, 24, 2),
    (4, '廟', p_temple, -28, 8, 3),
    (5, '老街屋', p_shophouse, 22, 8, 3),
    (6, '大樹與藍鵲', p_tree, -44, -14, 3),
    (7, '夜市攤', p_stall, 43, -16, 4),
    (8, '街角', p_street, 0, -40, 4),
]


def p_scooter5():
    """台灣街頭的速克達（側面，車頭朝右）。輪徑 10、軸距 26。"""
    pc = Piece('機車')
    for cx in (-13, 13):
        pc.f(C(cx, 5, 5), 'a'); pc.f(C(cx, 5, 3.1), 'b'); pc.f(C(cx, 5, 1.0), 'a')
        for a in range(0, 360, 60):
            pc.l(rot(L((cx, 6.2), (cx, 7.9)), a, (cx, 5)))
    # 前叉、前土除
    pc.f(P((12, 5), (14.3, 5), (10.8, 17.4), (8.5, 17.4)), 'a')
    pc.f(Polygon([(13 + 6.9 * math.cos(math.radians(a)), 5 + 6.9 * math.sin(math.radians(a))) for a in range(15, 171, 8)] +
                 [(13 + 5.5 * math.cos(math.radians(a)), 5 + 5.5 * math.sin(math.radians(a))) for a in range(170, 14, -8)]), 'b')
    # 後車身（座墊下的車殼，後端上揚）
    pc.f(SP([(-3.4, 7), (-2, 10.2), (-3, 14.2), (-5, 15.6), (-19, 15.8), (-22.4, 16.6), (-22.6, 13.4), (-20, 10.6), (-17, 9.4),
             (-13, 11.6), (-9, 10.2), (-7, 8.2), (-6, 6.6)], 8), 'a')
    pc.l(SL([(-20.6, 13.6), (-13, 13.0), (-5, 13.6)]))
    for xx in (-9.4, -8, -6.6):
        pc.l(L((xx, 9.6), (xx + 0.8, 11.8)))
    # 腳踏板
    pc.f(R(-4, 6.4, 11.6, 2.6, 1.0), 'b')
    pc.l(L((-2.4, 7.7), (6, 7.7)))
    # 前擋板（腿部護板）與車頭
    pc.f(SP([(6.6, 7.2), (9.6, 7.6), (11.4, 12.6), (12.2, 18.6), (10.6, 21.4), (8, 21), (7, 15.4), (5.6, 10)], 8), 'a')
    pc.l(SL([(8.2, 9.4), (9.4, 14), (9.8, 19.4)]))
    pc.f(E(12.5, 18.2, 1.7, 2.4), 'c')                                    # 頭燈
    pc.f(SP([(6.2, 21), (7.6, 23.8), (11.8, 24.2), (13.4, 22.4), (12.4, 20.4), (8, 20.2)]), 'b')     # 龍頭罩
    pc.f(R(2.6, 22.2, 4.6, 2.0, 0.9), 'a')                               # 握把
    pc.f(P((8.4, 23.6), (10.6, 23.6), (9.8, 28), (7.6, 28)), 'a')          # 後視鏡桿（2 mm 寬）
    pc.f(E(8.0, 29.2, 2.8, 2.0), 'b')
    # 座墊（前低後高兩段）
    pc.f(SP([(-19.6, 15.6), (-19.4, 18.4), (-13, 19.6), (-10, 18.4), (-5, 18.2), (-3.2, 16.6), (-3.8, 15.4)], 8), 'c')
    pc.l(SL([(-10.4, 15.8), (-10, 18.2)]))
    # 後扶手、尾燈、車牌
    pc.f(R(-25, 17.2, 6.4, 2.0, 0.9), 'a')
    pc.f(R(-23.8, 13.2, 2.0, 2.6, 0.6), 'c')
    pc.f(R(-23.6, 8.4, 3.6, 3.0, 0.4), 'b')
    return pc


def p_street():
    pc = Piece('街角', tabs=[(-26, 9), (24, 9)])
    pc.f(R(-43, 0, 86, 2.6), 'g')
    take(pc, V4.p_mail(), 0.9, dx=-30)
    take(pc, V4.p_azalea_b(), 1.0, dx=-5)
    take(pc, p_scooter5(), 0.78, dx=27.5, dy=2.0)
    return pc


LAYOUT = [
    (1, '群山', p_backdrop, None, None, 1),
    (2, '高樓', p_towers, 0, 40, 2),
    (3, '公寓', p_flats, 0, 24, 2),
    (4, '廟', p_temple, -28, 8, 3),
    (5, '老街屋', p_shophouse, 22, 8, 3),
    (6, '大樹與藍鵲', p_tree, -44, -14, 3),
    (7, '夜市攤', p_stall, 43, -16, 4),
    (8, '街角', p_street, 0, -40, 4),
]


# ================= 第二輪審查後：前景小物全部重畫 =================
def p_scooter5():
    """速克達（側面，車頭朝右）：兩輪完整露出；龍頭、前擋、踏板、座墊、尾燈五個塊面。"""
    pc = Piece('機車')
    for cx in (-14, 14):
        pc.f(C(cx, 5, 5), 'a'); pc.f(C(cx, 5, 3.0), 'b'); pc.f(C(cx, 5, 1.0), 'a')
        for a in range(0, 360, 72):
            pc.l(rot(L((cx, 6.3), (cx, 7.8)), a, (cx, 5)))
        pc.f(Polygon([(cx + 6.8 * math.cos(math.radians(a)), 5 + 6.8 * math.sin(math.radians(a))) for a in range(25, 156, 8)] +
                     [(cx + 5.6 * math.cos(math.radians(a)), 5 + 5.6 * math.sin(math.radians(a))) for a in range(155, 24, -8)]), 'b')
    pc.f(P((13, 5), (15.2, 5), (11.4, 17), (9.2, 17)), 'a')                               # 前叉
    pc.f(R(-7.5, 7.0, 16.5, 3.2, 1.2), 'b'); pc.l(L((-5.5, 8.6), (7, 8.6)))                # 踏板（厚 3.2）
    pc.f(SP([(-23, 12.6), (-22.2, 15.4), (-7, 15.6), (-5, 13), (-4.8, 10), (-8.6, 10), (-9.2, 11.6), (-19.4, 11.6)], 8), 'a')    # 後車殼
    pc.l(SL([(-21, 13.6), (-14, 13.2), (-6.4, 13.8)]))
    pc.f(SP([(-21.6, 15.4), (-21.2, 17.3), (-13, 17.7), (-8, 17.5), (-6.6, 16.4), (-7, 15.4)], 8), 'c')                       # 座墊（薄）
    pc.f(SP([(7, 8), (9.6, 8.4), (11.2, 13), (11.8, 19), (10.2, 21), (8.2, 20.6), (7.4, 15), (6.2, 10.4)], 8), 'a')              # 前擋
    pc.l(SL([(8.4, 10), (9.4, 14.6), (9.6, 19.2)]))
    pc.f(E(12.1, 18.6, 1.5, 2.1), 'c')                                                    # 頭燈
    pc.f(SP([(6.6, 20.6), (7.6, 22.8), (11.4, 23.2), (12.8, 21.8), (12, 20.2), (8, 20)]), 'b')   # 龍頭
    pc.f(R(3.4, 21.2, 4.2, 1.9, 0.9), 'a')
    pc.f(P((8.2, 22.6), (10, 22.6), (9.6, 25.2), (7.8, 25.2)), 'a'); pc.f(E(8.3, 26.2, 2.2, 1.5), 'b')    # 後視鏡（小）
    pc.f(R(-25.4, 15.8, 5.0, 1.9, 0.9), 'a')                                              # 後扶手
    pc.f(R(-24.6, 12.8, 1.9, 2.3, 0.6), 'c')                                              # 尾燈
    return pc


def _flw(pc, x, y, r, a0):
    pet = [rot(E(x, y + r * 0.78, r * 0.55, r * 0.95), a + a0, (x, y)) for a in range(0, 360, 72)]
    pc.f(unary_union(pet + [C(x, y, r * 0.5)]), 'c')
    pc.f(C(x, y, r * 0.24), 'a')
    for a in (-30, 0, 30):
        pc.l(rot(L((x, y + r * 0.3), (x, y + r * 1.1)), a + a0, (x, y)))


def p_azalea5():
    """杜鵑矮灌叢：輪廓由花的凹凸邊構成，葉子小而尖、三片成簇。"""
    pc = Piece('杜鵑')
    pc.f(Polygon([(-13, 0)] + cr([(-13, 0), (-13.6, 4), (-10, 7.4), (-5, 8.6), (0, 9.2), (5, 8.6), (10, 7.4), (13.6, 4), (13, 0)]) + [(13, 0)]).buffer(0), 'a')
    for (x, y, a) in [(-9.6, 3.2, 20), (-3.4, 2.6, -15), (3.6, 3.0, 10), (9.8, 3.0, -20), (-6.2, 6.0, 40), (6.4, 6.0, -40), (0.2, 5.6, 0)]:
        for da in (-38, 0, 38):
            pc.f(rot(E(x, y + 1.6, 0.8, 1.9), a + da, (x, y)), 'b')
    for i, (x, y) in enumerate([(-10.6, 9.0), (-5.2, 11.0), (0.4, 11.8), (6.0, 11.0), (11.0, 8.8), (-1.6, 7.6), (3.4, 7.2)]):
        _flw(pc, x, y, 2.5, i * 23)
    return pc


def p_tree():
    """榕樹：扁寬不規則的樹冠（小葉簇的鋸齒邊、中間有鏤空）、氣根、彎枝；枝頭一隻台灣藍鵲。"""
    pc = Piece('大樹與藍鵲', tabs=[(-2, 10)])
    pc.f(half(E(-2, 0, 13, 3.4), 0), 'g')
    pc.f(SP([(-7.5, 0), (-5, 6), (-4.4, 16), (-7, 24), (-3.6, 25), (-1.4, 19), (0.6, 25.4), (3.8, 24.6), (2.6, 16), (3, 6), (5.2, 0)], 8), 'a')
    pc.l(SL([(-2.6, 2), (-1.8, 10), (-2.4, 17)])); pc.l(SL([(0.8, 3), (0.6, 12)]))
    pc.f(LineString(cr([(1.6, 15), (8, 17.4), (14, 21.6), (19.6, 22.4)])).buffer(1.25, cap_style=2), 'a')      # 彎枝
    for xr in (-12.5, 10.5):                                                                                 # 氣根
        pc.f(R(xr, 0, 1.8, 28), 'a')
    rng = np.random.default_rng(21)
    blobs = []
    for _ in range(64):
        t = rng.uniform(0, 2 * np.pi); rr = np.sqrt(rng.uniform(0, 1))
        blobs.append(C(-1 + 18 * rr * np.cos(t), 33.5 + 8.2 * rr * np.sin(t) + 1.6 * np.cos(t * 2), float(rng.uniform(2.0, 3.2))))
    can = unary_union(blobs)
    pc.f(can, 'b')
    for (x, y, rx, ry) in [(-9, 33, 2.2, 1.5), (2.5, 36.4, 2.4, 1.5), (9.4, 32, 2.0, 1.4)]:
        pc.cut(E(x, y, rx, ry))
    for (x, y) in [(-12, 37), (-5, 39.4), (4, 31), (11, 36.4), (-14, 31), (-2, 33), (6.6, 39.6), (15, 33)]:
        pc.l(_arc5(x, y))
    # 台灣藍鵲：身體水平前傾、頭小、喙長；長尾沿斜線伸出、懸空
    bx, by = 15.6, 24.9
    tail = [(bx + 3.6, by + 1.2), (bx + 4.6, by - 0.8), (bx + 17.6, by - 9.6), (bx + 16.4, by - 7.6)]
    pc.f(LineString([(bx + 3.6, by + 0.2), (bx + 17, by - 8.8)]).buffer(1.25, cap_style=1), 'a')
    for t in (0.3, 0.48, 0.66, 0.84):
        x0 = bx + 3.6 + (17 - 3.6) * t; y0 = by + 0.2 - 9.0 * t
        pc.l(L((x0 - 0.7, y0 - 1.0), (x0 + 0.7, y0 + 1.0)))
    pc.f(SP([(bx + 4.6, by + 0.4), (bx + 2.6, by + 2.3), (bx - 2.4, by + 2.7), (bx - 4.8, by + 1.6), (bx - 4.2, by - 0.6), (bx - 1, by - 1.5), (bx + 3, by - 1.1)], 8), 'b')
    pc.l(SL([(bx + 3.4, by + 0.9), (bx + 0.2, by + 0.3), (bx - 2.6, by + 1.3)]))
    pc.f(C(bx - 5.0, by + 2.2, 1.7), 'c')
    pc.f(P((bx - 6.2, by + 2.9), (bx - 9.8, by + 2.0), (bx - 6.2, by + 1.5)), 'a')
    for dx in (-1.2, 0.8):
        pc.l(L((bx + dx, by - 1.3), (bx + dx, by - 2.6)))
    return pc


def _arc5(x, y):
    return L(*[(x + 1.9 * math.cos(math.radians(a)), y + 1.9 * math.sin(math.radians(a))) for a in range(200, 341, 28)])


def p_street():
    pc = Piece('街角', tabs=[(-22, 9), (22, 9)])
    pc.f(R(-38, 0, 76, 2.6), 'g')
    take(pc, V4.p_mail(), 0.62, dx=-27)
    take(pc, p_azalea5(), 1.0, dx=-3)
    take(pc, p_scooter5(), 0.68, dx=22.5, dy=2.0)
    return pc


LAYOUT = [
    (1, '群山', p_backdrop, None, None, 1),
    (2, '高樓', p_towers, 0, 40, 2),
    (3, '公寓', p_flats, 0, 24, 2),
    (4, '廟', p_temple, -26, 8, 3),
    (5, '老街屋', p_shophouse, 24, 8, 3),
    (6, '大樹與藍鵲', p_tree, -47, -16, 3),
    (7, '夜市攤', p_stall, 44, -18, 4),
    (8, '街角', p_street, -2, -43, 4),
]


# ================= CEO 回饋後（不要大鏤空、樹不要落地的氣根、機車重畫、山的線要被前層蓋住） =================
def p_backdrop():
    W = UW * 3
    k = W / 221.7; ky = 0.92
    pc = Piece('群山', tabs=[(UW * i + o, 10) for i in range(3) for o in (15, UW - 15)])
    ridge = [(0, 50), (16, 58), (34, 66), (52, 74), (70, 88), (88, 97), (100, 92), (116, 80), (132, 74), (150, 78), (166, 70), (184, 62), (200, 64), (214, 56), (221.7, 52)]
    midr = [(0, 40), (22, 48), (40, 44), (64, 60), (84, 54), (104, 62), (128, 56), (150, 66), (170, 52), (190, 56), (206, 44), (221.7, 42)]
    nearr = [(0, 26), (30, 34), (56, 28), (82, 36), (110, 30), (140, 40), (165, 30), (192, 34), (221.7, 28)]
    for r_, c, steps in ((ridge, 'a', (7, 14)), (midr, 'b', (6, 12)), (nearr, 'c', (6, 12))):
        pc.f(Polygon([(0, 0)] + cr([(x * k, y * ky) for x, y in r_]) + [(W, 0)]), c)
        for dy in steps:                      # 這一層的山紋，會被前面的山蓋住
            pc.l(LineString(cr([(x * k, y * ky - dy) for x, y in r_])))
    pc.f(R(0, 0, W, 2.6), 'g')
    clip = box(0, 0, W, 200)
    pc.items = [(k_, g.intersection(clip), c) for k_, g, c in pc.items]
    return pc


def p_towers():
    pc = Piece('高樓', tabs=[(-20, 9), (20, 9)])
    pc.f(R(-38, 0, 76, 3), 'g')
    tower(pc, -38, 11, 54, 'cells', 'tank')
    tower(pc, -27, 13, 72, 'grid', 'board')
    tower(pc, -14, 12, 60, 'bands', 'pent')
    tower(pc, -2, 14, 84, 'grid', 'slope')
    tower(pc, 12, 12, 66, 'cells', 'pent')
    tower(pc, 24, 14, 48, 'bands', 'mast')
    pc.cuts = []
    return pc


_tp0 = p_temple


def p_temple():
    pc = _tp0()
    for g in pc.cuts:                         # 門不鏤空，改成印線
        pc.f(g, 'c')
    pc.l(L((0, 4.9), (0, 16)))
    pc.cuts = []
    return pc


_sh0 = p_shophouse


def p_shophouse():
    pc = _sh0()
    for g in pc.cuts:                         # 拱廊不鏤空（怕站不住），改成印線
        pc.f(g, 'c')
    pc.cuts = []
    return pc


def p_scooter5():
    """速克達（側面，車頭朝右）：一個乾淨的車身輪廓＋兩個完整的輪子。"""
    pc = Piece('機車')
    for cx in (-14, 14):
        pc.f(C(cx, 5, 5), 'a'); pc.f(C(cx, 5, 3.0), 'b'); pc.f(C(cx, 5, 1.0), 'a')
    pc.f(P((11.6, 12), (13.8, 12), (15.1, 5), (13, 5)), 'a')                         # 前叉
    pc.f(Polygon([(14 + 6.9 * math.cos(math.radians(a)), 5 + 6.9 * math.sin(math.radians(a))) for a in range(40, 161, 8)] +
                 [(14 + 5.6 * math.cos(math.radians(a)), 5 + 5.6 * math.sin(math.radians(a))) for a in range(160, 39, -8)]), 'b')   # 前土除
    body = [(-21, 8.6), (-22.6, 12.4), (-21, 15.2), (-6, 15.6), (-4.6, 12.2), (-3, 9.8), (5.6, 9.8), (7.2, 11.4), (8.8, 17), (9.2, 21.4),
            (8, 23.2), (12.6, 23.6), (13.8, 21.6), (12.6, 19.4), (13.2, 13), (12.2, 8.8), (9, 6.6), (-4, 6.6), (-6, 8.4), (-9.2, 10.6), (-14, 11.4), (-18.8, 10.6)]
    pc.f(Polygon(body), 'a')
    pc.l(SL([(-20.6, 13.2), (-13, 12.8), (-5.6, 13.4)]))                              # 車殼飾線
    pc.l(L((-2.4, 8.2), (7.6, 8.2)))                                                 # 踏板
    pc.l(SL([(9.8, 10.4), (10.6, 15), (10.8, 19.6)]))                                 # 前擋飾線
    pc.f(SP([(-19.4, 15.2), (-18.8, 17.9), (-12, 18.3), (-7.6, 17.9), (-6, 15.6)], 8), 'c')     # 座墊
    pc.f(C(12.7, 18.4, 1.5), 'c')                                                    # 頭燈
    pc.f(R(4.4, 21.4, 4.2, 2.0, 0.9), 'b')                                           # 握把
    pc.f(R(-24.2, 12.2, 1.9, 2.4, 0.6), 'c')                                         # 尾燈
    return pc


def p_tree():
    """大樹：寬扁的樹冠（小葉簇的邊）、彎枝，枝頭一隻台灣藍鵲。沒有落地的氣根、沒有鏤空。"""
    pc = Piece('大樹與藍鵲', tabs=[(-2, 10)])
    pc.f(half(E(-2, 0, 12, 3.2), 0), 'g')
    pc.f(SP([(-7.5, 0), (-5, 6), (-4.4, 16), (-7.4, 25), (-3.6, 26.4), (-1.4, 20), (0.6, 26.6), (4, 25.6), (2.6, 16), (3, 6), (5.2, 0)], 8), 'a')
    pc.l(SL([(-2.6, 2), (-1.8, 10), (-2.4, 17)])); pc.l(SL([(0.8, 3), (0.6, 12)]))
    pc.f(LineString(cr([(1.6, 14.6), (8, 17), (14, 21), (19.6, 21.8)])).buffer(1.4, cap_style=2), 'a')
    rng = np.random.default_rng(21)
    blobs = [E(-1, 34, 15, 6.4)]
    for i in range(22):
        t = 2 * np.pi * i / 22
        blobs.append(C(-1 + 16.4 * np.cos(t), 34 + 7.4 * np.sin(t), float(rng.uniform(2.4, 3.4))))
    pc.f(unary_union(blobs), 'b')
    for (x, y) in [(-11, 37), (-4, 39), (5, 32), (10, 37), (-12, 31.4), (-2, 33.6), (4, 38.6)]:
        pc.l(_arc5(x, y))
    bx, by = 15.4, 24.6
    pc.f(P((bx + 3.4, by + 1.3), (bx + 4.6, by - 1.0), (bx + 15.4, by - 6.6), (bx + 15.0, by - 3.6)), 'a')        # 長尾（根部寬、尾端 3 mm）
    for t in (0.35, 0.55, 0.75):
        x0 = bx + 4 + 11.2 * t; y0 = by + 0.1 - 5.2 * t
        pc.l(L((x0 - 0.5, y0 - 1.3), (x0 + 0.5, y0 + 1.5)))
    pc.f(SP([(bx + 4.6, by + 0.4), (bx + 2.6, by + 2.4), (bx - 2.4, by + 2.8), (bx - 4.8, by + 1.6), (bx - 4.2, by - 0.6), (bx - 1, by - 1.6), (bx + 3, by - 1.2)], 8), 'b')
    pc.l(SL([(bx + 3.4, by + 0.9), (bx + 0.2, by + 0.3), (bx - 2.6, by + 1.3)]))
    pc.f(C(bx - 5.0, by + 2.2, 1.8), 'c')
    pc.f(P((bx - 6.2, by + 3.1), (bx - 9.6, by + 2.0), (bx - 6.2, by + 1.3)), 'a')
    return pc


def p_street():
    pc = Piece('街角', tabs=[(-24, 9), (22, 9)])
    pc.f(R(-43, 0, 86, 2.6), 'g')
    take(pc, V4.p_mail(), 0.7, dx=-32)
    take(pc, p_azalea5(), 0.84, dx=-11)
    take(pc, p_scooter5(), 0.8, dx=22.5, dy=2.0)
    return pc


# 分週：每週都有一件高的、一件矮的
LAYOUT = [
    (1, '群山', p_backdrop, None, None, 1),
    (2, '高樓', p_towers, 0, 40, 2),
    (3, '公寓', p_flats, 0, 24, 3),
    (4, '廟', p_temple, -26, 8, 2),
    (5, '老街屋', p_shophouse, 24, 8, 3),
    (6, '大樹與藍鵲', p_tree, -44, -16, 4),
    (7, '夜市攤', p_stall, 44, -18, 4),
    (8, '街角', p_street, 0, -43, 4),
]


# ================= 紙風景審查（v5 第三版第一輪）後 =================
def p_tree():
    """大樹：三四團大小不一的葉叢、分叉的樹幹、彎枝；枝頭一隻台灣藍鵲（兩根長尾羽）。"""
    pc = Piece('大樹與藍鵲', tabs=[(-2, 10)])
    pc.f(half(E(-2, 0, 12, 3.2), 0), 'g')
    pc.f(SP([(-7.5, 0), (-5, 6), (-4.4, 16), (-8.4, 26), (-4.6, 27.6), (-1.4, 20), (1.0, 28), (4.6, 26.6), (2.6, 16), (3, 6), (5.2, 0)], 8), 'a')
    pc.l(SL([(-2.6, 2), (-1.8, 10), (-2.4, 17)])); pc.l(SL([(0.8, 3), (0.6, 12)]))
    pc.f(LineString(cr([(1.6, 14.6), (8, 17), (14, 21), (20, 21.8)])).buffer(1.4, cap_style=2), 'a')
    for i, (x, y, r) in enumerate([(-10, 33, 8.6), (13, 31.5, 6.6), (3, 36.5, 9.6), (-3, 42, 6.0)]):
        pc.f(V4._clump(x, y, r, 61 + i), 'b')
    for (x, y) in [(-11, 35), (4, 39), (13, 33), (-3, 44), (1, 33)]:
        pc.l(_arc5(x, y))
    bx, by = 15.6, 24.6
    for (ex, ey) in ((bx + 16.5, by - 5.2), (bx + 15.0, by - 8.6)):                    # 兩根長尾羽，末端圓頭
        pc.f(LineString([(bx + 3.6, by + 0.2), (ex, ey)]).buffer(1.15, cap_style=1), 'a')
        for t in (0.4, 0.62, 0.84):
            x0 = bx + 3.6 + (ex - bx - 3.6) * t; y0 = by + 0.2 + (ey - by - 0.2) * t
            pc.l(L((x0 - 0.4, y0 - 0.95), (x0 + 0.4, y0 + 0.95)))
    pc.f(SP([(bx + 4.6, by + 0.4), (bx + 2.6, by + 2.4), (bx - 2.4, by + 2.8), (bx - 4.8, by + 1.6), (bx - 4.2, by - 0.6), (bx - 1, by - 1.6), (bx + 3, by - 1.2)], 8), 'b')
    pc.l(SL([(bx + 3.4, by + 0.9), (bx + 0.2, by + 0.3), (bx - 2.6, by + 1.3)]))
    pc.f(C(bx - 5.0, by + 2.2, 1.9), 'c')
    pc.f(P((bx - 6.4, by + 3.2), (bx - 10, by + 2.0), (bx - 6.4, by + 1.2)), 'a')
    return pc


def p_street():
    pc = Piece('街角', tabs=[(-20, 9), (18, 9)])
    pc.f(R(-36, 0, 72, 2.6), 'g')
    take(pc, V4.p_mail(), 0.62, dx=-27)
    take(pc, p_azalea5(), 0.84, dx=-7)
    take(pc, p_scooter5(), 0.64, dx=20, dy=2.0)
    return pc


LAYOUT = [
    (1, '群山', p_backdrop, None, None, 1),
    (2, '高樓', p_towers, 0, 40, 2),
    (3, '公寓', p_flats, 0, 24, 3),
    (4, '廟', p_temple, -21, 8, 2),
    (5, '老街屋', p_shophouse, 29, 8, 3),
    (6, '大樹與藍鵲', p_tree, -42, -18, 4),
    (7, '夜市攤', p_stall, 45, -18, 4),
    (8, '街角', p_street, 4, -43, 4),
]


# ================= 機車照 CEO 給的參考照片重畫（現代速克達，側面，車頭朝右；不放任何品牌字樣） =================
# 簡化版：只留「兩輪、前擋＋龍頭、踏板、座墊、後車殼」五大塊面。街角裡會縮到約 0.54 倍，
# 所以這裡所有細部 ≥ 4.5 mm、缺口不是 ≥ 6 mm 就直接連成一片（縮完 ≥ 2.4 / ≥ 3 mm）。
def p_scooter5():
    pc = Piece('機車')
    RW, FW, WR = (-14.0, 6.0), (15.0, 6.0), 6.0
    # 地面影子：把兩輪之間、輪子底下的楔形空隙填平（印成一塊淡影子）
    pc.f(R(-14.0, 0, 29.0, 7.4), 'g')
    # 後車殼（含引擎）：從踏板後端往後上方掃到微翹的車尾
    rear = pc.f(SP([(-3.0, 7.0), (-2.4, 12.0), (-4.0, 16.4), (-14.0, 17.0), (-23.0, 17.2), (-25.2, 15.8),
                    (-22.0, 12.4), (-16.0, 10.0), (-9.0, 6.0)], 10), 'a')
    pc.l(SL([(-4.4, 12.4), (-13.0, 13.4), (-21.6, 14.6)]))                                   # 車殼腰線
    pc.f(rear.intersection(P((-27, 13), (-21.6, 13.6), (-20.8, 18), (-27, 18))), 'c')         # 尾燈
    # 座墊：一條平順的長座墊，後段略高
    pc.f(SP([(-3.4, 16.0), (-2.6, 17.8), (-6.0, 19.0), (-14.0, 20.2), (-21.0, 20.6), (-23.6, 18.8),
             (-22.0, 16.8), (-12.0, 16.4)], 10), 'c')
    # 踏板
    pc.f(R(-5.0, 6.4, 12.0, 3.6, 1.0), 'b')
    # 前擋＋前車殼：一整塊，從踏板前端往上到龍頭，鼻頭朝前下壓住前輪
    arc = [(FW[0] + 7.4 * math.cos(math.radians(a)), FW[1] + 7.4 * math.sin(math.radians(a))) for a in range(150, 34, -9)]
    pc.f(Polygon([(5.6, 6.4), (9.6, 6.4)] + arc + [(21.6, 11.4), (22.0, 13.2)] +
                 cr([(22.2, 13.4), (19.8, 17.4), (16.4, 21.2), (14.2, 24.6)]) + [(9.6, 24.8)] +
                 cr([(9.6, 24.8), (8.4, 18.0), (6.4, 11.0), (5.6, 6.4)])).buffer(0), 'a')
    pc.l(LineString([(FW[0] + 7.4 * math.cos(math.radians(a)), FW[1] + 7.4 * math.sin(math.radians(a))) for a in range(36, 141, 4)]))   # 前土除
    pc.l(SL([(8.2, 12.4), (11.6, 15.0), (14.4, 15.6)]))                                       # 前擋與車殼的分界
    pc.f(SP([(15.6, 15.0), (19.6, 14.4), (18.4, 17.4), (15.8, 18.0)], 8), 'c')                # 大燈
    # 龍頭：一塊微微後傾的罩子＋往後的握把
    pc.f(SP([(3.6, 25.6), (4.6, 24.4), (9.0, 24.0), (14.8, 23.0), (16.4, 25.2), (14.0, 27.6), (9.0, 27.4), (4.4, 27.0)], 10), 'b')
    pc.l(SL([(8.0, 24.2), (7.8, 27.4)]))                                                     # 握把
    # 輪子：外胎＋輪框（印線），前輪上方加土除
    for (cx, cy) in (RW, FW):
        pc.f(C(cx, cy, WR), 'a'); pc.f(C(cx, cy, 3.6), 'b')
        pc.l(C(cx, cy, 1.2).exterior)
    return pc


def p_street():
    pc = Piece('街角', tabs=[(-22, 9), (20, 9)])
    pc.f(R(-40, 0, 80, 2.6), 'g')
    take(pc, V4.p_mail(), 0.62, dx=-31)
    take(pc, p_azalea5(), 0.84, dx=-11)
    take(pc, p_scooter5(), 0.54, dx=19.5, dy=2.2)
    return pc


# ================= 藍鵲照 CEO 的 Gemini 上色圖改（兩隻、黑頭紅嘴、深藍身體、長尾下垂、尾端白）；符合刀模常規 =================
def _taper(pts, ws):
    """沿平滑中心線做一條粗細漸變的長條（ws＝[(位置0~1, 寬mm)...]），末端圓頭。"""
    c = np.array(cr(pts, False, 12))
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(c, axis=0).T))]
    t = seg / seg[-1]
    w = np.interp(t, [a for a, _ in ws], [b for _, b in ws]) / 2
    d = np.gradient(c, axis=0); d /= np.hypot(d[:, 0], d[:, 1])[:, None]
    n = np.c_[-d[:, 1], d[:, 0]]
    left, right = c + n * w[:, None], c - n * w[:, None]
    g = Polygon(list(map(tuple, left)) + list(map(tuple, right[::-1]))).buffer(0)
    return g.union(Point(*c[-1]).buffer(w[-1], quad_segs=10)).union(Point(*c[0]).buffer(w[0], quad_segs=10)), LineString(c)


def _magpie(pc, x, y, s=1.0, tilt=20.0, tdx=-0.6, tl=12.0, branch=None):
    """一隻停在枝上的台灣藍鵲，面向右。(x, y)＝腳。身體修長、前傾；小黑頭、紅嘴；長尾從尾根往下垂、末端白。"""
    T = lambda g: AF.translate(AF.rotate(AF.scale(g, s, s, origin=(0, 0)), tilt, origin=(0, 0)), x, y)
    Tp = lambda px, py: T(Point(px, py)).coords[0]
    # 尾巴（世界座標往下垂，不跟身體一起轉）：根部 3.4 → 中段 2.6 → 末端 3.0 的槳狀，中間一條線分兩根中央尾羽
    ax, ay = Tp(-4.2, 1.9)
    tail, cl = _taper([(ax, ay), (ax - 0.9 * s, ay - 2.6 * s), (ax + (tdx * 0.45 - 0.9) * s, ay - tl * 0.55 * s), (ax + tdx * s, ay - tl * s)],
                      [(0, 3.6 * s), (0.4, 2.6 * s), (0.7, 2.6 * s), (1, 3.4 * s)])
    pc.f(tail, 'a')
    ex, ey = cl.coords[-1]
    pc.f(tail.intersection(Point(ex, ey + 0.2 * s).buffer(2.9 * s, quad_segs=12)), 'g')       # 白色尾端
    pc.l(substring(cl, 3.0 * s, cl.length - 2.6 * s))
    # 身體＋頭一整個輪廓（修長、前傾；頭小、和頸部順接）
    body = SP([(-5.2, 1.5), (-4.4, 2.7), (-2.0, 3.5), (0.8, 3.9), (2.8, 4.3), (3.9, 5.3), (5.0, 5.6), (6.0, 5.2),
               (6.5, 4.5), (6.3, 3.7), (5.4, 3.1), (4.0, 2.3), (2.2, 0.9), (0.0, 0.1), (-2.4, 0.2), (-4.0, 0.7)], 10)
    bw = T(body)
    if branch is not None:                                                                  # 腹部貼緊樹枝，不留楔形縫
        bb = bw.bounds
        u = bw.union(AF.translate(bw, 0, -2.5 * s)).convex_hull.intersection(box(bb[0] + 1.0 * s, bb[1] - 3 * s, x + 2.2 * s, y + 1.0 * s)).difference(branch)
        bw = unary_union([bw] + [g for g in getattr(u, 'geoms', [u]) if g.geom_type == 'Polygon' and g.distance(bw) < 0.01])
    pc.f(bw, 'b')
    # 摺起來的長翅膀（尖端壓在尾根上）
    pc.f(T(SP([(3.0, 3.8), (1.0, 3.6), (-2.0, 3.3), (-4.8, 2.5), (-5.2, 1.8), (-4.4, 1.4), (-1.5, 1.5), (1.4, 2.0), (3.0, 2.9)], 10)), 'a')
    pc.l(T(SL([(0.6, 2.5), (-2.4, 2.3), (-5.0, 2.0)])))
    # 黑頭＋黑頸（色塊交界自然成線）、紅嘴、眼
    pc.f(T(body).intersection(T(SP([(2.6, 7.0), (2.5, 4.4), (3.5, 3.0), (4.6, 1.6), (8, 1.2), (8, 7.0)], 6))), 'c')
    pc.f(T(P((5.9, 5.1), (8.3, 4.3), (5.9, 3.5))), 'a')
    pc.l(T(C(5.0, 4.6, 0.4).exterior))
    # 紅腳
    for dx in (-0.6, 0.9):
        p0 = Tp(dx, 0.4)
        pc.l(L(p0, (p0[0] + 0.2, p0[1] - 1.1 * s)))


def p_tree():
    """大樹：葉叢樹冠、分叉樹幹、一根往右上伸的粗枝，枝上停著兩隻台灣藍鵲。"""
    pc = Piece('大樹與藍鵲', tabs=[(-2, 10)])
    pc.f(half(E(-2, 0, 12, 3.2), 0), 'g')
    pc.f(SP([(-7.5, 0), (-5, 6), (-4.4, 16), (-8.4, 26), (-4.6, 27.6), (-1.4, 20), (1.0, 28), (4.6, 26.6), (2.6, 16), (3, 6), (5.2, 0)], 8), 'a')
    pc.l(SL([(-2.6, 2), (-1.8, 10), (-2.4, 17)])); pc.l(SL([(0.8, 3), (0.6, 12)]))
    # 粗枝：根部 3.8 漸細到 3.0，往右上伸
    br, _ = _taper([(1.6, 13.0), (8, 14.6), (16, 16.8), (29.5, 18.6)], [(0, 3.8), (1, 3.0)])
    pc.f(br, 'a')
    pc.l(LineString(cr([(4, 13.6), (11, 15.0), (18, 16.8)])))
    for i, (x, y, r) in enumerate([(-10, 34, 8.6), (11.5, 34.6, 6.4), (2.5, 37.5, 9.6), (-3, 43, 6.0)]):
        pc.f(V4._clump(x, y, r, 61 + i), 'b')
    for (x, y) in [(-11, 36), (4, 40), (12, 36.5), (-3, 45), (1, 34)]:
        pc.l(_arc5(x, y))
    # 兩隻藍鵲：後面那隻較挺、前面那隻較平伸，尾巴都垂在枝下
    _magpie(pc, 13.4, 16.5, 1.08, tilt=30, tdx=1.8, tl=10.4, branch=br)
    _magpie(pc, 25.6, 18.6, 1.08, tilt=18, tdx=-0.8, tl=14.4, branch=br)
    return pc


LAYOUT = [
    (1, '群山', p_backdrop, None, None, 1),
    (2, '高樓', p_towers, 0, 40, 2),
    (3, '公寓', p_flats, 0, 24, 3),
    (4, '廟', p_temple, -21, 8, 2),
    (5, '老街屋', p_shophouse, 29, 8, 3),
    (6, '大樹與藍鵲', p_tree, -42, -18, 4),
    (7, '夜市攤', p_stall, 45, -18, 4),
    (8, '街角', p_street, 2, -43, 4),
]
