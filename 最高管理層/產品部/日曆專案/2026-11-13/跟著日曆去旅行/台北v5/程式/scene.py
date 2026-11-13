# -*- coding: utf-8 -*-
"""建構零件、底座，合成「正面組裝預覽」（白紙＋線稿，不上色）。"""
import os, math, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from geo import *
import pieces as PC
import fonts as F_

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE = os.path.join(HERE, '_cache'); os.makedirs(CACHE, exist_ok=True)
PREV = os.path.join(ROOT, '預覽'); os.makedirs(PREV, exist_ok=True)
F_.ensure()

S = 12                      # px / mm
RH, UW, INSET = PC.RH, PC.UW, PC.INSET
HF = PC.AFLAT / 2           # 60
WALL = 12.0
KV = 0.22                   # 預覽的俯視程度
HEX = [(RH, 0), (RH / 2, HF), (-RH / 2, HF), (-RH, 0), (-RH / 2, -HF), (RH / 2, -HF)]
BUILT = {}


def build_all():
    for no, name, fn, px_, py_, wk in PC.LAYOUT:
        b = build(fn()); b.update(no=no, pos=(px_, py_), week=wk, label=name)
        BUILT[no] = b
        print('%d %-6s 寬 %.1f 高 %.1f' % (no, name, b['w'], b['maxy']))
    BUILT[1]['folds'] = [(UW, 0, 300), (UW * 2, 0, 300)]


def img(b):
    if '_img' not in b:
        b['_img'] = paint(b['shape'], b['regions'], b['lines'], S, colored=False, lw=0.22, dlines=b.get('dlines', ()))
    return b['_img']


def slits():
    out = []
    for no, b in BUILT.items():
        if no == 1:
            VL, BL, BR, VR = (-UW, 0), (-UW / 2, HF - INSET), (UW / 2, HF - INSET), (UW, 0)
            segs = [(VL, BL), (BL, BR), (BR, VR)]
            for (x, w) in b['tabs']:
                i = min(2, int(x // UW)); u = x - i * UW
                a, e = segs[i]
                L_ = math.dist(a, e); d = ((e[0] - a[0]) / L_, (e[1] - a[1]) / L_)
                u0, u1 = u - w / 2 - 0.75, u + w / 2 + 0.75
                out.append((no, (a[0] + d[0] * u0, a[1] + d[1] * u0), (a[0] + d[0] * u1, a[1] + d[1] * u1)))
        else:
            px_, py_ = b['pos']
            for (x, w) in b['tabs']:
                out.append((no, (px_ + x - w / 2 - 0.75, py_), (px_ + x + w / 2 + 0.75, py_)))
    return out


def deco_lines():
    """底座頂面的底圖：一張極簡的台北街廓地圖線（淡線），加一道河。"""
    hexp = Polygon(HEX); inner = hexp.buffer(-2.0)
    lines = []

    def add(pts):
        g = LineString(pts).intersection(inner)
        for l_ in ([g] if g.geom_type == 'LineString' else list(getattr(g, 'geoms', []))):
            if l_.length > 2:
                lines.append(l_)
    a = math.radians(12)
    ca, sa = math.cos(a), math.sin(a)
    rt = lambda x, y: (x * ca - y * sa, x * sa + y * ca)
    for i, x in enumerate(np.arange(-84, 85, 12)):
        add([rt(x, -90), rt(x, 90)])
    for j, y in enumerate(np.arange(-84, 85, 9)):
        add([rt(-90, y), rt(90, y)])
    river = cr([(-80, 30), (-52, 14), (-40, -10), (-52, -34), (-40, -70)])
    add(river); add([(x + 3.2, y) for x, y in river])
    return hexp, lines


X0, X1, Y0, Y1 = -86, 86, -26, 132


def px(x, y):
    return ((x - X0) * S, (Y1 - y) * S)


def _notab(im, bd):
    a = np.asarray(im).copy(); a[int(round(bd[3] * S)):, :, 3] = 0
    return Image.fromarray(a, 'RGBA')


def _dark(im, f):
    a = np.asarray(im, float).copy(); a[..., :3] *= f
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def _put(cv, im, x_mm, y_top, shadow=0.0):
    p = px(x_mm, y_top); p = (int(round(p[0])), int(round(p[1])))
    if shadow:
        a = im.split()[3].filter(ImageFilter.GaussianBlur(8))
        sh = Image.new('RGBA', im.size, (50, 44, 40, 0)); sh.putalpha(a.point(lambda v: int(v * shadow)))
        cv.alpha_composite(sh, (p[0] + 9, p[1] + 5))
    cv.alpha_composite(im, p)


def scene(nos=None, path=None, bg=(233, 229, 222), wall=(214, 208, 198), ink=(58, 54, 50)):
    nos = list(BUILT) if nos is None else nos
    W, H = int((X1 - X0) * S), int((Y1 - Y0) * S)
    cv = Image.new('RGBA', (W, H), bg + (255,))
    sh = Image.new('RGBA', cv.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    ds.ellipse([px(-82, 0)[0], px(0, 14)[1], px(82, 0)[0], px(0, -22)[1]], fill=(60, 52, 46, 70))
    cv.alpha_composite(sh.filter(ImageFilter.GaussianBlur(34)))
    d = ImageDraw.Draw(cv)
    lift = lambda y: (y + HF) * KV
    f0, f1 = px(-RH / 2, 0), px(RH / 2, 0)
    d.polygon([f0, f1, px(RH / 2, -WALL), px(-RH / 2, -WALL)], fill=wall + (255,))
    side = tuple(int(v * 0.9) for v in wall) + (255,)
    d.polygon([px(-RH, lift(0)), f0, px(-RH / 2, -WALL), px(-RH, lift(0) - WALL)], fill=side)
    d.polygon([px(RH, lift(0)), f1, px(RH / 2, -WALL), px(RH, lift(0) - WALL)], fill=side)
    ft = ImageFont.truetype(F_.path('SerifBold'), int(6.4 * S))
    tw = d.textlength('台 北', font=ft)
    d.text((px(0, 0)[0] - tw / 2, px(0, -2.4)[1]), '台 北', font=ft, fill=ink + (255,))
    d.polygon([px(x, lift(y)) for x, y in HEX], fill=(250, 248, 243, 255))
    hexp, dl = deco_lines()
    for l_ in dl:
        d.line([px(x, lift(y)) for x, y in l_.coords], fill=(205, 198, 188, 255), width=2)
    if 1 in nos:
        b = BUILT[1]; im, bd = img(b); im = _notab(im, bd)
        ck = math.sqrt(3) / 2 * KV
        pw = int(round(UW * S)); pad = int(round((0 - bd[0]) * S)); Hs = im.height
        panels = [im.crop((pad + i * pw, 0, pad + (i + 1) * pw, Hs)) for i in range(3)]
        _put(cv, panels[1], -UW / 2, lift(HF - INSET) + bd[3])
        Wd = pw // 2 + 2; Hd = Hs + int(ck * pw)
        lft = _dark(panels[0], 0.95).transform((Wd, Hd), Image.AFFINE, (2, 0, 0, 2 * ck, 1, Hs - Hd), Image.BICUBIC)
        rgt = _dark(panels[2], 0.92).transform((Wd, Hd), Image.AFFINE, (2, 0, 0, -2 * ck, 1, 0), Image.BICUBIC)
        ytop = lift(0) + bd[3] + ck * UW
        _put(cv, lft, -UW, ytop); _put(cv, rgt, UW / 2 - 0.3, ytop)
    for n in sorted([n for n in nos if n != 1], key=lambda n: -BUILT[n]['pos'][1]):
        b = BUILT[n]; im, bd = img(b); im = _notab(im, bd)
        x, y = b['pos']
        _put(cv, im, x + bd[0], lift(y) + bd[3], shadow=0.34)
    out = cv.convert('RGB')
    if path:
        out.save(path)
    return out


def closeup(fn, path, s=40):
    b = build(fn())
    im, bd = paint(b['shape'], b['regions'], b['lines'], s, colored=False, lw=0.2, dlines=b.get('dlines', ()))
    bg = Image.new('RGBA', im.size, (220, 226, 223, 255)); bg.alpha_composite(im); bg.convert('RGB').save(path)


if __name__ == '__main__':
    build_all()
    scene(path=os.path.join(PREV, '正面組裝預覽_線稿.png'))
