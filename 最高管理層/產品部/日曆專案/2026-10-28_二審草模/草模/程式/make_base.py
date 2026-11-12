"""六角底座展開圖（A4 直式，單位 mm）。
參數可調：紙厚影響插槽寬 SLOT_W。紅實線＝割線，藍虛線＝摺線，灰區＝膠水面。"""
import math, sys
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FLAT = 100.0          # 六角對邊距
WALL_H = 12.0         # 側牆高
SLOT_LEN = 26.0       # 插槽長（零件卡榫寬 24）
SLOT_W = 0.8          # 插槽寬（依卡紙厚度調）
SLOT_PITCH = 10.0     # 七個插槽間距
CONN_LEN = 14.0       # 側牆拼接插槽長

pdfmetrics.registerFont(TTFont('JH', 'C:/Windows/Fonts/msjh.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('JHB', 'C:/Windows/Fonts/msjhbd.ttc', subfontIndex=0))
R = (FLAT / 2) / math.cos(math.radians(30))
CX, CY = 105.0, 150.0
def V(k): a = math.radians(90 - 60 * k); return (CX + R * math.cos(a), CY + R * math.sin(a))
def add(p, q, s=1): return (p[0] + s * q[0], p[1] + s * q[1])
def unit(a, deg): r = math.radians(deg); return (math.cos(r), math.sin(r))

c = canvas.Canvas(sys.argv[1] if len(sys.argv) > 1 else '六角底座展開圖.pdf', pagesize=(210 * mm, 297 * mm))
def P(pts): return [(x * mm, y * mm) for x, y in pts]
def poly(pts, stroke, dash=None, fill=None, w=0.35):
    c.setLineWidth(w); c.setStrokeColorRGB(*stroke)
    c.setDash(*(dash or ([], 0)))
    p = c.beginPath(); q = P(pts); p.moveTo(*q[0])
    for x in q[1:]: p.lineTo(*x)
    p.close()
    if fill: c.setFillColorRGB(*fill)
    c.drawPath(p, stroke=1, fill=1 if fill else 0)
def line(a, b, stroke, dash=None, w=0.35):
    c.setLineWidth(w); c.setStrokeColorRGB(*stroke); c.setDash(*(dash or ([], 0)))
    c.line(a[0] * mm, a[1] * mm, b[0] * mm, b[1] * mm)
def text(x, y, s, size=8, bold=False, rot=0, rgb=(.25, .25, .3)):
    c.saveState(); c.setFillColorRGB(*rgb); c.setFont('JHB' if bold else 'JH', size)
    c.translate(x * mm, y * mm); c.rotate(rot); c.drawCentredString(0, 0, s); c.restoreState()

RED, BLUE, GRAY = (.85, .1, .1), (.1, .3, .85), (.88, .88, .9)
top = [V(k) for k in range(6)]

# 膠水面＋側牆
for k in range(6):
    A, B = V(k), V(k + 1)
    ang = 90 - 60 * k - 30             # 邊 k 的外法線方向角度
    n = unit(ang, 0) if False else unit(90 - 60 * k - 30, 0)
    n = (math.cos(math.radians(90 - 60 * k - 30)), math.sin(math.radians(90 - 60 * k - 30)))
    # 外法線：頂點 k 與 k+1 中點方向
    mid = ((A[0] + B[0]) / 2 - CX, (A[1] + B[1]) / 2 - CY); L = math.hypot(*mid); n = (mid[0] / L, mid[1] / L)
    A2, B2 = add(A, n, WALL_H), add(B, n, WALL_H)
    poly([A, B, B2, A2], RED, fill=(1, 1, 1))
    # 膠水面（接在 B 側）：落在牆與下一面牆之間的縫
    u = ((B[0] - A[0]) / R, (B[1] - A[1]) / R)
    bis = (math.cos(math.radians(math.degrees(math.atan2(n[1], n[0])) + 30)), math.sin(math.radians(math.degrees(math.atan2(n[1], n[0])) + 30)))
    tab = [B, B2, add(add(B, n, WALL_H - 1.5), bis, 6.5), add(B, bis, 3.0)]
    poly(tab, RED, fill=GRAY)
    # 牆中央拼接插槽（橫向）
    m = ((A2[0] + B2[0]) / 2, (A2[1] + B2[1]) / 2); m = add(((A[0] + B[0]) / 2, (A[1] + B[1]) / 2), n, WALL_H / 2)
    poly([add(m, u, -CONN_LEN / 2), add(m, u, CONN_LEN / 2), add(add(m, u, CONN_LEN / 2), n, SLOT_W), add(add(m, u, -CONN_LEN / 2), n, SLOT_W)], RED, w=0.3)
    line(A, B, BLUE, ([2, 1.5], 0))

# 頂面
poly(top, RED, w=0.45)
for k in range(6): line(V(k), V(k + 1), BLUE, ([2, 1.5], 0))
# 七個插槽（前＝下方 y 小，1 號最前、7 號最後）
for i in range(7):
    y = CY + (i - 3) * SLOT_PITCH
    poly([(CX - SLOT_LEN / 2, y), (CX + SLOT_LEN / 2, y), (CX + SLOT_LEN / 2, y + SLOT_W), (CX - SLOT_LEN / 2, y + SLOT_W)], RED, w=0.3)
    text(CX - SLOT_LEN / 2 - 5, y - 1, str(i + 1), 8, True)
text(CX + 33, CY - 32, '前', 14, True, rgb=(.4, .4, .5)); text(CX + 33, CY + 32, '後', 14, True, rgb=(.4, .4, .5))

# 說明與連接片
text(105, 285, '旬常｜六角底座展開圖（草模）', 15, True)
text(105, 278, '紅實線＝割線　藍虛線＝摺線（先用尺與鈍筆壓線）　灰色＝塗膠水面', 9.5)
text(105, 271, '建議：整張貼在 A4 硬紙卡上，再割。1～7 號插槽由前到後，零件由矮到高插入；最高那件背面是 QR。', 9)
text(105, 18, f'六角對邊 {FLAT:.0f} mm　側牆高 {WALL_H:.0f} mm　插槽 {SLOT_LEN:.0f}×{SLOT_W} mm（依卡紙厚度調整）　列印時請選「實際大小 100%」，不要縮放', 8.5)
text(105, 11, '拼接：兩座底座靠邊放，將下方連接片兩端分別插入兩面牆的小橫槽', 8.5)
# 連接片 ×3
for j in range(3):
    x0, y0 = 45 + j * 50, 28
    pts = [(x0, y0 + 3), (x0 + 6, y0 + 3), (x0 + 6, y0), (x0 + 14, y0), (x0 + 14, y0 + 3), (x0 + 26, y0 + 3), (x0 + 26, y0), (x0 + 34, y0), (x0 + 34, y0 + 3), (x0 + 40, y0 + 3),
           (x0 + 40, y0 + 7), (x0 + 34, y0 + 7), (x0 + 34, y0 + 10), (x0 + 26, y0 + 10), (x0 + 26, y0 + 7), (x0 + 14, y0 + 7), (x0 + 14, y0 + 10), (x0 + 6, y0 + 10), (x0 + 6, y0 + 7), (x0, y0 + 7)]
    poly(pts, RED, w=0.35)
text(105, 43, '連接片（剪 3 片，用法見下）', 8)
c.showPage(); c.save()
print('ok', round(R, 2))
