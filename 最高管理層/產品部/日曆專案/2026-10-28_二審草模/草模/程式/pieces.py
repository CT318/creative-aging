"""零件處理：依目標尺寸（mm）輸出 300dpi 彩色版與線稿版（都含自製卡榫）。"""
import json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
PPM = 300 / 25.4
INFO = json.load(open('../圖/零件/info.json', encoding='utf-8'))
HT = [45, 50, 60, 70, 75, 82, 90]; WMAX = 75
TAB_H = 8.0

def base_size(city, i):
    d = INFO[f'{city}_{i}']; s = min(HT[i - 1] / d['h'], WMAX / d['w'])
    return d['w'] * s, d['h'] * s

def tab_width(w_mm):
    return float(min(24, max(14, round(w_mm * 0.55))))

def build(city, i):
    """回傳 dict：color(RGBA)、line(RGBA)、w_mm、h_mm(含卡榫)、body_h、tab_w、tab_cx(mm，相對左緣)"""
    im = Image.open(f'../圖/零件/{city}_{i}.png').convert('RGBA')
    w_mm, h_mm = base_size(city, i)
    W, H = round(w_mm * PPM), round(h_mm * PPM)
    im = im.resize((W, H), Image.LANCZOS)
    a = np.asarray(im)[:, :, 3] > 128
    # 卡榫位置：本體底部 8% 的橫向質心
    ys, xs = np.where(a[int(H * .92):])
    cx = xs.mean() if len(xs) else W / 2
    tw = tab_width(w_mm); tabw_px, tabh_px = round(tw * PPM), round(TAB_H * PPM)
    x0 = int(min(max(cx - tabw_px / 2, 0), W - tabw_px))
    full = Image.new('RGBA', (W, H + tabh_px), (0, 0, 0, 0))
    full.paste(im, (0, 0))
    # 卡榫：奶油色紙 + 灰細線，與本體底部相接
    tab = Image.new('RGBA', (tabw_px, tabh_px + 4), (244, 238, 226, 255))
    td = ImageDraw.Draw(tab); g = (165, 165, 170, 255)
    td.line([(0, 0), (0, tabh_px + 3), (tabw_px - 1, tabh_px + 3), (tabw_px - 1, 0)], fill=g, width=3)
    full.paste(tab, (x0, H - 4), tab)
    # 線稿版：深色墨線留黑，其餘白；外緣用灰色虛線當割線
    rgb = np.asarray(full)[:, :, :3].astype(int); alpha = np.asarray(full)[:, :, 3] > 128
    gray = rgb.mean(axis=2)
    ink = (gray < 88) & alpha
    inkimg = Image.fromarray((ink * 255).astype('uint8'))
    # 取邊前先四周補透明邊，否則貼齊畫布邊緣的卡榫底邊（最後一列）取不到虛線；
    # 取完裁回原尺寸（外緣環落在形狀內側 3px），零件實際大小與卡榫位置不變
    P = 6
    apad = np.pad(alpha, P)
    alpha_img = Image.fromarray((apad * 255).astype('uint8'))
    edge = apad & ~(np.asarray(alpha_img.filter(ImageFilter.MinFilter(7))) > 0)
    edge = edge[P:-P, P:-P]
    alpha_img = Image.fromarray((alpha * 255).astype('uint8'))
    yy, xx = np.indices(edge.shape); dash = ((xx + yy) % 24) < 14
    out = np.zeros(edge.shape + (4,), 'uint8')
    out[alpha] = (255, 255, 255, 255)
    out[(np.asarray(inkimg) > 0)] = (45, 38, 34, 255)
    out[edge & dash] = (138, 118, 96, 255)
    line = Image.fromarray(out, 'RGBA')
    return dict(color=full, line=line, w_mm=w_mm, h_mm=h_mm + TAB_H, body_h=h_mm, tab_w=tw, tab_cx=(x0 + tabw_px / 2) / PPM, mask=alpha)
