"""輸出：三座城市的底座展開圖、零件頁（彩色拆件）。"""
import json, io, os
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from layout import solve
import base
OUT = '../列印檔'
NAMES = {'台北': 'TAIPEI', '東京': 'TOKYO', '雪梨': 'SYDNEY'}
res = {}
for city in ['台北', '東京', '雪梨']:
    P, slots = solve(city, order=list(range(1, 8)) if city == '台北' else None)
    res[city] = (P, slots)
    base.make(f'{OUT}/{city}_底座.pdf', city, slots)
    # 零件頁：由高到低、一排一排擺，放不下就換頁
    items = sorted(P.items(), key=lambda kv: -kv[1]['h_mm'])
    c = canvas.Canvas(f'{OUT}/{city}_零件_彩色.pdf', pagesize=(210 * mm, 297 * mm))
    def header():
        c.setFont('JHB', 15); c.setFillColorRGB(.25, .25, .3); c.drawCentredString(105 * mm, 285 * mm, f'旬常｜{city} 七件零件（彩色，草模）')
        c.setFont('JH', 9); c.drawCentredString(105 * mm, 277 * mm, '沿零件外緣細灰線割下（含下方卡榫），貼在薄硬卡上更挺。藍色數字＝零件編號，插入底座同編號的槽。列印請選「實際大小 100%」。')
    import random
    TOP, BOT, XL, XR, GAP = 265.0, 12.0, 12.0, 198.0, 5.0
    def shelf(order):
        pages = [[]]; x, ytop, rowh = XL, TOP, 0.0
        for i, rot in order:
            w, h = (P[i]['h_mm'], P[i]['w_mm']) if rot else (P[i]['w_mm'], P[i]['h_mm'])
            if x + w > XR: x = XL; ytop -= rowh + GAP; rowh = 0.0
            if ytop - h - 5 < BOT: pages.append([]); x, ytop, rowh = XL, TOP, 0.0
            pages[-1].append((i, x, ytop - h, rot, w, h)); x += w + GAP; rowh = max(rowh, h + 5)
        used = TOP - min(t[2] for t in pages[-1]) if pages[-1] else 0
        return pages, used
    best = None
    rnd = random.Random(1)
    orders = [[(i, False) for i, _ in items]]
    for _ in range(6000):
        o = [(i, rnd.random() < .4) for i in P]; rnd.shuffle(o); orders.append(o)
    for o in orders:
        pg, used = shelf(o); key = (len(pg), used)
        if best is None or key < best[0]: best = (key, pg)
    pages = best[1]
    for pi, pg in enumerate(pages):
        header()
        for i, px, py, rot, w, h in pg:
            p = P[i]; buf = io.BytesIO(); (p['color'].rotate(90, expand=True) if rot else p['color']).save(buf, 'PNG'); buf.seek(0)
            c.drawImage(ImageReader(buf), px * mm, py * mm, w * mm, h * mm, mask='auto')
            c.setFont('JHB', 11); c.setFillColorRGB(.1, .3, .85); c.drawString(px * mm, (py - 4.5) * mm, str(i))
        c.showPage()
    c.save(); print(city, 'pages', len(pages))
json.dump({k: v[1] for k, v in res.items()}, open('../圖/插槽配置.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
print('ok')
