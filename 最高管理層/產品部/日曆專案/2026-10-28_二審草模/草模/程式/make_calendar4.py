"""台北雙週日曆 v4（依資深平面設計師規格：木底＋奶油卡片＋內框線，底部兩列資訊條）。座標以頁面左上為原點，mm。"""
import io, datetime, sys
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pieces import build

pdfmetrics.registerFont(TTFont('JH', 'C:/Windows/Fonts/msjh.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('JHB', 'C:/Windows/Fonts/msjhbd.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('SYM', 'C:/Windows/Fonts/seguisym.ttf'))
CITY = '台北'; START = datetime.date(2026, 11, 2); WD = '一二三四五六日'
PW, PH = 105.0, 148.0
def H(h): return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
WOOD, CARD, FRAME, INK, INK2, INK3, GREEN, GREEN2, KEY, DASH = map(H, ['#D8BD94', '#F7F0DF', '#FFFDF6', '#4A3626', '#5C4632', '#6A5240', '#4F6B4E', '#6F8A6B', '#B79A72', '#8A7660'])

DRAW = {1: ('夜市小吃攤', '藍白條紋棚子，配上紅燈籠。'), 2: ('捷運列車', '藍白相間的車身，從車窗開始。'),
        3: ('迪化街的老街屋', '紅磚牆配拱形窗，從窗框開始塗。'), 4: ('龍山寺', '屋頂的燕尾，最適合塗上紅橙色。'),
        5: ('總統府', '紅磚配白線條，中間高塔最醒目。'), 6: ('象山步道', '層層綠意，再點上一位登山的人。'), 7: ('台北 101', '一節一節往上，頂端插著小旗。')}
INFO = {1: ('吃', '台北夜市', ['台北的夜晚從夜市開始。', '一碗熱湯、一杯飲料，／就是很多人的日常。']),
        2: ('行', '台北捷運', ['捷運一張悠遊卡，／走遍整座城市。', '不用開車，也能到處去。']),
        3: ('老街', '迪化街・大稻埕', ['清末起，大稻埕是茶葉與／南北貨的集散地。', '紅磚、拱窗與牆面雕飾，／就是今天這棟老街屋的模樣。', '每年過年前，這裡的年貨大街／掛滿紅燈籠，最熱鬧。']),
        4: ('信仰', '艋舺龍山寺', ['清乾隆三年（1738）由泉州移民／興建，主祀觀世音菩薩。', '三川殿的銅鑄龍柱是全台唯一，／屋頂的燕尾翹脊也很有特色。', '是國定古蹟，／至今仍有許多人來拜拜、散步。']),
        5: ('歷史', '總統府', ['紅磚建築是日治時期留下的。', '現在仍是重要的政府機關。']),
        6: ('近郊', '象山步道', ['台北的特色是城市旁邊就是山。', '走一小段步道，／就能看見整座城。']),
        7: ('城市的樣子', '台北 101', ['101 是台北最高的地標。', '每到跨年，大家一起看煙火，／迎接新的一年。', '掃最後一件背面的 QR，／看大家對台北的印象。'])}

CACHE = {}
def img(k, kind):
    if (k, kind) not in CACHE:
        p = build(CITY, k); buf = io.BytesIO(); p[kind].save(buf, 'PNG'); buf.seek(0); CACHE[(k, kind)] = (ImageReader(buf), p['w_mm'], p['h_mm'])
    return CACHE[(k, kind)]

def page(c, x, y, n):
    d = START + datetime.timedelta(days=n - 1); k = (n + 1) // 2
    c.saveState(); c.translate(x * mm, y * mm)
    def Y(v): return (PH - v) * mm
    def txt(s, xx, base, font, size, rgb, track=0, align='l'):
        w = sum(c.stringWidth(ch, font, size) for ch in s) + track * (len(s) - 1)
        x0 = xx * mm - (w if align == 'r' else w / 2 if align == 'c' else 0)
        t = c.beginText(x0, Y(base)); t.setFont(font, size); t.setFillColorRGB(*rgb); t.setCharSpace(track); t.textOut(s); c.drawText(t)
        return w / mm
    # 木底、奶油卡片、內框線
    c.setFillColorRGB(*WOOD); c.rect(0, 0, PW * mm, PH * mm, stroke=0, fill=1)
    c.setFillColorRGB(*CARD); c.roundRect(6 * mm, Y(142), 93 * mm, 136 * mm, 2.5 * mm, stroke=0, fill=1)
    c.setStrokeColorRGB(*KEY); c.setLineWidth(.35); c.roundRect(8.5 * mm, Y(139.5), 88 * mm, 131 * mm, 1.5 * mm, stroke=1, fill=0)

    if n % 2 == 1:   # 單數頁：今天來畫
        name, line = DRAW[k]
        c.setStrokeColorRGB(*GREEN); c.setLineWidth(.5); c.line(12 * mm, Y(14.2), 18 * mm, Y(14.2))
        txt('今天來畫', 19.5, 15.5, 'JHB', 11, GREEN, 1.65)
        txt(name, 12, 24, 'JHB', 22, INK, 1.1)
        txt(line, 12, 30.5, 'JH', 11.5, INK2)
        im, w, h = img(k, 'line'); s = min(1, 74 / h)
        c.drawImage(im, (52.5 - w * s / 2) * mm, Y(38 + h * s), w * s * mm, h * s * mm, mask='auto')
        cap = f'沿虛線割下、上色，插進第 {k} 號槽'
        wc = sum(c.stringWidth(ch, 'JH', 11) for ch in cap) / mm; wi = 5.5
        x0 = 52.5 - (wc + wi) / 2
        t = c.beginText(x0 * mm, Y(110.5)); t.setFont('SYM', 11); t.setFillColorRGB(*GREEN); t.textOut('✂'); c.drawText(t)
        txt(cap, x0 + wi, 110.5, 'JH', 11, GREEN)
    else:            # 雙數頁：認識城市
        title, sub, pts = INFO[k]
        txt(title, 12, 23, 'JHB', 32 if len(title) < 4 else 26, INK, 3.2)
        txt(sub, 93, 23, 'JHB', 11, GREEN, 0, 'r')
        c.setStrokeColorRGB(*INK); c.setLineWidth(.5); c.line(12 * mm, Y(26.5), 93 * mm, Y(26.5))
        yy = 34.5
        for p_ in pts:
            c.setFillColorRGB(*GREEN2); c.circle(13.9 * mm, Y(yy - 1.3), .9 * mm, stroke=0, fill=1)
            for ln in p_.split('／'):
                txt(ln, 17, yy, 'JH', 12, INK); yy += 6.2
            yy += 2.0
        c.setFillColorRGB(*FRAME); c.setStrokeColorRGB(*INK); c.setLineWidth(.5); c.roundRect(49 * mm, Y(112), 44 * mm, 41 * mm, 2 * mm, stroke=1, fill=1)
        cim, cw, ch = img(k, 'color'); s = min(40 / cw, 37 / ch)
        c.drawImage(cim, (71 - cw * s / 2) * mm, Y(91.5 + ch * s / 2), cw * s * mm, ch * s * mm, mask='auto')
        wlab = txt('照這樣上色', 12, 91, 'JHB', 16, GREEN)
        t = c.beginText((12 + wlab + 1.2) * mm, Y(91)); t.setFont('SYM', 16); t.setFillColorRGB(*GREEN); t.textOut('→'); c.drawText(t)
        txt('昨天那一件，', 12, 97, 'JH', 11, INK2); txt('上色後長這樣。', 12, 102.3, 'JH', 11, INK2)

    # 底部資訊條（兩列）
    txt('台 北', 12, 123.5, 'JHB', 22, INK, 6.6)
    wd = txt(f'星期{WD[d.weekday()]}', 93, 123.5, 'JH', 11, INK3, 0, 'r')
    txt(f'{d.month}月{d.day}日', 93 - wd - 2, 123.5, 'JHB', 22, INK, 0, 'r')
    c.setStrokeColorRGB(*INK); c.setLineWidth(.25); c.line(12 * mm, Y(126.5), 93 * mm, Y(126.5))
    txt('台灣　25.03°N　121.57°E', 12, 133, 'JH', 9, INK3, .45)
    for i in range(7):
        cx = 92 - 4.4 * (6 - i); cy = 131.9
        c.setStrokeColorRGB(*GREEN); c.setLineWidth(.5)
        if i < k: c.setFillColorRGB(*GREEN); c.circle(cx * mm, Y(cy), 1.0 * mm, stroke=1, fill=1)
        else: c.circle(cx * mm, Y(cy), 1.0 * mm, stroke=1, fill=0)
        if i == k - 1: c.circle(cx * mm, Y(cy), 1.7 * mm, stroke=1, fill=0)
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
        c.setFont('JH', 7); c.setFillColorRGB(*DASH); c.drawCentredString(105 * mm, 1 * mm, f'{CITY}日曆 第 {sheet + 1}/4 張　四頁以十字中心線裁開　列印請選實際大小 100%')
        c.showPage()
    c.save()
if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '../列印檔/台北_日曆.pdf', [int(a) for a in sys.argv[2:]] or None)
