"""台北雙週日曆 v2（參考雷射切割木地圖卡：暖木色、細線框、底部寬條放大字距城市名）。14 頁 A6，A4 一張排 4 頁。"""
import io, datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pieces import build

pdfmetrics.registerFont(TTFont('JH', 'C:/Windows/Fonts/msjh.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('JHB', 'C:/Windows/Fonts/msjhbd.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('GO', 'C:/Windows/Fonts/GOTHIC.TTF'))
pdfmetrics.registerFont(TTFont('GOB', 'C:/Windows/Fonts/GOTHICB.TTF'))
CITY, EN, COUNTRY, COORD = '台北', 'TAIPEI', 'TAIWAN', '25.0330° N, 121.5654° E'
START = datetime.date(2026, 11, 2)
WD = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
TOPICS = ['吃', '行', '老街', '信仰', '歷史', '近郊', '城市的樣子']
INTRO = [
 '台北的夜晚從夜市開始，一碗熱湯、一杯飲料，就是很多人的日常。',
 '捷運一張悠遊卡，走遍整座城市，不用開車也能到處去。',
 '迪化街保留了老街屋，過去是南北貨、布料與茶葉的集散地。',
 '龍山寺是萬華的信仰中心，老人家早晚來拜拜，也來散步聊天。',
 '總統府的紅磚建築是日治時期留下的，現在仍是重要的政府機關。',
 '台北的特色是城市旁邊就是山，走一小段步道就能看見整座城。',
 '101 是台北最高的地標，每到跨年，大家一起看煙火，迎接新的一年。',
]
PW, PH = 105.0, 148.0
WOOD = (.945, .905, .835); PAPER = (.985, .972, .945); INK = (.23, .17, .12); SAGE = (.42, .5, .4); MUTE = (.55, .48, .4)

def spaced(c, x, y, s, font, size, space, rgb, align='l'):
    w = sum(c.stringWidth(ch, font, size) for ch in s) + space * (len(s) - 1)
    if align == 'r': x -= w / mm
    t = c.beginText(x * mm, y * mm); t.setFont(font, size); t.setFillColorRGB(*rgb); t.setCharSpace(space); t.textOut(s); c.drawText(t)

def wrap(c, s, font, size, width):
    lines, cur = [], ''
    for ch in s:
        if c.stringWidth(cur + ch, font, size) > width * mm: lines.append(cur); cur = ch
        else: cur += ch
    return lines + [cur]

CACHE = {}
def piece_img(k):
    if k not in CACHE:
        p = build(CITY, k); buf = io.BytesIO(); p['line'].save(buf, 'PNG'); buf.seek(0); CACHE[k] = (ImageReader(buf), p['w_mm'], p['h_mm'])
    return CACHE[k]

def page(c, x, y, n):
    d = START + datetime.timedelta(days=n - 1); k = (n + 1) // 2
    c.saveState(); c.translate(x * mm, y * mm)
    c.setFillColorRGB(*WOOD); c.rect(0, 0, PW * mm, PH * mm, stroke=0, fill=1)
    fx, fy, fw, fh = 7, 40, PW - 14, 100
    c.setFillColorRGB(*PAPER); c.setStrokeColorRGB(*INK); c.setLineWidth(.5); c.rect(fx * mm, fy * mm, fw * mm, fh * mm, stroke=1, fill=1)
    if n % 2 == 1:
        img, w, h = piece_img(k)
        s = min(1, (fh - 14) / h, (fw - 6) / w)
        c.drawImage(img, (fx + (fw - w * s) / 2) * mm, (fy + 4) * mm, w * s * mm, h * s * mm, mask='auto')
        spaced(c, fx + 4, fy + fh - 6, f'PIECE {k} / 7', 'GOB', 8, 1.5, INK)
        c.setFont('JH', 8); c.setFillColorRGB(*MUTE); c.drawRightString((fx + fw - 9) * mm, (fy + fh - 6) * mm, '沿虛線割下，自己上色')
    else:
        c.setFillColorRGB(*SAGE); c.rect(fx * mm, fy * mm, fw * mm, 9 * mm, stroke=0, fill=1)
        spaced(c, fx + 4, fy + fh - 6, f'DAY {n}  |  {EN}', 'GOB', 8, 1.5, INK)
        c.setFont('JHB', 40 if len(TOPICS[k - 1]) < 4 else 28); c.setFillColorRGB(*INK); c.drawString((fx + 5) * mm, (fy + fh - 30) * mm, TOPICS[k - 1])
        c.setStrokeColorRGB(*INK); c.setLineWidth(.6); c.line((fx + 5) * mm, (fy + fh - 37) * mm, (fx + fw - 5) * mm, (fy + fh - 37) * mm)
        yy = fy + fh - 49
        for ln in wrap(c, INTRO[k - 1], 'JH', 13, fw - 18):
            c.setFont('JH', 13); c.setFillColorRGB(*INK); c.drawString((fx + 5) * mm, yy * mm, ln); yy -= 7.6
        if k == 7:
            c.setFont('JHB', 9.5); c.setFillColorRGB(*INK); c.drawString((fx + 5) * mm, (fy + 20) * mm, '掃最後一件背面的 QR，看大家對台北的印象')
        spaced(c, fx + fw - 4, fy + 3, f'PIECE {k} / 7', 'GOB', 7, 1.5, (1, 1, 1), 'r')
    # 底部寬條：城市名放大字距、細線、小字
    spaced(c, 8, 28, EN, 'GOB', 17, 3.2, INK)
    c.setStrokeColorRGB(*INK); c.setLineWidth(.4); c.line(8 * mm, 24 * mm, 62 * mm, 24 * mm)
    spaced(c, 8, 19, COUNTRY, 'GO', 8.5, 1.6, INK); spaced(c, 8, 14, COORD, 'GO', 6.5, .5, MUTE)
    spaced(c, PW - 8, 24.5, f'{d.month:02d} / {d.day:02d}', 'GOB', 20, 1.2, INK, 'r'); spaced(c, PW - 8, 18, WD[d.weekday()], 'GO', 8.5, 2, MUTE, 'r')
    for i in range(7):
        c.setFillColorRGB(*(SAGE if i < k else (.82, .78, .7))); c.circle((PW - 8 - 5.2 * (6 - i) - 1.2) * mm, 11 * mm, 1.35 * mm, stroke=0, fill=1)
    c.restoreState()

def main(out):
    c = canvas.Canvas(out, pagesize=(210 * mm, 297 * mm))
    ox, oy = (210 - 2 * PW) / 2, (297 - 2 * PH) / 2
    slots = [(ox, oy + PH), (ox + PW, oy + PH), (ox, oy), (ox + PW, oy)]
    for sheet in range(4):
        for j, (x, y) in enumerate(slots):
            n = sheet * 4 + j + 1
            if n <= 14: page(c, x, y, n)
        c.setStrokeColorRGB(.55, .55, .6); c.setLineWidth(.3); c.setDash(1.5, 1.5)
        c.line(105 * mm, 0, 105 * mm, 297 * mm); c.line(0, 148.5 * mm, 210 * mm, 148.5 * mm); c.setDash([], 0)
        c.setFont('JH', 7); c.setFillColorRGB(.4, .4, .45); c.drawCentredString(105 * mm, 3 * mm, f'{CITY}日曆 第 {sheet + 1}/4 張　A6 頁面沿灰色虛線裁開，列印請選實際大小 100%')
        c.showPage()
    c.save()
if __name__ == '__main__':
    main('../列印檔/台北_日曆.pdf')
