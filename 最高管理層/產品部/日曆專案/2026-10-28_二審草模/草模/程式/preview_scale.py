"""比例預覽：依目標高度／寬度上限換算成 mm，畫成『排成一列』與『前後疊起來（從正面看）』。"""
import json, sys
from PIL import Image, ImageDraw
info = json.load(open('../圖/零件/info.json', encoding='utf-8'))
HT = [45, 50, 60, 70, 75, 82, 90]; WMAX = 85; PX = 6   # 6 px / mm
def size_mm(k, i):
    d = info[f'{k}_{i}']; s = min(HT[i - 1] / d['h'], WMAX / d['w']); return d['w'] * s, d['h'] * s, s
for city in ['台北', '東京', '雪梨']:
    row = Image.new('RGB', (7 * 100 * PX // 1 + 20, 110 * PX), 'white'); d = ImageDraw.Draw(row)
    ov = Image.new('RGB', (110 * PX, 110 * PX), 'white')
    for i in range(7, 0, -1):
        im = Image.open(f'../圖/零件/{city}_{i}.png'); wmm, hmm, s = size_mm(city, i)
        im = im.resize((int(wmm * PX), int(hmm * PX)), Image.LANCZOS)
        ov.paste(im, ((110 * PX - im.width) // 2, 100 * PX - im.height), im)
        row.paste(im, ((i - 1) * 100 * PX + 50 * PX - im.width // 2, 100 * PX - im.height), im)
        d.text(((i - 1) * 100 * PX + 10, 10), f'{i}: {wmm:.0f}x{hmm:.0f}mm', fill='black')
        print(city, i, f'{wmm:.0f} x {hmm:.0f} mm  (dpi≈{25.4/ (1/s):.0f})' if False else f'{wmm:.0f} x {hmm:.0f} mm, {25.4/(1/s):.0f} dpi')
    row.save(f'../圖/_比例_{city}_一列.png'); ov.save(f'../圖/_比例_{city}_疊.png')
