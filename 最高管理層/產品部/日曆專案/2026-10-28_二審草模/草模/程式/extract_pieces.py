"""從 AI城市圖/ 取出每件零件：去背（含貼紙白邊）、去掉圖上自帶的卡榫、存成透明 PNG 到 ../圖/零件/。
輸出 info.json：每件的像素尺寸、卡榫寬。"""
import glob, os, json
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

SRC = '../AI城市圖'
OUT = '../圖/零件'
os.makedirs(OUT, exist_ok=True)
CITIES = {'台灣': '台北', '日本': '東京', '雪梨': '雪梨'}

def cutout(im):
    a = np.asarray(im.convert('RGB')).astype(int)
    nonbg = (255 - a.min(axis=2)) > 14
    b = Image.fromarray((nonbg * 255).astype('uint8')).filter(ImageFilter.MaxFilter(5))
    ImageDraw.floodfill(b, (0, 0), 128)
    m = np.asarray(b) != 128
    m = np.asarray(Image.fromarray((m * 255).astype('uint8')).filter(ImageFilter.MinFilter(5))) > 0
    return m

info = {}
for folder, city in CITIES.items():
    fs = sorted(glob.glob(f'{SRC}/{folder}/*.jpg'), key=os.path.getmtime)
    for i, f in enumerate(fs, 1):
        im = Image.open(f).convert('RGB')
        m = cutout(im)
        ys, xs = np.where(m)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        m = m[y0:y1, x0:x1]; arr = np.asarray(im)[y0:y1, x0:x1]
        widths = m.sum(axis=1)
        H, W = m.shape
        # 卡榫：從底部往上，寬度穩定的窄區；遇到寬度大幅變大處即為本體底
        tw = np.median(widths[-max(3, H // 40):])
        cut = H
        for y in range(H - 1, -1, -1):
            if widths[y] > tw * 1.5: cut = y + 1; break
        tab_h = H - cut
        body_w = widths[:cut].max()
        rgba = np.dstack([arr, (m * 255).astype('uint8')])[:cut]
        Image.fromarray(rgba, 'RGBA').save(f'{OUT}/{city}_{i}.png')
        info[f'{city}_{i}'] = dict(w=int(W), h=int(cut), body_w=int(body_w), tab_w=int(tw), tab_h=int(tab_h), src=os.path.basename(f))
        print(f'{city}_{i}: body {W}x{cut}px  tab {int(tw)}x{tab_h}px')
json.dump(info, open(f'{OUT}/info.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
