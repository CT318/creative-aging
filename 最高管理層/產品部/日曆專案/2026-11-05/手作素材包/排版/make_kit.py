"""手作素材包草模，兩款造型：①螺旋　②放射螺旋。每款輸出一個 PDF：
  p1 六角盒展開圖（盒底＝引導線版，盒底與牆同色）　p2-3 素材六角層（含摺線，素材片有立體感）　p4 完成示範　p5 做到一半
單位 mm。用法：python make_kit.py"""
import os, math
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('JH', 'C:/Windows/Fonts/msjh.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('JHB', 'C:/Windows/Fonts/msjhbd.ttc', subfontIndex=0))
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '輸出')
os.makedirs(OUT, exist_ok=True)


def H(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))


# 配色（平面設計考量）：深藍灰底，搭暖調的珊瑚、淡粉、鼠尾草綠、芥黃，奶油白當花心與亮點；麻線用暖米色
BASEC = H('#2F4B63')
CORAL, BLUSH, SAGE, MUSTARD, CREAM, THREAD = map(H, ['#E9866D', '#F4C7BA', '#A6BE98', '#E6B450', '#F6EBD4', '#EBD9B0'])
GUIDE = (.58, .70, .79)
LIGHT = (.93, .88, .75)
BOX_F, BOX_D = 140.0, 22.0       # 六角盒對邊、深（沒有上蓋）
BOARD_F = 136.0                  # 盒底內放的底板／素材層對邊


def darker(col, k=.62):
    return tuple(v * k for v in col)


def make_design(name):
    """回傳 dict(pcs, arms)。pcs 每片 (x, y, L, Wd, ang, kind, col, label)；arms＝各條路徑的片索引（麻線沿著走）。"""
    pcs, arms = [], []
    if name == 'spiral':
        n = 42
        pos = []
        for i in range(n):
            t = i / (n - 1)
            r = 9 + 52 * t
            th = -math.pi / 2 + t * 3.4 * 2 * math.pi
            pos.append((r * math.cos(th), r * math.sin(th), th))
        for i in range(n):
            t = i / (n - 1)
            petal = i % 2 == 0
            col = ((CORAL, BLUSH) if petal else (SAGE, MUSTARD))[(i // 2) % 2]
            L = 8 + 10 * t
            ang = math.degrees(pos[i][2]) + 90 + 12
            pcs.append((pos[i][0], pos[i][1], L, L * (.5 if petal else .36), ang, 'petal' if petal else 'leaf', col, str(i + 1)))
        arms.append(list(range(n)))
    else:
        A, P = 6, 8
        for a in range(A):
            pos = []
            for j in range(P):
                t = j / (P - 1)
                r = 12 + 50 * t ** .95
                th = math.radians(-90 + 60 * a) + math.radians(125) * t
                pos.append((r * math.cos(th), r * math.sin(th)))
            idx = []
            for j in range(P):
                t = j / (P - 1)
                nx, ny = pos[min(j + 1, P - 1)]
                px, py = pos[max(j - 1, 0)]
                ang = math.degrees(math.atan2(ny - py, nx - px))
                L = 9 + 11 * t
                petal = j % 2 == 0
                col = ((CORAL if a % 2 == 0 else BLUSH) if petal else (SAGE if a % 2 == 0 else MUSTARD))
                idx.append(len(pcs))
                pcs.append((pos[j][0], pos[j][1], L, L * (.5 if petal else .36), ang, 'petal' if petal else 'leaf', col, f'{"ABCDEF"[a]}{j + 1}'))
            arms.append(idx)
    return dict(pcs=pcs, arms=arms)


def shape(c, kind, L, Wd):
    p = c.beginPath()
    if kind == 'leaf':
        p.moveTo(-L / 2 * mm, 0)
        p.curveTo(-L / 4 * mm, Wd * .75 * mm, L / 4 * mm, Wd * .75 * mm, L / 2 * mm, 0)
        p.curveTo(L / 4 * mm, -Wd * .75 * mm, -L / 4 * mm, -Wd * .75 * mm, -L / 2 * mm, 0)
    else:
        p.moveTo(-L / 2 * mm, 0)
        p.curveTo(-L / 1.9 * mm, Wd * 1.05 * mm, L / 6 * mm, Wd * 1.0 * mm, L / 2 * mm, 0)
        p.curveTo(L / 6 * mm, -Wd * 1.0 * mm, -L / 1.9 * mm, -Wd * 1.05 * mm, -L / 2 * mm, 0)
    p.close()
    return p


def draw_piece(c, x, y, L, Wd, ang, kind, fill=None, w=.35, dash=None, stroke=None, crease=False):
    """fill 有色＝上色片（沿中脈一半較深，呈現摺起的立體感）；crease＝畫摺線與膠點（素材層用）。"""
    c.saveState()
    c.translate(x * mm, y * mm)
    c.rotate(ang)
    c.setDash(*(dash or ([], 0)))
    c.setLineWidth(w)
    if fill is not None:
        c.setFillColorRGB(*fill)
        c.drawPath(shape(c, kind, L, Wd), stroke=0, fill=1)
        if fill != (1, 1, 1):
            c.saveState()
            c.clipPath(shape(c, kind, L, Wd), stroke=0, fill=0)
            c.setFillColorRGB(*darker(fill, .84))
            c.rect(-L / 2 * mm, -Wd * mm, L * mm, Wd * mm, stroke=0, fill=1)
            c.restoreState()
        c.setStrokeColorRGB(*(stroke or darker(fill, .55)))
        c.drawPath(shape(c, kind, L, Wd), stroke=1, fill=0)
    else:
        c.setStrokeColorRGB(*(stroke or GUIDE))
        c.drawPath(shape(c, kind, L, Wd), stroke=1, fill=0)
    if crease:
        c.setStrokeColorRGB(.15, .3, .7)
        c.setLineWidth(.3)
        c.setDash(1.2, .9)
        c.line(-L * .4 * mm, 0, L * .45 * mm, 0)
        c.setDash([], 0)
        c.setFillColorRGB(.15, .3, .7)
        c.circle(-L * .36 * mm, 0, .7 * mm, stroke=0, fill=1)
    elif fill is not None and fill != (1, 1, 1):
        c.setStrokeColorRGB(*darker(fill, .7))
        c.setLineWidth(.25)
        c.setDash([], 0)
        c.line(-L * .4 * mm, 0, L * .4 * mm, 0)
    c.restoreState()


def hexpts(cx, cy, F, rot=0):
    R = F / math.sqrt(3)
    return [(cx + R * math.cos(math.radians(60 * k + rot)), cy + R * math.sin(math.radians(60 * k + rot))) for k in range(6)]


def poly(c, pts, stroke, fill=None, w=.4, dash=None):
    c.setStrokeColorRGB(*stroke)
    c.setLineWidth(w)
    c.setDash(*(dash or ([], 0)))
    if fill:
        c.setFillColorRGB(*fill)
    p = c.beginPath()
    p.moveTo(pts[0][0] * mm, pts[0][1] * mm)
    for x, y in pts[1:]:
        p.lineTo(x * mm, y * mm)
    p.close()
    c.drawPath(p, stroke=1, fill=1 if fill else 0)


def text(c, x, y, s, size=9, font='JH', rgb=(.3, .3, .35)):
    c.saveState()
    c.setFillColorRGB(*rgb)
    c.setFont(font, size)
    c.drawCentredString(x * mm, y * mm, s)
    c.restoreState()


def thread(c, cx, cy, D, counts, w=1.1):
    c.saveState()
    c.setStrokeColorRGB(*THREAD)
    c.setLineWidth(w)
    c.setLineCap(1)
    for arm, cnt in zip(D['arms'], counts):
        if cnt <= 0:
            continue
        p = c.beginPath()
        p.moveTo(cx * mm, cy * mm)
        for i in arm[:cnt]:
            p.lineTo((cx + D['pcs'][i][0]) * mm, (cy + D['pcs'][i][1]) * mm)
        c.drawPath(p, stroke=1, fill=0)
    c.restoreState()


def rings(c, cx, cy, F):
    pts = hexpts(cx, cy, F, 0)
    for sc in (.38, .7):
        poly(c, [(cx + (x - cx) * sc, cy + (y - cy) * sc) for x, y in pts], (.40, .55, .66), w=.25, dash=([1, 1.4], 0))


def guide(c, cx, cy, D, F):
    """盒底上的引導：六角淡虛線、麻線路徑、素材片虛線輪廓＋編號、起點。"""
    rings(c, cx, cy, F)
    c.saveState()
    c.setStrokeColorRGB(*GUIDE)
    c.setLineWidth(.4)
    c.setDash(1.2, 1.6)
    for arm in D['arms']:
        p = c.beginPath()
        p.moveTo(cx * mm, cy * mm)
        for i in arm:
            p.lineTo((cx + D['pcs'][i][0]) * mm, (cy + D['pcs'][i][1]) * mm)
        c.drawPath(p, stroke=1, fill=0)
    c.restoreState()
    for i, (x, y, L, Wd, a, k, col, lab) in enumerate(D['pcs']):
        draw_piece(c, cx + x, cy + y, L, Wd, a, k, None, .35, ([1, 1], 0))
        text(c, cx + x, cy + y - 1, lab, 5, 'JH', GUIDE)
    c.setStrokeColorRGB(*GUIDE)
    c.setDash(1, 1.4)
    c.circle(cx * mm, cy * mm, 6 * mm, stroke=1, fill=0)
    c.setDash([], 0)
    text(c, cx, cy - 1.2, '起點', 6.5, 'JH', GUIDE)


def board(c, cx, cy, D, mode):
    """mode: full 完成示範 / half 做到一半"""
    F = BOARD_F
    poly(c, hexpts(cx, cy, F, 0), (.2, .3, .4), fill=BASEC, w=.6)
    rings(c, cx, cy, F)
    pcs = D['pcs']
    N = len(pcs)
    n_col = N if mode == 'full' else int(N * .55)
    n_white = 0 if mode == 'full' else int(N * .1)
    thread(c, cx, cy, D, [sum(1 for i in arm if i < n_col) for arm in D['arms']])
    c.setLineWidth(.3)
    c.setFillColorRGB(*CORAL)
    c.setStrokeColorRGB(*darker(CORAL, .6))
    c.circle(cx * mm, cy * mm, 6 * mm, stroke=1, fill=1)
    c.setFillColorRGB(*CREAM)
    c.circle(cx * mm, cy * mm, 3 * mm, stroke=1, fill=1)
    for i, (x, y, L, Wd, a, k, col, lab) in enumerate(pcs):
        if i < n_col:
            draw_piece(c, cx + x, cy + y, L, Wd, a, k, col, .3)
        elif i < n_col + n_white:
            draw_piece(c, cx + x, cy + y, L, Wd, a, k, (1, 1, 1), .45, stroke=(.15, .15, .2))
        else:
            draw_piece(c, cx + x, cy + y, L, Wd, a, k, None, .35, ([1, 1], 0))
    if mode == 'half':
        text(c, cx, cy - F / 2 - 6, '做到一半：先做的已貼好，白色的等著自己上色，虛線的還沒貼', 8, 'JH')


def piece_h(L, Wd, kind):
    return Wd * (1.5 if kind == 'petal' else 1.1)


def hex_sheet(c, cx, cy, items, paper, extra):
    """素材六角層：一張紙層（大小＝底板），素材片實際大小整齊排好，帶摺線與膠點。"""
    F = BOARD_F
    poly(c, hexpts(cx, cy, F, 0), (.3, .35, .4), fill=paper, w=.6)
    R = F / math.sqrt(3)
    A = F / 2
    GAP = 3.4
    its = sorted(items, key=lambda t: (-piece_h(t[0], t[1], t[2]), -t[0]))
    rows = []
    i = 0
    ytop = A - 16
    ycur = ytop
    while i < len(its):
        rh = piece_h(*its[i][:3])
        yext = max(abs(ycur), abs(ycur - rh))
        avail = 2 * (R - yext / math.sqrt(3)) - 22
        row, w = [], 0
        while i < len(its) and (not row or w + its[i][0] + GAP <= avail):
            row.append(its[i])
            w += its[i][0] + GAP
            i += 1
        rows.append((ycur - rh / 2, row, w - GAP))
        ycur -= rh + GAP
    ext_h = 24
    off = -((ytop + (ycur - ext_h)) / 2)
    for ym, row, w in rows:
        x = -w / 2
        for (L, Wd, kind, col) in row:
            draw_piece(c, cx + x + L / 2, cy + ym + off, L, Wd, 0, kind, col, .35)
            x += L + GAP
    ye = ycur + off - ext_h / 2 + GAP
    if extra == 'flower':
        c.setLineWidth(.35)
        c.setFillColorRGB(*CORAL)
        c.setStrokeColorRGB(*darker(CORAL, .6))
        c.circle((cx - 9) * mm, (cy + ye) * mm, 6 * mm, stroke=1, fill=1)
        c.setFillColorRGB(*CREAM)
        c.setStrokeColorRGB(.6, .55, .45)
        c.circle((cx - 9) * mm, (cy + ye) * mm, 3 * mm, stroke=1, fill=1)
        c.circle((cx + 9) * mm, (cy + ye) * mm, 3 * mm, stroke=1, fill=1)
    else:
        c.setStrokeColorRGB(*THREAD)
        c.setLineWidth(1.1)
        for r_ in (7.5, 6, 4.5, 3):
            c.circle(cx * mm, (cy + ye) * mm, r_ * mm, stroke=1, fill=0)


def box_page(c, D, title):
    """六角盒展開圖：盒底（翻過來＝畫布）印引導線；底與六面牆、膠耳同一個深藍。沒有上蓋。"""
    cx, cy = 148.5, 105
    base = hexpts(cx, cy, BOX_F, 0)
    R = BOX_F / math.sqrt(3)
    poly(c, base, LIGHT, fill=BASEC, w=.5)
    for k in range(6):
        A, B = base[k], base[(k + 1) % 6]
        nang = math.radians(60 * k + 30)
        n = (math.cos(nang), math.sin(nang))
        t = ((B[0] - A[0]) / R, (B[1] - A[1]) / R)
        A2 = (A[0] + n[0] * BOX_D, A[1] + n[1] * BOX_D)
        B2 = (B[0] + n[0] * BOX_D, B[1] + n[1] * BOX_D)
        poly(c, [A, B, B2, A2], LIGHT, fill=BASEC, w=.5)
        poly(c, [B, B2, (B2[0] + t[0] * 5 - n[0] * 3, B2[1] + t[1] * 5 - n[1] * 3), (B[0] + t[0] * 5 + n[0] * 3, B[1] + t[1] * 5 + n[1] * 3)], LIGHT, fill=BASEC, w=.5)
        c.setStrokeColorRGB(*GUIDE)
        c.setLineWidth(.4)
        c.setDash(2, 1.5)
        c.line(A[0] * mm, A[1] * mm, B[0] * mm, B[1] * mm)
        c.setDash([], 0)
    guide(c, cx, cy, D, BOX_F)
    text(c, 148.5, 204, f'旬常｜手作素材包 {title} 六角盒展開圖（草模）', 13, 'JHB')
    text(c, 148.5, 3.5, '淺色實線＝割線　虛線＝摺線　側邊小耳＝膠面　貼在厚紙卡上再割　實際大小 100%', 7.5)
    text(c, 50, 10, f'對邊 {BOX_F:.0f} mm　深 {BOX_D:.0f} mm　無上蓋，翻過來盒底就是畫布', 7.5)
    c.showPage()


def build(name, title, fname):
    D = make_design(name)
    c = canvas.Canvas(os.path.join(OUT, fname), pagesize=(297 * mm, 210 * mm))
    box_page(c, D, title)
    petals = [(p[2], p[3], p[5], p[6]) for p in D['pcs'] if p[5] == 'petal']
    leaves = [(p[2], p[3], p[5], p[6]) for p in D['pcs'] if p[5] == 'leaf']
    for items, paper, extra, ttl, note in [
        (petals, H('#F7ECE6'), 'flower', '第 1 張：花瓣＋花心', ''),
        (leaves, H('#EDF1E4'), 'thread', '第 2 張：葉子＋麻線', '同心圓＝麻線')]:
        hex_sheet(c, 148.5, 104, items, paper, extra)
        text(c, 148.5, 202, f'旬常｜手作素材包 {title} 素材六角層 {ttl}（草模）', 14, 'JHB')
        text(c, 148.5, 196, f'對邊 {BOARD_F:.0f} mm，剛好放進六角盒　實際大小列印　{note}', 8.5)
        c.showPage()
    c.save()


if __name__ == '__main__':
    for f in os.listdir(OUT):
        os.remove(os.path.join(OUT, f))
    build('spiral', '螺旋款', '手作草模_螺旋款.pdf')
    build('radial', '放射螺旋款', '手作草模_放射螺旋款.pdf')
    print('ok')
