"""正面黑線稿（給 Gemini 上色做產品圖）：三種狀態——①第一週還在 ②撕掉前兩週 ③四週都撕掉。"""
import sys, os
sys.argv = [sys.argv[0], sys.argv[1]]
import cut_v2 as C
from PIL import Image, ImageDraw, ImageFont
import numpy as np

OUT = os.path.join(C.ROOT, "2026-11-25", "產品圖", "正面線稿")
os.makedirs(OUT, exist_ok=True)
S = 12                      # px/mm
FW, FH, FB = 190, 130, 10   # 前框／背景
M = 12                      # 畫布邊距 mm
CW, CH = FW + 2 * M, C.SH + 2 * M
SX = (FW - C.SW) / 2        # 週曆在框內置中
LW = 3                      # 線寬 px（約 0.25 mm）
SERIF = r"C:\Windows\Fonts\NotoSerifTC-VF.ttf"

def P(x, y):                # x 由框左緣算；y 由桌面（底）往上算 → 畫布座標
    return ((M + x) * S, (M + C.SH - y) * S)

def font(size_mm, wght=400):
    f = ImageFont.truetype(SERIF, int(size_mm * S))
    try: f.set_variation_by_axes([wght])
    except Exception: pass
    return f

R = {wk["n"]: C.process(wk) for wk in C.WEEKS}
WK = {wk["n"]: wk for wk in C.WEEKS}

def sheet_y(n):             # 週曆座標（由上往下）→ 由底往上
    return lambda y: C.SH - y

def draw_lines(d, n, clip_poly=None):
    r = R[n]; y0 = C.SH - r["H"] - C.SHIFT[n]
    for ls in r["lines"]:
        pts = [P(SX + x, C.SH - (y + y0)) for x, y in ls.coords]
        d.line(pts, fill="black", width=LW, joint="curve")

def tear_poly(n):
    r = R[n]; y0 = C.SH - r["H"] - C.SHIFT[n]
    return [P(SX, 0)] + [P(SX + x, C.SH - (y + y0)) for x, y in r["tear"]] + [P(SX + C.SW, 0)]

def date_bar(d, n):
    wk = WK[n]; top = C.SH                     # 週曆上緣
    T = lambda x, y_from_top: P(SX + x, top - y_from_top)
    d.text(T(6.5, 19.0), "二月", font=font(12.5, 600), fill="black", anchor="ls")
    w2 = d.textlength("二月", font=font(12.5, 600)) / S
    d.text(T(6.5 + w2 + 1.6, 19.0), "一一六年", font=font(3.0), fill="black", anchor="ls")
    d.line([T(51, 5.5), T(51, 21)], fill="black", width=2)
    x0, cw = 55, (182 - 55) / 7
    for i, (wd, (dd, note)) in enumerate(zip("日一二三四五六", wk["days"])):
        cx = x0 + cw * i + cw / 2
        d.text(T(cx, 8.0), wd, font=font(2.9), fill="black", anchor="ms")
        out = n == 1 and i == 0
        d.text(T(cx, 17.6), dd, font=font(6.0 if out else 9.5), fill="#999" if out else "black", anchor="ms")
        if note: d.text(T(cx, 22.3), note, font=font(2.6), fill="black", anchor="ms")
    d.line([T(7, 24.5), T(181, 24.5)], fill="black", width=2)

def render(torn, name):
    im = Image.new("RGB", (int(CW * S), int(CH * S)), "white"); d = ImageDraw.Draw(im)
    # 背景板
    d.rectangle([P(0, FH), P(FW, 0)], fill="white", outline="black", width=LW)
    # 後層到前層
    for n in (4, 3, 2, 1):
        if n in torn:
            d.polygon(tear_poly(n), fill="white", outline="black", width=LW)
            draw_lines(d, n)
        else:
            d.rectangle([P(SX, C.SH), P(SX + C.SW, 0)], fill="white", outline="black", width=LW)
            draw_lines(d, n); date_bar(d, n)
    # 前框（四邊，中間鏤空）
    for box_ in ([0, FH, FW, FH - FB], [0, FB, FW, 0], [0, FH, FB, 0], [FW - FB, FH, FW, 0]):
        d.rectangle([P(box_[0], box_[1]), P(box_[2], box_[3])], fill="white")
    d.rectangle([P(0, FH), P(FW, 0)], outline="black", width=LW)
    d.rectangle([P(FB, FH - FB), P(FW - FB, FB)], outline="black", width=LW)
    im.save(os.path.join(OUT, name))

render(set(), "狀態1_第一週還在.png")
render({1, 2}, "狀態2_撕掉前兩週.png")
render({1, 2, 3, 4}, "狀態3_四週都撕掉.png")
print("ok")
