import math, sys
od = sys.argv[1]
A = math.radians(20); G = 20; D = 7.5
L = math.hypot(D, G/2); OFF = (G/2)*math.sin(A); PW = math.sqrt(L*L-OFF*OFF)
SW, SH, BAR, TUN, BW, BH = 188, 155, 25, 130, 190, 130
TEARS = [30, 50, 70, 90]; FB = 10
CSS = (".cut{fill:none;stroke:#000;stroke-width:0.4}.valley{stroke:#2a8;stroke-width:0.4;stroke-dasharray:4 1 1 1}"
       ".mountain{stroke:#36c;stroke-width:0.4;stroke-dasharray:3 2}.tear{stroke:#c33;stroke-width:0.5;stroke-dasharray:1 1}"
       ".guide{stroke:#9ab;stroke-width:0.2}.dim{stroke:#555;stroke-width:0.25}.hid{fill:none;stroke:#888;stroke-width:0.3;stroke-dasharray:2 1.5}"
       ".part{fill:#f3f1ea;stroke:#000;stroke-width:0.4}text{font-family:Noto Sans TC,Microsoft JhengHei,sans-serif}")

def wrap(S, W, H):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.1f}mm" height="{H:.1f}mm" viewBox="0 0 {W:.1f} {H:.1f}">'
            f'<style>{CSS}</style><rect width="100%" height="100%" fill="#fff"/>' + "".join(S) + "</svg>")
def T(S, x, y, s, size=4, anchor="start", fill="#333"):
    S.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}">{s}</text>')
def Ln(S, x1, y1, x2, y2, c):
    S.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" class="{c}"/>')
def P(S, pts, c="cut", fill=None):
    f = f' fill="{fill}"' if fill else ""
    S.append('<path d="M' + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + f' Z" class="{c}"{f}/>')

# ---------------- 展開圖 v2 ----------------
S = []
def sheet(ox, oy, wk):
    P(S, [(ox, oy), (ox+SW, oy), (ox+SW, oy+SH), (ox, oy+SH)])
    S.append(f'<rect x="{ox}" y="{oy}" width="{SW}" height="{BAR}" fill="#e8eef6"/>')
    Ln(S, ox, oy+BAR, ox+SW, oy+BAR, "guide")
    cw = SW/7
    for i, n in enumerate("日一二三四五六"):
        if i: Ln(S, ox+i*cw, oy, ox+i*cw, oy+BAR, "guide")
        T(S, ox+i*cw+cw/2, oy+9, n, 5, "middle")
    h = TEARS[wk-1]
    S.append(f'<rect x="{ox}" y="{oy+SH-h}" width="{SW}" height="{h}" fill="#f6e3cc"/>')
    Ln(S, ox, oy+SH-h, ox+SW, oy+SH-h, "tear")
    T(S, ox+SW/2, oy+BAR+16, f"第{wk}週", 7, "middle")
    T(S, ox+SW/2, oy+SH-h-3, f"撕線（離底 {h}）", 4, "middle", "#c33")
    T(S, ox+SW/2, oy+SH-h/2, f"零件長條 {SW}×{h}", 4.5, "middle", "#844")
    T(S, ox+3, oy+BAR+6, f"日期條高 {BAR}（每格 {SW/7:.2f}）", 3.5)
    T(S, ox+SW-3, oy+BAR+6, f"框上緣（離底 {TUN}）", 3.5, "end")
    T(S, ox+SW/2, oy+SH+7, f"週曆 {SW}×{SH}（無插耳，順著風琴摺直接放下去）", 3.8, "middle")

def frame(ox, oy):
    P(S, [(ox, oy), (ox+BW, oy), (ox+BW, oy+BH), (ox, oy+BH)])
    P(S, [(ox+FB, oy+FB), (ox+BW-FB, oy+FB), (ox+BW-FB, oy+BH-FB), (ox+FB, oy+BH-FB)])
    T(S, ox+BW/2, oy+BH/2, "前框（中間鏤空）", 6, "middle")
    T(S, ox+BW/2, oy+BH/2+8, f"開口 {BW-2*FB}×{BH-2*FB}，四邊框寬 {FB}", 4, "middle", "#777")
    T(S, ox+BW/2, oy+BH+7, f"前框 {BW}×{BH}；背面左右框為側牆黏貼區", 3.8, "middle")

def bg(ox, oy):
    P(S, [(ox, oy), (ox+BW, oy), (ox+BW, oy+BH), (ox, oy+BH)], "cut", "#e6efe6")
    T(S, ox+BW/2, oy+BH/2, "背景", 6, "middle")
    T(S, ox+BW/2, oy+BH+7, f"背景 {BW}×{BH}；背面左右各 10 為側牆黏貼區", 3.8, "middle")

def side(ox, oy):
    k = OFF/PW; FL = 10
    xs = [0] + [FL+i*PW for i in range(11)] + [FL+10*PW+FL]
    yb = lambda x: oy+BH - k*x
    quad = lambda x1, x2: [(ox+x1, yb(x1)), (ox+x2, yb(x2)), (ox+x2, yb(x2)-BH), (ox+x1, yb(x1)-BH)]
    P(S, quad(xs[0], xs[1]), "cut", "#ddd"); P(S, quad(xs[-2], xs[-1]), "cut", "#ddd")
    P(S, quad(xs[0], xs[-1]))
    names = {0: "框", 2: "週1", 4: "週2", 6: "週3", 8: "週4", 10: "背景"}
    for i in range(11):
        x = xs[i+1]
        Ln(S, ox+x, yb(x), ox+x, yb(x)-BH, "valley" if i % 2 == 0 else "mountain")
        if i in names: T(S, ox+x, yb(x)-BH-2, names[i], 3.3, "middle")
    T(S, ox+FL/2, yb(FL/2)-BH/2, "黏框", 3.2, "middle")
    T(S, ox+xs[-1]-FL/2, yb(xs[-1]-FL/2)-BH/2, "黏背景", 3.2, "middle")
    tx = ox + xs[-1] + 10
    for j, s in enumerate([
        f"側牆 ×2（左右鏡像）",
        f"摺線長 {BH}；摺線間距 {PW:.2f}（共 10 格）；兩端黏貼片 {FL}",
        f"每往後一道摺線，下緣升高 {OFF:.2f}",
        "（整組往後斜 20°，所以展開是平行四邊形）",
        "綠＝外凸摺：週曆／框／背景的左右邊卡在這個 V 裡",
        "藍＝內凸摺",
        f"立起後：沿桌面前後層距 {G}；內凸往內縮 {D}",
        f"外寬 {BW}；內側淨寬約 {BW-2*D:.0f}（框開口 {BW-2*FB} 會擋住內凸）"]):
        T(S, tx, oy+12+j*6, s, 3.6)

M = 12
sheet(M, 20, 1); sheet(M+SW+20, 20, 2); sheet(M, 20+SH+25, 3); sheet(M+SW+20, 20+SH+25, 4)
y3 = 20 + 2*(SH+25) + 5
frame(M, y3); bg(M+BW+20, y3)
y4 = y3 + BH + 30 + 45; side(M, y4)
TW = 2*M + 2*SW + 20; TH = y4 + BH + 25
T(S, M, 10, "月份包（隧道書）平面展開圖 v2　單位 mm　比例 1:1　（整組往後斜 20°）", 6, fill="#222")
for i, (c, n) in enumerate([("cut", "裁切"), ("valley", "外凸摺"), ("mountain", "內凸摺"), ("tear", "撕線")]):
    x = M + i*45; Ln(S, x, TH-8, x+12, TH-8, c); T(S, x+15, TH-6.5, n, 4)
open(od + "/展開圖/月份包_展開圖_v2.svg", "w", encoding="utf-8").write(wrap(S, TW, TH))

# ---------------- 底座三視圖 v1 ----------------
S = []
tn = math.tan(A); FT = 3; WT = 3; LIP = 9; CL = 1; IW = BW + 2*CL; OW = IW + 2*WT
y_frame = WT + CL; y_bg = y_frame + 5*G; y_div = y_bg + CL; y_st = y_div + WT; SD = 45
y_bw = y_st + SD; y_end = y_bw + WT
WH = TUN*math.cos(A); sh = WH*tn; lip_sh = LIP*tn

def side_view(ox, oz):
    Y = lambda y: ox + y; Z = lambda z: oz - z
    P(S, [(Y(0), Z(0)), (Y(y_end), Z(0)), (Y(y_end), Z(FT)), (Y(0), Z(FT))], "part")
    def slab(y0, h):
        s = h*tn
        P(S, [(Y(y0), Z(FT)), (Y(y0+WT), Z(FT)), (Y(y0+WT+s), Z(FT+h)), (Y(y0+s), Z(FT+h))], "part")
    slab(0, LIP); slab(y_div, WH); slab(y_bw, WH)
    P(S, [(Y(y_div), Z(FT)), (Y(y_end), Z(FT)), (Y(y_end+sh), Z(FT+WH)), (Y(y_div+sh), Z(FT+WH))], "hid")
    P(S, [(Y(0), Z(FT)), (Y(y_div), Z(FT)), (Y(y_div+lip_sh), Z(FT+LIP)), (Y(lip_sh), Z(FT+LIP))], "hid")
    for i in range(6):
        y = y_frame + i*G; hh = BH if i in (0, 5) else SH
        Ln(S, Y(y), Z(FT), Y(y + hh*math.sin(A)), Z(FT + hh*math.cos(A)), "hid")
    def dimh(y1, y2, z, lab):
        Ln(S, Y(y1), Z(z), Y(y2), Z(z), "dim"); T(S, (Y(y1)+Y(y2))/2, Z(z)-1.2, lab, 3.2, "middle")
    dimh(0, y_div, -7, f"展示區 {y_div}"); dimh(y_div, y_end, -7, f"收納區 {y_end-y_div}（內 {SD}）")
    dimh(0, y_end, -14, f"底板深 {y_end}"); dimh(0, y_end+sh, -21, f"含牆頂斜出總深 {y_end+sh:.1f}")
    T(S, Y(y_end+sh+3), Z(FT+WH)+3, f"牆頂高 {FT+WH:.1f}", 3.2)
    T(S, Y(lip_sh+WT+3), Z(FT+LIP)-1, f"前緣高 {FT+LIP}", 3.2)
    T(S, Y(y_div+12), Z(FT+20), "20°", 4)
    T(S, Y(y_frame+20), Z(FT+SH*math.cos(A))-4, "虛線＝月份包", 3.5, fill="#888")
    T(S, ox, oz-165, "右側視圖（左＝前）", 5, fill="#222")

def front_view(ox, oz):
    X = lambda x: ox + x + OW/2; Z = lambda z: oz - z
    P(S, [(X(-OW/2), Z(0)), (X(OW/2), Z(0)), (X(OW/2), Z(FT+WH)), (X(-OW/2), Z(FT+WH))], "hid")
    P(S, [(X(-OW/2), Z(0)), (X(OW/2), Z(0)), (X(OW/2), Z(FT+LIP)), (X(-OW/2), Z(FT+LIP))], "part")
    Ln(S, X(-OW/2), Z(-7), X(OW/2), Z(-7), "dim")
    T(S, X(0), Z(-7)-1.2, f"外寬 {OW}（內寬 {IW}，壁厚 {WT}）", 3.2, "middle")
    T(S, X(0), Z(FT+WH/2), "虛線＝後方隔板與收納區（擺上月份包後被擋住）", 3.2, "middle", "#888")
    T(S, ox, oz-140, "前視圖", 5, fill="#222")

def top_view(ox, oy):
    X = lambda x: ox + x + OW/2; Yp = lambda y: oy + y
    P(S, [(X(-OW/2), Yp(0)), (X(OW/2), Yp(0)), (X(OW/2), Yp(y_end)), (X(-OW/2), Yp(y_end))], "part")
    P(S, [(X(-IW/2), Yp(WT)), (X(IW/2), Yp(WT)), (X(IW/2), Yp(y_div)), (X(-IW/2), Yp(y_div))])
    P(S, [(X(-IW/2), Yp(y_st)), (X(IW/2), Yp(y_st)), (X(IW/2), Yp(y_bw)), (X(-IW/2), Yp(y_bw))])
    P(S, [(X(-OW/2), Yp(y_div+sh)), (X(OW/2), Yp(y_div+sh)), (X(OW/2), Yp(y_end+sh)), (X(-OW/2), Yp(y_end+sh))], "hid")
    for i in range(6): Ln(S, X(-IW/2+1), Yp(y_frame+i*G), X(IW/2-1), Yp(y_frame+i*G), "guide")
    T(S, X(0), Yp(y_div/2), "展示區（月份包放這裡；細線＝框、週1～4、背景位置）", 3.4, "middle")
    T(S, X(0), Yp((y_st+y_bw)/2), "收納區", 3.6, "middle")
    T(S, X(OW/2+3), Yp(y_end+sh), "虛線＝牆頂往後斜出", 3.2)
    T(S, ox, oy-5, "俯視圖（上＝前）", 5, fill="#222")

top_view(20, 30)
base_z = 30 + y_end + sh + 25 + 135
front_view(20, base_z)
side_view(20 + OW + 35, base_z)
TW = 20 + OW + 35 + y_end + sh + 45; TH = base_z + 35
T(S, 20, 12, f"底座三視圖 v1（3D 列印）單位 mm　後仰 20°　底板 {FT}　壁厚 {WT}　前緣 {LIP}　層距 {G}　收納內深 {SD}", 5.2, fill="#222")
open(od + "/底座/底座三視圖_v1.svg", "w", encoding="utf-8").write(wrap(S, TW, TH))
print("PW", round(PW, 3), "OFF", round(OFF, 3), "y_div", y_div, "y_end", y_end, "sh", round(sh, 2), "WH", round(WH, 2), "OW", OW)
