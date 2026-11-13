# -*- coding: utf-8 -*-
"""思源宋體（可變字體）切出字重，只留用到的字，快取在 fonts/。"""
import os, glob
HERE = os.path.dirname(os.path.abspath(__file__)); FD = os.path.join(HERE, 'fonts')
W = {'SerifBlack': 900, 'SerifBold': 700, 'SerifSemi': 600, 'SerifReg': 400}


def path(name):
    return os.path.join(FD, name + '.ttf')


def ensure():
    from fontTools.ttLib import TTFont as FT
    from fontTools.varLib import instancer
    from fontTools import subset
    os.makedirs(FD, exist_ok=True)
    s = set('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ，、・（）：')
    srcs = glob.glob(os.path.join(HERE, '*.py'))
    for f in srcs:
        s |= set(open(f, encoding='utf-8').read())
    chars = ''.join(sorted(c for c in s if c >= ' '))
    newest = max(os.path.getmtime(f) for f in srcs)
    for name, w in W.items():
        p = path(name)
        if not os.path.exists(p) or os.path.getmtime(p) < newest:
            f = instancer.instantiateVariableFont(FT('C:/Windows/Fonts/NotoSerifTC-VF.ttf'), {'wght': w})
            o = subset.Options(); o.layout_features = ['*']; o.notdef_outline = True
            sb = subset.Subsetter(o); sb.populate(text=chars); sb.subset(f); f.save(p)
