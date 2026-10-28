"""日曆座展開圖（A4 直式，mm）：楔形紙座。低台面放日曆下緣，台面只微微向後傾（約 14°），日曆下緣自然靠進台面與斜面的夾角（約後仰 20°），不插卡。
側面輪廓（深度 d，高度 h）：(0,0)-(0,12)-(10,12)-(32,72)-(44,72)-(44,0)；一條連續長條（前→台面→斜面→頂→後→底）＋左右兩片側板（接在後壁兩側）。"""
import sys, math
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

W = 110.0                                   # 座寬（> A6 日曆 105 mm；兩片側板各 44 mm，A4 寬 210 剛好放下）
PROFILE = [(0, 0), (0, 11.5), (10, 9), (32, 72), (44, 72), (44, 0)]      # (深度 d, 高度 h)：前擋邊 → 向後傾斜的台面 → 斜面 → 頂 → 後壁 → 底
FLAP = 6.0                                  # 長條兩端的內摺膠面
RED, BLUE, GRAY = (.85, .1, .1), (.1, .3, .85), (.88, .88, .9)
pdfmetrics.registerFont(TTFont('JH', 'C:/Windows/Fonts/msjh.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('JHB', 'C:/Windows/Fonts/msjhbd.ttc', subfontIndex=0))

def make(out):
    c = canvas.Canvas(out, pagesize=(210 * mm, 297 * mm))
    def poly(pts, stroke, fill=None, w=0.35):
        c.setLineWidth(w); c.setStrokeColorRGB(*stroke); c.setDash([], 0)
        p = c.beginPath(); p.moveTo(pts[0][0] * mm, pts[0][1] * mm)
        for x, y in pts[1:]: p.lineTo(x * mm, y * mm)
        p.close()
        if fill: c.setFillColorRGB(*fill)
        c.drawPath(p, stroke=1, fill=1 if fill else 0)
    def line(a, b):
        c.setLineWidth(.35); c.setStrokeColorRGB(*BLUE); c.setDash(2, 1.5); c.line(a[0] * mm, a[1] * mm, b[0] * mm, b[1] * mm); c.setDash([], 0)
    def text(x, y, s, size=9, bold=False, rgb=(.25, .25, .3)):
        c.setFillColorRGB(*rgb); c.setFont('JHB' if bold else 'JH', size); c.drawCentredString(x * mm, y * mm, s)

    # 各面長度（沿輪廓每一邊）
    P = PROFILE
    seg = [math.dist(P[i], P[(i + 1) % len(P)]) for i in range(len(P))]    # 前、台面、斜面、頂、後、底
    order = list(range(len(P)))
    BACK = 4
    xL = (210 - W) / 2; xR = xL + W
    y = 262.0
    ys = []                                  # 每條的上下邊 y
    for i in order:
        ys.append((y, y - seg[i])); y -= seg[i]
    f = 4.0
    for i in order:
        top, bot = ys[i]
        if i != BACK:    # 後壁兩側接側板，其餘兩端各一內摺膠面
            poly([(xL, top), (xL - FLAP, top - f), (xL - FLAP, bot + f), (xL, bot)], RED, fill=GRAY)
            poly([(xR, top), (xR + FLAP, top - f), (xR + FLAP, bot + f), (xR, bot)], RED, fill=GRAY)
        poly([(xL, top), (xR, top), (xR, bot), (xL, bot)], RED, fill=(1, 1, 1))
        if i > 0: line((xL, top), (xR, top))
    # 側板（接在後壁兩側）：輪廓座標 (d,h) → 頁面。後壁上端接「頂」、下端接「底」，h 由下往上
    btop, bbot = ys[BACK]
    for side in (-1, 1):
        pts = []
        for d, h in P:
            px = (xL - (44 - d)) if side < 0 else (xR + (44 - d))
            pts.append((px, bbot + h))
        poly(pts, RED, fill=(1, 1, 1))
        edge = xL if side < 0 else xR
        line((edge, btop), (edge, bbot))
    # 說明
    text(105, 285, '旬常｜日曆座 展開圖（草模）', 15, True)
    text(105, 278, '紅實線＝割線　藍虛線＝摺線（先用尺與鈍筆壓線）　灰色＝塗膠水面', 9.5)
    text(105, 30, '組裝：①沿藍線摺成楔形筒（台面微微向後傾，斜面向後升高）②兩片側板向內摺蓋住兩端', 8.5)
    text(105, 24, '③長條兩端的灰色膠面黏在側板內側　④A6 日曆下緣放進台面與斜面的夾角，靠著斜面', 8.5)
    text(105, 17, f'座寬 {W:.0f} mm　深 44 mm　前緣高 11.5 mm　後高 72 mm　斜面約 70°（日曆後仰約 20°）', 8.5)
    text(105, 11, '整張貼在硬紙卡上再割　列印請選「實際大小 100%」', 8.5)
    c.showPage(); c.save()

if __name__ == '__main__':
    make(sys.argv[1] if len(sys.argv) > 1 else '../列印檔/日曆座.pdf')
