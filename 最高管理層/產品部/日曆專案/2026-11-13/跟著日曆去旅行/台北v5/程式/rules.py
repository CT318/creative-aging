# -*- coding: utf-8 -*-
"""①照「製作規範」與刀模常規檢查每一件零件，輸出報告；②輸出刀模用的刀線初稿（給刀模廠評估）。"""
from pages import *
from geo import _polys

BLADE = dict(min_w=1.5, min_gap=1.6, hole=2.0, space=3.0, edge=10.0)      # 快切機（製作規範/README）
DIE = dict(min_w=2.0, min_gap=3.0, hole=3.0, space=3.0, edge=10.0)        # 刀模常規（刀片彎折與排刀間距；以刀模廠回覆為準）


def thin_area(sh, w):
    """比 w 細的部分面積（mm²）。"""
    r = w / 2
    return sh.area - sh.buffer(-r, join_style=2).buffer(r, join_style=2, mitre_limit=3).intersection(sh).area


def gap_area(sh, g):
    """比 g 窄的缺口面積（mm²）。"""
    r = g / 2
    return sh.buffer(r, join_style=2).buffer(-r, join_style=2, mitre_limit=3).area - sh.area


def die_shape(sh):
    """刀模版外形：補掉窄於 3 mm 的缺口、去掉細於 2 mm 的部分、轉角 R1。"""
    body = sh.intersection(box(-999, 0.2, 999, 999)); tabs = sh.intersection(box(-999, -99, 999, 0.6))
    d = body.buffer(1.5, join_style=2).buffer(-1.5, join_style=2, mitre_limit=3)
    d = d.buffer(-1.0).buffer(1.0, quad_segs=6)
    big = sorted(_polys(d), key=lambda p: -p.area)[0]
    d = Polygon(big.exterior, [r for r in big.interiors if Polygon(r).buffer(-1.5).area > 0])      # 保留夠大的內孔（≥3 mm）
    d = d.union(tabs).buffer(0.01)
    return sorted(_polys(d), key=lambda p: -p.area)[0]


def report():
    rows = []
    for n, b in BUILT.items():
        sh = b['shape']
        body = sh.intersection(box(-999, 0.2, 999, 999))
        holes = [Polygon(r) for r in sh.interiors]
        hmin = min([min(h.bounds[2] - h.bounds[0], h.bounds[3] - h.bounds[1]) for h in holes], default=None)
        d = die_shape(sh)
        rows.append((n, b['label'], b['w'], b['maxy'], thin_area(body, 1.5), thin_area(body, 2.0), gap_area(body, 3.0), len(holes), hmin,
                     len(b['tabs']), 100 * abs(d.area - sh.area) / sh.area, d.exterior.length, sh.exterior.length))
    out = ['# 製作規範檢查（台北 v5）', '',
           '> 程式依 `製作規範/README.md`（快切機）與刀模常規自動檢查。數字是幾何計算，**不是實體試切結果**。', '',
           '| # | 零件 | 寬×高 mm | 細於 1.5 mm 的面積 | 細於 2 mm 的面積 | 窄於 3 mm 的缺口面積 | 內孔數（最小邊） | 插榫數 | 刀模版外形改變 |',
           '|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        out.append('| %d | %s | %.0f×%.0f | %.1f mm² | %.1f mm² | %.1f mm² | %d（%s） | %d | %.1f%% |' % (
            r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], ('%.1f mm' % r[8]) if r[8] else '—', r[9], r[10]))
    out += ['', '## 怎麼讀',
            '- **細於 1.5 mm 的面積**應接近 0：快切機規範的最細寬度。',
            '- **細於 2 mm／窄於 3 mm 的缺口**：刀模的刀片彎折半徑與兩刀間距通常需要更寬（一般建議刀距 ≥ 3 mm、細條 ≥ 2 mm、轉角有 R），數字越大代表開刀模時越需要簡化。確切數值要問刀模廠。',
            '- **刀模版外形改變**：把外形簡化到符合上面刀模常規後，面積改變的比例。超過 3% 的零件，刀模版的剪影會和快切版看得出差別。',
            '', '## 版面',]
    # 版面間距與邊距
    for wk, items in WEEKX.items():
        bs = []
        for no, x in items:
            b = BUILT[no]
            bs.append(AF.translate(b['shape'], x - b['minx'], GROUND))
        mn = min((bs[i].distance(bs[j]) for i in range(len(bs)) for j in range(i + 1, len(bs))), default=None)
        bb = unary_union(bs).bounds
        edge = min(bb[0], bb[1], PW - bb[2], PH - bb[3])
        out.append('- 第 %d 週：零件最小間距 %s；離紙邊最近 %.1f mm（規範 ≥ 10）。' % (wk, ('%.1f mm（規範 ≥ 3）' % mn) if mn is not None else '—（只有一件）', edge))
    out += ['', '## 還沒處理、要靠試切或廠商確認的',
            '- 留點（連接點）0.8 mm 在刀模上要改成「缺口刀（nick）」，數量與寬度由刀模廠定。',
            '- 底座插槽是單線切口；刀模可做，但紙厚與鬆緊要試。',
            '- 印刷與切割的對位誤差：目前零件白邊 0.3 mm、輪廓線內縮 0.4 mm，誤差超過 0.4 mm 會切到線。',
            '- 刀模版 PDF 是把外形自動簡化的**初稿**，印刷線稿尚未跟著改，只供刀模廠評估與報價。']
    open(os.path.join(ROOT, '製作規範檢查.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print('\n'.join(out[4:4 + 2 + len(rows)]))


def die_pdf():
    path = os.path.join(OUT, '台北週曆_刀模刀線初稿.pdf')
    c = RC.Canvas(path, pagesize=(PW * mm, PH * mm))
    for i in range(5):
        pg = Pg(c, 'die', i)
        if i == 0:
            cx, cy = 169.5, 107
            T = lambda pts: [(x + cx, y + cy) for x, y in pts]
            for f in base_net():
                pg.poly(T(f['cut'][0] + f['cut'][1]), (0, 0, 0), 0.1)
                pg.poly(T(f['slit']), (0, 0, 0), 0.1); pg.poly(T(f['edge']), (0, 0.6, 0.9), 0.1); pg.poly(T(f['hinge']), (0, 0.6, 0.9), 0.1)
            for no, a, e in slits():
                pg.poly(T([a, e]), (0, 0, 0), 0.1)
        else:
            for no, x in WEEKX[i]:
                b = BUILT[no]; d = die_shape(b['shape'])
                ox, oy = x - b['minx'], GROUND
                pg.poly([(px_ + ox, py_ + oy) for px_, py_ in d.exterior.coords], (0, 0, 0), 0.1, close=True)
                for fx, fy0, fy1 in b.get('folds', []):
                    g = LineString([(fx, fy0), (fx, fy1)]).intersection(d)
                    if not g.is_empty:
                        pg.poly([(px_ + ox, py_ + oy) for px_, py_ in g.coords], (0, 0.6, 0.9), 0.1)
        pg.lmark()
        c.showPage()
    c.save()
    print('刀模刀線初稿：黑＝刀線、藍＝壓線')


if __name__ == '__main__':
    build_all()
    report(); die_pdf()
