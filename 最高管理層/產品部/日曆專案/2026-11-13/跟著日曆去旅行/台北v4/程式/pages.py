# -*- coding: utf-8 -*-
"""週曆五頁（封面＝底座、第 1～4 週）。版型沿用 11/05 定案：木色作品區＋奶油色日期卡、思源宋體、文字極少。
輸出：印刷檔、切割檔（台科大快切機規範）、預覽圖。"""
from scene import *
from reportlab.pdfgen import canvas as RC
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import pymupdf
import fonts as F_

for n in F_.W:
    pdfmetrics.registerFont(TTFont(n, F_.path(n)))
PW, PH = 297.0, 210.0
OUT = os.path.join(ROOT, '切割與印刷檔'); os.makedirs(OUT, exist_ok=True)
YEAR, MONTH, MONTH_ZH, MONTH_EN = 2027, 3, '3月', 'MARCH'
H_ = lambda h: tuple(hexrgb(h))
BOARD, WOOD, INK, INK2, RED_, CREAM, GRAIN_D, GRAIN_L, EDGE = map(H_, ['#F2E9D5', '#DEC6A0', '#2E2218', '#4D3B2C', '#A33F2A', '#FBF5E6', '#B08F5E', '#EFDDB8', '#B99A6A'])
KRAFT = H_('#C9A77C')
RED, GREEN = (1, 0, 0), (0, 1, 0)
CUTLEN = {}
WHITE_EDGE = 1.2     # 零件外圍的白邊（印刷與切割對位誤差的緩衝）


class Pg:
    def __init__(s, c, mode, page):
        s.c, s.mode, s.page = c, mode, page
        CUTLEN.setdefault(page, 0.0)

    def _path(s, pts, close):
        p = s.c.beginPath(); p.moveTo(pts[0][0] * mm, pts[0][1] * mm)
        for x, y in pts[1:]:
            p.lineTo(x * mm, y * mm)
        if close:
            p.close()
        return p

    def poly(s, pts, col, w, dash=None, close=False):
        c = s.c
        c.setStrokeColorRGB(*col); c.setLineWidth(w * mm); c.setLineCap(1); c.setLineJoin(1); c.setDash(dash or [])
        c.drawPath(s._path(pts, close), stroke=1, fill=0)

    def cut(s, pts, close=False):
        if s.mode == 'cut':
            CUTLEN[s.page] += LineString(list(pts) + ([pts[0]] if close else [])).length
            s.poly(pts, RED, 0.1, close=close)
        elif s.mode == 'both':
            s.poly(pts, H_('#6B5A4A'), 0.25, dash=[1.2 * mm, 0.9 * mm], close=close)

    def fold(s, pts):
        if s.mode == 'cut':
            CUTLEN[s.page] += LineString(pts).length
            s.poly(pts, GREEN, 0.1)
        elif s.mode == 'both':
            s.poly(pts, H_('#8A7A5C'), 0.25, dash=[0.5 * mm, 1.0 * mm])

    def ink(s, pts, w=0.22, col=None):
        if s.mode != 'cut':
            s.poly(pts, col or H_('#7A6A5E'), w)

    def text(s, x, y, t, size, font='SerifBold', col=INK, align='l', cs=0):
        if s.mode == 'cut':
            return
        c = s.c; c.setFillColorRGB(*col)
        to = c.beginText(); to.setFont(font, size); to.setCharSpace(cs)
        w = pdfmetrics.stringWidth(t, font, size) + cs * max(len(t) - 1, 0)
        x0 = x * mm - (0 if align == 'l' else w if align == 'r' else w / 2)
        to.setTextOrigin(x0, y * mm); to.textOut(t); c.drawText(to)

    def fill(s, pts, col):
        if s.mode != 'cut':
            s.c.setFillColorRGB(*col); s.c.drawPath(s._path(pts, True), stroke=0, fill=1)

    def geom_fill(s, g, col, dx=0, dy=0):
        for p in ([g] if g.geom_type == 'Polygon' else list(g.geoms)):
            s.fill([(x + dx, y + dy) for x, y in p.exterior.coords], col)

    def rrect(s, x, y, w, h, r, col, stroke=None):
        if s.mode == 'cut':
            return
        c = s.c; c.setFillColorRGB(*col)
        if stroke:
            c.setStrokeColorRGB(*stroke); c.setLineWidth(0.25 * mm); c.setDash([])
        c.roundRect(x * mm, y * mm, w * mm, h * mm, r * mm, stroke=1 if stroke else 0, fill=1)

    def image(s, path, x, y, w, h):
        if s.mode != 'cut':
            s.c.drawImage(ImageReader(path), x * mm, y * mm, w * mm, h * mm, mask='auto')

    def lmark(s):
        s.poly([(5, PH - 5), (5, 5), (PW - 5, 5)], (0, 0, 0), 0.3)


def board(pg, x, y, w, h):
    """木色作品區：平塗＋細密的平行淡木紋。"""
    pg.rrect(x, y, w, h, 3, WOOD)
    if pg.mode == 'cut':
        return
    rng = np.random.default_rng(int(x * 7 + y))
    yy = y + 1.6
    k = 0
    while yy < y + h - 1.2:
        ph = float(rng.uniform(0, 6)); am = float(rng.uniform(0.15, 0.5))
        pts = [(xx, yy + am * np.sin(xx / 31.0 + ph)) for xx in np.arange(x + 1.5, x + w - 1.4, 5)]
        pg.poly(pts, H_('#E1CAA5') if k % 3 else H_('#DAC29C'), 0.2)
        yy += float(rng.uniform(1.3, 2.4)); k += 1


def place(pg, b, ox, oy, number=None):
    T = lambda pts: [(x + ox, y + oy) for x, y in pts]
    sh = b['shape']
    if pg.mode != 'cut':
        pg.geom_fill(sh.buffer(WHITE_EDGE, quad_segs=6), (1, 1, 1), ox, oy)
    for ln in b['lines']:
        pg.ink(T(ln.coords))
    for seg in ring_with_gaps(sh.exterior):
        pg.cut(T(seg))
    for r in sh.interiors:
        if pg.mode != 'cut':
            pg.geom_fill(Polygon(r).buffer(-WHITE_EDGE * 0.6), WOOD, ox, oy)
        pg.cut(T(list(r.coords)[:-1]), close=True)
    for fx, fy0, fy1 in b.get('folds', []):
        g = LineString([(fx, fy0), (fx, fy1)]).intersection(sh)
        for l_ in ([g] if g.geom_type == 'LineString' else list(g.geoms)):
            pg.fold(T(l_.coords))
    if number and b['tabs']:
        x, w = b['tabs'][0]
        pg.text(ox + x, oy - 6.2, str(number), 8, 'SerifSemi', H_('#9A8E82'), 'c')


# ---------- 底座展開圖 ----------
TABP = [(0, 11.7), (7.4, 11.7), (8.2, 13.5), (10.5, 13.5), (12.5, 10.8), (12.5, 9.6), (9, 7.5), (5, 5.2), (0, 5.2)]


def base_net():
    L_ = RH
    flaps = []
    for i in range(6):
        a, e = HEX[i], HEX[(i + 1) % 6]
        ex, ey = (e[0] - a[0]) / L_, (e[1] - a[1]) / L_
        nx, ny = ey, -ex
        W_ = lambda u, t, a=a, ex=ex, ey=ey, nx=nx, ny=ny: (a[0] + ex * u + nx * t, a[1] + ey * u + ny * t)
        outline = [W_(0, 0), W_(0, WALL), W_(L_ / 2 - 0.4, WALL)], \
                  [W_(L_ / 2 + 0.4, WALL), W_(L_, WALL)] + [W_(L_ + r, t) for r, t in TABP] + [W_(L_, 0)]
        poly = Polygon([W_(0, 0), W_(0, WALL), W_(L_, WALL)] + [W_(L_ + r, t) for r, t in TABP] + [W_(L_, 0)])
        flaps.append(dict(cut=outline, poly=poly, hinge=[W_(L_, 5.2), W_(L_, 11.7)], slit=[W_(6.5, 4.9), W_(6.5, 12.0)], edge=[a, e]))
    return flaps


def draw_base(pg, cx, cy):
    T = lambda pts: [(x + cx, y + cy) for x, y in pts]
    flaps = base_net()
    if pg.mode != 'cut':
        for f in flaps:
            pg.geom_fill(f['poly'].buffer(1.0), KRAFT, cx, cy)
        dpath = os.path.join(CACHE, 'deco.png'); deco_image()[0].save(dpath)
        pg.image(dpath, cx - RH, cy - 70, RH * 2, 140)
        pg.text(cx, cy - 81.4, '台北', 24, 'SerifBlack', H_('#4E3A2A'), 'c', cs=8)
    done = set()
    for no, a, e in slits():
        pg.cut(T([a, e]))
        if no not in done:
            done.add(no)
            pg.text(cx + a[0] - 2.2, cy + a[1] - 0.8, str(no), 6, 'SerifSemi', H_('#B5A792'), 'c')
    for f in flaps:
        for seg in f['cut']:
            pg.cut(T(seg))
        pg.cut(T(f['slit']))
        pg.fold(T(f['edge'])); pg.fold(T(f['hinge']))


# ---------- 頁面 ----------
def stage_img(upto, crop=(150, 170, 1930, 1680)):
    p = os.path.join(CACHE, 'stage%d.jpg' % upto)
    nos = [n for n, b in BUILT.items() if b['week'] <= upto]
    scene(nos, True, table=False).crop(crop).save(p, quality=95)
    return p, (crop[2] - crop[0]) / (crop[3] - crop[1])


BX, BY, BW, BH = 12, 76, 273, 122       # 作品區


def info(pg, wk):
    """下方資訊區：只有月份、城市、七天（日期卡留白可寫字）。"""
    pg.text(12, 64, MONTH_ZH, 21, 'SerifBlack', INK)
    pg.text(31, 64.3, MONTH_EN, 10, 'SerifBold', INK2, cs=2.6)
    pg.text(285, 64.3, '台北', 13, 'SerifBold', INK, 'r', cs=2)
    wd = '一二三四五六日'
    gap = 5.0; cw = (273 - gap * 6) / 7
    for i in range(7):
        x = 12 + i * (cw + gap)
        col = RED_ if i >= 5 else INK
        pg.rrect(x, 12, cw, 46, 2.5, CREAM, stroke=H_('#D9C7A6'))
        pg.text(x + 4, 44.5, '%d' % ((wk - 1) * 7 + i + 1), 25, 'SerifBlack', col)
        pg.text(x + cw - 4, 47.5, '星期' + wd[i], 10.5, 'SerifSemi', col if i >= 5 else INK2, 'r')


WEEKS = {1: [(1, 0)], 2: [(2, 0), (3, 0)], 3: [(4, 0), (4, 1), (5, 0)], 4: [(6, 0), (7, 0), (8, 0), (8, 1)]}
GAPX = {1: 0, 2: 30, 3: 30, 4: 26}


def page_week(pg, wk):
    pg.fill([(0, 0), (PW, 0), (PW, PH), (0, PH)], BOARD)
    board(pg, BX, BY, BW, BH)
    items = [(no, isb, CROSSB[no] if isb else BUILT[no]) for no, isb in WEEKS[wk]]
    tot = sum(b['w'] for _, _, b in items) + GAPX[wk] * (len(items) - 1)
    hmax = max(b['maxy'] for _, _, b in items)
    oy = BY + (BH - (hmax + TAB_H + (0 if wk == 1 else 19))) / 2 + TAB_H     # 零件底部齊一條地平線，整組上下置中
    ty = BY + BH - 11 if wk == 1 else oy + hmax + 12.5                      # 標題排成一列
    x = BX + (BW - tot) / 2
    for no, isb, b in items:
        place(pg, b, x - b['minx'], oy, number=no)
        cxp = x + b['w'] / 2
        if wk == 1:
            pg.text(BX + 34, ty - 2, b['label'], 16, 'SerifBlack', INK, 'c')
            pg.text(BX + 34, ty - 8.4, PC.CAPTION[no], 10.5, 'SerifSemi', INK2, 'c')
        elif isb:
            pg.text(cxp, ty, b['label'], 12, 'SerifBold', INK2, 'c')
        else:
            pg.text(cxp, ty, b['label'], 16, 'SerifBlack', INK, 'c')
            pg.text(cxp, ty - 6.4, PC.CAPTION[no], 10.5, 'SerifSemi', INK2, 'c')
        x += b['w'] + GAPX[wk]
    info(pg, wk)
    pg.lmark()


def page_cover(pg):
    pg.fill([(0, 0), (PW, 0), (PW, PH), (0, PH)], BOARD)
    board(pg, 88, 10, 201, 190)
    draw_base(pg, 188.5, 105)
    pg.text(12, 186, '跟著日曆去旅行', 13, 'SerifBold', INK2, cs=2)
    pg.text(11, 158, '台北', 56, 'SerifBlack', INK, cs=5)
    pg.text(12, 146.5, MONTH_ZH, 21, 'SerifBlack', INK)
    pg.text(31, 146.8, MONTH_EN, 10, 'SerifBold', INK2, cs=2.6)
    if pg.mode != 'cut':
        p, ar = stage_img(4)
        pg.image(p, 6, 128 - 78 / ar, 78, 78 / ar)
    pg.lmark()


def make(mode, path):
    c = RC.Canvas(path, pagesize=(PW * mm, PH * mm))
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
    fr = Image.open(os.path.join(PREV, '正面預覽_上色.png'))
    w, h = ims[0].size; g = 30
    sheet = Image.new('RGB', (w * 3 + g * 4, h * 2 + g * 3), (226, 219, 206))
    for i, t in enumerate([fr] + ims):
        t2 = t.copy(); t2.thumbnail((w, h))
        sheet.paste(t2, (g + (i % 3) * (w + g) + (w - t2.width) // 2, g + (i // 3) * (h + g) + (h - t2.height) // 2))
    sheet.save(os.path.join(PREV, '整套總覽.png'))
    tot = sum(CUTLEN.values())
    info_ = dict(頁面='A4 橫式 297×210 mm，共 5 頁', 月份='%d 年 %d 月' % (YEAR, MONTH), 底座='六角對邊 140、牆高 14',
                 每頁切線長度mm={str(k): round(v) for k, v in CUTLEN.items()}, 切線總長mm=round(tot), 校內費用元=round(tot * 0.03),
                 零件={('%d%s' % (n, 'B' if isb else '')): dict(名稱=b['label'], 寬=round(b['w'], 1), 高=round(b['maxy'], 1))
                     for isb, d in ((0, BUILT), (1, CROSSB)) for n, b in d.items()})
    json.dump(info_, open(os.path.join(ROOT, '尺寸.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('切線總長 %d mm，校內約 %d 元' % (tot, tot * 0.03))
