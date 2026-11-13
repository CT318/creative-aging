"""台北 v2 輸出：線稿總覽、立體模擬（斜俯視）、切割檔 PDF（紅切／綠壓／黑 L）、印刷檔 PDF（上色線＋同位置 L）。
全部取自 shapes.py 同一份幾何，尺寸一致。"""
import os, math, json
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import Polygon, LineString, box
from shapely.ops import unary_union
from shapely import affinity
import shapes as S

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
PNG = os.path.join(ROOT, '預覽'); CUT = os.path.join(ROOT, '切割檔')
os.makedirs(PNG, exist_ok=True); os.makedirs(CUT, exist_ok=True)
FONT = 'C:/Windows/Fonts/msjh.ttc'; FONTB = 'C:/Windows/Fonts/msjhbd.ttc'

# ── 底座（六角，對邊 140）
F = 140.0; A = F / 2; R = A / math.cos(math.radians(30)); WALL = 14.0
INSET = 6.0; Ri = (A - INSET) / math.cos(math.radians(30)); U = Ri          # 背板每片寬＝內縮六角的邊長
HEX = [(-R / 2, 0), (R / 2, 0), (R, A), (R / 2, F), (-R / 2, F), (-R, A)]
BACK = [(-Ri, A), (-Ri / 2, F - INSET), (Ri / 2, F - INSET), (Ri, A)]       # 背板沿後三邊的折線（x, 深度）

# 名稱, 幾何函式, x, 深度
LAYOUT = [('1 小籠包', S.p_xlb, -30, 13), ('4 機車', S.p_scooter, 25, 17), ('6 歪腰郵筒', S.p_mail, -53, 60),
          ('5 夜市攤', S.p_stall, -4, 50), ('3 杜鵑花叢 A', S.p_azalea_a, 48, 46), ('7 老街屋', S.p_house, -21, 86), ('2 藍鵲與樹 A', S.p_magpie_a, 32, 96)]
CROSS = {'3 杜鵑花叢 A': ('3 杜鵑花叢 B', S.p_azalea_b, 0), '2 藍鵲與樹 A': ('2 藍鵲與樹 B', S.p_magpie_b, 44)}   # B 片名稱, 函式, 安裝高度

def lines_of(g):
    if g is None or g.is_empty: return []
    if g.geom_type == 'LineString': return [list(g.coords)]
    if g.geom_type == 'Polygon': return [list(g.exterior.coords)] + [list(i.coords) for i in g.interiors]
    if hasattr(g, 'geoms'):
        out = []
        for s in g.geoms: out += lines_of(s)
        return out
    return []

class Canvas:
    def __init__(s, x0, y0, x1, y1, ppm=6, ss=3, bg=(250, 248, 243), title=None):
        s.x0, s.y1, s.ppm, s.ss, s.title = x0, y1, ppm, ss, title
        s.top = 70 if title else 0
        s.img = Image.new('RGB', (int((x1 - x0) * ppm * ss), int(((y1 - y0) * ppm + s.top) * ss)), bg); s.dr = ImageDraw.Draw(s.img)
    def pt(s, x, y): return ((x - s.x0) * s.ppm * s.ss, ((s.y1 - y) * s.ppm + s.top) * s.ss)
    def poly(s, pts, fill): s.dr.polygon([s.pt(*p) for p in pts], fill=fill)
    def line(s, pts, color=(40, 40, 40), w=0.4):
        s.dr.line([s.pt(*p) for p in pts], fill=color, width=max(1, round(w * s.ppm * s.ss)), joint='curve')
    def text(s, x, y, t, size=11, color=(70, 70, 70), bold=False, anchor='mm', raw=False):
        f = ImageFont.truetype(FONTB if bold else FONT, size * s.ss)
        s.dr.text((x * s.ss, y * s.ss) if raw else s.pt(x, y), t, font=f, fill=color, anchor=anchor)
    def save(s, path):
        if s.title:
            s.text(20, 24, s.title[0], 20, (40, 40, 40), True, 'lm', raw=True); s.text(20, 52, s.title[1], 12, (110, 110, 110), False, 'lm', raw=True)
        s.img.resize((s.img.width // s.ss, s.img.height // s.ss), Image.LANCZOS).save(path)

OUT_W, IN_W = 0.55, 0.32
def draw(cv, d, T, fill=(255, 255, 255), tab=False, clip=None):
    shp = d['shape'] if tab else d['shape'].intersection(box(-999, 0, 999, 999))
    inner = d['inner']
    if clip is not None: shp = shp.intersection(clip); inner = inner.intersection(clip)
    polys = [shp] if shp.geom_type == 'Polygon' else [g for g in getattr(shp, 'geoms', []) if g.geom_type == 'Polygon']
    for pg in polys:
        cv.poly([T(*p) for p in pg.exterior.coords], fill)
    for l in lines_of(inner): cv.line([T(*p) for p in l], w=IN_W)
    for pg in polys: cv.line([T(*p) for p in pg.exterior.coords], w=OUT_W)

def backdrop_floor(u):
    """背板上的橫向位置 u → 底座上的 (x, 深度)。"""
    i = min(2, max(0, int(u // U))); t = (u - i * U) / U
    a, b = BACK[i], BACK[i + 1]
    return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t

def main():
    data = {n: S.build(fn()) for n, fn, x, dep in LAYOUT}
    for n, (nb, fnb, yo) in CROSS.items(): data[nb] = S.build(fnb())
    bd = S.build(S.p_backdrop(U)); data['8 群山背板'] = bd
    info = {n: dict(寬=round(d['w'], 1), 高=round(d['h'], 1)) for n, d in data.items()}

    # ── 線稿總覽
    order = ['1 小籠包', '4 機車', '6 歪腰郵筒', '3 杜鵑花叢 A', '3 杜鵑花叢 B', '5 夜市攤', '2 藍鵲與樹 A', '2 藍鵲與樹 B', '7 老街屋']
    cv = Canvas(0, -20, 300, 232, ppm=5, title=('台北 v2　線稿總覽（未上色）', '同一比例；粗線＝切割外形，細線＝印刷的上色線，底下方塊＝插進底座的卡榫，紅線＝十字插槽'))
    def place(n, x, y):
        d = data[n]; T = lambda px, py: (x + px - d['minx'], y + py)
        draw(cv, d, T, tab=True)
        if d['slot']:
            sx, side, yy = d['slot']
            y0, y1 = (yy, d['maxy']) if side == 'top' else (d['miny'], yy)
            cv.line([T(sx, y0), T(sx, y1)], color=(210, 50, 40), w=0.6)
        for fx in d['folds']: cv.line([T(fx, 0), T(fx, d['maxy'])], color=(40, 170, 70), w=0.5)
        cv.text(x + d['w'] / 2, y - 12.5, n, 10, (60, 60, 60), True); cv.text(x + d['w'] / 2, y - 16.5, f'{d["w"]:.0f}×{d["h"]:.0f} mm', 8, (130, 130, 130))
    x = 6
    for n in order[:5]: place(n, x, 150); x += data[n]['w'] + 9
    x = 6
    for n in order[5:]: place(n, x, 128 - 78 + 0); x += data[n]['w'] + 10
    place('8 群山背板', 20, -120 + 130 - 0) if False else None
    cv.save(os.path.join(PNG, '線稿總覽_零件.png'))
    cv = Canvas(0, -22, 240, 126, ppm=5, title=('台北 v2　8 群山背板（未上色）', f'三片各寬 {U:.1f} mm，綠線＝壓線（往前折 60°），沿六角底座後三邊插入，像盆地把城市包起來'))
    d = bd; T = lambda px, py: (8 + px, py)
    draw(cv, d, T, tab=True)
    for fx in d['folds']: cv.line([T(fx, -S.TAB_H * 0), T(fx, 118)], color=(40, 170, 70), w=0.5)
    cv.save(os.path.join(PNG, '線稿總覽_背板.png'))

    # ── 立體模擬（斜俯視）
    kx, ky = 0.26, 0.30
    Pj = lambda x, dep, y: (x + dep * kx, y + dep * ky)
    cv = Canvas(-R - 12, -10, R + 12 + F * kx, WALL + 122 + F * ky, ppm=6, title=('台北 v2　立體模擬（斜俯視）', f'與向量檔同尺寸：六角底座對邊 {F:.0f} mm；零件依實際位置擺放；群山背板沿後三邊環繞；未上色'))
    cv.poly([Pj(x, dd, WALL) for x, dd in HEX], (244, 238, 226)); cv.line([Pj(x, dd, WALL) for x, dd in HEX + HEX[:1]], w=OUT_W)
    for l in lines_of(top_deco()): cv.line([Pj(x, dd, WALL) for x, dd in l], w=IN_W, color=(120, 120, 120))
    for a, b in (((-R / 2, 0), (R / 2, 0)), ((-R, A), (-R / 2, 0)), ((R / 2, 0), (R, A))):
        q = [Pj(a[0], a[1], 0), Pj(b[0], b[1], 0), Pj(b[0], b[1], WALL), Pj(a[0], a[1], WALL)]
        cv.poly(q, (236, 228, 212)); cv.line(q + q[:1], w=OUT_W)
    # 背板：左、中、右三片
    for i in (0, 2, 1):
        clip = box(i * U, 0, (i + 1) * U, 999)
        def T(u, y):
            fx, fd = backdrop_floor(min(max(u, i * U), (i + 1) * U)); return Pj(fx, fd, WALL + y)
        draw(cv, bd, T, fill=(252, 252, 250), clip=clip)
    for i in (1, 2):
        fx, fd = BACK[i]; cv.line([Pj(fx, fd, WALL), Pj(fx, fd, WALL + bd['shape'].intersection(LineString([(i * U, 0), (i * U, 200)])).bounds[3])], w=IN_W, color=(120, 120, 120))
    # 零件：由後往前
    items = []
    for n, fn, x, dep in LAYOUT:
        d = data[n]
        items.append((dep, 1, n, d, x, None))
        if n in CROSS:
            nb, fnb, yo = CROSS[n]; b = data[nb]
            xs = x + d['slot'][0] - d['xc']                      # 插槽在底座上的 x
            items.append((dep + 0.01, 0, nb, b, xs, ('back', yo, dep)))
            items.append((dep - 0.01, 2, nb, b, xs, ('front', yo, dep)))
    items.sort(key=lambda t: (-t[0], t[1]))
    for dep, _, n, d, x, cross in items:
        if cross is None:
            draw(cv, d, lambda px, py, d=d, x=x, dep=dep: Pj(x + px - d['xc'], dep, WALL + py))
        else:
            side, yo, dep0 = cross; su = d['slot'][0]
            clip = box(su, -99, 999, 999) if side == 'back' else box(-999, -99, su, 999)
            draw(cv, d, lambda px, py, su=su, x=x, dep0=dep0, yo=yo: Pj(x, dep0 + (px - su), WALL + yo + py), clip=clip)
    cv.save(os.path.join(PNG, '立體模擬_斜俯視.png'))

    # ── 切割檔與印刷檔（A4 橫式）
    sheets = make_pdfs(data, order + ['8 群山背板'])
    info['切割檔'] = sheets
    info['底座'] = dict(六角對邊=F, 背板每片寬=round(U, 1), 背板內縮=INSET)
    json.dump(info, open(os.path.join(ROOT, '尺寸.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(info, ensure_ascii=False, indent=1))

def top_deco():
    """底座頂面的印刷線：前方斑馬線、左側淡水河。"""
    ls = [LineString([(x, 27), (x, 37)]) for x in range(-12, 20, 4)]
    hexp = Polygon(HEX).buffer(-4)
    river = [LineString(S.cr([(-70, 60), (-58, 52), (-52, 38), (-40, 30), (-36, 14), (-30, 2)])), LineString(S.cr([(-78, 78), (-66, 66), (-60, 50), (-48, 40), (-44, 22), (-39, 4)]))]
    return unary_union(ls + [r.intersection(hexp) for r in river])

# ───────── PDF ─────────
def gaps(coords, n, glen=0.8):
    """把封閉外形切成 n 段，段與段之間留 glen 的連接點（放在直的地方）。"""
    ring = LineString(coords); Ltot = ring.length
    def straight(s):
        a, b, c = (ring.interpolate((s + o) % Ltot) for o in (-1.6, 0, 1.6))
        v1 = (b.x - a.x, b.y - a.y); v2 = (c.x - b.x, c.y - b.y)
        return abs(math.atan2(v1[0] * v2[1] - v1[1] * v2[0], v1[0] * v2[0] + v1[1] * v2[1])) < math.radians(4)
    pos = []
    for i in range(n):
        s0 = Ltot * (i + 0.37) / n
        for off in [o * 0.5 for o in range(0, 60)]:
            hit = next((s for s in (s0 + off, s0 - off) if straight(s)), None)
            if hit is not None: pos.append(hit % Ltot); break
    pos.sort(); segs = []
    from shapely.ops import substring
    for i, p in enumerate(pos):
        a = p + glen / 2; b = pos[(i + 1) % len(pos)] - glen / 2
        if b < a: b += Ltot
        if b <= Ltot: segs.append(list(substring(ring, a, b).coords))
        else: segs.append(list(substring(ring, a, Ltot).coords) + list(substring(ring, 0, b - Ltot).coords)[1:])
    return segs if segs else [list(coords)]

def make_pdfs(data, names):
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    PW, PH, M, GAP = 297, 210, 12, 5
    # 簡單排版：由左到右、放不下換列、放不下換頁
    pages = [[]]; x = M; y = PH - M; rowh = 0
    for n in sorted(names, key=lambda n: -data[n]['shape'].bounds[3] + data[n]['shape'].bounds[1]):
        b = data[n]['shape'].bounds; w, h = b[2] - b[0], b[3] - b[1]
        if x + w > PW - M: x = M; y -= rowh + GAP; rowh = 0
        if y - h < M: pages.append([]); x = M; y = PH - M; rowh = 0
        pages[-1].append((n, x - b[0], y - h - b[1])); x += w + GAP; rowh = max(rowh, h)
    out = []
    for kind in ('切割', '印刷'):
        path = os.path.join(CUT, f'台北v2_{kind}檔.pdf'); c = canvas.Canvas(path, pagesize=(PW * mm, PH * mm))
        tot = 0
        for pg in pages:
            c.setLineJoin(1); c.setLineCap(1)
            c.setStrokeColorRGB(0, 0, 0); c.setLineWidth(0.1 * mm)       # 左下角 L 型對位線（切割檔與印刷檔同位置）
            p = c.beginPath(); p.moveTo(5 * mm, (PH - 5) * mm); p.lineTo(5 * mm, 5 * mm); p.lineTo((PW - 5) * mm, 5 * mm); c.drawPath(p)
            for n, ox, oy in pg:
                d = data[n]
                def poly(coords, close=False):
                    p = c.beginPath(); p.moveTo((coords[0][0] + ox) * mm, (coords[0][1] + oy) * mm)
                    for (px, py) in coords[1:]: p.lineTo((px + ox) * mm, (py + oy) * mm)
                    c.drawPath(p)
                if kind == '切割':
                    c.setStrokeColorRGB(1, 0, 0); c.setLineWidth(0.1 * mm)
                    ring = list(d['shape'].exterior.coords); per = LineString(ring).length; tot += per
                    for seg in gaps(ring, 2 if per < 130 else 3 if per < 260 else 5): poly(seg)
                    c.setStrokeColorRGB(0, 1, 0)
                    for fx in d['folds']:
                        ln = d['shape'].intersection(LineString([(fx, -50), (fx, 300)]))
                        poly([(fx, ln.bounds[1] + 0.6), (fx, ln.bounds[3] - 0.6)]); tot += ln.length
                else:
                    c.setStrokeColorRGB(0.25, 0.25, 0.25); c.setLineWidth(0.3 * mm)
                    for l in lines_of(d['inner']): poly(l)
            c.showPage()
        c.save(); out.append(dict(檔案=os.path.basename(path), 頁數=len(pages)))
        if kind == '切割': out[-1].update(切割總長_mm=round(tot), 校內費用_元=round(tot * 0.03))
    out.append({'各頁內容': [[n for n, _, _ in pg] for pg in pages]})
    return out

if __name__ == '__main__':
    main()
