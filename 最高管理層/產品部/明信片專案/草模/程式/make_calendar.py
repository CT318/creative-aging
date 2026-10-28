"""台北雙週日曆（14 頁 A6 撕頁，A4 一張排 4 頁）。單數頁＝割下的零件，雙數頁＝城市介紹。
零件輪廓若 ../圖/輪廓/台北_n.png 存在就自動放入，否則先放虛線佔位框。"""
import os, sys, datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

pdfmetrics.registerFont(TTFont('JH', 'C:/Windows/Fonts/msjh.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('JHB', 'C:/Windows/Fonts/msjhbd.ttc', subfontIndex=0))
CITY = '台北'
START = datetime.date(2026, 11, 2)
WD = '一二三四五六日'
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
BLUE = (.23, .47, .85); NAVY = (.09, .2, .36); GRAY = (.5, .55, .65)

def font(c, name, size, rgb): c.setFont(name, size); c.setFillColorRGB(*rgb)
def wrap(c, s, name, size, width):
    lines, cur = [], ''
    for ch in s:
        if c.stringWidth(cur + ch, name, size) > width * mm: lines.append(cur); cur = ch
        else: cur += ch
    return lines + [cur]

def page(c, x, y, n):
    """x,y＝頁面左下角（mm），n＝1..14"""
    d = START + datetime.timedelta(days=n - 1)
    k = (n + 1) // 2          # 第幾件
    c.saveState(); c.translate(x * mm, y * mm)
    # 日期帶
    font(c, 'JHB', 30, NAVY); c.drawString(8 * mm, 18 * mm, f'{d.month}/{d.day}')
    font(c, 'JH', 12, GRAY); c.drawString(8 * mm, 11 * mm, f'星期{WD[d.weekday()]}')
    font(c, 'JHB', 12, BLUE); c.drawRightString((PW - 8) * mm, 18 * mm, f'{CITY}　{k} / 7')
    # 進度點
    for i in range(7):
        c.setFillColorRGB(*(BLUE if i < k else (.85, .88, .94))); c.circle((PW - 8 - 6 * (6 - i) - 1.2) * mm, 12 * mm, 1.5 * mm, stroke=0, fill=1)
    if n % 2 == 1:   # 單數頁：零件
        px = f'../圖/輪廓/{CITY}_{k}.png'
        box = (8, 30, PW - 16, 92)    # x,y,w,h
        if os.path.exists(px):
            img = ImageReader(px); w, h = img.getSize(); s = min(box[2] / w, box[3] / h)
            c.drawImage(img, (box[0] + (box[2] - w * s) / 2) * mm, box[1] * mm, w * s * mm, h * s * mm, mask='auto')
        else:
            c.setStrokeColorRGB(*BLUE); c.setLineWidth(.6); c.setDash(2, 1.6)
            c.roundRect(box[0] * mm, box[1] * mm, box[2] * mm, box[3] * mm, 8 * mm, stroke=1, fill=0); c.setDash([], 0)
            font(c, 'JH', 10, GRAY); c.drawCentredString(PW / 2 * mm, 76 * mm, f'第 {k} 件零件輪廓（圖到後自動放入）')
        font(c, 'JHB', 11, NAVY); c.drawString(8 * mm, 136 * mm, f'今天：沿虛線割下，自己上色')
        font(c, 'JH', 9, GRAY); c.drawString(8 * mm, 130 * mm, f'完成後插進底座第 {k} 號槽')
        font(c, 'JH', 8, GRAY); c.drawRightString((PW - 8) * mm, 136 * mm, '單數頁・創作')
    else:            # 雙數頁：介紹
        font(c, 'JH', 8, GRAY); c.drawRightString((PW - 8) * mm, 136 * mm, '雙數頁・認識城市')
        font(c, 'JHB', 11, BLUE); c.drawString(8 * mm, 136 * mm, f'認識{CITY}')
        font(c, 'JHB', 34, NAVY); c.drawString(8 * mm, 108 * mm, TOPICS[k - 1])
        c.setStrokeColorRGB(*BLUE); c.setLineWidth(1.2); c.line(8 * mm, 102 * mm, 30 * mm, 102 * mm)
        yy = 92
        for ln in wrap(c, INTRO[k - 1], 'JH', 14, PW - 16):
            font(c, 'JH', 14, (.15, .2, .3)); c.drawString(8 * mm, yy * mm, ln); yy -= 8
        if k == 7:
            font(c, 'JHB', 11, BLUE); c.drawString(8 * mm, 46 * mm, '掃最後一件的背面 QR，')
            c.drawString(8 * mm, 40 * mm, '看大家對台北的印象')
    c.restoreState()

out = sys.argv[1] if len(sys.argv) > 1 else f'{CITY}日曆.pdf'
c = canvas.Canvas(out, pagesize=(210 * mm, 297 * mm))
ox, oy = (210 - 2 * PW) / 2, (297 - 2 * PH) / 2
slots = [(ox, oy + PH), (ox + PW, oy + PH), (ox, oy), (ox + PW, oy)]
for sheet in range(4):
    for j, (x, y) in enumerate(slots):
        n = sheet * 4 + j + 1
        if n <= 14: page(c, x, y, n)
    # 裁切線
    c.setStrokeColorRGB(.7, .7, .75); c.setLineWidth(.3); c.setDash(1.5, 1.5)
    c.line(105 * mm, 0, 105 * mm, 297 * mm); c.line(0, 148.5 * mm, 210 * mm, 148.5 * mm); c.setDash([], 0)
    font(c, 'JH', 7, GRAY); c.drawCentredString(105 * mm, 4 * mm, f'{CITY}日曆 第 {sheet + 1}/4 張　A6 頁面沿灰色虛線裁開，列印請選實際大小 100%')
    c.showPage()
c.save(); print('ok')
