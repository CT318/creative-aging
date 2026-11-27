import cv2, numpy as np, base64, sys, os
from skimage.morphology import skeletonize, remove_small_objects

ROOT = sys.argv[1]            # 日曆專案v2
OUT = os.path.join(ROOT, "2026-11-25", "排版預覽")
os.makedirs(OUT, exist_ok=True)
PX = 10                       # px per mm
SW, SH, BAR = 188, 155, 25
TOP4 = 115
SHIFT = {1: 0, 2: (TOP4 - 90) / 3, 3: (TOP4 - 90) * 2 / 3, 4: TOP4 - 90}
OFFSET = 2.5                  # 撕線離輪廓 mm
WEEKS = [
    dict(n=1, name="第一週", sub="文湖線", f="週1.jpg", h=30,
         days=[("31", ""), ("1", ""), ("2", ""), ("3", ""), ("4", "立春"), ("5", "除夕"), ("6", "春節")]),
    dict(n=2, name="第二週", sub="迪化街．北門", f="週2.webp", h=50,
         days=[(str(d), "") for d in range(7, 14)]),
    dict(n=3, name="第三週", sub="總統府．圓山", f="週3.webp", h=70,
         days=[(str(d), "元宵" if d == 20 else "") for d in range(14, 21)]),
    dict(n=4, name="第四週", sub="台北一〇一", f="週4.webp", h=90,
         days=[(str(d), "") for d in range(21, 28)]),
]

def process(wk):
    g = cv2.imdecode(np.fromfile(os.path.join(ROOT, "2026-11-25", "線稿", wk["f"]), np.uint8), cv2.IMREAD_GRAYSCALE)
    W = SW * PX
    g = cv2.resize(g, (W, int(g.shape[0] * W / g.shape[1])), interpolation=cv2.INTER_AREA)
    ink = g < 140
    top = np.where(ink.any(1))[0].min()
    draw_h = int((wk["h"] - OFFSET) * PX)
    ink = ink[top: top + draw_h]                      # 直接裁掉下方，不變形
    ink = np.vstack([np.zeros((int(OFFSET * PX) + 5, W), bool), ink])
    H = ink.shape[0]
    # 天空：從上緣灌水，得到剪影
    closed = cv2.morphologyEx(ink.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    ff = (1 - closed).astype(np.uint8) * 255
    mask = np.zeros((H + 2, W + 2), np.uint8)
    for x in range(0, W, 20):
        if ff[0, x]: cv2.floodFill(ff, mask, (x, 0), 128)
    sky = ff == 128
    sil = ~sky
    sil[-1, :] = True
    # 撕線：剪影外擴 OFFSET 後平滑
    k = int(OFFSET * PX) * 2 + 1
    big = cv2.dilate(sil.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    big = cv2.GaussianBlur(big.astype(np.float32), (0, 0), 8) > 0.5
    tear = []
    for x in range(0, W, 5):
        col = np.where(big[:, x])[0]
        tear.append((x / PX, col.min() / PX if len(col) else H / PX))
    tear.append((SW, tear[-1][1]))
    # 內部線：填掉太小的封閉白區（< 5 mm 見方），再細線化，去掉短線
    sk = skeletonize(ink & sil)
    sk = remove_small_objects(sk, max_size=4 * PX, connectivity=2)
    return dict(H=H / PX, tear=tear, sk=sk)

def sk_png(sk, color):
    rgba = np.zeros((*sk.shape, 4), np.uint8)
    d = cv2.dilate(sk.astype(np.uint8), np.ones((2, 2), np.uint8)) > 0
    rgba[d] = (*color[::-1], 255)
    ok, buf = cv2.imencode(".png", rgba)
    return base64.b64encode(buf).decode()

SERIF = "'Noto Serif TC','Noto Serif HK',serif"
NUM = "'Noto Serif TC',serif"
INK = "#2b3a2f"

def date_bar(wk):
    s = []
    s.append(f'<text x="6.6" y="15.8" font-family="{SERIF}" font-size="10" font-weight="600" fill="{INK}">二月</text>')
    s.append(f'<text x="7" y="21.6" font-family="{SERIF}" font-size="3.2" letter-spacing="1.2" fill="{INK}">{wk["name"]}</text>')
    s.append(f'<line x1="44" y1="5" x2="44" y2="21.5" stroke="{INK}" stroke-width="0.25"/>')
    x0, cw = 48, (182 - 48) / 7
    for i, (w, (d, note)) in enumerate(zip("日一二三四五六", wk["days"])):
        cx = x0 + cw * i + cw / 2
        s.append(f'<text x="{cx:.2f}" y="7.6" text-anchor="middle" font-family="{SERIF}" font-size="2.9" fill="{INK}">{w}</text>')
        out = wk["n"] == 1 and i == 0
        size = 6 if out else 9.5
        fill = "#b9bfba" if out else INK
        s.append(f'<text x="{cx:.2f}" y="17.2" text-anchor="middle" font-family="{NUM}" font-size="{size}" fill="{fill}">{d}</text>')
        if note:
            s.append(f'<text x="{cx:.2f}" y="22.4" text-anchor="middle" font-family="{SERIF}" font-size="2.6" fill="{INK}">{note}</text>')
    s.append(f'<line x1="7" y1="{BAR - 0.5}" x2="181" y2="{BAR - 0.5}" stroke="{INK}" stroke-width="0.2"/>')
    return "".join(s)

def sheet_svg(wk, r, ox=0, oy=0):
    y0 = SH - r["H"] - SHIFT[wk["n"]]
    tear = " ".join(f"{x:.2f},{y + y0:.2f}" for x, y in r["tear"])
    img = sk_png(r["sk"], (40, 110, 60))
    return (f'<g transform="translate({ox},{oy})">'
            f'<rect x="0" y="0" width="{SW}" height="{SH}" fill="#fff" stroke="#bbb" stroke-width="0.3"/>'
            f'{date_bar(wk)}'
            f'<image href="data:image/png;base64,{img}" x="0" y="{y0:.2f}" width="{SW}" height="{r["H"]:.2f}"/>'
            f'<polyline points="{tear}" fill="none" stroke="#e00" stroke-width="0.35" stroke-dasharray="3 1"/>'
            f'</g>')

res = [process(w) for w in WEEKS]
for wk, r in zip(WEEKS, res):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{SW + 20}mm" height="{SH + 20}mm" viewBox="-10 -10 {SW + 20} {SH + 20}">'
           f'<rect x="-10" y="-10" width="{SW + 20}" height="{SH + 20}" fill="#f4f2ec"/>{sheet_svg(wk, r)}</svg>')
    open(os.path.join(OUT, f"週{wk['n']}_排版預覽.svg"), "w", encoding="utf-8").write(svg)

# 疊層預覽：四週撕完後從正面看（後層在下）
parts = []
for wk, r in reversed(list(zip(WEEKS, res))):
    y0 = SH - r["H"] - SHIFT[wk["n"]]
    poly = [(0, SH)] + [(x, y + y0) for x, y in r["tear"]] + [(SW, SH)]
    pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in poly)
    shade = {1: "#fffdf8", 2: "#f7f3ea", 3: "#efeadf", 4: "#e7e1d4"}[wk["n"]]
    parts.append(f'<polygon points="{pts}" fill="{shade}" stroke="#c44" stroke-width="0.3"/>'
                 f'<image href="data:image/png;base64,{sk_png(r["sk"], (40, 110, 60))}" x="0" y="{y0:.2f}" width="{SW}" height="{r["H"]:.2f}"/>')
stack = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{SW + 20}mm" height="{SH + 20}mm" viewBox="-10 -10 {SW + 20} {SH + 20}">'
         f'<rect x="-10" y="-10" width="{SW + 20}" height="{SH + 20}" fill="#dfe8ee"/>{"".join(parts)}'
         f'<rect x="5" y="{SH - 125}" width="{SW - 10}" height="120" fill="none" stroke="#555" stroke-width="10" stroke-opacity="0.35"/>'
         f'<text x="{SW / 2}" y="{SH - 134}" text-anchor="middle" font-family="{SERIF}" font-size="4" fill="#444">四週撕完後正面示意（灰框＝前框位置，背景本次不做）</text></svg>')
open(os.path.join(OUT, "疊層示意.svg"), "w", encoding="utf-8").write(stack)
print("ok", [round(r["H"], 1) for r in res])
