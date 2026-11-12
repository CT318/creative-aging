"""台北底座展開圖（A4 橫式 ×3 頁）：①頂板（8 個插槽）②六面側牆（3 條，每條 2 面）③下底板。紅實線＝割線，藍虛線＝摺線，灰＝膠水面。"""
import os, json, math
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import fonts; fonts.register()
from pieceset import build, NAMES, FULL
HERE = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(HERE, '輸出', '插槽配置.json'), encoding='utf-8'))
F = 180.0; A = F / 2; R = A / math.cos(math.radians(30)); S_SIDE = F / math.sqrt(3)
WALL_H = 14.0; FLAP = 8.0; SLOT_W = 0.8; TABG = 6.0
BOARD = (0xF2/255, 0xE9/255, 0xD5/255)   # 與週曆底色相同
RED, BLUE, GRAY, INK = (.42, .33, .22), (.62, .52, .38), BOARD, (.25, .25, .3)

def run(out):
    c = canvas.Canvas(out, pagesize=(297 * mm, 210 * mm))
    def poly(pts, stroke, fill=None, w=.35, dash=None):
        c.setLineWidth(w); c.setStrokeColorRGB(*stroke); c.setDash(*(dash or ([], 0)))
        p = c.beginPath(); p.moveTo(pts[0][0] * mm, pts[0][1] * mm)
        for x, y in pts[1:]: p.lineTo(x * mm, y * mm)
        p.close()
        if fill: c.setFillColorRGB(*fill)
        c.drawPath(p, stroke=1, fill=1 if fill else 0)
    def line(a, b, stroke, dash=None, w=.35):
        c.setLineWidth(w); c.setStrokeColorRGB(*stroke); c.setDash(*(dash or ([], 0))); c.line(a[0] * mm, a[1] * mm, b[0] * mm, b[1] * mm)
    def text(*a, **k):
        pass   # 底座上不放任何文字
    # ── 頁1 頂板：前緣（平邊）在下
    CX, CY0 = 148.5, 105 - A       # CY0＝前緣 y
    hexv = [(-R / 2, 0), (R / 2, 0), (R, A), (R / 2, 2 * A), (-R / 2, 2 * A), (-R, A)]
    pts = [(CX + x, CY0 + y) for x, y in hexv]
    poly(pts, RED, fill=BOARD, w=.5)
    for k in range(6): line(pts[k], pts[(k + 1) % 6], BLUE, ([2, 1.5], 0))
    for i in range(8):
        d = build(i); dep = CFG['depth'][str(i)]; xc = CFG['xs'][str(i)] + (d['tab_cx'] - d['w'] / 2); L = d['tab_w'] + 2
        xs_, ys_ = CX + xc, CY0 + dep
        poly([(xs_ - L / 2, ys_), (xs_ + L / 2, ys_), (xs_ + L / 2, ys_ + SLOT_W), (xs_ - L / 2, ys_ + SLOT_W)], RED, fill=(.3,.22,.14), w=.3)
        text(xs_, ys_ - 4.2, f'{i + 1} {NAMES[i]}', 8, 'JHB', (.45, .45, .5))
    text(148.5, 202, '旬常｜台北 底座 頂板（草模）', 14, 'JHB')
    text(148.5, 196, '紅實線＝割線　藍虛線＝摺線　插槽（紅色細長方形）用刀片割開，卡榫由上往下插入　整張貼在厚紙卡上再割　列印請選「實際大小 100%」', 8.5)
    text(148.5, 12, f'六角對邊 {F:.0f} mm　插槽寬 {SLOT_W} mm（依卡紙厚度調整）　插槽旁的號碼＝零件編號　正前方（下方）那一邊對準「台北」那面牆', 8.5)
    c.showPage()
    # ── 頁2 側牆：3 條，每條 2 面（兩面中間是摺線）；右端有膠面，貼進下一條的左緣內側
    s = S_SIDE; ox = (297 - 2 * s - TABG) / 2
    for r in range(3):
        y0 = 158 - r * 56       # 牆下緣 y
        for k in range(2):
            x0 = ox + k * s
            poly([(x0 + 4, y0 + WALL_H), (x0 + s - 4, y0 + WALL_H), (x0 + s - 4 - FLAP * .3, y0 + WALL_H + FLAP), (x0 + 4 + FLAP * .3, y0 + WALL_H + FLAP)], RED, fill=GRAY)   # 頂摺片（向內摺，貼在頂板下緣）
            poly([(x0 + 4, y0), (x0 + s - 4, y0), (x0 + s - 4 - FLAP * .3, y0 - FLAP), (x0 + 4 + FLAP * .3, y0 - FLAP)], RED, fill=GRAY)   # 底摺片（向內摺，貼在下底板邊緣）
            line((x0 + 4, y0), (x0 + s - 4, y0), BLUE, ([2, 1.5], 0))
            poly([(x0, y0), (x0 + s, y0), (x0 + s, y0 + WALL_H), (x0, y0 + WALL_H)], RED, fill=BOARD)
            line((x0 + 4, y0 + WALL_H), (x0 + s - 4, y0 + WALL_H), BLUE, ([2, 1.5], 0))
            text(x0 + s / 2, y0 + 4, f'側牆 {2 * r + k + 1}', 8, 'JH', (.6, .6, .65))
        line((ox + s, y0), (ox + s, y0 + WALL_H), BLUE, ([2, 1.5], 0))
        xr = ox + 2 * s
        poly([(xr, y0), (xr + TABG, y0 + 2.5), (xr + TABG, y0 + WALL_H - 2.5), (xr, y0 + WALL_H)], RED, fill=GRAY)
    text(148.5, 202, '旬常｜台北 底座 側牆（草模）', 14, 'JHB')
    text(148.5, 196, '先把三條各自沿藍線摺成兩面牆　再用右端灰色膠面把三條接成一圈（第 3 條右端貼回第 1 條左緣內側）　上摺片貼頂板背面邊緣、下摺片貼下底板邊緣（都向內摺）', 8.5)
    text(148.5, 12, f'牆長 {S_SIDE:.1f} mm　牆高 {WALL_H:.0f} mm　整張貼在薄卡紙上再割', 8.5)
    c.showPage()
    # ── 頁3 下底板
    pr = R - 0.8; pts = [(CX + x * pr / R, 105 - A + A + (y - A) * pr / R) for x, y in hexv]
    poly(pts, RED, fill=BOARD, w=.5)
    text(148.5, 103, '下底', 18, 'JHB', (.6, .6, .65))
    text(148.5, 94, '貼在側牆下摺片上封底', 9, 'JH', (.6, .6, .65))
    text(148.5, 202, '旬常｜台北 底座 下底板（草模）', 14, 'JHB')
    c.showPage(); c.save()
if __name__ == '__main__':
    run(os.path.join(HERE, '輸出', '台北底座_展開圖_A4.pdf')); print('ok')
