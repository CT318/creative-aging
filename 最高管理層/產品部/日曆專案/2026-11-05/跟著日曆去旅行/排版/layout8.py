"""八件在 180 mm 六角底座（平邊朝前）上的排列：四排、每排約 2 件，爬山演算法讓前面不擋後面。
輸出 輸出/插槽配置.json 與 正面預覽圖。用法：python layout8.py"""
import os, json, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pieceset import build, NAMES, FULL, PPM
HERE = os.path.dirname(os.path.abspath(__file__))
F = 180.0; A = F / 2; R = A / math.cos(math.radians(30)); K = math.tan(math.radians(30))
ROWS = [[0, 1], [2, 3], [4, 5], [6, 7]]           # 由前到後
DEPTH = [26.0, 62.0, 98.0, 134.0]                 # 各排離前緣的深度 mm
ELEV = math.radians(25); S = 3                     # 相機俯角、px/mm
def HW(d): return R - abs(A - d) * (R / 2 / A) * 1.0
def hw(d):  # 平邊朝前六角：d=0 時半寬 R/2，d=A 時 R
    return R / 2 + (R / 2) * (1 - abs(A - d) / A) if False else (R / 2 + R / 2 * (min(d, 2 * A - d) / A))

def pieces():
    P = [build(i) for i in range(8)]
    return P
def body_img(i):
    d = build(i); return d['img'].crop((0, 0, d['img'].width, d['body_px']))

from functools import lru_cache
@lru_cache(maxsize=None)
def front_mask(i):
    d = build(i); m = np.asarray(body_img(i).getchannel('A')) > 128
    im = Image.fromarray((m * 255).astype('uint8')).resize((round(d['w'] * S), round(d['body_px'] / PPM * S)))
    return np.asarray(im) > 0

def place(i, x, depth, W, Y0):
    d = build(i); m = front_mask(i); h, w = m.shape
    sx = int(W / 2 + x * S - w / 2); by = int(Y0 - depth * math.sin(ELEV) * S); return m, sx, by - h

def visibility(order, xs, W=900, Hc=700, Y0=620):
    cover = np.zeros((Hc, W), bool); vis = {}
    for i in sorted(order, key=lambda k: depth_of(k)):           # 前→後
        m, sx, sy = place(i, xs[i], depth_of(i), W, Y0); h, w = m.shape
        reg = np.zeros_like(cover)
        y0, x0 = max(sy, 0), max(sx, 0); y1, x1 = min(sy + h, Hc), min(sx + w, W)
        reg[y0:y1, x0:x1] = m[y0 - sy:y1 - sy, x0 - sx:x1 - sx]
        vis[i] = (reg & ~cover).sum() / max(1, reg.sum()); cover |= reg
    return vis

ROW_OF = {i: r for r, row in enumerate(ROWS) for i in row}
def depth_of(i): return DEPTH[ROW_OF[i]]
def ok(i, x):
    d = build(i); dep = depth_of(i); tabc = x + (d['tab_cx'] - d['w'] / 2)
    return abs(tabc) + (d['tab_w'] + 2) / 2 <= hw(dep) - 8 and abs(x) + d['w'] / 2 <= hw(dep) - 3

def solve(seed=11, iters=1500, restarts=8):
    global ROW_OF
    gbest = None
    for rs in range(restarts):
        rnd = random.Random(seed + rs)
        ROW_OF = {i: r for r, row in enumerate(ROWS) for i in row}
        xs = {i: rnd.uniform(-40, 40) for i in range(8)}
        for i in range(8):
            while not ok(i, xs[i]): xs[i] = rnd.uniform(-30, 30)
        sc = lambda v: (min(v.values()), sum(v.values()))
        v = visibility(range(8), xs); cur = sc(v); best = v
        for it in range(iters):
            if False:           # 換排（停用：保持由矮到高由前到後）：兩件對調排別（高度差不太離譜才換）
                i, j = rnd.sample(range(8), 2)
                if ROW_OF[i] == ROW_OF[j]: continue
                ROW_OF[i], ROW_OF[j] = ROW_OF[j], ROW_OF[i]
                if not (ok(i, xs[i]) and ok(j, xs[j])): ROW_OF[i], ROW_OF[j] = ROW_OF[j], ROW_OF[i]; continue
                v = visibility(range(8), xs); s_ = sc(v)
                if s_ > cur: cur, best = s_, v
                else: ROW_OF[i], ROW_OF[j] = ROW_OF[j], ROW_OF[i]
                continue
            i = rnd.randrange(8); old = xs[i]; xs[i] = old + rnd.uniform(-14, 14)
            if not ok(i, xs[i]): xs[i] = old; continue
            v = visibility(range(8), xs); s_ = sc(v)
            if s_ > cur: cur, best = s_, v
            else: xs[i] = old
        if gbest is None or cur > gbest[0]: gbest = (cur, dict(xs), dict(ROW_OF), best)
    ROW_OF = gbest[2]
    return gbest[1], gbest[3]

def draw_preview(xs, shown, out, title='', extra_left=None):
    W, Hc, Y0 = 900, 700, 620
    img = Image.new('RGBA', (W, Hc), (250, 246, 236, 255)); d = ImageDraw.Draw(img)
    def P(x, dep, z=0): return (W / 2 + x * S, Y0 - dep * math.sin(ELEV) * S - z * math.cos(ELEV) * S)
    hexv = [(-R / 2, 0), (R / 2, 0), (R, A), (R / 2, 2 * A), (-R / 2, 2 * A), (-R, A)]
    top = [P(x, y) for x, y in hexv]
    d.polygon([P(-R / 2, 0), P(R / 2, 0), P(R / 2, 0, -12), P(-R / 2, 0, -12)], fill=(228, 220, 204, 255), outline=(150, 140, 120, 255))
    d.polygon([P(R / 2, 0), P(R, A), P(R, A, -12), P(R / 2, 0, -12)], fill=(214, 206, 190, 255), outline=(150, 140, 120, 255))
    d.polygon([P(-R / 2, 0), P(-R, A), P(-R, A, -12), P(-R / 2, 0, -12)], fill=(214, 206, 190, 255), outline=(150, 140, 120, 255))
    d.polygon(top, fill=(240, 234, 220, 255), outline=(150, 140, 120, 255))
    # 插槽
    for i in range(8):
        dd = build(i); dep = depth_of(i); xc = xs[i] + (dd['tab_cx'] - dd['w'] / 2); L = dd['tab_w'] + 2
        d.line([P(xc - L / 2, dep), P(xc + L / 2, dep)], fill=(120, 110, 100, 255), width=2)
    for i in sorted(range(8), key=lambda k: -depth_of(k)):
        if i not in shown: continue
        b = body_img(i); w = round(build(i)['w'] * S); h = round(b.height / PPM * S)
        b = b.resize((w, h), Image.LANCZOS); bx, by = P(xs[i], depth_of(i))
        img.alpha_composite(b, (int(bx - w / 2), int(by - h)))
    d.text((10, 8), title, fill=(60, 50, 40, 255))
    img.convert('RGB').save(out)

if __name__ == '__main__':
    xs, vis = solve()
    print({NAMES[i]: round(v, 2) for i, v in sorted(vis.items())})
    json.dump({'xs': {str(i): xs[i] for i in xs}, 'depth': {str(i): depth_of(i) for i in range(8)}, 'vis': {str(i): float(vis[i]) for i in vis}},
              open(os.path.join(HERE, '輸出', '插槽配置.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    draw_preview(xs, set(range(8)), os.path.join(HERE, '輸出', '預覽_正面_八件.png'), '8 pieces, base 180mm, front view (25deg)')
    draw_preview(xs, {0, 1, 2, 3}, os.path.join(HERE, '輸出', '預覽_正面_做到一半.png'), 'half-finished: pieces 1-4 inserted')
