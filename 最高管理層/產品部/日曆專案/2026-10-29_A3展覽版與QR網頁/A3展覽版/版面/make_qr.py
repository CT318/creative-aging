"""產生 QR 貼圖並合成到背面照（最高那件背面）。網址寫在 ../../介面/網址.txt，換網址後重跑本檔再重出 A3。"""
import sys, os, io
import segno
from PIL import Image, ImageFilter, ImageChops
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
url = open(os.path.join(ROOT, '介面', '網址.txt'), encoding='utf-8').read().strip()
q = segno.make(url, error='m', micro=False)
buf = io.BytesIO(); q.save(buf, kind='png', scale=24, border=4, dark='#111111', light='#FFFFFF'); buf.seek(0)
qr = Image.open(buf).convert('RGB'); qr.save(os.path.join(HERE, '素材', 'qr.png'))
# 合成到背面照：照片座標（原圖 1792x2390）
back = Image.open(os.path.join(ROOT, 'A3展覽版', '背面圖', 'Gemini_Generated_Image_ec79zlec79zlec79.jpg')).convert('RGB')
S = 1.1946
cx, cy, size = 640 * S, 850 * S, 300 * S            # 左邊樹形那張紙背面中間偏上、放大（像素）
rot = -2                                              # 貼面略斜
mod = qr.resize((int(size), int(size)), Image.LANCZOS)
# 透明底：白色部分全透明、只留黑色模組（像直接印在紙上，不貼白標籤），微模糊與紙面融合
alpha = mod.convert('L').point(lambda v: 255 - v).filter(ImageFilter.GaussianBlur(0.9))
dark = Image.new('RGB', mod.size, (42, 40, 40))
label = Image.new('RGBA', mod.size, (0, 0, 0, 0)); label.paste(dark, (0, 0), alpha.point(lambda v: int(v * 0.86)))
# 另存透明背景 QR（供實物列印／簡報使用）
qa = qr.convert('L').point(lambda v: 255 - v); qt = Image.new('RGBA', qr.size, (17, 17, 17, 0)); qt.putalpha(qa); qt.save(os.path.join(HERE, '素材', 'qr_透明.png'))
label = label.rotate(rot, expand=True, resample=Image.BICUBIC)
out = back.convert('RGBA'); out.alpha_composite(label, (int(cx - label.width / 2), int(cy - label.height / 2)))
out.convert('RGB').save(os.path.join(HERE, '素材', '背面_含QR.jpg'), quality=92)
print('ok', url)
