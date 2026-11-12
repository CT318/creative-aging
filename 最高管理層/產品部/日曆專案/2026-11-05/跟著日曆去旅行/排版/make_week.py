"""週曆頁（A5 橫式 210×148 mm）：第 3 週（龍山寺已割下＋101 未割）、第 4 週（總統府＋象山，未割）。
輸出 A4 直式一張（兩頁上下排，各為 A5 橫式實際大小）。座標以頁面左上為原點、mm。"""
import os, io, datetime, random
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from PIL import Image, ImageFilter
import numpy as np
from scipy import ndimage as ndi
import fonts; fonts.register()
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('GeoB', 'C:/Windows/Fonts/georgiab.ttf'))
from pieceset import build, NAMES, FULL, PPM
HERE = os.path.dirname(os.path.abspath(__file__))
PW, PH = 210.0, 148.0
START = datetime.date(2026, 11, 2)      # 第 1 週的星期一（示範日期，可改）
WD = '一二三四五六日'
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']


def H(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))


BOARD, WOOD, INK, INK2, RED, CREAM, GRAIN_D, GRAIN_L, EDGE = map(H, ['#F2E9D5', '#DEC6A0', '#2E2218', '#4D3B2C', '#A33F2A', '#FBF5E6', '#B08F5E', '#EFDDB8', '#B99A6A'])
INTRO = {4: ('艋舺龍山寺', '高高翹起的燕尾屋頂，層層飛簷'), 7: ('台北 101', '八節竹節的造型，是台北的天際線地標'),
         5: ('總統府', '紅磚的老建築，中央高塔最好認'), 6: ('象山步道', '走石階登高，看得見整座台北城')}
WEEKS = {3: [(4, 'cut'), (7, 'line')], 4: [(5, 'line'), (6, 'line')]}


def with_shadow(im, blur=6, off=(0.5, 0.9), alpha=.35):
    pad = 40
    W, Hh = im.size
    a = Image.new('L', (W + 2 * pad, Hh + 2 * pad), 0)
    a.paste(im.getchannel('A'), (pad, pad))
    sh = a.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * alpha))
    base = Image.new('RGBA', a.size, (70, 46, 22, 0))
    base.putalpha(sh)
    full = Image.new('RGBA', a.size, (0, 0, 0, 0))
    full.alpha_composite(base, (round(off[0] * PPM), round(off[1] * PPM)))
    full.alpha_composite(im, (pad, pad))
    return full, pad / PPM


def hole_img(i):
    """已割下的零件：留下鏤空的形狀（深色代表紙被割掉、露出下面）加割線虛線。"""
    d = build(i)
    im = d['img']
    m = np.asarray(im.getchannel('A')) > 128
    arr = np.zeros(m.shape + (4,), 'uint8')
    arr[m] = (178, 156, 120, 255)
    inner = m & ~ndi.binary_erosion(m, iterations=22)
    arr[inner] = (150, 128, 96, 255)
    edge = m & ~ndi.binary_erosion(m, iterations=4)
    yy, xx = np.indices(m.shape)
    dash = ((xx + yy) % 24) < 14
    arr[edge & dash] = (110, 90, 66, 255)
    return Image.fromarray(arr, 'RGBA')


def page(c, x, y, wk):
    c.saveState()
    c.translate(x * mm, y * mm)

    def Y(v):
        return (PH - v) * mm

    def txt(s, xx, base, font, size, rgb, track=0, align='l'):
        w = sum(pdfmetrics.stringWidth(ch, font, size) for ch in s) + track * (len(s) - 1)
        x0 = xx * mm - (w if align == 'r' else w / 2 if align == 'c' else 0)
        t = c.beginText(x0, Y(base))
        t.setFont(font, size)
        t.setFillColorRGB(*rgb)
        t.setCharSpace(track)
        t.textOut(s)
        c.drawText(t)
        return w / mm

    c.setFillColorRGB(*BOARD)
    c.rect(0, 0, PW * mm, PH * mm, stroke=0, fill=1)
    WX, WY, WW, WH = 6, 6, PW - 12, 102
    c.saveState()
    p = c.beginPath()
    p.roundRect(WX * mm, Y(WY + WH), WW * mm, WH * mm, 1.2 * mm)
    c.clipPath(p, stroke=0, fill=0)
    c.setFillColorRGB(*WOOD)
    c.rect(WX * mm, Y(WY + WH), WW * mm, WH * mm, stroke=0, fill=1)
    rnd = random.Random(7 + wk)
    for i in range(70):
        yy = WY - 4 + i * (WH + 8) / 70 + rnd.uniform(-.6, .6)
        pts = [(WX - 3, yy)]
        for j in range(1, 6):
            pts.append((WX + WW * j / 5 + rnd.uniform(-6, 6), yy + rnd.uniform(-1.2, 1.2)))
        dark = rnd.random() < .72
        c.setStrokeColorRGB(*(GRAIN_D if dark else GRAIN_L))
        c.setStrokeAlpha(rnd.uniform(.10, .26) if dark else rnd.uniform(.25, .5))
        c.setLineWidth(rnd.uniform(.15, .55))
        pa = c.beginPath()
        pa.moveTo(pts[0][0] * mm, Y(pts[0][1]))
        for j in range(1, len(pts) - 1):
            xa = (pts[j][0] + pts[j + 1][0]) / 2
            ya = (pts[j][1] + pts[j + 1][1]) / 2
            pa.curveTo(((pts[j - 1][0] + pts[j][0]) / 2) * mm, Y(pts[j][1]), pts[j][0] * mm, Y(pts[j][1]), xa * mm, Y(ya))
        pa.lineTo((WX + WW + 3) * mm, Y(pts[-1][1]))
        c.drawPath(pa, stroke=1, fill=0)
    c.setStrokeAlpha(1)
    c.restoreState()
    c.setStrokeColorRGB(*EDGE)
    c.setLineWidth(.6)
    c.roundRect(WX * mm, Y(WY + WH), WW * mm, WH * mm, 1.2 * mm, stroke=1, fill=0)

    # 兩件並列：能放在說明下方的用「上方說明」，太高的（101）說明放左側、件靠右
    ids = WEEKS[wk]
    bottom = WY + WH - 3
    modes = ['top' if bottom - build(i)['h'] >= WY + 13 else 'beside' for i, _ in ids]
    ws = [build(i)['w'] for i, _ in ids]
    EDGE_M = 12
    gap = (WW - 2 * EDGE_M - sum(ws)) / (len(ws) - 1)
    xcur = WX + EDGE_M
    for k, (i, kind) in enumerate(ids):
        d = build(i)
        name, desc = INTRO[i]
        w, h = d['w'], d['h']
        px = xcur
        if modes[k] == 'top':
            wm = max(sum(pdfmetrics.stringWidth(ch, 'SerifSemi', 8.5) for ch in desc) / mm + .4 * len(desc), 30)
            ccx = min(max(px + w / 2, WX + 4 + wm / 2), WX + WW - 4 - wm / 2)
            txt(name, ccx, WY + 9, 'SerifBlack', 14, INK, .8, 'c')
            txt(desc, ccx, WY + 15, 'SerifSemi', 8.5, INK2, .4, 'c')
        else:
            txt(name, px - 4, WY + 10, 'SerifBlack', 14, INK, .8, 'r')
            half = (len(desc) + 1) // 2
            txt(desc[:half], px - 4, WY + 16, 'SerifSemi', 8.5, INK2, .4, 'r')
            txt(desc[half:], px - 4, WY + 21, 'SerifSemi', 8.5, INK2, .4, 'r')
        xcur += w + gap
        im = hole_img(i) if kind == 'cut' else d['img']
        full, pad = with_shadow(im) if kind != 'cut' else (im, 0)
        buf = io.BytesIO()
        full.save(buf, 'PNG')
        buf.seek(0)
        top = bottom - h
        c.drawImage(ImageReader(buf), (px - pad) * mm, Y(top + h + pad), (w + 2 * pad) * mm, (h + 2 * pad) * mm, mask='auto')
        if kind == 'cut':
            txt('已割下，上色中', px + w / 2, top + h * 0.5, 'SerifBold', 10, (.96, .93, .85), .8, 'c')

    # 資訊區
    d0 = START + datetime.timedelta(days=7 * (wk - 1))
    d6 = d0 + datetime.timedelta(days=6)
    mth = d0.month
    mw = txt(f'{mth}月', 10, 116.6, 'SerifBlack', 17, INK, 1)
    txt(MONTHS[mth - 1].upper(), 10 + mw + 4, 116.6, 'GeoB', 10, INK2, 2.2)
    txt('台北', PW - 10, 116.6, 'SerifSemi', 10.5, INK2, 1.5, 'r')
    bw = (PW - 20 - 6 * 2.5) / 7
    by = 120.5
    for j in range(7):
        dd = d0 + datetime.timedelta(days=j)
        bx = 10 + j * (bw + 2.5)
        c.setFillColorRGB(*CREAM)
        c.setStrokeColorRGB(*EDGE)
        c.setLineWidth(.5)
        c.roundRect(bx * mm, Y(by + 22), bw * mm, 22 * mm, 1.6 * mm, stroke=1, fill=1)
        wkday = dd.weekday()
        txt(f'星期{WD[wkday]}', bx + bw / 2, by + 6.8, 'SerifBold', 10, RED if wkday >= 5 else INK2, .6, 'c')
        txt(str(dd.day), bx + bw / 2, by + 18.2, 'SerifBlack', 22, INK, 0, 'c')
    c.setStrokeColorRGB(*H('#6B5A4A'))
    c.setLineWidth(.3)
    c.setDash([])
    c.rect(.15 * mm, .15 * mm, (PW - .3) * mm, (PH - .3) * mm, stroke=1, fill=0)
    c.restoreState()


def run(out):
    """雙面列印版（A4 直式，翻頁式記分板）：正面下半＝第 3 週（本頁），背面上半＝第 4 週（轉 180°，翻過去才是正的）。
    印表機選「雙面列印・短邊翻轉」。沿中線對折：下半是會翻的頁，上半是後面的底板。"""
    c = canvas.Canvas(out, pagesize=(210 * mm, 297 * mm))

    def mark(c, upright=True):
        c.setStrokeColorRGB(.45, .4, .35)
        c.setLineWidth(.25)
        c.setDash(1.5, 1.5)
        c.line(0, 148.5 * mm, 4 * mm, 148.5 * mm)
        c.line(206 * mm, 148.5 * mm, 210 * mm, 148.5 * mm)
        c.setDash([], 0)
    # 第 1 面（正面）：下半＝第 3 週；上半＝底板（空白，只標折線與說明）
    c.setFillColorRGB(*BOARD)
    c.rect(0, 0, 210 * mm, 297 * mm, stroke=0, fill=1)
    page(c, 0, 0, 3)
    mark(c)
    c.showPage()
    # 第 2 面（背面）：上半＝第 4 週，轉 180°
    c.setFillColorRGB(*BOARD)
    c.rect(0, 0, 210 * mm, 297 * mm, stroke=0, fill=1)
    c.saveState()
    c.translate(210 * mm, 297 * mm)
    c.rotate(180)
    page(c, 0, 0, 4)
    c.restoreState()
    mark(c)
    c.showPage()
    c.save()


def run_single(out):
    c = canvas.Canvas(out, pagesize=(210 * mm, 297 * mm))
    oy = (297 - 2 * PH) / 2
    page(c, 0, oy + PH, 3)
    page(c, 0, oy, 4)
    c.showPage()
    c.save()


if __name__ == '__main__':
    run(os.path.join(HERE, '輸出', '台北週曆_雙面列印_第3週與第4週_A4.pdf'))
    run_single(os.path.join(HERE, '輸出', '台北週曆_單面預覽_第3週與第4週_A4.pdf'))
    print('ok')
