"""日曆專案v2 台北週曆 A4 切割檔 v5（11-25 定）：只改切線——外框四邊與撕線都改成留點切線、留點 3.5 mm（0.8 實切會被切斷）；圖的虛線壓線與日期條單線壓線全部照 v2。
（v4 說明：留點加大到 3.5 mm；日期條回到 v2 的單線壓線。）
以下為 v3 說明：v3（11-25 試切後）：壓線看不出來 → 圖與文字全部改成「留點切線」（交會處與長線每 16 mm 留 0.8 mm 點，不會掉塊）；外框四邊也留點，切完仍連在 A4 上。
舊說明（v2）：線稿保留原細節（單線、平滑）、圖的壓線用虛線省錢、文字單線、輸出後逐項檢查規範。
紅＝切線（外框＋撕線斷線），綠＝壓線，黑＝L 型對位線。"""
import cv2, numpy as np, sys, os, itertools
from skimage.morphology import skeletonize
from shapely.geometry import LineString, box, Point
from shapely.strtree import STRtree
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from reportlab.pdfgen import canvas as RC
from reportlab.lib.units import mm
import pymupdf

ROOT = sys.argv[1]
OUT = os.path.join(ROOT, "2026-11-25", "切割檔_v5")
os.makedirs(OUT, exist_ok=True)
PX, PXL = 10, 20                 # 剪影用 10 px/mm，描線用 20 px/mm
SW, SH, BAR, OFFSET = 188, 155, 25, 2.5
TOP4 = 115
SHIFT = {1: 0, 2: (TOP4 - 90) / 3, 3: (TOP4 - 90) * 2 / 3, 4: TOP4 - 90}
MINLEN = 1.5                     # 圖的線短於 1.5 mm 刪掉
SPUR = 1.0                       # 骨架小分岔短於 1 mm 刪掉
DASH_ON, DASH_OFF = 2.0, 1.5     # 圖的壓線用虛線（約省 43%）
PERF_CUT, PERF_GAP = 3.0, 1.0    # 撕線斷線
PW, PH = 297, 210
OX, OY = (PW - SW) / 2, (PH - SH) / 2
EDGE = 0.8                       # 壓線離外框切線至少 0.8 mm
TEAR_CLEAR = 0.5                 # 壓線離撕線至少 0.5 mm
FONT = r"C:\Windows\Fonts\NotoSansTC-VF.ttf"   # 單線文字用無襯線骨架較乾淨

WEEKS = [
    dict(n=1, f="週1.jpg", h=30, days=[("31", ""), ("1", ""), ("2", ""), ("3", ""), ("4", "立春"), ("5", "除夕"), ("6", "春節")]),
    dict(n=2, f="週2.webp", h=50, days=[(str(d), "") for d in range(7, 14)]),
    dict(n=3, f="週3.webp", h=70, days=[(str(d), "元宵" if d == 20 else "") for d in range(14, 21)]),
    dict(n=4, f="週4.webp", h=90, days=[(str(d), "") for d in range(21, 28)]),
]
NB = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

def trace_chains(sk):
    ys, xs = np.nonzero(sk)
    pix = set(zip(ys.tolist(), xs.tolist()))
    deg = {p: sum((p[0] + dy, p[1] + dx) in pix for dy, dx in NB) for p in pix}
    used = set(); chains = []
    def walk(a, b):
        ch = [a, b]; used.add((a, b)); used.add((b, a)); prev, cur = a, b
        while deg[cur] == 2:
            nxt = [(cur[0] + dy, cur[1] + dx) for dy, dx in NB]
            nxt = [q for q in nxt if q in pix and q != prev and (cur, q) not in used]
            if not nxt: break
            prev, cur = cur, nxt[0]; used.add((prev, cur)); used.add((cur, prev)); ch.append(cur)
        return ch
    for p in [p for p in pix if deg[p] != 2] + list(pix):
        for dy, dx in NB:
            q = (p[0] + dy, p[1] + dx)
            if q in pix and (p, q) not in used: chains.append(walk(p, q))
    return chains, deg

def chains_to_lines(sk, scale, spur, minlen, smooth=5, eps=0.03):
    chains, deg = trace_chains(sk)
    out = []
    for ch in chains:
        L = len(ch) / scale
        ends = [deg.get(ch[0], 0), deg.get(ch[-1], 0)]
        if L < spur and (1 in ends) and max(ends) >= 3: continue        # 小分岔
        pts = np.array([(x / scale, y / scale) for y, x in ch], np.float64)
        if len(pts) >= smooth * 2:
            k = np.ones(smooth) / smooth
            sm = np.column_stack([np.convolve(np.pad(pts[:, i], smooth // 2, mode="edge"), k, "valid") for i in (0, 1)])
            sm[0], sm[-1] = pts[0], pts[-1]
            pts = sm[:len(pts)]
        ap = cv2.approxPolyDP(pts.astype(np.float32).reshape(-1, 1, 2), eps, False).reshape(-1, 2)
        if len(ap) < 2: continue
        ls = LineString(ap)
        if ls.length >= minlen: out.append(ls)
    return out

def load(name, width_px):
    g = cv2.imdecode(np.fromfile(os.path.join(ROOT, "2026-11-25", "線稿", name), np.uint8), cv2.IMREAD_GRAYSCALE)
    return cv2.resize(g, (width_px, int(g.shape[0] * width_px / g.shape[1])), interpolation=cv2.INTER_CUBIC)

def crop(ink, scale, h):
    top = np.where(ink.any(1))[0].min()
    ink = ink[top: top + int((h - OFFSET) * scale)]
    return np.vstack([np.zeros((int(OFFSET * scale) + scale // 2, ink.shape[1]), bool), ink])

def process(wk):
    ink = crop(load(wk["f"], SW * PX) < 140, PX, wk["h"]); H, W = ink.shape
    closed = cv2.morphologyEx(ink.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    ff = (1 - closed).astype(np.uint8) * 255
    m = np.zeros((H + 2, W + 2), np.uint8)
    for x in range(0, W, 20):
        if ff[0, x]: cv2.floodFill(ff, m, (x, 0), 128)
    sil = ff != 128; sil[-1, :] = True
    k = int(OFFSET * PX) * 2 + 1
    big = cv2.dilate(sil.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    big = cv2.GaussianBlur(big.astype(np.float32), (0, 0), 8) > 0.5
    tear = [(x / PX, np.where(big[:, min(x, W - 1)])[0].min() / PX) for x in range(0, W + 1, 5)]
    # 描線：20 px/mm、原細節、單線
    ink2 = crop(load(wk["f"], SW * PXL) < 140, PXL, wk["h"])
    ink2 = cv2.morphologyEx(ink2.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)) > 0
    lines = chains_to_lines(skeletonize(ink2), PXL, SPUR, MINLEN)
    return dict(H=H / PX, tear=tear, lines=lines)

# ---------- 單線文字：字形填滿 → 骨架 ----------
font = TTFont(FONT); cmap = font.getBestCmap(); upm = font["head"].unitsPerEm
_gs = {}
def gset(w):
    if w not in _gs: _gs[w] = font.getGlyphSet(location={"wght": w})
    return _gs[w]
class Collect(BasePen):
    def __init__(s, gs, f): super().__init__(gs); s.f = f; s.paths = []; s.cur = []
    def _moveTo(s, p): s.cur = [s.f(p)]
    def _lineTo(s, p): s.cur.append(s.f(p))
    def _curveToOne(s, a, b, c):
        p0 = s.cur[-1]; A, B, C = s.f(a), s.f(b), s.f(c)
        for t in np.linspace(0.1, 1, 10):
            u = 1 - t
            s.cur.append((u**3*p0[0]+3*u*u*t*A[0]+3*u*t*t*B[0]+t**3*C[0], u**3*p0[1]+3*u*u*t*A[1]+3*u*t*t*B[1]+t**3*C[1]))
    def _closePath(s):
        if len(s.cur) > 2: s.paths.append(s.cur)
        s.cur = []
    _endPath = _closePath
def twidth(t, size, w=150, sp=0.0): return sum(gset(w)[cmap[ord(c)]].width for c in t) * size / upm + sp * (len(t) - 1)
def text_lines(t, x, y, size, anchor="start", w=150, sp=0.0):
    if anchor == "middle": x -= twidth(t, size, w, sp) / 2
    gs = gset(w); sc = size / upm; S = 60   # 60 px/mm
    polys = []
    for ch in t:
        pen = Collect(gs, lambda p, x0=x: (x0 + p[0] * sc, y - p[1] * sc)); gs[cmap[ord(ch)]].draw(pen)
        polys += pen.paths; x += gs[cmap[ord(ch)]].width * sc + sp
    allp = np.vstack(polys); x0, y0 = allp.min(0) - 1; x1, y1 = allp.max(0) + 1
    mask = np.zeros((int((y1 - y0) * S), int((x1 - x0) * S)), np.uint8)
    cv2.fillPoly(mask, [((np.array(p) - (x0, y0)) * S).astype(np.int32) for p in polys], 1)
    ls = chains_to_lines(skeletonize(mask > 0), S, spur=size * 0.08, minlen=size * 0.05, smooth=7, eps=0.02)
    return [[(px + x0, py + y0) for px, py in l.coords] for l in ls]

def date_bar(wk):
    P = []
    P += text_lines("二月", 6.5, 19.0, 12.5, w=150)
    P += text_lines("一一六年", 6.5 + twidth("二月", 12.5, 150) + 1.6, 19.0, 3.0, sp=0.4)
    P.append([(51, 5.5), (51, 21)])
    x0, cw = 55, (182 - 55) / 7
    for i, (wd, (d, note)) in enumerate(zip("日一二三四五六", wk["days"])):
        cx = x0 + cw * i + cw / 2
        P += text_lines(wd, cx, 8.0, 2.9, "middle")
        out = wk["n"] == 1 and i == 0
        P += text_lines(d, cx, 17.6, 6.0 if out else 9.5, "middle")
        if note: P += text_lines(note, cx, 22.3, 2.6, "middle")
    P.append([(7, 24.5), (181, 24.5)])
    return P

def dashes(ls, on, off, start=0.0):
    out, d = [], start
    while d < ls.length:
        e = min(d + on, ls.length)
        if e - d >= 0.6:
            seg = [ls.interpolate(t) for t in np.linspace(d, e, max(2, int((e - d) / 0.25) + 1))]
            out.append([(p.x, p.y) for p in seg])
        d += on + off
    return out

BR_GAP, BR_SPACING = 3.5, 16.0   # 撕線：連續切線＋留點。留點寬同 v5（0.8 mm），密度約 v5 的 3 倍（每 16 mm 一個）
def bridged(ls):
    L = ls.length; n = max(1, round(L / BR_SPACING))
    def bend(s0):
        a, m_, c_ = [np.array(ls.interpolate(min(max(s0 + e, 0), L)).coords[0]) for e in (-1.5, 0, 1.5)]
        v1, v2 = m_ - a, c_ - m_
        return abs(v1[0] * v2[1] - v1[1] * v2[0])
    pos = [0.0]
    for i in range(1, n):
        tgt = i * L / n
        pos.append(min(np.arange(tgt - 4, tgt + 4.01, 0.5), key=lambda s0: bend(s0) + abs(s0 - tgt) * 0.01))
    pos.append(L)
    segs = []
    for a, b in zip(pos[:-1], pos[1:]):
        a2, b2 = a + BR_GAP if a == 0 else a + BR_GAP / 2, b - BR_GAP if b == L else b - BR_GAP / 2
        pts = [ls.interpolate(t) for t in np.linspace(a2, b2, max(2, int((b2 - a2) / 0.25) + 1))]
        segs.append([(q.x, q.y) for q in pts])
    return segs

FRAME_SPACING = 40.0             # 外框留點：約每 40 mm 一個（每邊至少 2 個），避開四角
JOIN = 0.25                      # 線端離其他線 < 0.25 mm 視為交會，要留點
TXT_GAP = 0.5                    # 文字筆畫交會處留點較小（字很小）

def frame_bridged():
    sides = []; segs = []
    for (x0, y0), (x1, y1) in [((0, 0), (SW, 0)), ((SW, 0), (SW, SH)), ((SW, SH), (0, SH)), ((0, SH), (0, 0))]:
        L = np.hypot(x1 - x0, y1 - y0); n = max(2, round(L / FRAME_SPACING))
        cuts = [0.0] + [L * (i + 0.5) / n for i in range(n)] + [L]   # 留點在每段中央，不在角上
        for i in range(len(cuts) - 1):
            a = cuts[i] + (0 if i == 0 else BR_GAP / 2); b = cuts[i + 1] - (0 if i == len(cuts) - 2 else BR_GAP / 2)
            pa = (x0 + (x1 - x0) * a / L, y0 + (y1 - y0) * a / L); pb = (x0 + (x1 - x0) * b / L, y0 + (y1 - y0) * b / L)
            segs.append([pa, pb])
        sides.append(segs); segs = []
    # 四角：把相鄰兩邊在角落的段合併成 L 型一筆（角不留點、不相接）
    out = []
    for k in range(4):
        out += sides[k][1:-1]
        out.append(sides[k][-1] + sides[(k + 1) % 4][0][1:])
    return out

def tabbed(lines, gap, spacing, minseg):
    """開放線：只在『碰到別條線的端點』留點（避免圍出封閉塊）；封閉線至少一個點；長線每 spacing 再留一個。"""
    geoms = [LineString(l) if not isinstance(l, LineString) else l for l in lines]
    tree = STRtree(geoms); out = []
    for i, g in enumerate(geoms):
        L = g.length
        closed = Point(g.coords[0]).distance(Point(g.coords[-1])) < JOIN
        def joined(pt):
            return any(j != i and geoms[j].distance(pt) < JOIN for j in tree.query(pt.buffer(JOIN)))
        s0 = gap if (closed or joined(Point(g.coords[0]))) else 0.0
        s1 = L - gap if (closed or joined(Point(g.coords[-1]))) else L
        if s1 - s0 < minseg: continue
        n = max(1, round((s1 - s0) / spacing)); pos = np.linspace(s0, s1, n + 1)
        for k in range(n):
            a = pos[k] + (0 if k == 0 else gap / 2); b = pos[k + 1] - (0 if k == n - 1 else gap / 2)
            if b - a < minseg: continue
            pts = [g.interpolate(t) for t in np.linspace(a, b, max(2, int((b - a) / 0.25) + 1))]
            out.append([(q.x, q.y) for q in pts])
    return out

def build(wk, r):
    cut = frame_bridged()
    y0 = SH - r["H"] - SHIFT[wk["n"]]
    tl = LineString([(x, y + y0) for x, y in r["tear"]])
    frame = box(0, 0, SW, SH).exterior
    cut += [c for c in bridged(LineString(list(tl.coords))) if LineString(c).distance(frame) >= 0.5]
    keep = box(EDGE, EDGE, SW - EDGE, SH - EDGE).difference(tl.buffer(TEAR_CLEAR))
    img = []
    for ls in r["lines"]:
        g = LineString([(x, y + y0) for x, y in ls.coords]).intersection(keep)
        for part in getattr(g, "geoms", [g]):
            if part.geom_type == "LineString" and part.length >= MINLEN: img.append(part)
    score = []
    for part in img: score += dashes(part, DASH_ON, DASH_OFF)   # 圖：照 v2 虛線壓線
    return cut, score + date_bar(wk)

def check(cut, score):
    """規範檢查：同色線不可重疊（相接可）；切線之間不可相接；壓線不可碰切線；全部在紙邊 10 mm 內側。"""
    issues = []
    G = [("cut", LineString(c)) for c in cut] + [("score", LineString(s)) for s in score]
    geoms = [g for _, g in G]; tree = STRtree(geoms)
    for i, (ki, gi) in enumerate(G):
        for j in tree.query(gi.buffer(0.05)):
            if j <= i: continue
            kj, gj = G[j]
            inter = gi.intersection(gj)
            if inter.length > 0.01: issues.append(f"重疊 {ki}/{kj} 長 {inter.length:.2f}")
            elif ki == "cut" and kj == "cut" and gi.distance(gj) < 0.2: issues.append(f"切線太近 {gi.distance(gj):.2f}")
            elif ki != kj and gi.distance(gj) < 0.3: issues.append(f"壓線太靠近切線 {gi.distance(gj):.2f}")
    for k, g in G:
        if g.length < 1e-6: issues.append("零長度線")
    allb = np.array([g.bounds for g in geoms])
    if OX + allb[:, 0].min() < 10 or OX + allb[:, 2].max() > PW - 10 or OY + allb[:, 1].min() < 10 or OY + allb[:, 3].max() > PH - 10:
        issues.append("離紙邊不足 10 mm")
    return issues

def to_page(x, y): return ((OX + x) * mm, (OY + SH - y) * mm)
def draw_pdf(path, cut, score):
    c = RC.Canvas(path, pagesize=(PW * mm, PH * mm)); tot = {"cut": 0.0, "score": 0.0}
    for kind, segs, col in (("cut", cut, (1, 0, 0)), ("score", score, (0, 1, 0))):
        c.setStrokeColorRGB(*col); c.setLineWidth(0.1 * mm); c.setLineCap(1); c.setLineJoin(1)
        for pts in segs:
            tot[kind] += LineString(pts).length
            p = c.beginPath(); p.moveTo(*to_page(*pts[0]))
            for q in pts[1:]: p.lineTo(*to_page(*q))
            c.drawPath(p, stroke=1, fill=0)
    c.setStrokeColorRGB(0, 0, 0); c.setLineWidth(0.3 * mm)
    p = c.beginPath(); p.moveTo(5 * mm, (PH - 5) * mm); p.lineTo(5 * mm, 5 * mm); p.lineTo((PW - 5) * mm, 5 * mm)
    c.drawPath(p, stroke=1, fill=0); c.save()
    return tot

if __name__ == "__main__":
    for f in os.listdir(OUT): os.remove(os.path.join(OUT, f))
    lines_out = []
    for wk in WEEKS:
        r = process(wk); cut, score = build(wk, r)
        pdf = os.path.join(OUT, f"週{wk['n']}_A4切割檔.pdf"); t = draw_pdf(pdf, cut, score)
        doc = pymupdf.open(pdf); pg = doc[0]
        pg.get_pixmap(dpi=110).save(os.path.join(OUT, f"週{wk['n']}_預覽.png"))
        pg.get_pixmap(dpi=300, clip=pymupdf.Rect(OX * 2.835, (OY + 0) * 2.835, (OX + SW) * 2.835, (OY + SH) * 2.835)).save(os.path.join(OUT, f"週{wk['n']}_預覽_放大.png"))
        cols = sorted({tuple(round(v, 3) for v in (d.get("color") or ())) for d in pg.get_drawings()})
        iss = check(cut, score)
        lines_out.append(f"W{wk['n']} cut={t['cut']:.0f} score={t['score']:.0f} total={t['cut'] + t['score']:.0f} colors={cols} issues={len(iss)} {iss[:5]}")
    open(os.path.join(OUT, "_check.txt"), "w", encoding="utf-8").write("\n".join(lines_out))
    print("\n".join(lines_out))
