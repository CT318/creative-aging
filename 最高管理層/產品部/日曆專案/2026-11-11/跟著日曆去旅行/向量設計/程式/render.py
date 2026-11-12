"""輸出：①每件 SVG 向量檔（mm 實寸）②底座 SVG（頂板、十字行道樹）③線稿總覽 PNG
④正面模擬（正立面、斜俯視）PNG——全部直接取自同一份幾何，尺寸比例完全一致。"""
import os, math, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import Polygon, LineString, MultiLineString, GeometryCollection
from shapely import affinity
from pieces import PIECES, TREES, build, p_tree, TAB_H

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SVG_DIR = os.path.join(ROOT, '向量檔'); PNG_DIR = os.path.join(ROOT, '預覽')
os.makedirs(SVG_DIR, exist_ok=True); os.makedirs(PNG_DIR, exist_ok=True)
FONT = 'C:/Windows/Fonts/msjh.ttc'; FONTB = 'C:/Windows/Fonts/msjhbd.ttc'

# 底座
F = 140.0; A = F / 2; R = A / math.cos(math.radians(30)); WALL = 14.0; SLOT_W = 0.8
def half_w(d):      # 深度 d（離前緣）處的底座半寬
    return R / 2 + d * math.tan(math.radians(30)) if d <= A else R - (d - A) * math.tan(math.radians(30))

OUT_W, IN_W = 0.6, 0.45   # 線寬 mm

def lines_of(g):
    if g.is_empty: return []
    if isinstance(g, LineString): return [list(g.coords)]
    if isinstance(g, (MultiLineString, GeometryCollection)):
        out = []
        for s in g.geoms: out += lines_of(s)
        return out
    if hasattr(g, 'exterior'):
        return [list(g.exterior.coords)] + [list(i.coords) for i in g.interiors]
    if hasattr(g, 'geoms'):
        out = []
        for s in g.geoms: out += lines_of(s)
        return out
    return []

def rings(shape):
    return lines_of(shape)

# ───────── SVG ─────────
def svg_piece(name, d, path, extra=None):
    m = 3
    minx, miny, maxx, maxy = d['shape'].bounds
    W, H = maxx - minx + 2 * m, maxy - miny + 2 * m
    tf = lambda x, y: (x - minx + m, maxy - y + m)
    def pth(coords, close):
        s = ' '.join(f'{"M" if i == 0 else "L"}{tf(x, y)[0]:.3f},{tf(x, y)[1]:.3f}' for i, (x, y) in enumerate(coords))
        return s + (' Z' if close else '')
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.2f}mm" height="{H:.2f}mm" viewBox="0 0 {W:.3f} {H:.3f}">',
           f'<!-- 旬常｜台北｜{name}　本體 {d["w"]:.1f} × {d["h"]:.1f} mm（不含卡榫）　單位 mm，列印 100% -->',
           '<g fill="none" stroke="#222" stroke-linejoin="round" stroke-linecap="round">']
    out.append(f'<path id="cut" stroke-width="{OUT_W}" d="{" ".join(pth(r, True) for r in rings(d["shape"]))}"/>')
    inner = ' '.join(pth(l, False) for l in lines_of(d['inner']))
    if inner: out.append(f'<path id="color-lines" stroke-width="{IN_W}" d="{inner}"/>')
    if d['tab_w']:
        x0, x1 = d['xc'] - d['tab_w'] / 2, d['xc'] + d['tab_w'] / 2
        out.append(f'<path id="tab-line" stroke="#999" stroke-width="0.3" stroke-dasharray="1.2 0.8" d="M{tf(x0,0)[0]:.3f},{tf(x0,0)[1]:.3f} L{tf(x1,0)[0]:.3f},{tf(x1,0)[1]:.3f}"/>')
    if extra: out += [e(tf) for e in extra]
    out += ['</g>', '</svg>']
    open(path, 'w', encoding='utf-8').write('\n'.join(out))

def base_top_svg(path, slots):
    """底座頂板（俯視）：外框割線、內框與淡水河（上色線）、插槽（紅）。前緣在下。"""
    m = 4; W, H = 2 * R + 2 * m, F + 2 * m
    tf = lambda x, d: (x + R + m, F - d + m)
    hexp = [(-R / 2, 0), (R / 2, 0), (R, A), (R / 2, F), (-R / 2, F), (-R, A)]
    def pp(pts, close=True): return ' '.join(f'{"M" if i == 0 else "L"}{tf(*p)[0]:.3f},{tf(*p)[1]:.3f}' for i, p in enumerate(pts)) + (' Z' if close else '')
    inset = Polygon(hexp).buffer(-5, join_style=2)
    river = river_poly().intersection(inset)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.2f}mm" height="{H:.2f}mm" viewBox="0 0 {W:.3f} {H:.3f}">',
         f'<!-- 旬常｜台北底座 頂板　六角對邊 {F:.0f} mm　前緣（平邊）朝下　紅＝插槽 {SLOT_W} mm -->',
         '<g fill="none" stroke="#222" stroke-linejoin="round" stroke-linecap="round">',
         f'<path stroke-width="{OUT_W}" d="{pp(hexp)}"/>',
         f'<path stroke-width="{IN_W}" d="{pp(list(inset.exterior.coords)[:-1])}"/>']
    for r_ in rings(river):
        s.append(f'<path stroke-width="{IN_W}" d="{pp(r_[:-1])}"/>')
    for (x0, x1, dd) in slots:
        s.append(f'<path stroke="#c0392b" stroke-width="0.3" fill="#c0392b" d="{pp([(x0, dd), (x1, dd), (x1, dd + SLOT_W), (x0, dd + SLOT_W)])}"/>')
    s += ['</g>', '</svg>']
    open(path, 'w', encoding='utf-8').write('\n'.join(s))

def river_poly():
    """淡水河：從左後方斜流到左側邊的帶狀河道（印在頂板，可上色）。"""
    pts_c = [(-R - 5, 52 + 0), (-60, 66), (-48, 84), (-30, 100), (-10, 112), (15, 122), (40, 132), (60, 150)]
    return LineString(pts_c).buffer(7, cap_style=2, join_style=1)

# ───────── 點陣預覽 ─────────
class Canvas:
    def __init__(self, x0, y0, x1, y1, ppm=8, ss=2, title=None):
        self.x0, self.y1, self.ppm, self.ss = x0, y1, ppm, ss
        self.W, self.H = int((x1 - x0) * ppm), int((y1 - y0) * ppm)
        self.top = 70 if title else 0
        self.img = Image.new('RGB', (self.W * ss, (self.H + self.top) * ss), (250, 247, 240))
        self.dr = ImageDraw.Draw(self.img); self.title = title
    def pt(self, x, y):
        return ((x - self.x0) * self.ppm * self.ss, ((self.y1 - y) * self.ppm + self.top) * self.ss)
    def poly(self, pts, fill=None, outline=None, w=0.5):
        q = [self.pt(*p) for p in pts]
        if fill: self.dr.polygon(q, fill=fill)
        if outline: self.dr.line(q + [q[0]], fill=outline, width=max(1, round(w * self.ppm * self.ss)), joint='curve')
    def line(self, pts, color=(34, 34, 34), w=0.45, dash=None):
        q = [self.pt(*p) for p in pts]
        if dash:
            for a, b in zip(q, q[1:]):
                L = math.dist(a, b); n = max(1, int(L / (dash * self.ppm * self.ss)))
                for k in range(0, n, 2):
                    t0, t1 = k / n, min(1, (k + 1) / n)
                    self.dr.line([(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0), (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)], fill=color, width=max(1, round(w * self.ppm * self.ss)))
        else:
            self.dr.line(q, fill=color, width=max(1, round(w * self.ppm * self.ss)), joint='curve')
    def text(self, x, y, s, size=11, color=(60, 60, 60), bold=False, anchor='mm', raw=False):
        f = ImageFont.truetype(FONTB if bold else FONT, size * self.ss)
        p = (x * self.ss, y * self.ss) if raw else self.pt(x, y)
        self.dr.text(p, s, font=f, fill=color, anchor=anchor)
    def save(self, path):
        if self.title:
            self.text(20, 24, self.title[0], 20, (40, 40, 40), True, 'lm', raw=True)
            self.text(20, 52, self.title[1], 12, (110, 110, 110), False, 'lm', raw=True)
        self.img.resize((self.img.width // self.ss, self.img.height // self.ss), Image.LANCZOS).save(path)

def draw_piece(cv, d, ox, oy, fill=(255, 255, 255), tab=False, sx=1.0):
    """把件畫到畫布：本體左下角 → (ox + (x-xc)*sx, oy + y)。sx 用於側向平面（十字插件的另一片）。"""
    shp = d['shape'] if tab else d['body']
    T = lambda pts: [(ox + (x - d['xc']) * sx, oy + y) for x, y in pts]
    for r_ in rings(shp)[:1]: cv.poly(T(r_), fill=fill)
    for r_ in rings(shp)[1:]: cv.poly(T(r_), fill=(250, 247, 240))
    for l in lines_of(d['inner']): cv.line(T(l), w=IN_W)
    for r_ in rings(shp): cv.line(T(r_), w=OUT_W)
    if tab and d['tab_w']:
        cv.line(T([(d['xc'] - d['tab_w'] / 2, 0), (d['xc'] + d['tab_w'] / 2, 0)]), color=(150, 150, 150), w=0.3, dash=1.2)

# ───────── 主程式 ─────────
def main():
    data = [(n, build(fn), dep, x) for n, fn, dep, x in PIECES]
    tree = build(p_tree)
    info = {}
    slots = []
    for i, (n, d, dep, x) in enumerate(data):
        svg_piece(n, d, os.path.join(SVG_DIR, f'{i + 1}_{n}.svg'))
        if d['tab_w']: slots.append((x - d['tab_w'] / 2 - 1, x + d['tab_w'] / 2 + 1, dep))
        info[n] = dict(本體寬=round(d['w'], 1), 本體高=round(d['h'], 1), 卡榫寬=d['tab_w'], 深度=dep, 中心x=x)
    # 十字行道樹：A 片從上方開槽、B 片從下方開槽；A 片有卡榫插底座
    th = tree['h']; tx = tree['xc']
    tA = build(lambda: (p_tree()[0], 8))
    svg_piece('行道樹A（十字插件）', tA, os.path.join(SVG_DIR, '9_行道樹A_上開槽.svg'),
              extra=[lambda tf: f'<path id="slot" stroke="#c0392b" stroke-width="0.3" d="M{tf(tx-.4,th)[0]:.3f},{tf(tx-.4,th)[1]:.3f} L{tf(tx-.4,th/2)[0]:.3f},{tf(tx-.4,th/2)[1]:.3f} L{tf(tx+.4,th/2)[0]:.3f},{tf(tx+.4,th/2)[1]:.3f} L{tf(tx+.4,th)[0]:.3f},{tf(tx+.4,th)[1]:.3f}"/>'])
    svg_piece('行道樹B（十字插件）', tree, os.path.join(SVG_DIR, '10_行道樹B_下開槽.svg'),
              extra=[lambda tf: f'<path id="slot" stroke="#c0392b" stroke-width="0.3" d="M{tf(tx-.4,0)[0]:.3f},{tf(tx-.4,0)[1]:.3f} L{tf(tx-.4,th/2)[0]:.3f},{tf(tx-.4,th/2)[1]:.3f} L{tf(tx+.4,th/2)[0]:.3f},{tf(tx+.4,th/2)[1]:.3f} L{tf(tx+.4,0)[0]:.3f},{tf(tx+.4,0)[1]:.3f}"/>'])
    for dep, x in TREES: slots.append((x - 4 - 1, x + 4 + 1, dep))
    base_top_svg(os.path.join(SVG_DIR, '11_底座頂板.svg'), slots)
    info['行道樹（兩片十字）'] = dict(本體寬=round(tree['w'], 1), 本體高=round(tree['h'], 1), 位置=TREES)
    info['底座'] = dict(六角對邊=F, 牆高=WALL, 前緣寬=round(R, 1), 最寬=round(2 * R, 1))

    # ── 線稿總覽（1:1 比例並排）
    cv = Canvas(0, -24, 545, 140, ppm=5, title=('台北八件＋十字行道樹　線稿總覽（未上色）', '同一比例尺排列；粗線＝外輪廓割線，細線＝上色分區線，灰虛線下方＝卡榫（插進底座）'))
    xcur, ybase, row_h = 6, 2, 0
    order = list(range(8))
    for i in order:
        n, d, dep, x = data[i]
        draw_piece(cv, d, xcur + (d['xc'] - d['minx']), ybase, tab=True)
        cv.text(xcur + d['w'] / 2, ybase - 11, f'{i + 1} {n}', 10, (60, 60, 60), True)
        cv.text(xcur + d['w'] / 2, ybase - 15.5 + 0, f'{d["w"]:.0f}×{d["h"]:.0f} mm', 8, (120, 120, 120))
        xcur += d['w'] + 8
    draw_piece(cv, tA, xcur + (tree['xc'] - tree['minx']), ybase, tab=True)
    cv.line([(xcur + tree['w'] / 2 - .4, th + ybase), (xcur + tree['w'] / 2 - .4, th / 2 + ybase)], color=(192, 57, 43), w=.4)
    cv.text(xcur + tree['w'] / 2, ybase - 11, '9 行道樹', 10, (60, 60, 60), True)
    cv.text(xcur + tree['w'] / 2, ybase - 15.5, '十字兩片', 8, (120, 120, 120))
    cv.save(os.path.join(PNG_DIR, '線稿總覽.png'))

    # ── 正面模擬
    for mode, kx, ky, fname, ttl in [('ortho', 0, 0, '正面模擬_正立面.png', '正立面（眼睛與底座同高，正前方看）'),
                                      ('oblique', 0.18, 0.32, '正面模擬_斜俯視.png', '斜俯視（正面平面不變形，只依深度往上、往右平移）')]:
        cv = Canvas(-R - 14, -14, R + 14 + F * kx, WALL + 135 + F * ky + 4, ppm=6,
                    title=(f'台北底座　{ttl}', f'與向量檔同尺寸：底座對邊 {F:.0f} mm、牆高 {WALL:.0f} mm；八件與行道樹皆以實際 mm 擺放，未上色'))
        P = lambda x, dd, y: (x + dd * kx, y + dd * ky)
        hexp = [(-R / 2, 0), (R / 2, 0), (R, A), (R / 2, F), (-R / 2, F), (-R, A)]
        # 頂面
        if ky:
            cv.poly([P(x, dd, WALL) for x, dd in hexp], fill=(244, 238, 226), outline=(34, 34, 34), w=OUT_W)
            inset = Polygon(hexp).buffer(-5, join_style=2)
            cv.line([P(x, dd, WALL) for x, dd in inset.exterior.coords], w=IN_W)
            for r_ in rings(river_poly().intersection(inset)):
                cv.line([P(x, dd, WALL) for x, dd in r_], w=IN_W)
        # 可見牆面（前、左前、右前）
        walls = [((-R / 2, 0), (R / 2, 0)), ((-R, A), (-R / 2, 0)), ((R / 2, 0), (R, A))]
        for (a, b) in walls:
            q = [P(a[0], a[1], 0), P(b[0], b[1], 0), P(b[0], b[1], WALL), P(a[0], a[1], WALL)]
            cv.poly(q, fill=(236, 228, 212), outline=(34, 34, 34), w=OUT_W)
            # 牆面花紋：淡水河波浪（上色線）
            n = max(2, int(math.dist(a, b) / 10))
            for row, yy in enumerate((4.5, 9.5)):
                pts = []
                for k in range(n * 8 + 1):
                    t = k / (n * 8); x = a[0] + (b[0] - a[0]) * t; dd = a[1] + (b[1] - a[1]) * t
                    pts.append(P(x, dd, yy + 1.4 * math.sin(2 * math.pi * (t * n + row * .5))))
                cv.line(pts, w=IN_W)
        # 件：由後往前畫
        items = [(dep, 'p', d, x) for n, d, dep, x in data] + [(dep, 't', tree, x) for dep, x in TREES]
        items.sort(key=lambda t: -t[0])
        for dep, kind, d, x in items:
            if kind == 't' and kx:
                # B 片（沿深度方向）以斜投影畫：寬度方向 → 深度
                T = lambda pts: [P(x, dep + (px - d['xc']), WALL + py) for px, py in pts]
                for r_ in rings(d['body'])[:1]: cv.poly(T(r_), fill=(252, 252, 250))
                for l in lines_of(d['inner']): cv.line(T(l), w=IN_W)
                for r_ in rings(d['body']): cv.line(T(r_), w=OUT_W)
            ox, oy = P(x, dep, WALL)
            draw_piece(cv, d, ox, oy)
        cv.save(os.path.join(PNG_DIR, fname))
        info[f'可見比例_{mode}'] = visibility(data, kx, ky)
    json.dump(info, open(os.path.join(ROOT, '尺寸與排位.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(info, ensure_ascii=False, indent=1))

def visibility(data, kx, ky, ppm=4):
    """各件被前面的件擋住後，剩下可見的面積比例。"""
    from PIL import ImageDraw as D
    W, H = int((2 * R + 40 + F * kx) * ppm), int((200 + F * ky) * ppm)
    def mask(d, x, dep):
        im = Image.new('1', (W, H), 0); dr = D.Draw(im)
        ox, oy = x + dep * kx, WALL + dep * ky
        q = [((ox + (px - d['xc']) + R + 20) * ppm, H - (oy + py) * ppm) for px, py in rings(d['body'])[0]]
        dr.polygon(q, fill=1); return np.array(im)
    ms = [(n, dep, mask(d, x, dep)) for n, d, dep, x in data]
    res = {}
    for n, dep, m in ms:
        front = np.zeros_like(m)
        for n2, dep2, m2 in ms:
            if dep2 < dep: front |= m2
        res[n] = f'{(m & ~front).sum() / m.sum() * 100:.0f}%'
    return res

if __name__ == '__main__':
    main()
