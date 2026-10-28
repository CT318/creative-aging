"""台北雙週日曆 v3：全中文（給長輩）、資訊頁內容加多、單數頁標件號、雙數頁右下放前一天零件的彩色小圖當上色參考。"""
import io, datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pieces import build

pdfmetrics.registerFont(TTFont('JH', 'C:/Windows/Fonts/msjh.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('JHB', 'C:/Windows/Fonts/msjhbd.ttc', subfontIndex=0))
CITY, COUNTRY, COORD = '台北', '台灣', '北緯 25.03°　東經 121.57°'
START = datetime.date(2026, 11, 2)
WD = '一二三四五六日'
NAMES = ['夜市小吃攤', '捷運列車', '迪化街老街屋', '龍山寺', '總統府', '象山步道', '台北 101']
# 每頁：(主題, 副標, [重點...], 想一想)  ※第 3、4 件已查證補充，其餘待補
TOPICS = [
 ('吃', '台北夜市', ['台北的夜晚從夜市開始。', '一碗熱湯、一杯飲料，就是很多人的日常。'], ''),
 ('行', '台北捷運', ['捷運一張悠遊卡，走遍整座城市。', '不用開車，也能到處去。'], ''),
 ('老街', '迪化街・大稻埕', ['清末淡水開港後，大稻埕成為北台灣茶葉與南北貨的集散地。',
                          '街上至今還有南北雜貨、中藥材、布料的老店。',
                          '華麗的仿巴洛克街屋，有紅磚、拱窗與牆面雕飾，就是這件作品的樣子。',
                          '每年農曆年前的「年貨大街」，掛滿紅燈籠，最熱鬧。'], '想一想：你家過年會買哪些年貨？'),
 ('信仰', '艋舺龍山寺', ['清乾隆三年（1738）創建，是泉州移民從家鄉分靈而來，主祀觀世音菩薩。',
                       '經地震、風災多次重修，1919 年重建，奠定今日的格局。',
                       '三川殿的銅鑄龍柱是全台唯一，屋頂的燕尾翹脊也很有特色。',
                       '是國定古蹟，至今仍有許多人來拜拜、散步。'], '想一想：你去過龍山寺嗎？'),
 ('歷史', '總統府', ['紅磚建築是日治時期留下的。', '現在仍是重要的政府機關。'], ''),
 ('近郊', '象山步道', ['台北的特色是城市旁邊就是山。', '走一小段步道，就能看見整座城。'], ''),
 ('城市的樣子', '台北 101', ['101 是台北最高的地標。', '每到跨年，大家一起看煙火，迎接新的一年。'], '掃最後一件背面的 QR，看大家對台北的印象'),
]
PW, PH = 105.0, 148.0
WOOD = (.945, .905, .835); PAPER = (.985, .972, .945); INK = (.23, .17, .12); SAGE = (.42, .5, .4); MUTE = (.5, .43, .35)

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

PUNCT = set('，。、）」？！：；,.)')
def tokens(t):
    out, cur = [], ''
    for ch in t:
        if ch.isascii() and (ch.isalnum()): cur += ch
        else:
            if cur: out.append(cur); cur = ''
            out.append(ch)
    if cur: out.append(cur)
    return out

CACHE = {}
def img(k, kind):
    if (k, kind) not in CACHE:
        p = build(CITY, k); buf = io.BytesIO(); p[kind].save(buf, 'PNG'); buf.seek(0); CACHE[(k, kind)] = (ImageReader(buf), p['w_mm'], p['h_mm'])
    return CACHE[(k, kind)]

def page(c, x, y, n):
    d = START + datetime.timedelta(days=n - 1); k = (n + 1) // 2
    c.saveState(); c.translate(x * mm, y * mm)
    c.setFillColorRGB(*WOOD); c.rect(0, 0, PW * mm, PH * mm, stroke=0, fill=1)
    fx, fy, fw, fh = 7, 40, PW - 14, 100
    c.setFillColorRGB(*PAPER); c.setStrokeColorRGB(*INK); c.setLineWidth(.5); c.rect(fx * mm, fy * mm, fw * mm, fh * mm, stroke=1, fill=1)
    if n % 2 == 1:      # 單數頁：割下創作
        im, w, h = img(k, 'line')
        s = min(1, (fh - 16) / h, (fw - 6) / w)
        c.drawImage(im, (fx + (fw - w * s) / 2) * mm, (fy + 4) * mm, w * s * mm, h * s * mm, mask='auto')
        c.setFont('JHB', 15); c.setFillColorRGB(*INK); c.drawString((fx + 4) * mm, (fy + fh - 9) * mm, f'第 {k} 件　共 7 件')
        c.setFont('JH', 9.5); c.setFillColorRGB(*MUTE); c.drawString((fx + 4) * mm, (fy + fh - 15.5) * mm, f'沿虛線割下，自己上色，完成後插進底座第 {k} 號槽')
    else:               # 雙數頁：認識城市
        title, sub, pts, ask = TOPICS[k - 1]
        c.setFont('JHB', 26 if len(title) < 4 else 21); c.setFillColorRGB(*INK); c.drawString((fx + 5) * mm, (fy + fh - 13) * mm, title)
        c.setFont('JHB', 11); c.setFillColorRGB(*SAGE); c.drawRightString((fx + fw - 5) * mm, (fy + fh - 12) * mm, sub)
        c.setStrokeColorRGB(*INK); c.setLineWidth(.5); c.line((fx + 5) * mm, (fy + fh - 18) * mm, (fx + fw - 5) * mm, (fy + fh - 18) * mm)
        # 右下：前一天零件的彩色小圖（上色參考）
        cim, cw, ch = img(k, 'color'); bw, bh = 29.0, 50.0; s = min(bw / cw, bh / ch)
        ix = fx + fw - 4 - cw * s; iy = fy + 9
        c.drawImage(cim, ix * mm, iy * mm, cw * s * mm, ch * s * mm, mask='auto')
        c.setFont('JH', 7.5); c.setFillColorRGB(*MUTE); c.drawCentredString((ix + cw * s / 2) * mm, (fy + 4.5) * mm, '照這樣上色')
        # 文字欄：避頭尾、小圖上方用寬欄，放不下就縮字
        img_top = iy + ch * s + 2
        def widthfn(yy, x0):
            return (fx + fw - 4.5) - x0 - (cw * s + 3 if yy < img_top else 0)
        def layout(size):
            lead = size * .58; yy = fy + fh - 25; out = []
            for p_ in pts:
                toks = tokens(p_); cur = ''; x0 = fx + 9.5
                out.append(('dot', fx + 6.2, yy + lead * .32))
                for t in toks:
                    w = widthfn(yy, x0)
                    if cur and c.stringWidth(cur + t, 'JH', size) > w * mm and t not in PUNCT:
                        out.append(('t', x0, yy, cur, 'JH')); yy -= lead; cur = t
                    else: cur += t
                out.append(('t', x0, yy, cur, 'JH')); yy -= lead * 1.5
            if ask:
                toks = tokens(ask); cur = ''; x0 = fx + 5
                for t in toks:
                    w = widthfn(yy, x0)
                    if cur and c.stringWidth(cur + t, 'JHB', size) > w * mm and t not in PUNCT:
                        out.append(('q', x0, yy, cur, 'JHB')); yy -= lead; cur = t
                    else: cur += t
                out.append(('q', x0, yy, cur, 'JHB')); yy -= lead
            return out, yy
        size = 11.5
        while True:
            out, yend = layout(size)
            if yend >= fy + 2.5 or size <= 10: break
            size -= .5
        for o in out:
            if o[0] == 'dot':
                c.setFillColorRGB(*SAGE); c.circle(o[1] * mm, o[2] * mm, .9 * mm, stroke=0, fill=1)
            else:
                c.setFont(o[4], size); c.setFillColorRGB(*(SAGE if o[0] == 'q' else INK)); c.drawString(o[1] * mm, o[2] * mm, o[3])
    # 底部寬條（全中文）
    spaced(c, 8, 27, CITY, 'JHB', 24, 6, INK)
    c.setStrokeColorRGB(*INK); c.setLineWidth(.4); c.line(8 * mm, 23.5 * mm, 56 * mm, 23.5 * mm)
    spaced(c, 8, 18.2, COUNTRY, 'JH', 10, 3, INK); spaced(c, 8, 12.5, COORD, 'JH', 8, .5, MUTE)
    c.setFont('JHB', 26); c.setFillColorRGB(*INK); c.drawRightString((PW - 8) * mm, 21.5 * mm, f'{d.month}月{d.day}日')
    c.setFont('JH', 12); c.setFillColorRGB(*MUTE); c.drawRightString((PW - 8) * mm, 15 * mm, f'星期{WD[d.weekday()]}')
    for i in range(7):
        c.setFillColorRGB(*(SAGE if i < k else (.82, .78, .7))); c.circle((PW - 8 - 5.2 * (6 - i) - 1.2) * mm, 8.5 * mm, 1.35 * mm, stroke=0, fill=1)
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
