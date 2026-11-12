"""台北日曆 v5（設計師全權改版）。座標以頁面左上為原點，mm。

版型（仿雷射切割木地圖卡）：上方是一整塊「作品區」（淺橡木底、細木紋），下方是一條明確分開的奶油色「資訊區」。
字體：標題＝思源宋體（Noto Serif TC，Black），內文＝思源黑體（Noto Sans TC，Medium），日期數字＝Georgia Bold。
思源字體是可變字體，這裡用 fontTools 切出需要的字重並只留用到的字，快取在 字體快取/。
用法：python make_calendar5.py 輸出.pdf 2   （2＝只輸出第 2 張 A4）
"""
import io, os, datetime, sys, random
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image, ImageFilter
import numpy as np
from pieces import build, PPM

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, '字體快取')

def make_static(src, wght, out, chars):
    if os.path.exists(out) and os.path.getmtime(out) > os.path.getmtime(__file__):
        return
    from fontTools.ttLib import TTFont as FT
    from fontTools.varLib import instancer
    from fontTools import subset
    os.makedirs(FONT_DIR, exist_ok=True)
    f = FT(src); f = instancer.instantiateVariableFont(f, {'wght': wght})
    opt = subset.Options(); opt.layout_features = ['*']; opt.notdef_outline = True
    s = subset.Subsetter(opt); s.populate(text=chars); s.subset(f); f.save(out)

_src = open(__file__, encoding='utf-8').read()
CHARS = ''.join(sorted(set(_src))) + '0123456789°・，。、（）：；「」'
LSB = {}
for name, src, w in [('SerifBlack', 'NotoSerifTC-VF.ttf', 900), ('SerifBold', 'NotoSerifTC-VF.ttf', 700), ('SerifSemi', 'NotoSerifTC-VF.ttf', 600),
                     ('SansMed', 'NotoSansTC-VF.ttf', 500), ('SansBold', 'NotoSansTC-VF.ttf', 700)]:
    p = os.path.join(FONT_DIR, f'{name}.ttf')
    make_static('C:/Windows/Fonts/' + src, w, p, CHARS)
    pdfmetrics.registerFont(TTFont(name, p))
    from fontTools.ttLib import TTFont as _FT
    _f = _FT(p); LSB[name] = (_f.getBestCmap(), _f['glyf'], _f['head'].unitsPerEm)
pdfmetrics.registerFont(TTFont('GeoB', 'C:/Windows/Fonts/georgiab.ttf'))
pdfmetrics.registerFont(TTFont('SYM', 'C:/Windows/Fonts/seguisym.ttf'))

SCISSOR_ROT, SCISSOR_W, SCISSOR_DY, SCISSOR_PT = 0, 5.2, 0.55, 17   # 剪刀符號：旋轉角、寬(mm)、基線偏移(mm)、字級
MB, NB, WB = 5.68, 18.49, 24.32   # 日期章內：月份、大數字、星期的基線（相對章上緣 mm）
CITY = '台北'; START = datetime.date(2026, 11, 2); WD = '一二三四五六日'
PW, PH = 105.0, 148.0
def H(h): return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
BOARD, WOOD, INK, INK2, RED, CREAM, GRAIN_D, GRAIN_L, EDGE = map(H, ['#F2E9D5', '#DEC6A0', '#2E2218', '#4D3B2C', '#A33F2A', '#FBF5E6', '#B08F5E', '#EFDDB8', '#B99A6A'])

DRAW = {3: ('迪化街的老街屋', '紅磚外牆，拱形窗與細緻的雕飾'), 4: ('龍山寺', '高高翹起的燕尾屋頂，層層飛簷')}
INFO = {3: ('老街', '迪化街・大稻埕', ['清末起，大稻埕是茶葉與／南北貨的集散地', '紅磚、拱窗與牆面雕飾／是老街屋的特色']),
        4: ('信仰', '艋舺龍山寺', ['清乾隆三年（1738）由泉州／移民興建，主祀觀世音菩薩', '三川殿的銅鑄龍柱／是全台唯一'])}

CACHE = {}
def shadowed(im, blur=7, off=(0.5, 0.9), alpha=.38):
    """回傳 (含柔影的 PNG ImageReader, 影像相對本體的位移 mm 與尺寸 mm)。"""
    pad = 40
    W, Hh = im.size
    a = Image.new('L', (W + 2 * pad, Hh + 2 * pad), 0); a.paste(im.split()[3], (pad, pad))
    sh = a.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * alpha))
    base = Image.new('RGBA', a.size, (70, 46, 22, 0)); base.putalpha(sh)
    dx, dy = round(off[0] * PPM), round(off[1] * PPM)
    canvas_ = Image.new('RGBA', a.size, (0, 0, 0, 0)); canvas_.alpha_composite(base, (dx, dy))
    full = Image.new('RGBA', a.size, (0, 0, 0, 0)); full.alpha_composite(canvas_); full.alpha_composite(im, (pad, pad))
    return full, pad / PPM

def piece(k, kind):
    if (k, kind) in CACHE: return CACHE[(k, kind)]
    p = build(CITY, k); im = p[kind]
    if kind == 'color':   # 彩色參考圖：去掉卡榫，只留本體
        im = im.crop((0, 0, im.width, round(p['body_h'] * PPM) - 4))
    full, padmm = shadowed(im)
    buf = io.BytesIO(); full.save(buf, 'PNG'); buf.seek(0)
    CACHE[(k, kind)] = (ImageReader(buf), im.width / PPM, im.height / PPM, padmm, p['tab_cx'], p['tab_w'])
    return CACHE[(k, kind)]

def page(c, x, y, n):
    d = START + datetime.timedelta(days=n - 1); k = (n + 1) // 2
    c.saveState(); c.translate(x * mm, y * mm)
    def Y(v): return (PH - v) * mm
    def tw(s, font, size, track=0): return (sum(pdfmetrics.stringWidth(ch, font, size) for ch in s) + track * mm * 0 + track * (len(s) - 1)) / mm
    def txt(s, xx, base, font, size, rgb, track=0, align='l', optical=False):
        if optical and align == 'l' and font in LSB:   # 光學對齊：扣掉第一個字的左側空隙，字面貼齊基準線
            cm, gl, upm = LSB[font]; g = gl[cm[ord(s[0])]] if ord(s[0]) in cm else None
            if g is not None and hasattr(g, 'xMin'): xx -= g.xMin / upm * size * 0.3528
        w = sum(pdfmetrics.stringWidth(ch, font, size) for ch in s) + track * (len(s) - 1)
        x0 = xx * mm - (w if align == 'r' else w / 2 if align == 'c' else 0)
        t = c.beginText(x0, Y(base)); t.setFont(font, size); t.setFillColorRGB(*rgb); t.setCharSpace(track); t.textOut(s); c.drawText(t)
        return w / mm

    WX, WY, WW, WH = 6, 6, 93, 106        # 作品區（窗）
    BY = WY + WH                          # 資訊區起點 y=112
    # ── 整頁奶油板材
    c.setFillColorRGB(*BOARD); c.rect(0, 0, PW * mm, PH * mm, stroke=0, fill=1)
    # ── 作品區：淺橡木＋細木紋
    c.saveState()
    p = c.beginPath(); p.roundRect(WX * mm, Y(WY + WH), WW * mm, WH * mm, 1.2 * mm); c.clipPath(p, stroke=0, fill=0)
    c.setFillColorRGB(*WOOD); c.rect(WX * mm, Y(WY + WH), WW * mm, WH * mm, stroke=0, fill=1)
    rnd = random.Random(7)
    for i in range(64):
        yy = WY - 4 + i * (WH + 8) / 64 + rnd.uniform(-.6, .6)
        pts = [(WX - 3, yy)]
        for j in range(1, 5): pts.append((WX + WW * j / 4 + rnd.uniform(-5, 5), yy + rnd.uniform(-1.2, 1.2)))
        dark = rnd.random() < .72
        c.setStrokeColorRGB(*(GRAIN_D if dark else GRAIN_L)); c.setStrokeAlpha(rnd.uniform(.10, .26) if dark else rnd.uniform(.25, .5))
        c.setLineWidth(rnd.uniform(.15, .55))
        pa = c.beginPath(); pa.moveTo(pts[0][0] * mm, Y(pts[0][1]))
        for j in range(1, len(pts) - 1, 1):
            xa = (pts[j][0] + pts[j + 1][0]) / 2; ya = (pts[j][1] + pts[j + 1][1]) / 2
            pa.curveTo(((pts[j - 1][0] + pts[j][0]) / 2) * mm, Y(pts[j][1]), pts[j][0] * mm, Y(pts[j][1]), xa * mm, Y(ya))
        pa.lineTo((WX + WW + 3) * mm, Y(pts[-1][1])); c.drawPath(pa, stroke=1, fill=0)
    c.setStrokeAlpha(1); c.restoreState()
    # 窗緣：一圈細暗線，像板材切開的邊
    c.setStrokeColorRGB(*EDGE); c.setLineWidth(.6); c.roundRect(WX * mm, Y(WY + WH), WW * mm, WH * mm, 1.2 * mm, stroke=1, fill=0)

    L, R = 13, 92   # 內容左右界（左基準線，所有左對齊文字的「字面」都貼這條線）
    if n % 2 == 1:   # ── 單數頁
        name, desc = DRAW[k]
        txt('今天來畫', L, 14.5, 'SerifBold', 11.5, RED, 1.8, optical=True)
        txt(name, L, 25.5, 'SerifBlack', 23, INK, 1.2, optical=True)
        txt(desc, L, 33.2, 'SerifSemi', 11.5, INK2, optical=True)
        im, w, h, pad, tabx, tabw = piece(k, 'line')
        top = 36 + (WY + WH - 4 - 36 - h) / 2
        px = 52.5 - w / 2
        c.drawImage(im, (px - pad) * mm, Y(top + h + pad), (w + 2 * pad) * mm, (h + 2 * pad) * mm, mask='auto')
        # 剪刀：停在卡榫底邊最左下角外側，刀口朝右，沿著底邊虛線的方向起剪
        sx, sy = px + tabx - tabw / 2 - 1.2, top + h
        c.saveState(); c.translate(sx * mm, Y(sy - .2)); c.rotate(SCISSOR_ROT)
        t = c.beginText(-SCISSOR_W * mm, -SCISSOR_DY * mm); t.setFont('SYM', SCISSOR_PT); t.setFillColorRGB(*RED); t.textOut('✂'); c.drawText(t)
        c.restoreState()
    else:            # ── 雙數頁
        title, sub, pts = INFO[k]
        txt(title, L, 30.5, 'SerifBlack', 36, INK, 2.4, optical=True)
        txt(sub, L, 39.8, 'SerifBold', 12, RED, 0, optical=True)
        im, w, h, pad = piece(k, 'color')[:4]
        s = min(50 / w, 49 / h); ww, hh = w * s, h * s
        c.drawImage(im, (R + 3.5 - ww - pad * s) * mm, Y(9.5 + (49 - hh) / 2 + hh + pad * s), (ww + 2 * pad * s) * mm, (hh + 2 * pad * s) * mm, mask='auto')
        yy = 73
        for p_ in pts:
            lines = p_.split('／'); y0 = yy
            for ln in lines:
                txt(ln, L + 4.2, yy, 'SerifSemi', 13, INK, optical=True); yy += 8
            top_, bot_ = y0 - 4.9, y0 + 8 * (len(lines) - 1) + 1.9
            c.setFillColorRGB(*RED); c.rect(L * mm, Y(bot_), 1.1 * mm, (bot_ - top_) * mm, stroke=0, fill=1)
            yy += 6

    # ── 資訊區（奶油寬條）
    txt('台 北', L, 126.5, 'SerifBlack', 26, INK, 7, optical=True)
    c.setStrokeColorRGB(*INK); c.setLineWidth(.4); c.line(L * mm, Y(130), 58 * mm, Y(130))
    txt('北緯 25.03°　東經 121.57°', L, 135.4, 'SerifSemi', 10, INK2, .3, optical=True)
    # 進度：七個點（只靠點表達進度），今天是紅色
    for i in range(7):
        cx = L + 1.3 + 5.2 * i; cy = 140.6
        if i + 1 == k: c.setFillColorRGB(*RED); c.circle(cx * mm, Y(cy), 1.5 * mm, stroke=0, fill=1)
        elif i + 1 < k: c.setFillColorRGB(*INK2); c.circle(cx * mm, Y(cy), 1.1 * mm, stroke=0, fill=1)
        else: c.setStrokeColorRGB(*INK2); c.setLineWidth(.45); c.circle(cx * mm, Y(cy), 1.1 * mm, stroke=1, fill=0)
    # 日期章：上緣對齊「台 北」字頂，下緣對齊進度點下緣
    cx0, cy0, cw, ch = 70, 115, 22, 27.4
    c.setFillColorRGB(*RED); c.roundRect(cx0 * mm, Y(cy0 + ch), cw * mm, ch * mm, 1.4 * mm, stroke=0, fill=1)
    c.setStrokeColorRGB(*CREAM); c.setStrokeAlpha(.55); c.setLineWidth(.3); c.roundRect((cx0 + 1) * mm, Y(cy0 + ch - 1), (cw - 2) * mm, (ch - 2) * mm, .8 * mm, stroke=1, fill=0); c.setStrokeAlpha(1)
    txt(f'{d.month}月', cx0 + cw / 2, cy0 + MB, 'SerifBold', 13, CREAM, 1.4, 'c')
    txt(str(d.day), cx0 + cw / 2, cy0 + NB, 'SerifBlack', 38 if d.day < 10 else 34, CREAM, 0, 'c')
    txt(f'星期{WD[d.weekday()]}', cx0 + cw / 2, cy0 + WB, 'SerifBold', 11.5, CREAM, .8, 'c')
    # 剪裁線：A6 頁外緣的圓角矩形（R3 mm），沿線剪出 105×148 圓角頁；角外側維持奶油底色
    c.setStrokeColorRGB(*H('#6B5A4A')); c.setLineWidth(.3); c.setDash([]); c.roundRect(.15 * mm, .15 * mm, (PW - .3) * mm, (PH - .3) * mm, 3 * mm, stroke=1, fill=0)
    c.restoreState()

def main(out, pages_sheet=None):
    c = canvas.Canvas(out, pagesize=(210 * mm, 297 * mm))
    ox, oy = (210 - 2 * PW) / 2, (297 - 2 * PH) / 2
    slots = [(ox, oy + PH), (ox + PW, oy + PH), (ox, oy), (ox + PW, oy)]
    for sheet in range(4):
        if pages_sheet and sheet + 1 not in pages_sheet: continue
        for j, (x, y) in enumerate(slots):
            n = sheet * 4 + j + 1
            if n <= 14: page(c, x, y, n)
        c.setStrokeColorRGB(.45, .4, .35); c.setLineWidth(.25); c.setDash(1.5, 1.5)
        c.line(105 * mm, 0, 105 * mm, 3 * mm); c.line(105 * mm, 294 * mm, 105 * mm, 297 * mm)
        c.line(0, 148.5 * mm, 3 * mm, 148.5 * mm); c.line(207 * mm, 148.5 * mm, 210 * mm, 148.5 * mm); c.setDash([], 0)
        c.showPage()
    c.save()
if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '../列印檔/台北_日曆.pdf', [int(a) for a in sys.argv[2:]] or None)
