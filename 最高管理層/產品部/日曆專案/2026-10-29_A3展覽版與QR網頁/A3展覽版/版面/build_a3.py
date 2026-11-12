"""由 a3_v2_上半.html（標題、旅遊、主題包、主圖）＋ 下半（思考脈絡圖示步驟 ＋ 3 個網頁步驟）組出 a3.html。"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'a3_v2_上半.html'), encoding='utf-8').read()
icons = {l.split('|', 1)[0]: l.split('|', 1)[1] for l in open(os.path.join(HERE, '素材', 'icons.txt'), encoding='utf-8').read().split('\n')}
KEEP = [('1', '長期參與<br>日常'), ('2', '日曆載體<br>自選主題'), ('3', '接起循環<br>圖斷差'), ('4', '慢慢累積<br>成作品'), ('8', '卡扣拼接<br>世界城市')]   # 去掉 5、6、7
CW, GAP, X0, Y0, H = 27.0, 3.6, 14.0, 196.0, 56.0
small = ''
for i, (k, title) in enumerate(KEEP):
    x = X0 + i * (CW + GAP)
    small += f'<div class="mini" style="left:{x:.1f}mm;top:{Y0}mm;width:{CW}mm;height:{H}mm"><span class="n">{i+1}</span>{icons[k]}<span class="t">{title}</span></div>'
    if i < len(KEEP) - 1:
        small += f'<div class="marr" style="left:{x+CW-0.2:.1f}mm;top:{Y0+H/2-3}mm">›</div>'
GX = X0 + len(KEEP) * CW + (len(KEEP) - 1) * GAP     # 小步驟群右緣
BX, BW, BG = 170.0, 72.0, 10.0   # 右緣 = 170+2*82+72 = 406 = 420-14，與左邊距一致
def bx(i): return BX + i * (BW + BG)
big = f'''
<div class="lab" style="left:14mm;top:187mm">設計思考脈絡</div>
<div class="lab" style="left:{BX}mm;top:187mm">掃 QR 之後，在手機上看到的三步</div>
<div class="bigarr" style="left:{GX+0.2:.1f}mm;top:{Y0+H/2-6}mm">›</div>
<div class="step" style="left:{bx(0)}mm"><div class="shotbox"><div class="shot photo"><img src="素材/背面_含QR.jpg" style="object-position:66% 56%" alt=""></div></div>
  <div class="cap"><b class="serif"><em>1</em>掃描</b><span>掃底座背面的 QR，免下載免註冊</span></div></div>
<div class="arr" style="left:{bx(0)+BW:.1f}mm">›</div>
<div class="step" style="left:{bx(1)}mm"><div class="shotbox"><div class="shot"><img src="../../介面/截圖/step2_city.png" alt=""></div></div>
  <div class="cap"><b class="serif"><em>2</em>認識城市</b><span>台北的故事，點開進入留言板</span></div></div>
<div class="arr" style="left:{bx(1)+BW:.1f}mm">›</div>
<div class="step" style="left:{bx(2)}mm"><div class="shotbox"><div class="shot"><img src="../../介面/截圖/step3_wall.png" alt=""></div></div>
  <div class="cap"><b class="serif"><em>3</em>城市主題留言板</b><span>照片、文字、語音都能留言</span></div></div>
<div class="hmw"><b>HMW</b>幫助退休後的樂齡族群，讓藝術成為生活的一部分，<br>無壓力且低負擔地長期參與日常藝術創作，達到「藝術創齡」。</div>
'''
css = '''
.lab{position:absolute;font-size:4.4mm;font-weight:700;letter-spacing:.2em;color:var(--red)}
.mini{position:absolute;background:var(--cream);border:.7mm solid var(--edge);border-radius:3.6mm;display:flex;flex-direction:column;align-items:center;padding-top:3mm;text-align:center}
.mini .n{width:6.4mm;height:6.4mm;border-radius:50%;background:var(--red);color:var(--cream);font-size:4mm;font-weight:900;display:flex;align-items:center;justify-content:center}
.mini svg{width:13mm;height:13mm;margin:4mm 0 3mm;stroke:var(--red);stroke-width:3;fill:none;stroke-linecap:round;stroke-linejoin:round}
.mini .t{font-size:4.2mm;font-weight:700;line-height:1.5;color:var(--ink);white-space:nowrap}
.marr{position:absolute;width:3.8mm;text-align:center;color:var(--red);font-size:6mm;font-weight:900;line-height:1}
.bigarr{position:absolute;width:8mm;text-align:center;color:var(--red);font-size:12mm;font-weight:900;line-height:1}
.hmw{position:absolute;left:14mm;top:258mm;width:149.4mm;height:23mm;border-radius:4mm;background:var(--ink);color:var(--cream);padding:3.6mm 5mm;font-size:4.8mm;line-height:1.6;font-weight:500}
.hmw b{display:inline-block;margin-right:2.4mm;padding:.2mm 2.6mm;border-radius:9mm;background:var(--red);font-size:4.2mm;letter-spacing:.14em}
'''
html = src.replace('<!--BOTTOM-->', small + big).replace('/*CSS*/', css)
open(os.path.join(HERE, 'a3.html'), 'w', encoding='utf-8').write(html)
print('ok')
