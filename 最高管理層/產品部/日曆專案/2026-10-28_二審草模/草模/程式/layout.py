"""計算每座城市七件的插槽順序與錯落位置（正面看被前面擋住的比例最小）。"""
import numpy as np, itertools, json
from PIL import Image
from pieces import build, base_size
R = 57.735
def halfw(y): return R - abs(y) * 0.5774   # 平邊朝前（flat-top）六角：深度方向 ±50，左右最寬 ±57.7
def solve(city, order=None):
    P = {i: build(city, i) for i in range(1, 8)}
    if order is None:
        order = sorted(range(1, 8), key=lambda i: P[i]['body_h'])      # 矮→高
    S = 2  # px per mm
    masks = []
    for i in order:
        m = np.asarray(Image.fromarray((P[i]['mask'] * 255).astype('uint8')).resize((int(P[i]['w_mm'] * S), int(P[i]['h_mm'] * S)))) > 0
        masks.append(m)
    n = 7; Wc = 240
    def vis(offs):
        cover = np.zeros((int(100 * S), Wc * S), bool); res = []
        for k in range(n):
            m = masks[k]; h, w = m.shape; x = int((Wc / 2 + offs[k]) * S - w / 2); y = int(100 * S) - h
            reg = np.zeros_like(cover); reg[y:y + h, x:x + w] = m
            res.append((reg & ~cover).sum() / max(1, m.sum())); cover |= reg
        return res
    ys = [(k - 3) * 10.0 for k in range(n)]
    def ok(k, x):
        w = P[order[k]]['w_mm']; tw = P[order[k]]['tab_w']; cx = P[order[k]]['tab_cx'] - w / 2   # 卡榫相對零件中心
        slit_c = x + cx
        return abs(x) + w / 2 <= 56 and abs(slit_c) + (tw + 2) / 2 <= halfw(ys[k]) - 4
    offs = [(-10 if k % 2 == 0 else 10) for k in range(n)]
    for _ in range(8):
        for k in range(n):
            best = None
            for x in range(-40, 41, 2):
                if not ok(k, x): continue
                t = offs[:]; t[k] = x; v = vis(t); sc = (min(v), sum(v))
                if best is None or sc > best[0]: best = (sc, x)
            if best: offs[k] = best[1]
    v = vis(offs)
    slots = []
    for k, i in enumerate(order):
        w = P[i]['w_mm']; cx = P[i]['tab_cx'] - w / 2
        slots.append(dict(piece=i, slot=k + 1, y=ys[k], piece_cx=offs[k], slit_cx=offs[k] + cx, slit_len=P[i]['tab_w'] + 2, vis=round(v[k], 2),
                          w=round(w, 1), h=round(P[i]['body_h'], 1)))
    return P, slots
if __name__ == '__main__':
    res = {}
    for c in ['台北', '東京', '雪梨']:
        P, slots = solve(c, order=list(range(1, 8)) if c == '台北' else None); res[c] = slots
        print(c); [print(' ', s) for s in slots]
    json.dump(res, open('../圖/插槽配置.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
