"""從 AI素材圖/ 抽出 8 件零件：去背（含白色貼紙邊與卡榫）→ 零件/N_名稱.png（RGBA，300dpi 以像素計）＋ info.json
順序依檔案修改時間 0..7＝夜市、捷運、紅樓、迪化街、龍山寺(半)、總統府、象山、101"""
import os, glob, json
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
NAMES = ['夜市', '捷運', '紅樓', '迪化街', '龍山寺', '總統府', '象山', '101']
fs = sorted(glob.glob(os.path.join(ROOT, 'AI素材圖', '*.jpg')), key=os.path.getmtime)
OUT = os.path.join(HERE, '零件'); os.makedirs(OUT, exist_ok=True)
info = {}
for i, f in enumerate(fs):
    im = Image.open(f).convert('RGB'); a = np.asarray(im).astype(float)
    g = a.mean(axis=2)
    bgest = np.asarray(Image.fromarray(g.astype('uint8')).filter(ImageFilter.GaussianBlur(120))).astype(float)
    # 背景：四角附近的平滑估計；內容 = 與背景差距大，或比背景更亮(白邊)
    diff = np.abs(g - np.median(g[:40, :40]))
    sat = a.max(axis=2) - a.min(axis=2)
    content = (diff > 14) | (sat > 18)
    content = ndi.binary_closing(content, iterations=3)
    # 白色貼紙邊：把內容膨脹到邊緣，再用「比背景亮」收緊
    dil = ndi.binary_dilation(content, iterations=26)
    white = g > (np.median(g[:40, :40]) + 3)
    m = dil & (white | content)
    m = ndi.binary_closing(m, iterations=5); m = ndi.binary_fill_holes(m)
    lab, n = ndi.label(m); sizes = ndi.sum(m, lab, range(1, n + 1)); k = 1 + int(np.argmax(sizes)); m = lab == k
    m = ndi.binary_opening(m, iterations=2)
    ys, xs = np.where(m); x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    rgba = np.dstack([a.astype('uint8'), (m * 255).astype('uint8')])[y0:y1, x0:x1]
    # 邊緣羽化 1px
    alpha = Image.fromarray(rgba[:, :, 3]).filter(ImageFilter.GaussianBlur(0.8)); rgba[:, :, 3] = np.asarray(alpha)
    Image.fromarray(rgba, 'RGBA').save(os.path.join(OUT, f'{i + 1}_{NAMES[i]}.png'))
    mm = m[y0:y1, x0:x1]; W, H = mm.shape[1], mm.shape[0]
    # 卡榫：由底往上，寬度小且穩定的列
    widths = mm.sum(axis=1); tw = widths[-3:].mean(); th = 0
    for r in range(H - 1, 0, -1):
        if widths[r] <= tw * 1.25: th += 1
        else: break
    info[NAMES[i]] = dict(file=f'{i + 1}_{NAMES[i]}.png', w=W, h=H, tab_w=float(tw), tab_h=th, src=os.path.basename(f))
    print(i + 1, NAMES[i], W, H, 'tab', round(tw), th)
json.dump(info, open(os.path.join(HERE, '零件', 'info.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
