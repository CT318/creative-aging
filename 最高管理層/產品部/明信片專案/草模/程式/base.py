"""六角底座展開圖（A4 橫式，mm）。左：上蓋（頂面七插槽＋六面側牆＋牆底梯形膠面）；右：下底六角板。
slots 由 layout.py 計算。紅實線＝割線，藍虛線＝摺線，灰＝膠水面。"""
import math
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FLAT = 100.0; WALL_H = 12.0; SLOT_W = 0.8; FLANGE = 8.0; TAB = 4.0
pdfmetrics.registerFont(TTFont('JH', 'C:/Windows/Fonts/msjh.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('JHB', 'C:/Windows/Fonts/msjhbd.ttc', subfontIndex=0))
import os
_FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '字體快取'); _CF = os.path.join(_FD, 'CitySerifBlack.ttf')
if not os.path.exists(_CF):      # 城市名字體＝日曆標題同款（思源宋體 Black），只留城市名用字
    from fontTools.ttLib import TTFont as FT
    from fontTools.varLib import instancer
    from fontTools import subset
    os.makedirs(_FD, exist_ok=True)
    _f = instancer.instantiateVariableFont(FT('C:/Windows/Fonts/NotoSerifTC-VF.ttf'), {'wght': 900})
    _o = subset.Options(); _o.notdef_outline = True; _s = subset.Subsetter(_o); _s.populate(text='台北東京雪梨'); _s.subset(_f); _f.save(_CF)
pdfmetrics.registerFont(TTFont('CITY', _CF))
R = (FLAT / 2) / math.cos(math.radians(30))
RED, BLUE, GRAY = (.85, .1, .1), (.1, .3, .85), (.88, .88, .9)

def add(p, q, s=1): return (p[0] + s * q[0], p[1] + s * q[1])

def make(out, city, slots):
    c = canvas.Canvas(out, pagesize=(297 * mm, 210 * mm))
    CX, CY = 88.0, 102.0            # 上蓋頂面中心
    PX, PY = 233.0, 102.0           # 下底中心
    def V(k, cx=CX, cy=CY, r=R):
        a = math.radians(-60 * k); return (cx + r * math.cos(a), cy + r * math.sin(a))
    def P(pts): return [(x * mm, y * mm) for x, y in pts]
    def poly(pts, stroke, fill=None, w=0.35):
        c.setLineWidth(w); c.setStrokeColorRGB(*stroke); c.setDash([], 0)
        p = c.beginPath(); q = P(pts); p.moveTo(*q[0])
        for x in q[1:]: p.lineTo(*x)
        p.close()
        if fill: c.setFillColorRGB(*fill)
        c.drawPath(p, stroke=1, fill=1 if fill else 0)
    def line(a, b, stroke, dash=None, w=0.35):
        c.setLineWidth(w); c.setStrokeColorRGB(*stroke); c.setDash(*(dash or ([], 0)))
        c.line(a[0] * mm, a[1] * mm, b[0] * mm, b[1] * mm)
    def text(x, y, s, size=8, bold=False, rgb=(.25, .25, .3)):
        c.saveState(); c.setFillColorRGB(*rgb); c.setFont('JHB' if bold else 'JH', size)
        c.drawCentredString(x * mm, y * mm, s); c.restoreState()

    for k in range(6):
        A, B = V(k), V(k + 1)
        mid = ((A[0] + B[0]) / 2 - CX, (A[1] + B[1]) / 2 - CY); L = math.hypot(*mid); n = (mid[0] / L, mid[1] / L)
        u = ((B[0] - A[0]) / R, (B[1] - A[1]) / R)
        A2, B2 = add(A, n, WALL_H), add(B, n, WALL_H)
        # 牆底梯形膠面（向內摺後與下底貼合）
        poly([A2, B2, add(add(B2, n, FLANGE), u, -4.0), add(add(A2, n, FLANGE), u, 4.0)], RED, fill=GRAY)
        poly([A, B, B2, A2], RED, fill=(1, 1, 1))
        # 牆兩側各一個三角膠面：底邊貼著牆的側邊，尖端朝外（沿牆外側延伸方向，離開牆面），黏在隔壁牆內側
        poly([B, B2, add(add(B, n, WALL_H * .5), u, TAB)], RED, fill=GRAY)
        poly([A, A2, add(add(A, n, WALL_H * .5), u, -TAB)], RED, fill=GRAY)
        line(A, B, BLUE, ([2, 1.5], 0))
        line(A2, B2, BLUE, ([2, 1.5], 0))
        if n[1] < -0.9:    # 正前方那面牆：城市名
            cx_, cy_ = (A[0] + B[0]) / 2, (A[1] + B[1]) / 2 - WALL_H / 2
            c.saveState(); c.setFillColorRGB(.29, .21, .15)
            w_ = sum(c.stringWidth(ch, 'CITY', 22) for ch in city) + 7 * (len(city) - 1)
            t = c.beginText((cx_ - w_ / mm / 2) * mm, (cy_ - 3.0) * mm); t.setFont('CITY', 22); t.setCharSpace(7); t.textOut(city); c.drawText(t); c.restoreState()
    poly([V(k) for k in range(6)], RED, w=0.45)
    for k in range(6): line(V(k), V(k + 1), BLUE, ([2, 1.5], 0))
    for sl in slots:
        y = CY + sl['y']; xc = CX + sl['slit_cx']; Ls = sl['slit_len']
        poly([(xc - Ls / 2, y), (xc + Ls / 2, y), (xc + Ls / 2, y + SLOT_W), (xc - Ls / 2, y + SLOT_W)], RED, w=0.3)

    # 下底六角板（略小 1 mm，放進牆內）
    pr = R - 0.6
    poly([V(k, PX, PY, pr) for k in range(6)], RED, w=0.45)
    text(PX, PY - 2, '下底', 16, True, rgb=(.6, .6, .65))
    text(PX, PY - 10, '貼在牆底的梯形膠面上封底', 9, rgb=(.6, .6, .65))

    text(148.5, 199, f'旬常｜{city} 六角底座展開圖（草模）', 15, True)
    text(148.5, 192, '紅實線＝割線　藍虛線＝摺線（先用尺與鈍筆壓線）　灰色＝塗膠水面', 9.5)
    text(148.5, 22, '組裝：①沿藍線把六面牆摺起　②三角膠面黏在隔壁牆內側　③牆底梯形膠面向內摺　④下底六角板貼在梯形膠面上封底　⑤零件卡榫插進頂面插槽', 8.5)
    text(148.5, 15, f'六角對邊 {FLAT:.0f} mm　側牆高 {WALL_H:.0f} mm　插槽寬 {SLOT_W} mm（依卡紙厚度調整）　整張貼在硬紙卡上再割　列印請選「實際大小 100%」', 8.5)
    c.showPage(); c.save()
