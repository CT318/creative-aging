# -*- coding: utf-8 -*-
"""幾何工具、零件建構、水彩上色。單位 mm，y 向上，地面 y=0。"""
import numpy as np
from shapely.geometry import Polygon, LineString, Point, box, MultiPolygon, MultiLineString, GeometryCollection
from shapely.ops import unary_union, substring, linemerge
from shapely import affinity as AF
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter as gf

TAB_H = 8.0     # 卡榫高
SLOT_W = 0.5    # 十字插槽寬（紙厚＋餘隙，試切後調）
MIN_R = 0.75    # 最細 1.5 mm


def R(x, y, w, h, r=0):
    b = box(x, y, x + w, y + h)
    return b.buffer(-r).buffer(r, quad_segs=6) if r else b


def C(x, y, r):
    return Point(x, y).buffer(r, quad_segs=14)


def E(x, y, rx, ry, a=0):
    return AF.rotate(AF.scale(Point(x, y).buffer(1, quad_segs=14), rx, ry), a, origin=(x, y))


def P(*pts):
    return Polygon(pts)


def L(*pts):
    return LineString(pts)


def cr(pts, closed=False, n=10):
    p = np.array(pts, float)
    q = np.vstack([p[-1], p, p[0], p[1]]) if closed else np.vstack([p[0], p, p[-1]])
    out = []
    for i in range(len(q) - 3):
        p0, p1, p2, p3 = q[i:i + 4]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    if not closed:
        out.append(p[-1])
    return [tuple(v) for v in out]


def SP(pts, n=10):
    return Polygon(cr(pts, True, n)).buffer(0)


def SL(pts, n=10):
    return LineString(cr(pts, False, n))


def half(g, y, up=True):
    b = g.bounds
    return g.intersection(box(b[0] - 1, y, b[2] + 1, b[3] + 1) if up else box(b[0] - 1, b[1] - 1, b[2] + 1, y))


def rot(g, a, o=(0, 0)):
    return AF.rotate(g, a, origin=o)


def mv(g, dx, dy):
    return AF.translate(g, dx, dy)


def arch(xc, y0, w, hs, ):
    """拱：寬 w、直壁到 hs、上面半圓。"""
    return unary_union([box(xc - w / 2, y0, xc + w / 2, hs), C(xc, hs, w / 2)])


class Piece:
    def __init__(s, name, tabs=(), slot=None):
        s.name, s.items, s.cuts, s.tabs, s.slot = name, [], [], list(tabs), slot

    def f(s, g, c):
        s.items.append(('f', g, c)); return g

    def l(s, g):
        s.items.append(('l', g, None)); return g

    def cut(s, g):
        s.cuts.append(g)


def _polys(g):
    if g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    return [p for p in getattr(g, 'geoms', []) if isinstance(p, Polygon) and not p.is_empty]


def _lines(g):
    if g.is_empty:
        return []
    if isinstance(g, LineString):
        return [g]
    out = []
    for p in getattr(g, 'geoms', []):
        out += _lines(p)
    return out


def _jit(ln, seed, amp=0.0):
    return ln


def _jit_old(ln, seed, amp=0.05):
    """手繪感：線條加一點很小的平滑位移。"""
    if ln.length < 8:
        return ln
    n = max(3, int(ln.length / 0.8))
    pts = np.array([ln.interpolate(t, normalized=True).coords[0] for t in np.linspace(0, 1, n)])
    rng = np.random.default_rng(seed)
    off = gf(rng.standard_normal((n, 2)), (max(1.5, n / 8), 0)) if n > 6 else np.zeros((n, 2))
    if off.std() > 0:
        off = off / off.std() * amp
    return LineString(pts + off)


def build(pc):
    fills = [(g, c) for k, g, c in pc.items if k == 'f']
    body = unary_union([g for g, _ in fills]).buffer(0.8, join_style=2).buffer(-0.8 - MIN_R, join_style=2).buffer(MIN_R, join_style=2, mitre_limit=3)
    ps = sorted(_polys(body), key=lambda p: -p.area)
    if len(ps) > 1 and ps[1].area > 3:
        print('  ! %s 有分離碎片 %.1f mm2' % (pc.name, sum(p.area for p in ps[1:])))
    body = Polygon(ps[0].exterior, [r for r in ps[0].interiors if Polygon(r).buffer(-1.0).area > 6])
    for cg in pc.cuts:
        for h in _polys(cg.buffer(-0.6).buffer(0.6, quad_segs=6)):
            if h.area > 5:
                body = body.difference(h)
    shape = body
    for (x, w) in pc.tabs:
        t = P((x - w / 2, 0.4), (x - w / 2, -TAB_H + 1.5), (x - w / 2 + 1.5, -TAB_H),
              (x + w / 2 - 1.5, -TAB_H), (x + w / 2, -TAB_H + 1.5), (x + w / 2, 0.4))
        shape = shape.union(t)
    shape = shape.buffer(0.5, quad_segs=6).buffer(-0.5, join_style=2, mitre_limit=3)      # 內凹角 R0.5
    shape = sorted(_polys(shape), key=lambda p: -p.area)[0]
    shape0 = shape
    b = shape.bounds
    if pc.slot:
        kind, sx, sy = pc.slot
        if kind == 'top':
            shape = shape.difference(box(sx - SLOT_W / 2, sy, sx + SLOT_W / 2, b[3] + 1))
        else:
            shape = shape.difference(box(sx - SLOT_W / 2, b[1] - 1, sx + SLOT_W / 2, sy))
    ps = sorted(_polys(shape), key=lambda p: -p.area)
    shape = ps[0]
    # 可見色塊與內線
    inner = shape.buffer(-0.45)
    regions, lines, dl = [], [], []
    later = Polygon()
    for k, g, c in reversed(pc.items):
        if k == 'f':
            vis = unary_union(_polys(g.difference(later).intersection(shape0)))
            if not vis.is_empty:
                regions.append((vis, c))
                lines += _lines(vis.boundary.intersection(inner))
            later = later.union(g)
        else:
            dl += _lines(g.difference(later).intersection(inner))
    regions.reverse()
    m = unary_union(lines) if lines else GeometryCollection()
    m = linemerge(m) if not m.is_empty and m.geom_type != 'LineString' else m
    lines = [_jit(l, i) for i, l in enumerate(_lines(m)) if l.length > 0.5]
    b = shape.bounds
    md = unary_union(dl) if dl else GeometryCollection()
    dlines = [l for l in _lines(md) if l.length > 0.4]
    return dict(name=pc.name, shape0=shape0, shape=shape, regions=regions, lines=lines, dlines=dlines, tabs=pc.tabs, slot=pc.slot,
                minx=b[0], miny=b[1], maxx=b[2], maxy=b[3], w=b[2] - b[0], h=b[3], folds=[])


# ---------- 留點（連接點） ----------
def ring_with_gaps(ring, gap=0.8, n=None, avoid_below=0.3):
    ln = LineString(ring.coords)
    Pm = ln.length
    if n is None:
        n = 3 if Pm < 130 else 4 if Pm < 260 else 6
    cuts = []
    for i in range(n):
        tgt = (i + 0.37) * Pm / n
        best, bd = tgt, 1e9
        for d in np.arange(-9, 9.01, 0.75):
            s0 = (tgt + d) % Pm
            a, m_, c_ = [np.array(ln.interpolate((s0 + e) % Pm).coords[0]) for e in (-2.0, 0, 2.0)]
            v1, v2 = m_ - a, c_ - m_
            dev = abs(v1[0] * v2[1] - v1[1] * v2[0]) + (5 if m_[1] < avoid_below else 0) + abs(d) * 0.01
            if dev < bd:
                bd, best = dev, s0
        cuts.append(best)
    cuts.sort()
    segs = []
    for i in range(len(cuts)):
        a = cuts[i] + gap / 2
        bnd = cuts[(i + 1) % len(cuts)] - gap / 2
        if i == len(cuts) - 1:
            c1 = list(substring(ln, a, Pm).coords)
            c2 = list(substring(ln, 0, bnd).coords)
            segs.append(c1 + c2[1:])
        else:
            segs.append(list(substring(ln, a, bnd).coords))
    return segs


# ---------- 上色 ----------
def hexrgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])


PAPER = np.array([0.985, 0.975, 0.955])


def _mask(geom, bounds, s, ss=2):
    minx, miny, maxx, maxy = bounds
    W, H = int(round((maxx - minx) * s)), int(round((maxy - miny) * s))
    im = Image.new('L', (W * ss, H * ss), 0)
    d = ImageDraw.Draw(im)
    k = s * ss
    for p in _polys(geom):
        d.polygon([((x - minx) * k, (maxy - y) * k) for x, y in p.exterior.coords], fill=255)
        for r in p.interiors:
            d.polygon([((x - minx) * k, (maxy - y) * k) for x, y in r.coords], fill=0)
    return np.asarray(im.resize((W, H), Image.LANCZOS), float) / 255


INK = np.array([0x5A, 0x46, 0x36]) / 255


def paint(shape, regions, lines, s=10, seed=1, colored=True, pad=1.0, fade=0.0, outline=True, ink=None, lw=0.24, dlines=()):
    """線稿＋低彩度水彩平塗（色塊邊緣略深）。回傳 (RGBA, bounds)。"""
    b = shape.bounds
    bounds = (b[0] - pad, b[1] - pad, b[2] + pad, b[3] + pad)
    alpha = _mask(shape, bounds, s)
    H, W = alpha.shape
    rgb = np.ones((H, W, 3)) * PAPER
    if colored:
        for g, c in regions:
            m = _mask(g, bounds, s)
            if m.max() <= 0:
                continue
            col = hexrgb(c) if isinstance(c, str) else np.array(c)
            if fade:
                col = col + (1 - col) * fade
            ms = gf(m, 0.8)
            rim = np.clip(ms - gf(ms, s * 0.55), 0, 1)
            dens = 0.95 + 0.5 * rim
            layer = PAPER * (col[None, None, :] ** dens[..., None])
            rgb = rgb * (1 - ms[..., None]) + layer * ms[..., None]
    lim = Image.new('L', (W * 2, H * 2), 0)
    d = ImageDraw.Draw(lim)
    k = s * 2
    wd = max(2, int(round(lw * k)))
    for ln in lines:
        d.line([((x - bounds[0]) * k, (bounds[3] - y) * k) for x, y in ln.coords], fill=255, width=wd, joint='curve')
    for ln in dlines:
        d.line([((x - bounds[0]) * k, (bounds[3] - y) * k) for x, y in ln.coords], fill=200, width=max(1, int(round(0.13 * k))))
    if outline:
        wo = max(3, int(round(0.58 * k)))
        for p in _polys(shape):
            for r in [p.exterior] + list(p.interiors):
                d.line([((x - bounds[0]) * k, (bounds[3] - y) * k) for x, y in r.coords], fill=255, width=wo, joint='curve')
    lm = np.asarray(lim.resize((W, H), Image.LANCZOS), float) / 255
    a = 0.92 * lm[..., None]
    rgb = rgb * (1 - a) + (INK if ink is None else np.array(ink)) * a
    out = np.dstack([np.clip(rgb, 0, 1), alpha])
    return Image.fromarray((out * 255).astype(np.uint8), 'RGBA'), bounds
