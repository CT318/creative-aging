"""零件列印頁（A4 直式、實際大小）：已完成的 4 件（彩色）＋做到一半的龍山寺。虛線是割線，下方凸出的是卡榫。"""
import os, io
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
import fonts; fonts.register()
from pieceset import build, NAMES, FULL
HERE = os.path.dirname(os.path.abspath(__file__))


def run(out, ids=(0, 1, 2, 3, 4), title='零件（已完成與做到一半）'):
    c = canvas.Canvas(out, pagesize=(210 * mm, 297 * mm))
    items = sorted(ids, key=lambda i: -build(i)['h'])
    M = 12
    x = M
    y = 297 - 22
    rowh = 0
    GAP = 7

    def head():
        c.setFont('JHB', 13)
        c.setFillColorRGB(.25, .25, .3)
        c.drawCentredString(105 * mm, 288 * mm, f'旬常｜台北 {title}（草模）')
        c.setFont('JH', 8.5)
        c.drawCentredString(105 * mm, 282 * mm, '實際大小列印（100%）　沿虛線割下　下方凸出的小方塊是卡榫，插進底座插槽　整張貼在厚紙卡上再割更挺')

    head()
    for i in items:
        d = build(i)
        w, h = d['w'], d['h']
        if x + w > 210 - M:
            x = M
            y -= rowh + GAP + 6
            rowh = 0
        if y - h < 14:
            c.showPage()
            head()
            x = M
            y = 297 - 22
            rowh = 0
        buf = io.BytesIO()
        d['img'].save(buf, 'PNG')
        buf.seek(0)
        c.drawImage(ImageReader(buf), x * mm, (y - h) * mm, w * mm, h * mm, mask='auto')
        c.setFont('JH', 8)
        c.setFillColorRGB(.5, .5, .55)
        c.drawString(x * mm, (y - h - 4) * mm, f'{i + 1} {FULL[i]}')
        x += w + GAP
        rowh = max(rowh, h)
    c.showPage()
    c.save()


if __name__ == '__main__':
    run(os.path.join(HERE, '輸出', '台北零件_已完成與半成品_A4.pdf'))
    print('ok')
