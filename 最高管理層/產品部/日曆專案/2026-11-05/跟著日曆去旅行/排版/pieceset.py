"""零件處理：讀 零件/N_名稱.png（extract.py 輸出）→ 依目標高度縮放 → 加白色貼紙邊、自製卡榫、割線虛線。單位 mm，300dpi。"""
import os
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__))
PPM = 300 / 25.4
NAMES = ['夜市', '捷運', '紅樓', '迪化街', '龍山寺', '總統府', '象山', '101']
FULL = ['夜市小吃攤', '捷運列車', '西門紅樓', '迪化街老街屋', '龍山寺', '總統府', '象山步道', '台北 101']
H_BODY = [45, 50, 52, 56, 60, 62, 62, 80]       # 本體高度 mm（不含卡榫）
TAB_H = 8.0
BORDER_MM = 1.2
_C = {}

def build(i):
    """i＝0..7。回傳 dict：img(RGBA 含卡榫與割線)、w、h、body_h(含白邊的本體高度 mm)、tab_w、tab_cx(相對左緣 mm)、mask_body"""
    if i in _C: return _C[i]
    im = Image.open(os.path.join(HERE, '零件', f'{i + 1}_{NAMES[i]}.png')).convert('RGBA')
    bb = im.getchannel('A').point(lambda v: 255 if v > 128 else 0).getbbox(); im = im.crop(bb)
    s = H_BODY[i] * PPM / im.height
    im = im.resize((round(im.width * s), round(H_BODY[i] * PPM)), Image.LANCZOS)
    r = round(BORDER_MM * PPM); pad = r + 6; tabh = round(TAB_H * PPM)
    W = im.width + 2 * pad; Hh = im.height + 2 * pad + tabh
    can = Image.new('RGBA', (W, Hh), (255, 255, 255, 0)); can.paste(im, (pad, pad))
    a = np.asarray(can.getchannel('A')) > 128
    body = ndi.binary_dilation(a, structure=ndi.generate_binary_structure(2, 1), iterations=1)
    dist = ndi.distance_transform_edt(~a); sticker = dist <= r
    sticker = ndi.binary_fill_holes(sticker)
    bottom = int(np.where(a.any(axis=1))[0].max()) + 1       # 本體(未含白邊)底緣
    sb = int(np.where(sticker.any(axis=1))[0].max()) + 1     # 含白邊底緣
    # 卡榫位置：在寬 tw 的滑動視窗中，選底緣平均最低（最貼近底部）的位置；卡榫由視窗內最高的底緣往下延伸，保證與本體相連
    colb = np.array([(np.where(sticker[:, x])[0].max() + 1) if sticker[:, x].any() else 0 for x in range(W)])
    tw_mm = float(min(24, max(14, round(im.width / PPM * 0.45)))); tw = round(tw_mm * PPM)
    best = None
    for x0_ in range(r, W - r - tw, 3):
        win = colb[x0_:x0_ + tw]
        if (win > 0).all():
            sc = win.mean() - 0.5 * (win.max() - win.min())
            if best is None or sc > best[0]: best = (sc, x0_)
    x0 = best[1]
    top_ = int(colb[x0:x0 + tw].min()) - 6
    tab = np.zeros_like(sticker); tab[top_:sb + tabh - 4, x0:x0 + tw] = True
    final = sticker | tab
    arr = np.asarray(can).copy()
    white_zone = final & ~a
    arr[white_zone] = (255, 255, 255, 255)
    arr[~final] = (255, 255, 255, 0)
    arr[final, 3] = 255
    # 半透明邊緣：原圖本體 alpha 柔邊保留
    soft = np.asarray(can.getchannel('A')).astype(float) / 255
    inner = a
    out = Image.fromarray(arr, 'RGBA')
    # 割線虛線（外緣內側 3px）
    er = ndi.binary_erosion(final, iterations=4)
    edge = final & ~er
    yy, xx = np.indices(edge.shape); dash = ((xx + yy) % 24) < 14
    arr2 = np.asarray(out).copy(); arr2[edge & dash] = (138, 118, 96, 255)
    # 卡榫左右兩邊與底邊的灰線
    tabline = (final & ~ndi.binary_erosion(final, iterations=2)) & (np.arange(Hh)[:, None] >= int(sb - 6))
    arr2[tabline & tab] = (150, 140, 130, 255)
    img = Image.fromarray(arr2, 'RGBA')
    d = dict(img=img, w=W / PPM, h=Hh / PPM, body_h=sb / PPM, tab_w=tw_mm, tab_cx=(x0 + tw / 2) / PPM,
             mask=final[:sb], body_px=sb)
    _C[i] = d
    return d
if __name__ == '__main__':
    for i in range(8):
        d = build(i); print(i + 1, NAMES[i], round(d['w'], 1), round(d['h'], 1), 'body', round(d['body_h'], 1), 'tab', d['tab_w'], round(d['tab_cx'], 1))
