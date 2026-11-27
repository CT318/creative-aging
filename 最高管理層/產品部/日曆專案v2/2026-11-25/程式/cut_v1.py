"""日曆專案v2 台北週曆 A4 切割檔（簡化版）：紅＝切線（含撕線斷線），綠＝壓線，黑＝L 型對位線。"""
import cv2, numpy as np, sys, os
from scipy import ndimage
from skimage.morphology import skeletonize
from shapely.geometry import LineString, box
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from reportlab.pdfgen import canvas as RC
from reportlab.lib.units import mm
import pymupdf

ROOT = sys.argv[1]
OUT = os.path.join(ROOT, "2026-11-25", "切割檔")
os.makedirs(OUT, exist_ok=True)
PX = 10
SW, SH, BAR, OFFSET = 188, 155, 25, 2.5
TOP4 = 115
SHIFT = {1: 0, 2: (TOP4 - 90) / 3, 3: (TOP4 - 90) * 2 / 3, 4: TOP4 - 90}
AMIN = 60 * PX * PX          # 保留的區塊至少 60 mm²（小於就併入旁邊，只留看得出物件的輪廓）
MINLEN = 3.0                 # 壓線短於 3 mm 刪掉
PERF_CUT, PERF_GAP = 3.0, 1.0
PW, PH = 297, 210
OX, OY = (PW - SW) / 2, (PH - SH) / 2
EDGE = 0.8                   # 壓線離紙張外框至少 0.8 mm，不與切線相接
FONT = r"C:\Windows\Fonts\NotoSerifTC-VF.ttf"

WEEKS = [
    dict(n=1, f="週1.jpg", h=30,
         days=[("31", ""), ("1", ""), ("2", ""), ("3", ""), ("4", "立春"), ("5", "除夕"), ("6", "春節")]),
    dict(n=2, f="週2.webp", h=50, days=[(str(d), "") for d in range(7, 14)]),
    dict(n=3, f="週3.webp", h=70,
         days=[(str(d), "元宵" if d == 20 else "") for d in range(14, 21)]),
    dict(n=4, f="週4.webp", h=90, days=[(str(d), "") for d in range(21, 28)]),
]

# ---------- 圖：剪影、撕線、簡化輪廓 ----------
def trace_chains(sk):
    sk = sk.copy().astype(bool)
    H, W = sk.shape
    nb = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    ys, xs = np.nonzero(sk)
    pix = set(zip(ys.tolist(), xs.tolist()))
    deg = {p: sum((p[0] + dy, p[1] + dx) in pix for dy, dx in nb) for p in pix}
    used = set(); chains = []
    def walk(a, b):
        ch = [a, b]; used.add((a, b)); used.add((b, a))
        prev, cur = a, b
        while deg[cur] == 2:
            nxt = [(cur[0] + dy, cur[1] + dx) for dy, dx in nb if (cur[0] + dy, cur[1] + dx) in pix and (cur[0] + dy, cur[1] + dx) != prev]
            nxt = [q for q in nxt if (cur, q) not in used]
            if not nxt: break
            prev, cur = cur, nxt[0]; used.add((prev, cur)); used.add((cur, prev)); ch.append(cur)
        return ch
    for p in pix:
        if deg[p] != 2:
            for dy, dx in nb:
                q = (p[0] + dy, p[1] + dx)
                if q in pix and (p, q) not in used: chains.append(walk(p, q))
    for p in pix:
        for dy, dx in nb:
            q = (p[0] + dy, p[1] + dx)
            if q in pix and (p, q) not in used: chains.append(walk(p, q))
    return chains

def process(wk):
    g = cv2.imdecode(np.fromfile(os.path.join(ROOT, "2026-11-25", "線稿", wk["f"]), np.uint8), cv2.IMREAD_GRAYSCALE)
    W = SW * PX
    g = cv2.resize(g, (W, int(g.shape[0] * W / g.shape[1])), interpolation=cv2.INTER_AREA)
    ink = g < 140
    top = np.where(ink.any(1))[0].min()
    ink = ink[top: top + int((wk["h"] - OFFSET) * PX)]
    ink = np.vstack([np.zeros((int(OFFSET * PX) + 5, W), bool), ink])
    H = ink.shape[0]
    closed = cv2.morphologyEx(ink.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    ff = (1 - closed).astype(np.uint8) * 255
    m = np.zeros((H + 2, W + 2), np.uint8)
    for x in range(0, W, 20):
        if ff[0, x]: cv2.floodFill(ff, m, (x, 0), 128)
    sky = ff == 128
    sil = ~sky; sil[-1, :] = True
    k = int(OFFSET * PX) * 2 + 1
    big = cv2.dilate(sil.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    big = cv2.GaussianBlur(big.astype(np.float32), (0, 0), 8) > 0.5
    tear = []
    for x in range(0, W + 1, 5):
        col = np.where(big[:, min(x, W - 1)])[0]
        tear.append((x / PX, col.min() / PX))
    # 簡化：只保留大區塊，邊界＝物件輪廓
    n, lab = cv2.connectedComponents((~ink & ~sky).astype(np.uint8), connectivity=4)
    areas = np.bincount(lab.ravel(), minlength=n)
    keep = np.zeros_like(lab)
    keep[sky] = 1
    idx = 2
    for i in range(1, n):
        if areas[i] >= AMIN:
            keep[lab == i] = idx; idx += 1
    _, (iy, ix) = ndimage.distance_transform_edt(keep == 0, return_indices=True)
    full = keep[iy, ix]
    bd = np.zeros_like(ink)
    bd[:, :-1] |= full[:, :-1] != full[:, 1:]
    bd[:-1, :] |= full[:-1, :] != full[1:, :]
    sk = skeletonize(cv2.dilate(bd.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
    lines = []
    for ch in trace_chains(sk):
        pts = np.array([(x / PX, y / PX) for y, x in ch], np.float32)
        if len(pts) < 2: continue
        ap = cv2.approxPolyDP(pts.reshape(-1, 1, 2), 0.25, False).reshape(-1, 2)
        ls = LineString(ap)
        if ls.length >= MINLEN: lines.append(ls)
    return dict(H=H / PX, tear=tear, lines=lines)

# ---------- 文字轉外框 ----------
font = TTFont(FONT)
cmap = font.getBestCmap(); upm = font["head"].unitsPerEm
gs_cache = {}
def glyphset(wght):
    if wght not in gs_cache: gs_cache[wght] = font.getGlyphSet(location={"wght": wght})
    return gs_cache[wght]

class Collect(BasePen):
    def __init__(s, gs, f):
        super().__init__(gs); s.f = f; s.paths = []; s.cur = []
    def _moveTo(s, p): s.cur = [s.f(p)]
    def _lineTo(s, p): s.cur.append(s.f(p))
    def _curveToOne(s, a, b, c):
        p0 = s.cur[-1]; A, B, C = s.f(a), s.f(b), s.f(c)
        for t in np.linspace(0.125, 1, 8):
            u = 1 - t
            s.cur.append((u**3*p0[0]+3*u*u*t*A[0]+3*u*t*t*B[0]+t**3*C[0], u**3*p0[1]+3*u*u*t*A[1]+3*u*t*t*B[1]+t**3*C[1]))
    def _closePath(s):
        if len(s.cur) > 2: s.paths.append(s.cur + [s.cur[0]])
        s.cur = []
    _endPath = _closePath

def text_width(t, size, wght=400):
    gs = glyphset(wght)
    return sum(gs[cmap[ord(ch)]].width for ch in t) * size / upm

def text_paths(t, x, y, size, anchor="start", wght=400, spacing=0.0):
    """x, y：基線位置（mm，y 由上往下）。回傳封閉路徑串列。"""
    gs = glyphset(wght); sc = size / upm
    w = text_width(t, size, wght) + spacing * (len(t) - 1)
    if anchor == "middle": x -= w / 2
    out = []
    for ch in t:
        gn = cmap[ord(ch)]
        pen = Collect(gs, lambda p, x0=x: (x0 + p[0] * sc, y - p[1] * sc))
        gs[gn].draw(pen); out += pen.paths
        x += gs[gn].width * sc + spacing
    return out

def date_bar(wk):
    P = []   # (pts) 壓線
    P += text_paths("二月", 6.5, 19.0, 12.5, wght=600)
    w2 = text_width("二月", 12.5, 600)
    P += text_paths("一一六年", 6.5 + w2 + 1.6, 19.0, 3.0, spacing=0.4)
    P.append([(51, 5.5), (51, 21)])
    x0, cw = 55, (182 - 55) / 7
    for i, (wd, (d, note)) in enumerate(zip("日一二三四五六", wk["days"])):
        cx = x0 + cw * i + cw / 2
        P += text_paths(wd, cx, 8.0, 2.9, "middle")
        out = wk["n"] == 1 and i == 0
        P += text_paths(d, cx, 17.6, 6.0 if out else 9.5, "middle")
        if note: P += text_paths(note, cx, 22.3, 2.6, "middle")
    P.append([(7, 24.5), (181, 24.5)])
    return P

# ---------- 輸出 ----------
def to_page(x, y): return ((OX + x) * mm, (OY + SH - y) * mm)

def build(wk, r):
    cut, score = [], []
    cut.append([(0, 0), (SW, 0), (SW, SH), (0, SH), (0, 0)])
    y0 = SH - r["H"] - SHIFT[wk["n"]]
    tl = LineString([(x, y + y0) for x, y in r["tear"]])
    d = 1.0
    while d + PERF_CUT <= tl.length - 1.0:
        seg = [tl.interpolate(d + t) for t in np.linspace(0, PERF_CUT, 7)]
        cut.append([(p.x, p.y) for p in seg]); d += PERF_CUT + PERF_GAP
    clip = box(EDGE, EDGE, SW - EDGE, SH - EDGE)
    for ls in r["lines"]:
        g = LineString([(x, y + y0) for x, y in ls.coords]).intersection(clip)
        for part in getattr(g, "geoms", [g]):
            if part.geom_type == "LineString" and part.length >= MINLEN: score.append(list(part.coords))
    score += date_bar(wk)
    return cut, score

def draw_pdf(path, cut, score):
    c = RC.Canvas(path, pagesize=(PW * mm, PH * mm))
    total = {"cut": 0.0, "score": 0.0}
    for kind, segs, col in (("cut", cut, (1, 0, 0)), ("score", score, (0, 1, 0))):
        c.setStrokeColorRGB(*col); c.setLineWidth(0.1 * mm); c.setLineCap(1); c.setLineJoin(1)
        for pts in segs:
            total[kind] += LineString(pts).length
            p = c.beginPath(); p.moveTo(*to_page(*pts[0]))
            for q in pts[1:]: p.lineTo(*to_page(*q))
            c.drawPath(p, stroke=1, fill=0)
    c.setStrokeColorRGB(0, 0, 0); c.setLineWidth(0.3 * mm)
    p = c.beginPath(); p.moveTo(5 * mm, (PH - 5) * mm); p.lineTo(5 * mm, 5 * mm); p.lineTo((PW - 5) * mm, 5 * mm)
    c.drawPath(p, stroke=1, fill=0)
    c.save()
    return total

report = []
for wk in WEEKS:
    r = process(wk)
    cut, score = build(wk, r)
    pdf = os.path.join(OUT, f"週{wk['n']}_A4切割檔.pdf")
    t = draw_pdf(pdf, cut, score)
    doc = pymupdf.open(pdf)
    doc[0].get_pixmap(dpi=110).save(os.path.join(OUT, f"週{wk['n']}_預覽.png"))
    cols = {tuple(round(v, 3) for v in (dr.get("color") or ())) for dr in doc[0].get_drawings()}
    report.append(f"週{wk['n']}: 切線 {t['cut']:.0f} mm, 壓線 {t['score']:.0f} mm, 合計 {t['cut'] + t['score']:.0f} mm, 線色 {sorted(cols)}")
print("\n".join(report))
