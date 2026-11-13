# -*- coding: utf-8 -*-
"""週曆五頁（封面＝底座、第 1～4 週）。版式由編排設計師定：一套 7 欄格線、留白當主角、數字不加框、
只有霧灰底色＋一個朱色。印刷檔不畫任何切割線或虛線；切割檔另出（台科大快切機規範）。"""
from scene import *
from shapely import affinity as AF
from geo import _polys
from reportlab.pdfgen import canvas as RC
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pymupdf

for n in F_.W:
    pdfmetrics.registerFont(TTFont(n, F_.path(n)))
pdfmetrics.registerFont(TTFont('Bodoni', 'C:/Windows/Fonts/BOD_R.TTF'))
pdfmetrics.registerFont(TTFont('GaraI', 'C:/Windows/Fonts/GARAIT.TTF'))
PW, PH = 297.0, 210.0
OUT = os.path.join(ROOT, '切割與印刷檔'); os.makedirs(OUT, exist_ok=True)
H_ = lambda h: tuple(hexrgb(h))
INKC, MIST, GREY, ACC = H_('#1C1C1C'), H_('#DCE2DF'), H_('#6E7370'), H_('#C8452D')
DARK = H_('#3A3D3B')
TERM = {6: '驚蟄', 21: '春分'}      # 2027 年節氣，付印前請再核對
RED, GREEN = (1, 0, 0), (0, 1, 0)
COLX = [20, 58, 96, 134, 172, 210, 248]
GROUND = 81.0
CUTLEN = {}
ZH = '一二三四五六日'
WEEKNAME = ['', '第一週', '第二週', '第三週', '第四週']
NAMES = {3: '老公寓', 4: '老廟'}
SERIES = '跟著日曆去旅行'
QR_PATH = os.path.join(ROOT, '..', '..', '..', '..', 'LINE官方帳號草模', 'QR', '日曆QR_柿子教學.png')   # 先用之前日曆上的 QR，之後換教學
QR_MM = 17.0
WEEKSUB = ['', '先看山', '再進城', '走巷子', '逛街角']
# 文字由國文老師定稿：只寫眼睛看得到的東西，用長輩平常會說的話，一句只講一件事
COPY = {1: '台北，四面都是山', 2: '大樓一棟比一棟高', 3: '陽台上，有人澆花', 4: '路過，進來拜一拜', 5: '紅磚樓下，是亭仔腳',
        6: '長尾巴的藍鵲來了', 7: '天黑了，燈才亮', 8: '杜鵑開了，機車停著'}
WEEKX = {1: [(1, 74)], 2: [(2, 74), (3, 172)], 3: [(4, 74), (5, 134), (6, 194)], 4: [(7, 74), (8, 134)]}


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

    def poly(s, pts, col, w, close=False):
        c = s.c
        c.setStrokeColorRGB(*col); c.setLineWidth(w * mm); c.setLineCap(1); c.setLineJoin(1); c.setDash([])
        c.drawPath(s._path(pts, close), stroke=1, fill=0)

    def cut(s, pts, close=False):
        if s.mode == 'cut':
            CUTLEN[s.page] += LineString(list(pts) + ([pts[0]] if close else [])).length
            s.poly(pts, RED, 0.1, close=close)

    def fold(s, pts):
        if s.mode == 'cut':
            CUTLEN[s.page] += LineString(pts).length
            s.poly(pts, GREEN, 0.1)

    def ink(s, pts, w=0.16, col=GREY, close=False):
        if s.mode != 'cut':
            s.poly(pts, col, w, close=close)

    def text(s, x, y, t, size, font='SerifSemi', col=INKC, align='l', cs=0.0):
        if s.mode == 'cut':
            return
        c = s.c; c.setFillColorRGB(*col)
        to = c.beginText(); to.setFont(font, size); to.setCharSpace(cs)
        w = pdfmetrics.stringWidth(t, font, size) + cs * max(len(t) - 1, 0)
        to.setTextOrigin(x * mm - (0 if align == 'l' else w if align == 'r' else w / 2), y * mm); to.textOut(t); c.drawText(to)

    def fill(s, pts, col):
        if s.mode != 'cut':
            s.c.setFillColorRGB(*col); s.c.drawPath(s._path(pts, True), stroke=0, fill=1)

    def gfill(s, g, col, dx=0, dy=0):
        for p in ([g] if g.geom_type == 'Polygon' else list(g.geoms)):
            if s.mode == 'cut':
                return
            c = s.c; c.setFillColorRGB(*col)
            path = c.beginPath()
            for r in [p.exterior] + list(p.interiors):
                pts = [(x + dx, y + dy) for x, y in r.coords]
                path.moveTo(pts[0][0] * mm, pts[0][1] * mm)
                for x, y in pts[1:]:
                    path.lineTo(x * mm, y * mm)
                path.close()
            c.drawPath(path, stroke=0, fill=1, fillMode=0)

    def lmark(s):
        s.poly([(5, PH - 5), (5, 5), (PW - 5, 5)], (0, 0, 0), 0.3)


def place(pg, b, ox, oy):
    """印刷：紙白的零件形狀＋細實線線稿（輪廓線往內縮，切歪也不會切到線）。切割：紅線外形。"""
    T = lambda pts: [(x + ox, y + oy) for x, y in pts]
    sh = b['shape']
    pg.gfill(sh.buffer(0.3, join_style=2), (1, 1, 1), ox, oy)
    for ln in b.get('dlines', []):
        pg.ink(T(ln.coords), 0.11)
    for ln in b['lines']:
        pg.ink(T(ln.coords), 0.2, DARK)
    body = sh.intersection(box(-999, 0.0, 999, 999))          # 插榫不畫輪廓
    for p in _polys(body.buffer(-0.4, join_style=2)):
        for r in [p.exterior] + list(p.interiors):
            pg.ink(T(r.coords), 0.36, DARK, close=True)
    for seg in ring_with_gaps(sh.exterior):
        pg.cut(T(seg))
    for r in sh.interiors:
        pg.cut(T(list(r.coords)[:-1]), close=True)
    for fx, fy0, fy1 in b.get('folds', []):
        g = LineString([(fx, fy0), (fx, fy1)]).intersection(sh)
        for l_ in ([g] if g.geom_type == 'LineString' else list(g.geoms)):
            pg.fold(T(l_.coords))


# ---------- 底座展開圖 ----------
KT = WALL / 14.0
TABP = [(r, t * KT) for r, t in [(0, 11.7), (7.4, 11.7), (8.2, 13.5), (10.5, 13.5), (12.5, 10.8), (12.5, 9.6), (9, 7.5), (5, 5.2), (0, 5.2)]]


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
        flaps.append(dict(cut=outline, poly=poly, hinge=[W_(L_, 5.2 * KT), W_(L_, 11.7 * KT)], slit=[W_(6.5, 4.9 * KT), W_(6.5, 12.0 * KT)], edge=[a, e]))
    return flaps


def draw_base(pg, cx, cy):
    T = lambda pts: [(x + cx, y + cy) for x, y in pts]
    flaps = base_net()
    hexp, dl = deco_lines()
    pg.gfill(unary_union([f['poly'] for f in flaps] + [hexp]).buffer(0.3, join_style=2), (1, 1, 1), cx, cy)
    pg.ink(T(list(hexp.buffer(-0.5, join_style=2).exterior.coords)), 0.3, DARK, close=True)
    for l_ in dl:
        pg.ink(T(l_.coords), 0.14, H_('#B9C0BC'))
    pg.text(cx, cy - HF - 8.6, '台北', 15, 'SerifSemi', INKC, 'c', cs=6)
    seen = set()
    for no, a, e in slits():
        pg.cut(T([a, e]))
    for f in flaps:
        for seg in f['cut']:
            pg.cut(T(seg))
        pg.cut(T(f['slit']))
        pg.fold(T(f['edge'])); pg.fold(T(f['hinge']))


BLK_Y = 90.0            # 作品區下緣
GROUND = 101.0
WEEKX = {1: [(1, 74)], 2: [(2, 74), (4, 176)], 3: [(3, 74), (5, 190)], 4: [(6, 74), (7, 142), (8, 194)]}


def page_week(pg, wk):
    pg.fill([(58, BLK_Y), (281, BLK_Y), (281, 194), (58, 194)], MIST)
    hmax = max(BUILT[no]['maxy'] for no, _ in WEEKX[wk])
    gy = max(GROUND, BLK_Y + (194 - BLK_Y - hmax - 8) / 2 + 8)
    for no, x in WEEKX[wk]:
        b = BUILT[no]
        place(pg, b, x - b['minx'], gy)
        pg.text(x, 80, NAMES.get(no, b['label']), 15, 'SerifSemi', INKC, cs=1)
        pg.text(x, 73.5, COPY[no], 12, 'SerifReg', DARK, cs=0.4)
    pg.text(20, 186.5, '三月', 22, 'SerifSemi', INKC, cs=1)
    pg.text(20, 179.5, 'March', 14, 'GaraI', INKC)
    pg.text(20, 171, WEEKNAME[wk], 13, 'SerifSemi', INKC, cs=1)
    pg.text(20, 164, WEEKSUB[wk], 13, 'SerifReg', DARK, cs=1)
    pg.text(20, 98, SERIES, 11, 'SerifReg', DARK)
    pg.text(20, 90.5, '台北', 14, 'SerifSemi', INKC, cs=1)
    if pg.mode != 'cut':
        from reportlab.lib.utils import ImageReader
        pg.c.drawImage(ImageReader(QR_PATH), (281 - QR_MM) * mm, (BLK_Y - 3 - QR_MM) * mm, QR_MM * mm, QR_MM * mm)
    # 日期帶：七欄、欄線、數字下面留兩行可以寫字
    pg.ink([(20, 66), (281, 66)], 0.3, INKC)
    for i in range(7):
        x = COLX[i]; day = (wk - 1) * 7 + i + 1
        col = ACC if i == 6 else INKC
        if i:
            pg.ink([(x - 2.5, 20), (x - 2.5, 62)], 0.15, GREY)
        pg.text(x, 56.5, '星期' + ZH[i], 13, 'SerifSemi', col)
        if day in TERM:
            pg.text(x + 30, 56.5, TERM[day], 11, 'SerifReg', DARK, 'r')
        pg.text(x - 0.5, 40, '%d' % day, 34, 'Bodoni', col)
        for yy in (30, 21):
            pg.ink([(x, yy), (x + 30, yy)], 0.18, H_('#8E9692'))
    pg.lmark()


def skyline(pg, x, y, w):
    """整座城的正面剪影（單一深灰色塊）。"""
    gs = []
    for n, b in BUILT.items():
        if n == 1:
            continue
        px_, py_ = b['pos']
        g = b['shape'].intersection(box(-999, 0, 999, 999))
        gs.append(AF.translate(g, px_, (py_ + HF) * 0.22))
    u = unary_union(gs)
    k = w / (u.bounds[2] - u.bounds[0])
    u = AF.translate(AF.scale(u, k, k, origin=(u.bounds[0], u.bounds[1])), x - u.bounds[0], y - u.bounds[1])
    pg.gfill(u, DARK)


def page_cover(pg):
    pg.fill([(58, 20), (281, 20), (281, 194), (58, 194)], MIST)
    draw_base(pg, 169.5, 107)
    pg.text(30, 176, '台', 54, 'SerifSemi', ACC, 'c'); pg.text(30, 154, '北', 54, 'SerifSemi', ACC, 'c')
    pg.text(20, 136, '跟著日曆去旅行', 12, 'SerifSemi', INKC)
    pg.text(20, 128, '每週畫一點，', 12, 'SerifReg', DARK)
    pg.text(20, 121.5, '蓋一座台北', 12, 'SerifReg', DARK)
    pg.text(20, 46, '撥下・上色・插上', 11, 'SerifReg', DARK)
    pg.text(20, 33, '紙雕週曆', 13, 'SerifSemi', INKC, cs=1)
    skyline(pg, 20, 62, 33)
    pg.text(20, 20, '2027 · 3', 24, 'Bodoni', INKC)
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
    scene(path=os.path.join(PREV, '正面組裝預覽_線稿.png'), bg=(220, 226, 223), wall=(250, 248, 244))
    scene(path=os.path.join(PREV, '給Gemini上色_組裝線稿.png'), bg=(255, 255, 255), wall=(255, 255, 255))
    fc, fp = [os.path.join(OUT, n) for n in ('台北週曆_切割檔.pdf', '台北週曆_印刷檔.pdf')]
    make('cut', fc); make('print', fp)
    check(fc)
    names = ['週曆_0_封面與底座', '週曆_1_第一週', '週曆_2_第二週', '週曆_3_第三週', '週曆_4_第四週']
    ims = []
    for i, pgx in enumerate(pymupdf.open(fp)):
        pm = pgx.get_pixmap(dpi=150); p = os.path.join(PREV, names[i] + '.png'); pm.save(p)
        ims.append(Image.open(p).convert('RGB'))
    fr = Image.open(os.path.join(PREV, '正面組裝預覽_線稿.png'))
    w, h = ims[0].size; g = 36
    sheet = Image.new('RGB', (w * 3 + g * 4, h * 2 + g * 3), (196, 198, 196))
    for i, t in enumerate([fr] + ims):
        t2 = t.copy(); t2.thumbnail((w, h))
        sheet.paste(t2, (g + (i % 3) * (w + g) + (w - t2.width) // 2, g + (i // 3) * (h + g) + (h - t2.height) // 2))
    try:
        sheet.save(os.path.join(PREV, '整套總覽.png'))
    except OSError:
        sheet.save(os.path.join(PREV, '整套總覽_新.png')); print('整套總覽.png 被占用，另存為 整套總覽_新.png')
    tot = sum(CUTLEN.values())
    info_ = dict(頁面='A4 橫式 297×210 mm，共 5 頁', 月份='2027 年 3 月', 底座='六角對邊 120、牆高 12',
                 每頁切線長度mm={str(k): round(v) for k, v in CUTLEN.items()}, 切線總長mm=round(tot), 校內費用元=round(tot * 0.03),
                 零件={str(n): dict(名稱=b['label'], 寬=round(b['w'], 1), 高=round(b['maxy'], 1)) for n, b in BUILT.items()})
    json.dump(info_, open(os.path.join(ROOT, '尺寸.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('切線總長 %d mm，校內約 %d 元' % (tot, tot * 0.03))
