"""思源字體（可變字體）切出需要的字重並只留用到的字，快取在 字體快取/。"""
import os, glob
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
HERE = os.path.dirname(os.path.abspath(__file__)); FD = os.path.join(HERE, '字體快取')
def _chars():
    s = set('0123456789°・，、（）：；「」＋－×—～ ')
    for f in glob.glob(os.path.join(HERE, '*.py')):
        s |= set(open(f, encoding='utf-8').read())
    return ''.join(sorted(s))
def register():
    from fontTools.ttLib import TTFont as FT
    from fontTools.varLib import instancer
    from fontTools import subset
    os.makedirs(FD, exist_ok=True); chars = _chars()
    for name, src, w in [('SerifBlack', 'NotoSerifTC-VF.ttf', 900), ('SerifBold', 'NotoSerifTC-VF.ttf', 700), ('SerifSemi', 'NotoSerifTC-VF.ttf', 600),
                         ('SansMed', 'NotoSansTC-VF.ttf', 500)]:
        p = os.path.join(FD, f'{name}_w.ttf')
        if not os.path.exists(p) or os.path.getmtime(p) < max(os.path.getmtime(f) for f in glob.glob(os.path.join(HERE, '*.py'))):
            f = instancer.instantiateVariableFont(FT('C:/Windows/Fonts/' + src), {'wght': w})
            o = subset.Options(); o.layout_features = ['*']; o.notdef_outline = True
            s = subset.Subsetter(o); s.populate(text=chars); s.subset(f); f.save(p)
        pdfmetrics.registerFont(TTFont(name, p))
    pdfmetrics.registerFont(TTFont('SYM', 'C:/Windows/Fonts/seguisym.ttf'))
    pdfmetrics.registerFont(TTFont('JH', 'C:/Windows/Fonts/msjh.ttc', subfontIndex=0))
    pdfmetrics.registerFont(TTFont('JHB', 'C:/Windows/Fonts/msjhbd.ttc', subfontIndex=0))
