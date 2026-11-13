# -*- coding: utf-8 -*-
"""建構所有零件、底座，並合成「正面預覽」（上色／線稿）。"""
import os, math, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from geo import *
import pieces as PC

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE = os.path.join(HERE, '_cache'); os.makedirs(CACHE, exist_ok=True)
PREV = os.path.join(ROOT, '預覽'); os.makedirs(PREV, exist_ok=True)

S = 10            # px / mm
AF_ = 140.0       # 六角對邊
RH = AF_ / math.sqrt(3)   # 80.83 邊長＝外接圓半徑
WALL = 14.0
INSET = 6.0
KV = 0.25         # 正面預覽的俯視程度（深度往上移的比例）
HEX = [(RH, 0), (RH / 2, 70), (-RH / 2, 70), (-RH, 0), (-RH / 2, -70), (RH / 2, -70)]
import fonts as _F
_F.ensure()
FONT_K = _F.path('SerifBlack')
FONT_B = _F.path('SerifBold')
FONT_R = _F.path('SerifSemi')

BUILT = {}     # 編號 -> build dict（含 pos）
CROSSB = {}


def build_all():
    for no, name, fn, px, py, wk in PC.LAYOUT:
        b = build(fn()); b.update(no=no, pos=(px, py), week=wk, label=name)
        BUILT[no] = b
        print('%d %-6s 寬 %.1f 高 %.1f' % (no, name, b['w'], b['maxy']))
    for no, fn in PC.CROSS.items():
        b = build(fn()); b.update(no=no, label=b['name']); CROSSB[no] = b
        print('%d B      寬 %.1f 高 %.1f' % (no, b['w'], b['maxy']))
    bd = BUILT[1]
    bd['folds'] = [(PC.UW, 0, 300), (PC.UW * 2, 0, 300)]
    BUILT[2]['folds'] = [(-43, 0, 40), (43, 0, 40)]; BUILT[2]['view'] = (-43.3, 43.3)


def img(b, colored=True, key=None):
    key = key or ('%s_%d' % (b['label'], colored))
    if '_img' not in b:
        b['_img'] = {}
    if colored not in b['_img']:
        b['_img'][colored] = paint(b.get('shape0', b['shape']) if b.get('slot') else b['shape'], b['regions'], b['lines'], S, colored=colored, fade={1: 0.10, 2: 0.14}.get(b['no'], 0.0) if b['label'] in ('群山', '老街屋') else 0.0)
    return b['_img'][colored]


# ---------- 底座頂面的底圖（俯視，先印好） ----------
def slits():
    """回傳 [(編號, (x0,y0),(x1,y1))]：底座頂面的插槽（單線切口）。"""
    out = []
    for no, b in BUILT.items():
        if no == 1:
            c, s_ = 0.5, math.sqrt(3) / 2
            R2 = RH - INSET * 2 / math.sqrt(3)
            VL, BL, BR, VR = (-R2, 0), (-R2 / 2, 70 - INSET), (R2 / 2, 70 - INSET), (R2, 0)
            segs = [(VL, BL), (BL, BR), (BR, VR)]
            for (x, w) in b['tabs']:
                i = int(x // PC.UW); u = x - i * PC.UW
                a, e = segs[i]
                L_ = math.dist(a, e); d = ((e[0] - a[0]) / L_, (e[1] - a[1]) / L_)
                u0, u1 = u - w / 2 - 0.75, u + w / 2 + 0.75
                out.append((no, (a[0] + d[0] * u0, a[1] + d[1] * u0), (a[0] + d[0] * u1, a[1] + d[1] * u1)))
        else:
            px, py = b['pos']
            for (x, w) in b['tabs']:
                out.append((no, (px + x - w / 2 - 0.75, py), (px + x + w / 2 + 0.75, py)))
            if no in CROSSB and CROSSB[no]['tabs']:
                bb = CROSSB[no]; xw = px + b['slot'][1]
                for (xt, wt) in bb['tabs']:
                    yc = py - (xt - bb['slot'][1])
                    out.append((no, (xw, yc - wt / 2 - 0.75), (xw, yc + wt / 2 + 0.75)))
    return out


def deco_regions():
    hexp = Polygon(HEX)
    regs = [(hexp, '#EFE6D6')]
    regs.append((box(-90, -54, 90, -33).intersection(hexp), '#D9D2C4'))
    for i in range(5):
        regs.append((box(-30 + i * 4.6, -51.5, -30 + i * 4.6 + 2.2, -35.5), '#F6EFE2'))
    regs.append((C(52, -43.5, 4.2), '#C9C2B6'))
    lines = []
    inner = hexp.buffer(-1.2)

    def add(a, b_):
        g = LineString([a, b_]).intersection(inner)
        if not g.is_empty and g.geom_type == 'LineString':
            lines.append(g)
    for r, y in enumerate(np.arange(-27, 69, 6.0)):
        add((-90, y), (90, y))
        for x in np.arange(-84 + (6 if r % 2 else 0), 90, 12.0):
            add((x, y), (x, y + 6.0))
    add((-90, -33), (90, -33)); add((-90, -54), (90, -54))
    for y in np.arange(-66, -54, 6.0):
        add((-90, y), (90, y))
    add((49, -43.5), (55, -43.5)); add((52, -46.5), (52, -40.5))
    return hexp, regs, lines


def deco_image():
    hexp, regs, lines = deco_regions()
    return paint(hexp, regs, lines, S, seed=99, colored=True, pad=0, outline=False, ink=(0.79, 0.72, 0.61), lw=0.2)


def font(path, mm):
    return ImageFont.truetype(path, int(mm * S))


# ---------- 正面預覽 ----------
X0, X1, Y0, Y1 = -104, 104, -30, 152


def px(x, y):
    return ((x - X0) * S, (Y1 - y) * S)


def _shadow(canvas, im, pos, off=(9, 7), blur=7, op=0.30):
    a = im.split()[3].filter(ImageFilter.GaussianBlur(blur))
    sh = Image.new('RGBA', im.size, (40, 35, 45, 0)); sh.putalpha(a.point(lambda v: int(v * op)))
    canvas.alpha_composite(sh, (int(pos[0] + off[0]), int(pos[1] + off[1])))


def _notab(im, bd):
    a = np.asarray(im).copy(); a[int(round(bd[3] * S)):, :, 3] = 0
    return Image.fromarray(a, 'RGBA')


def _put(canvas, im, x_mm, y_mm_top, shadow=True, op=0.3):
    p = px(x_mm, y_mm_top); p = (int(round(p[0])), int(round(p[1])))
    if shadow:
        _shadow(canvas, im, p, op=op)
    canvas.alpha_composite(im, p)


def _dark(im, f):
    a = np.asarray(im, float).copy(); a[..., :3] *= f
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def scene(nos=None, colored=True, title=True, path=None, base_colored=True, table=True):
    nos = list(BUILT) if nos is None else nos
    W, H = int((X1 - X0) * S), int((Y1 - Y0) * S)
    g = np.linspace(0, 1, H)[:, None, None]
    bg = (np.array([242, 233, 213]) * (1 - g) + np.array([242, 233, 213]) * g) * np.ones((H, W, 1))
    cv = Image.fromarray(bg.astype(np.uint8), 'RGB').convert('RGBA')
    d = ImageDraw.Draw(cv)
    # 桌面陰影
    sh = Image.new('RGBA', cv.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    ds.ellipse([px(-98, 12)[0], px(0, 16)[1], px(98, 0)[0], px(0, -26)[1]], fill=(90, 70, 50, 60))
    if table:
        cv.alpha_composite(sh.filter(ImageFilter.GaussianBlur(30)))
    # 底座牆
    lift = lambda y: (y + 70) * KV
    top = [px(x, lift(y)) for x, y in HEX]
    wallc = (201, 167, 124, 255)
    f0, f1 = px(-RH / 2, 0), px(RH / 2, 0)
    d.polygon([f0, f1, px(RH / 2, -WALL), px(-RH / 2, -WALL)], fill=wallc)
    d.polygon([px(-RH, lift(0)), f0, px(-RH / 2, -WALL), px(-RH, lift(0) - WALL)], fill=(181, 147, 106, 255))
    d.polygon([px(RH, lift(0)), f1, px(RH / 2, -WALL), px(RH, lift(0) - WALL)], fill=(181, 147, 106, 255))
    ft = font(FONT_K, 9.5); tx = '台 北'
    tw = d.textlength(tx, font=ft)
    d.text((px(0, 0)[0] - tw / 2, px(0, -1.6)[1]), tx, font=ft, fill=(78, 58, 42, 255))
    fe = font(FONT_B, 4.2)
    # 頂面底圖
    dim, db = deco_image()
    if not base_colored:
        dim = dim
    dimk = dim.resize((dim.width, int(dim.height * KV)), Image.LANCZOS)
    cv.alpha_composite(dimk, (int(px(db[0], 0)[0]), int(px(0, lift(db[3]))[1])))
    d = ImageDraw.Draw(cv)
    for no, a, e in slits():
        if no in nos:
            continue
        d.line([px(a[0], lift(a[1])), px(e[0], lift(e[1]))], fill=(120, 110, 100, 255), width=2)
    # 背板
    if 1 in nos:
        b = BUILT[1]; im, bd = img(b, colored); im = _notab(im, bd)
        U = PC.UW; ck = math.sqrt(3) / 2 * KV
        R2 = RH - INSET * 2 / math.sqrt(3)
        pw = int(round(U * S)); pad = int(round((0 - bd[0]) * S))
        Hs = im.height
        base_row = int(round((bd[3] - 0) * S))      # 影像中 y=0 的列
        panels = [im.crop((pad + i * pw, 0, pad + (i + 1) * pw, Hs)) for i in range(3)]
        # 中片
        yb = lift(70 - INSET)
        _put(cv, panels[1], -R2 / 2, yb + bd[3], shadow=False)
        # 側片（斜向，寬度變一半）
        Wd = pw // 2 + 2; Hd = Hs + int(ck * pw)
        lft = _dark(panels[0], 0.93).transform((Wd, Hd), Image.AFFINE, (2, 0, 0, 2 * ck, 1, Hs - Hd), Image.BICUBIC)
        rgt = _dark(panels[2], 0.90).transform((Wd, Hd), Image.AFFINE, (2, 0, 0, -2 * ck, 1, 0), Image.BICUBIC)
        ytop = lift(0) + bd[3] + ck * U      # 側片影像頂端（mm）
        _put(cv, lft, -R2, ytop, shadow=False)
        _put(cv, rgt, R2 / 2 - 0.3, ytop, shadow=False)
    # 其他零件：由後往前
    order = sorted([n for n in nos if n != 1], key=lambda n: -BUILT[n]['pos'][1])
    for n in order:
        b = BUILT[n]; im, bd = img(b, colored); im = _notab(im, bd)
        if 'view' in b:
            a_ = np.asarray(im).copy(); a_[:, :int((b['view'][0] - bd[0]) * S), 3] = 0; a_[:, int((b['view'][1] - bd[0]) * S):, 3] = 0
            im = Image.fromarray(a_, 'RGBA')
        x, y = b['pos']
        _put(cv, im, x + bd[0], lift(y) + bd[3], op=0.26 + 0.22 * (40 - y) / 100)
        if False and n in CROSSB:
            bb = CROSSB[n]; im2, b2 = img(bb, colored); im2 = _notab(im2, b2)
            fsh = 0.1
            im2 = _dark(im2.resize((max(2, int(im2.width * fsh)), im2.height), Image.LANCZOS), 0.95)
            sx = x + b['slot'][1] + (b2[0] - bb['slot'][1]) * fsh
            _put(cv, im2, sx, lift(y) + b2[3], shadow=False)
    out = cv.convert('RGB')
    if path:
        out.save(path)
    return out


if __name__ == '__main__':
    build_all()
    scene(colored=True, path=os.path.join(PREV, '正面預覽_上色.png'))
    scene(colored=False, path=os.path.join(PREV, '正面預覽_未上色.png'))
    # 零件一覽
    for n, b in list(BUILT.items()) + [(k + 100, v) for k, v in CROSSB.items()]:
        img(b, True)[0].save(os.path.join(CACHE, 'p%d.png' % n))
