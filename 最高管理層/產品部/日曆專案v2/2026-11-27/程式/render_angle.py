"""2026-11-27 斜側黑線稿（給 Gemini 上色做產品圖）：三種狀態＋台北花磚前框＋3D 列印底座。
座標 mm：x 向右、y 向後、z 向上。月份包整組往後仰 A 度（底座展示區底面斜），後方垂直收納 12 個月。
用法：python render_angle.py <日曆專案v2 資料夾>"""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = sys.argv[1]
sys.path.insert(0, os.path.join(ROOT, "2026-11-25", "程式"))
sys.argv = [sys.argv[0], ROOT]
import cut_v2 as C
from PIL import Image, ImageDraw, ImageFont
import numpy as np

OUT = os.path.join(ROOT, "2026-11-27", "產品圖", "斜側線稿")
os.makedirs(OUT, exist_ok=True)
SERIF = r"C:\Windows\Fonts\NotoSerifTC-VF.ttf"

# ---------- 尺寸 ----------
A = math.radians(10)              # 後仰角（11-27 CEO：再平緩一點）
FW, FH, FB = 190, 130, 10         # 前框／背景
SX = (FW - C.SW) / 2
GAP = 20                          # 層距
AMP = math.sqrt(14 ** 2 - (GAP / 2) ** 2)   # 風琴摺每摺 14 mm → 往外凸出量
Y0 = 8                            # 前框底邊離底座前緣
ZF = 3 + 100 * math.sin(A) + 2    # 前框底邊高度（展示區最低處約 3）
LIP = 2                           # 側牆／前擋只比底面高 2 mm，不擋前框
X0, X1 = -14, FW + 14             # 底座外寬
YS0 = round(8 + 100 * math.cos(A) + 130 * math.sin(A)) + 4   # 收納區前牆：剛好在後仰月份包頂端後面
YS1 = YS0 + 55                    # 收納區後牆
ZS = 40                           # 收納區牆高（11-27 壓低）
NPACK = 12
U = np.array([0, math.sin(A), math.cos(A)])     # 月份包「往上」
B = np.array([0, math.cos(A), -math.sin(A)])    # 月份包「往後」（沿底面）

def LP(x, d, h):                  # 月份包內座標：x 寬、d 往後層距、h 往上
    return np.array([x, Y0, ZF]) + d * B + h * U

# ---------- 相機 ----------
T = np.array([95, 95, 75])
AZ, EL, DIST, F = math.radians(32), math.radians(17), 760, 1.0
CAM = T + DIST * np.array([-math.sin(AZ) * math.cos(EL), -math.cos(AZ) * math.cos(EL), math.sin(EL)])
FWD = (T - CAM) / np.linalg.norm(T - CAM)
RIGHT = np.cross(FWD, [0, 0, 1]); RIGHT /= np.linalg.norm(RIGHT)
UPV = np.cross(RIGHT, FWD)
def proj_raw(p):
    v = np.asarray(p, float) - CAM
    z = v @ FWD
    return np.array([(v @ RIGHT) / z, -(v @ UPV) / z])

# 先算畫面範圍
probe = [LP(x, d, h) for x in (-AMP, FW + AMP) for d in (0, 100) for h in (0, C.SH)]
probe += [np.array([x, y, z]) for x in (X0, X1) for y in (0, YS1) for z in (0, ZS + C.SH)]
P2 = np.array([proj_raw(p) for p in probe])
mn, mx = P2.min(0), P2.max(0)
W_OUT = 3200; SS = 2                      # 輸出寬、超取樣
MARG = 0.06
scale = W_OUT * SS * (1 - 2 * MARG) / (mx[0] - mn[0])
H_OUT = int((mx[1] - mn[1]) * scale / SS / (1 - 2 * MARG))
CWp, CHp = W_OUT * SS, H_OUT * SS
def S(p):
    q = proj_raw(p)
    return (float((q[0] - mn[0]) * scale + CWp * MARG), float((q[1] - mn[1]) * scale + CHp * MARG))
LW = 3 * SS

canvas = Image.new("RGB", (CWp, CHp), "white")
dr = ImageDraw.Draw(canvas)

def poly(pts3, fill="white", outline="black", width=LW):
    pts = [S(p) for p in pts3]
    dr.polygon(pts, fill=fill)
    if outline: dr.line(pts + [pts[0]], fill=outline, width=width, joint="curve")

def line3(pts3, width=LW, fill="black"):
    dr.line([S(p) for p in pts3], fill=fill, width=width, joint="curve")

# ---------- 貼圖：平面 RGBA → 透視貼上 ----------
TS = 14                           # 貼圖 px/mm
def homog(src, dst):              # PIL PERSPECTIVE：輸出座標 → 輸入座標
    M = []; b = []
    for (x, y), (u, v) in zip(dst, src):
        M.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.append(u)
        M.append([0, 0, 0, x, y, 1, -v * x, -v * y]); b.append(v)
    return np.linalg.solve(np.array(M, float), np.array(b, float))

def paste_plane(tex, corner3):    # corner3：貼圖左上、右上、右下、左下的 3D 點
    w, h = tex.size
    dst = [S(p) for p in corner3]
    co = homog([(0, 0), (w, 0), (w, h), (0, h)], dst)
    warped = tex.transform((CWp, CHp), Image.PERSPECTIVE, tuple(co), Image.BICUBIC)
    canvas.paste(warped, (0, 0), warped)

def font(size_mm, wght=400, s=TS):
    f = ImageFont.truetype(SERIF, int(size_mm * s))
    try: f.set_variation_by_axes([wght])
    except Exception: pass
    return f

R = {wk["n"]: C.process(wk) for wk in C.WEEKS}
WK = {wk["n"]: wk for wk in C.WEEKS}
TLW = 4                           # 貼圖線寬 px（約 0.3 mm）

def sheet_tex(n, torn):           # 週曆貼圖：寬 188、高 155（底→上）
    w, h = int(C.SW * TS), int(C.SH * TS)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    P = lambda x, hh: (x * TS, (C.SH - hh) * TS)
    r = R[n]; y0 = C.SH - r["H"] - C.SHIFT[n]
    if torn:
        pts = [P(0, 0)] + [P(x, C.SH - (y + y0)) for x, y in r["tear"]] + [P(C.SW, 0)]
        d.polygon(pts, fill="white"); d.line(pts + [pts[0]], fill="black", width=TLW)
    else:
        d.rectangle([0, 0, w - 1, h - 1], fill="white", outline="black", width=TLW)
    for ls in r["lines"]:
        d.line([P(x, C.SH - (y + y0)) for x, y in ls.coords], fill="black", width=TLW, joint="curve")
    if not torn:                  # 日期條
        wk = WK[n]
        Tt = lambda x, yt: (x * TS, yt * TS)
        d.text(Tt(6.5, 19.0), "二月", font=font(12.5, 600), fill="black", anchor="ls")
        w2 = d.textlength("二月", font=font(12.5, 600)) / TS
        d.text(Tt(6.5 + w2 + 1.6, 19.0), "一一六年", font=font(3.0), fill="black", anchor="ls")
        d.line([Tt(51, 5.5), Tt(51, 21)], fill="black", width=3)
        x0, cw = 55, (182 - 55) / 7
        for i, (wd, (dd, note)) in enumerate(zip("日一二三四五六", wk["days"])):
            cx = x0 + cw * i + cw / 2
            d.text(Tt(cx, 8.0), wd, font=font(2.9), fill="black", anchor="ms")
            out = n == 1 and i == 0
            d.text(Tt(cx, 17.6), dd, font=font(6.0 if out else 9.5), fill="#999" if out else "black", anchor="ms")
            if note: d.text(Tt(cx, 22.3), note, font=font(2.6), fill="black", anchor="ms")
        d.line([Tt(7, 24.5), Tt(181, 24.5)], fill="black", width=3)
    return im

def tile(d, x, y, s, kind):       # 花磚：x,y 左上 px，s 邊長 px
    d.rectangle([x, y, x + s, y + s], outline="black", width=3)
    c = (x + s / 2, y + s / 2); q = s * 0.5
    if kind == 0:                 # 四瓣花＋中心圓
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            ex, ey = c[0] + dx * q * 0.42, c[1] + dy * q * 0.42
            rx, ry = (q * 0.40, q * 0.26) if dx else (q * 0.26, q * 0.40)
            d.ellipse([ex - rx, ey - ry, ex + rx, ey + ry], outline="black", width=3)
        d.ellipse([c[0] - q * .16, c[1] - q * .16, c[0] + q * .16, c[1] + q * .16], outline="black", width=3)
    else:                         # 菱形＋四角四分之一圓
        k = q * 0.72
        d.polygon([(c[0], c[1] - k), (c[0] + k, c[1]), (c[0], c[1] + k), (c[0] - k, c[1])], outline="black", width=3)
        rr = q * 0.42
        for cx, cy, a0 in ((x, y, 0), (x + s, y, 90), (x + s, y + s, 180), (x, y + s, 270)):
            d.arc([cx - rr, cy - rr, cx + rr, cy + rr], a0, a0 + 90, fill="black", width=3)
        d.ellipse([c[0] - q * .14, c[1] - q * .14, c[0] + q * .14, c[1] + q * .14], outline="black", width=3)

def frame_tex():                  # 台北前框：四邊花磚＋下緣「台北」名牌
    w, h = int(FW * TS), int(FH * TS)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, h - 1], fill="white")
    d.rectangle([FB * TS, FB * TS, (FW - FB) * TS, (FH - FB) * TS], fill=(0, 0, 0, 0))
    s = FB * TS
    cells = [(i, 0) for i in range(19)] + [(i, 12) for i in range(19)] + \
            [(0, j) for j in range(1, 12)] + [(18, j) for j in range(1, 12)]
    for i, j in cells:
        if j == 12 and 7 <= i <= 11: continue          # 名牌位置
        tile(d, i * s, j * s, s, (i + j) % 2)
    # 名牌
    d.rounded_rectangle([7 * s + 4, 12 * s + 6, 12 * s - 4, 13 * s - 6], radius=s * 0.18, fill="white", outline="black", width=3)
    d.text((9.5 * s, 12.5 * s), "台  北", font=font(6.2, 600), fill="black", anchor="mm")
    d.rectangle([0, 0, w - 1, h - 1], outline="black", width=TLW)
    d.rectangle([FB * TS, FB * TS, (FW - FB) * TS, (FH - FB) * TS], outline="black", width=TLW)
    return im

def rect_plane(x0, x1, d, h0, h1):            # 左上、右上、右下、左下
    return [LP(x0, d, h1), LP(x1, d, h1), LP(x1, d, h0), LP(x0, d, h0)]

FRAME = frame_tex()

# ---------- 繪製 ----------
def render(torn, name):
    global canvas, dr
    canvas = Image.new("RGB", (CWp, CHp), "white"); dr = ImageDraw.Draw(canvas)
    zb = 4
    # 1. 收納區：後牆、左牆（後段）、12 份收起來的月份包、前牆
    poly([[X0, YS1, 0], [X1, YS1, 0], [X1, YS1, ZS], [X0, YS1, ZS]])
    poly([[X1 - 3, YS0, zb], [X1 - 3, YS1, zb], [X1 - 3, YS1, ZS], [X1 - 3, YS0, ZS]])   # 右牆內面
    t = (YS1 - 3 - YS0 - 3) / NPACK
    for k in range(NPACK - 1, -1, -1):
        y = YS0 + 3 + k * t + 0.4
        x0, x1 = 3 + X0 + 1, X1 - 3 - 1
        top = zb + FH                 # 收起來的是撕完的月份：只剩前框高 130
        poly([[x0, y + t - 0.8, top], [x1, y + t - 0.8, top], [x1, y, top], [x0, y, top]], width=2 * SS)  # 頂面
        poly([[x0, y, zb], [x1, y, zb], [x1, y, top], [x0, y, top]], width=2 * SS)                     # 正面
        poly([[x0, y, top], [x0, y + t - 0.8, top], [x0, y + t - 0.8, zb], [x0, y, zb]], width=2 * SS)  # 左側面
    poly([[X0, YS0, 0], [X0, YS1, 0], [X0, YS1, ZS], [X0, YS0, ZS]])                      # 左牆外面（後段）
    poly([[X0, YS0, ZS], [X0, YS1, ZS], [X0 + 3, YS1, ZS], [X0 + 3, YS0, ZS]], width=2 * SS)
    poly([[X0, YS0, 0], [X1, YS0, 0], [X1, YS0, ZS], [X0, YS0, ZS]])                      # 前牆
    poly([[X0, YS0, ZS], [X1, YS0, ZS], [X1, YS0 + 3, ZS], [X0, YS0 + 3, ZS]], width=2 * SS)
    # 2. 展示區底面（斜）與中段平台
    yend = Y0 + 104 * math.cos(A); zend = ZF - 104 * math.sin(A)
    poly([[X0 + 3, Y0, ZF], [X1 - 3, Y0, ZF], [X1 - 3, yend, zend], [X0 + 3, yend, zend]])
    poly([[X0 + 3, yend, zend], [X1 - 3, yend, zend], [X1 - 3, YS0, zend], [X0 + 3, YS0, zend]])
    poly([[X1 - 3, Y0, ZF + LIP], [X1 - 3, yend, zend + LIP], [X1 - 3, YS0, zend + LIP], [X1 - 3, YS0, zend], [X1 - 3, yend, zend], [X1 - 3, Y0, ZF]])  # 右牆內面
    # 3. 右側風琴摺（內面）
    zig = lambda xs, sgn: [(xs + sgn * (AMP if (i % 2) else 0), i * GAP / 2) for i in range(11)]
    rz = zig(FW, 1)
    for (xa, da), (xb, db) in zip(rz, rz[1:]):
        poly([LP(xa, da, 0), LP(xb, db, 0), LP(xb, db, FH), LP(xa, da, FH)], width=2 * SS)
    # 4. 背景、週 4～1
    paste_plane(Image.new("RGBA", (int(FW * TS), int(FH * TS)), "white"), rect_plane(0, FW, 100, 0, FH))
    line3(rect_plane(0, FW, 100, 0, FH) + [rect_plane(0, FW, 100, 0, FH)[0]])
    for n in (4, 3, 2, 1):
        d = n * GAP
        paste_plane(sheet_tex(n, n in torn), rect_plane(SX, SX + C.SW, d, 0, C.SH))
    # 5. 左側風琴摺（外面）
    lz = zig(0, -1)
    for (xa, da), (xb, db) in zip(lz, lz[1:]):
        poly([LP(xa, da, 0), LP(xb, db, 0), LP(xb, db, FH), LP(xa, da, FH)], width=2 * SS)
    # 6. 前框
    paste_plane(FRAME, rect_plane(0, FW, 0, 0, FH))
    # 7. 底座左牆（展示段）、前擋
    poly([[X0, 0, 0], [X0, 0, ZF + LIP], [X0, Y0, ZF + LIP], [X0, yend, zend + LIP], [X0, YS0, zend + LIP], [X0, YS0, 0]])
    poly([[X0, 0, ZF + LIP], [X0 + 3, 0, ZF + LIP], [X0 + 3, Y0, ZF + LIP], [X0 + 3, yend, zend + LIP],
          [X0 + 3, YS0, zend + LIP], [X0, YS0, zend + LIP], [X0, yend, zend + LIP], [X0, Y0, ZF + LIP]], width=2 * SS)
    poly([[X0, 0, ZF + LIP], [X1, 0, ZF + LIP], [X1, Y0 - 2, ZF + LIP], [X0, Y0 - 2, ZF + LIP]], width=2 * SS)  # 前擋頂面
    poly([[X0, 0, 0], [X1, 0, 0], [X1, 0, ZF + LIP], [X0, 0, ZF + LIP]])                                       # 前擋正面
    out = canvas.resize((W_OUT, H_OUT), Image.LANCZOS)
    out.save(os.path.join(OUT, name.replace(".png", "_v2.png")))   # v2：11-27 CEO 回饋（後仰 10°、收納壓低）

render(set(), "狀態1_第一週還在.png")
render({1, 2}, "狀態2_撕掉前兩週.png")
render({1, 2, 3, 4}, "狀態3_四週都撕掉.png")
FRAME.save(os.path.join(OUT, "台北前框_平面.png"))
print("ok", W_OUT, H_OUT)
