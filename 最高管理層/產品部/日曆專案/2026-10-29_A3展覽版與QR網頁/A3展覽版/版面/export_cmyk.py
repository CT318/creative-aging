"""A3 展覽版輸出（覆蓋舊檔）：
  成品尺寸 420×297 mm：A3展覽版.pdf（RGB 向量）、_300dpi.png、_CMYK.tif／.jpg／.pdf
  含出血 426×303 mm（四邊各 3 mm）：A3展覽版_出血_CMYK.tif／.pdf（送印建議用這組，輸出店通常要出血）
CMYK 以 Windows 內建 US Web Coated SWOP 描述檔轉換（點陣 300 dpi），並限制油墨總量 ≤ 300%。
用法：python build_a3.py && python export_cmyk.py"""
import os, subprocess
import numpy as np
from PIL import Image, ImageCms
H = os.path.dirname(os.path.abspath(__file__))
CH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TMP = os.environ['TEMP']
def url(name): return "file:///" + os.path.join(H, name).replace(chr(92), '/')
base = [CH, '--headless', '--disable-gpu', '--allow-file-access-from-files', '--virtual-time-budget=6000']

SRGB = ImageCms.createProfile('sRGB')
SWOP = ImageCms.getOpenProfile(r"C:\Windows\System32\spool\drivers\color\RSWOP.icm")
ICC = open(r"C:\Windows\System32\spool\drivers\color\RSWOP.icm", 'rb').read()
def to_cmyk(im):
    c = ImageCms.profileToProfile(im, SRGB, SWOP, renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC,
                                  outputMode='CMYK', flags=ImageCms.Flags.BLACKPOINTCOMPENSATION)
    a = np.asarray(c).astype(np.float32)               # 0..255 = 0..100%
    tac = a.sum(axis=2) / 255.0 * 100.0
    over = tac > 300.0
    if over.any():                                     # 超過 300% 的像素，等比例壓回 300%
        a[over] *= (300.0 / tac[over])[:, None]
    return Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8), 'CMYK'), float(tac.max()), float(over.mean() * 100)

def shot(page, out, w_px, h_px):
    subprocess.run(base + ['--hide-scrollbars', f'--window-size={w_px},{h_px}', '--force-device-scale-factor=3.125', f'--screenshot={out}', url(page)], capture_output=True)

# ---- 成品尺寸 ----
subprocess.run(base + ['--no-pdf-header-footer', f'--print-to-pdf={os.path.join(H, "A3展覽版.pdf")}', url('a3.html')], capture_output=True)
t1 = os.path.join(TMP, 'a3_full.png'); shot('a3.html', t1, 1588, 1123)
im = Image.open(t1).convert('RGB').crop((0, 0, 4963, 3509)).resize((4961, 3508), Image.LANCZOS)
im.save(os.path.join(H, 'A3展覽版_300dpi.png'), dpi=(300, 300))
cm, tmax, tover = to_cmyk(im)
cm.save(os.path.join(H, 'A3展覽版_CMYK.tif'), compression='tiff_lzw', dpi=(300, 300), icc_profile=ICC)
cm.save(os.path.join(H, 'A3展覽版_CMYK.pdf'), resolution=300.0, icc_profile=ICC)
cm.save(os.path.join(H, 'A3展覽版_CMYK.jpg'), quality=95, dpi=(300, 300), icc_profile=ICC)
print('成品尺寸', cm.size, '油墨總量最大 %.0f%%' % tmax)

# ---- 含出血（426×303 mm = 5031×3579 px @300dpi）----
t2 = os.path.join(TMP, 'a3_bleed.png'); shot('a3_出血.html', t2, 1610, 1145)
bi = Image.open(t2).convert('RGB')
bi = bi.crop((0, 0, min(bi.width, 5033), min(bi.height, 3581))).resize((5031, 3579), Image.LANCZOS)
bc, tmax2, _ = to_cmyk(bi)
bc.save(os.path.join(H, 'A3展覽版_出血_CMYK.tif'), compression='tiff_lzw', dpi=(300, 300), icc_profile=ICC)
bc.save(os.path.join(H, 'A3展覽版_出血_CMYK.pdf'), resolution=300.0, icc_profile=ICC)
print('含出血', bc.size, '油墨總量最大 %.0f%%' % tmax2)
