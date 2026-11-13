# -*- coding: utf-8 -*-
"""週曆五頁（封面＝底座、第 1～4 週）：印刷檔、切割檔（台科大快切機規範）、預覽圖。"""
import sys
from scene import *
from reportlab.pdfgen import canvas as RC
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import pymupdf

pdfmetrics.registerFont(TTFont('JH', FONT_R, subfontIndex=0))
pdfmetrics.registerFont(TTFont('JHB', FONT_B, subfontIndex=0))
pdfmetrics.registerFont(TTFont('KAI', FONT_K))
PW, PH = 297.0, 210.0
OUT = os.path.join(ROOT, '切割與印刷檔'); os.makedirs(OUT, exist_ok=True)
YEAR, MONTH = 2027, 3          # 2027/3/1 是星期一；三月是台北杜鵑花季
ACC = (0.275, 0.384, 0.494)
RED, GREEN = (1, 0, 0), (0, 1, 0)
CUTLEN = {}
CIRC = '⓪①②③④⑤⑥⑦⑧'


class Pg:
    def __init__(s, c, mode, page):
        s.c, s.mode, s.page = c, mode, page
        CUTLEN.setdefault(page, 0.0)

    def poly(s, pts, col, w, dash=None, close=False):
        c = s.c
        c.setStrokeColorRGB(*col); c.setLineWidth(w * mm); c.setLineCap(1); c.setLineJoin(1)
        c.setDash(dash or [])
        p = c.beginPath(); p.moveTo(pts[0][0] * mm, pts[0][1] * mm)
        for x, y in pts[1:]:
            p.lineTo(x * mm, y * mm)
        if close:
            p.close()
        c.drawPath(p, stroke=1, fill=0)

    def cut(s, pts, close=False):
        n = LineString(list(pts) + ([pts[0]] if close else [])).length
        if s.mode == 'cut':
            CUTLEN[s.page] += n
            s.poly(pts, RED, 0.1, close=close)
        elif s.mode == 'both':
            s.poly(pts, (0.2, 0.19, 0.22), 0.42, close=close)

    def fold(s, pts):
        if s.mode == 'cut':
            CUTLEN[s.page] += LineString(pts).length
            s.poly(pts, GREEN, 0.1)
        elif s.mode == 'both':
            s.poly(pts, (0.25, 0.65, 0.35), 0.3, dash=[2 * mm, 1.2 * mm])

    def ink(s, pts, w=0.22, g=0.6):
        if s.mode != 'cut':
            s.poly(pts, (g, g, g + 0.02), w)

    def text(s, x, y, t, size, font='JH', col=(0.2, 0.2, 0.22), align='l'):
        if s.mode == 'cut':
            return
        c = s.c; c.setFillColorRGB(*col); c.setFont(font, size)
        (c.drawString if align == 'l' else c.drawRightString if align == 'r' else c.drawCentredString)(x * mm, y * mm, t)

    def fill(s, pts, col):
        if s.mode == 'cut':
            return
        c = s.c; c.setFillColorRGB(*col)
        p = c.beginPath(); p.moveTo(pts[0][0] * mm, pts[0][1] * mm)
        for x, y in pts[1:]:
            p.lineTo(x * mm, y * mm)
        p.close(); c.drawPath(p, stroke=0, fill=1)

    def image(s, path, x, y, w, h):
        if s.mode != 'cut':
            s.c.drawImage(ImageReader(path), x * mm, y * mm, w * mm, h * mm, mask='auto')

    def lmark(s):
        s.poly([(5, PH - 5), (5, 5), (PW - 5, 5)], (0, 0, 0), 0.3)


def place(pg, b, ox, oy):
    T = lambda pts: [(x + ox, y + oy) for x, y in pts]
    for ln in b['lines']:
        pg.ink(T(ln.coords))
    sh = b['shape']
    for seg in ring_with_gaps(sh.exterior):
        pg.cut(T(seg))
    for r in sh.interiors:
        pg.cut(T(list(r.coords)[:-1]), close=True)
    for fx, fy0, fy1 in b.get('folds', []):
        g = LineString([(fx, fy0), (fx, fy1)]).intersection(sh)
        for l_ in ([g] if g.geom_type == 'LineString' else list(g.geoms)):
            pg.fold(T(l_.coords))


# ---------- 底座展開圖 ----------
TABP = [(0, 11.7), (7.4, 11.7), (8.2, 13.5), (10.5, 13.5), (12.5, 10.8), (12.5, 9.6), (9, 7.5), (5, 5.2), (0, 5.2)]   # (超出牆端的距離 r, 離折線 t)


def base_net():
    L_ = RH
    flaps = []
    for i in range(6):
        a, e = HEX[i], HEX[(i + 1) % 6]
        ex, ey = (e[0] - a[0]) / L_, (e[1] - a[1]) / L_
        nx, ny = ey, -ex
        W_ = lambda u, t: (a[0] + ex * u + nx * t, a[1] + ey * u + ny * t)
        outline = [W_(0, 0), W_(0, WALL), W_(L_ / 2 - 0.4, WALL)], \
                  [W_(L_ / 2 + 0.4, WALL), W_(L_, WALL)] + [W_(L_ + r, t) for r, t in TABP] + [W_(L_, 0)]
        poly = Polygon([W_(0, 0), W_(0, WALL), W_(L_, WALL)] + [W_(L_ + r, t) for r, t in TABP] + [W_(L_, 0)])
        flaps.append(dict(cut=outline, poly=poly, hinge=[W_(L_, 5.2), W_(L_, 11.7)], slit=[W_(6.5, 4.9), W_(6.5, 12.0)],
                          edge=[a, e], mid=W_(L_ / 2, WALL / 2), W=W_))
    return flaps


def draw_base(pg, cx, cy):
    T = lambda pts: [(x + cx, y + cy) for x, y in pts]
    flaps = base_net()
    if pg.mode != 'cut':
        for f in flaps:
            pg.fill(T(list(f['poly'].buffer(1.0).exterior.coords)), ACC)
        dpath = os.path.join(CACHE, 'deco.png')
        if not os.path.exists(dpath) or True:
            deco_image()[0].save(dpath)
        pg.image(dpath, cx - RH, cy - 70, RH * 2, 140)
        pg.text(cx - 5, cy - 81.6, '台北', 27, 'KAI', (0.98, 0.96, 0.9), 'r')
        pg.text(cx - 1, cy - 80.2, 'TAIPEI', 12, 'JHB', (0.98, 0.96, 0.9))
    done = set()
    for no, a, e in slits():
        pg.cut(T([a, e]))
        if no not in done:
            done.add(no)
            pg.text(cx + a[0] + 0.5, cy + a[1] - 5.6, CIRC[no], 14, 'JHB', (0.3, 0.28, 0.28))
    for f in flaps:
        for seg in f['cut']:
            pg.cut(T(seg))
        pg.cut(T(f['slit']))
        pg.fold(T(f['edge'])); pg.fold(T(f['hinge']))


# ---------- 頁面 ----------
def stage_img(upto, crop=(60, 120, 2020, 1700)):
    p = os.path.join(CACHE, 'stage%d.jpg' % upto)
    nos = [n for n, b in BUILT.items() if b['week'] <= upto]
    scene(nos, True).crop(crop).save(p, quality=92)
    return p, (crop[2] - crop[0]) / (crop[3] - crop[1])


def header(pg, wk):
    pg.fill([(12, 184.5), (285, 184.5), (285, 185.3), (12, 185.3)], ACC)
    pg.text(12, 188.5, '台北', 30, 'KAI', ACC)
    pg.text(38, 192.5, '跟著日曆去旅行', 13, 'JHB')
    pg.text(38, 187.3, '%d 年 %d 月　第 %d 週' % (YEAR, MONTH, wk), 12, 'JH')
    names = '、'.join(CIRC[n] + b['label'] for n, b in BUILT.items() if b['week'] == wk)
    pg.text(285, 189, '這週的零件：' + names, 14, 'JHB', align='r')
    # 日期列
    wd = '一二三四五六日'
    cw = 273 / 7
    for i in range(7):
        x = 12 + i * cw
        day = (wk - 1) * 7 + i + 1
        col = (0.78, 0.33, 0.24) if i >= 5 else (0.2, 0.2, 0.22)
        pg.ink([(x, 145.5), (x + cw - 2.5, 145.5), (x + cw - 2.5, 181), (x, 181), (x, 145.5)], 0.3, 0.6)
        pg.text(x + 2.5, 170.5, '%d' % day, 26, 'JHB', col)
        pg.text(x + cw - 5, 173.5, '週' + wd[i], 14, 'JH', col, 'r')
        for yy in (165, 158.5, 152):
            pg.ink([(x + 2.5, yy), (x + cw - 5, yy)], 0.2, 0.78)


def minimap(pg, cx, cy, wk, k=0.26):
    pg.text(cx, cy + 70 * k + 4, '照號碼插在這裡', 13, 'JHB', align='c')
    hx = [(cx + x * k, cy + y * k) for x, y in HEX]
    if pg.mode != 'cut':
        pg.fill(hx, (0.95, 0.93, 0.88))
    pg.ink(hx + [hx[0]], 0.3, 0.5)
    seen = set()
    for no, a, e in slits():
        now = BUILT[no]['week'] == wk
        pts = [(cx + a[0] * k, cy + a[1] * k), (cx + e[0] * k, cy + e[1] * k)]
        if pg.mode != 'cut':
            pg.poly(pts, (0.85, 0.33, 0.22) if now else (0.72, 0.70, 0.68), 0.9 if now else 0.5)
        if now and no not in seen and no != 1:
            seen.add(no)
            pg.text(pts[0][0] - 0.5, pts[0][1] + 1.2, CIRC[no], 15, 'JHB', (0.85, 0.33, 0.22))
    if wk == 1:
        pg.text(cx, cy - 2, '①', 15, 'JHB', (0.85, 0.33, 0.22), 'c')
    pg.text(cx, cy - 70 * k - 5, '▲ 正面（寫台北那一邊）', 12, 'JH', align='c')


K_ = PC.K
WEEKS = {
    1: dict(theme=('盆地的山', '台北是盆地，四面都是山。左右兩片沿綠線折向自己，圍住底座後面三邊。'),
            parts=[(1, 0, 14, 30, '', 0, 0)], map=(264, 108, 0.26), stage=(243, 30, 42),
            sw=[('遠山', 'far'), ('近山', 'near'), ('樓房', 'bld2'), ('小樹', 'leaf3')]),
    2: dict(theme=('老街與大樹', '走進紅磚老街，樹上停著台灣藍鵲（台北市的市鳥）。'),
            parts=[(2, 0, 66, 38, '② 老街屋（兩端小翼折向背面）', 30, 23), (3, 0, 153, 38, '③ 藍鵲與樹', 138, 23),
                   (3, 1, 202, 38, '③ 樹的側片', 188, 23)],
            map=(253.5, 116, 0.3), stage=(222, 28, 63),
            sw=[('紅磚', 'brick'), ('米牆', 'plaster'), ('樹葉', 'leaf'), ('藍鵲', 'blue')]),
    3: dict(theme=('逛夜市', '燈籠亮了，小籠包剛蒸好。街角有一對歪著腰的郵筒。'),
            parts=[(4, 0, 62, 38, '④ 夜市攤', 50, 23), (5, 0, 124, 38, '⑤ 小籠包', 112, 23), (6, 0, 176, 38, '⑥ 歪腰郵筒', 160, 23)],
            map=(253.5, 116, 0.3), stage=(222, 28, 63),
            sw=[('遮棚', 'cloth'), ('蒸籠', 'bamboo'), ('郵筒', 'green'), ('湯鍋', 'grey')]),
    4: dict(theme=('三月的街頭', '杜鵑花開了（台北市的市花），機車停在路邊。台北完成了！29～31 日接下一座城市。'),
            parts=[(7, 0, 56, 38, '⑦ 機車', 46, 23), (8, 0, 116, 38, '⑧ 杜鵑花', 104, 23),
                   (8, 1, 174, 38, '⑧ 側片（十字卡進花叢）', 150, 23)],
            map=(253.5, 116, 0.3), stage=(222, 28, 63),
            sw=[('杜鵑', 'pink'), ('葉子', 'leaf3'), ('機車', 'scoot'), ('安全帽', 'helmet')]),
}


def page_week(pg, wk):
    cfg = WEEKS[wk]
    header(pg, wk)
    for no, isb, ox, oy, lab, lx, ly in cfg['parts']:
        b = CROSSB[no] if isb else BUILT[no]
        place(pg, b, ox, oy)
        if lab:
            pg.text(lx, ly, lab, 14, 'JHB')
    th = cfg['theme']
    pg.text(14, 135.5, th[0], 17, 'JHB', ACC)
    pg.text(14 + len(th[0]) * 6.2 + 4, 135.8, th[1], 13, 'JH')
    if cfg['sw'] and pg.mode != 'cut':
        pg.text(285, 12.5, '先上色，等乾了再撥下來', 13, 'JHB', (0.78, 0.33, 0.24), 'r')
        pg.text(14, 12.5, '建議顏色', 13, 'JHB')
        x = 40
        for nm, key in cfg['sw']:
            pg.fill([(x, 11.5), (x + 10, 11.5), (x + 10, 17.5), (x, 17.5)], tuple(hexrgb(K_[key])))
            pg.text(x + 12, 12.5, nm, 13, 'JH'); x += 16 + len(nm) * 4.8 + 8
    mx, my, mk = cfg['map']
    minimap(pg, mx, my, wk, mk)
    if pg.mode != 'cut':
        p, ar = stage_img(wk)
        x, y, w = cfg['stage']
        pg.image(p, x, y, w, w / ar)
        pg.text(x + w / 2, y - 5, '這週完成的樣子', 11, 'JH', align='c')
    if wk in (3, 4):
        q = {3: '這週的旅行小記：你最喜歡的夜市小吃是什麼？', 4: '這週的旅行小記：三月，你家附近開了什麼花？'}[wk]
        pg.text(14, 122, q, 14, 'JHB')
        for yy in (112, 102):
            pg.ink([(14, yy), (170 if wk == 4 else 212, yy)], 0.25, 0.7)
    # 十字卡法小圖（俯視）
    if wk in (2, 4) and pg.mode != 'cut':
        x0, y0 = (60, 122) if wk == 2 else (190, 78)
        pg.poly([(x0 - 9, y0), (x0 + 9, y0)], (0.3, 0.3, 0.32), 0.7); pg.poly([(x0 + 2, y0 - 6), (x0 + 2, y0 + 6)], (0.85, 0.33, 0.22), 0.7)
        pg.text(x0, y0 - 11, '從上面看：側片（紅）', 11, 'JH', align='c'); pg.text(x0, y0 - 15.5, '十字卡進主片的縫', 11, 'JH', align='c')
    pg.lmark()


def page_cover(pg):
    pg.text(14, 190, '跟著日曆去旅行', 18, 'JHB')
    pg.text(12, 160, '台北', 78, 'KAI', ACC)
    pg.text(15, 149, 'TAIPEI　%d 年 %d 月' % (YEAR, MONTH), 15, 'JH')
    if pg.mode != 'cut':
        p, ar = stage_img(4)
        pg.image(p, 12, 142 - 76 / ar, 76, 76 / ar)
    y = 62
    for t in ['這一頁就是城市的底座', '① 把六角形整片撥下來', '② 六片牆沿折線往下折', '③ 小耳朵插進隔壁牆的縫', '④ 每週撥零件、上色、插上']:
        pg.text(14, y, t, 14 if y == 62 else 13, 'JHB' if y == 62 else 'JH'); y -= 8
    draw_base(pg, 189, 100)
    pg.text(189 + RH / 2 + 15, 100 - 70 - 10.6, '← 小耳朵', 12, 'JHB', (0.78, 0.33, 0.24))
    pg.text(189 - RH / 2 + 6.5, 100 - 70 - 19.5, '↑ 縫', 12, 'JHB', (0.78, 0.33, 0.24), 'c')
    pg.lmark()


def make(mode, path):
    c = RC.Canvas(path, pagesize=(PW * mm, PH * mm))
    c.setTitle('台北週曆 ' + mode)
    for i in range(5):
        pg = Pg(c, mode, i)
        page_cover(pg) if i == 0 else page_week(pg, i)
        c.showPage()
    c.save()


def check(path):
    doc = pymupdf.open(path); cols = set(); n = 0
    for pgx in doc:
        for d in pgx.get_drawings():
            cols.add(tuple(round(v, 3) for v in (d.get('color') or ()))); n += 1
        assert not pgx.get_text().strip() and not pgx.get_images(), '切割檔不該有文字或圖片'
    print('切割檔顏色：', sorted(cols), '路徑數', n)
    assert cols <= {(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.0)}


if __name__ == '__main__':
    build_all()
    scene(colored=True, path=os.path.join(PREV, '正面預覽_上色.png'))
    scene(colored=False, path=os.path.join(PREV, '正面預覽_未上色.png'))
    fc, fp, fb = [os.path.join(OUT, n) for n in ('台北週曆_切割檔.pdf', '台北週曆_印刷檔.pdf')] + [os.path.join(CACHE, 'both.pdf')]
    make('cut', fc); make('print', fp); make('both', fb)
    check(fc)
    names = ['週曆_0_封面與底座', '週曆_1_第一週', '週曆_2_第二週', '週曆_3_第三週', '週曆_4_第四週']
    ims = []
    for i, pgx in enumerate(pymupdf.open(fb)):
        pm = pgx.get_pixmap(dpi=130); p = os.path.join(PREV, names[i] + '.png'); pm.save(p)
        ims.append(Image.open(p).convert('RGB'))
    # 整套總覽
    fr = Image.open(os.path.join(PREV, '正面預覽_上色.png'))
    w, h = ims[0].size; g = 30
    sheet = Image.new('RGB', (w * 3 + g * 4, h * 2 + g * 3), (236, 231, 222))
    tiles = [fr] + ims
    for i, t in enumerate(tiles):
        t2 = t.copy(); t2.thumbnail((w, h))
        x = g + (i % 3) * (w + g) + (w - t2.width) // 2; y = g + (i // 3) * (h + g) + (h - t2.height) // 2
        sheet.paste(t2, (x, y))
    sheet.save(os.path.join(PREV, '整套總覽.png'))
    tot = sum(CUTLEN.values())
    info = dict(頁面='A4 橫式 297×210 mm，共 5 頁', 月份='%d 年 %d 月' % (YEAR, MONTH), 底座='六角對邊 140、牆高 14',
                每頁切線長度mm={str(k): round(v) for k, v in CUTLEN.items()}, 切線總長mm=round(tot), 校內費用元=round(tot * 0.03),
                零件={('%d%s' % (n, 'B' if isb else '')): dict(名稱=b['label'], 寬=round(b['w'], 1), 高=round(b['maxy'], 1))
                    for isb, d in ((0, BUILT), (1, CROSSB)) for n, b in d.items()})
    json.dump(info, open(os.path.join(ROOT, '尺寸.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(info, ensure_ascii=False))
