"""合併 img/lm/<n>/comments.json 與地標文字，輸出 data.js（網頁讀取）。素材或文字改了就重跑：python make_data.py"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
INFO = {
 1: dict(name='夜市小吃', tag='美食', sub='天一黑就熱鬧起來的攤車',
         intro=['夜市是台北人的日常，天一黑，攤車亮起燈，油煙和香味混在一起，從小吃吃到飲料，走一圈就飽了。', '攤車是夜市的靈魂：蚵仔煎、滷肉飯、烤香腸、豆花，每一攤都有自己的熟客。'],
         think='你小時候逛夜市，最常吃的是哪一樣？'),
 2: dict(name='台北捷運', tag='交通', sub='藍白色的城市動線',
         intro=['1996 年木柵線通車，從此台北有了捷運。藍白配色的列車，穿梭在高樓與街區之間。', '長輩搭捷運有敬老優惠，出門逛街、看展、探訪朋友，都很方便。'],
         think='最近一次搭捷運，是去哪裡？'),
 3: dict(name='迪化街老街屋', tag='老街', sub='大稻埕的百年老街',
         intro=['清末淡水開港後，大稻埕成為北台灣茶葉與南北貨的集散地。', '街上至今還有南北雜貨、中藥材、布料的老店，華麗的仿巴洛克街屋有紅磚、拱窗與牆面雕飾。', '每年農曆年前的「年貨大街」，掛滿紅燈籠，最熱鬧。'],
         think='你家過年會買哪些年貨？'),
 4: dict(name='艋舺龍山寺', tag='信仰', sub='艋舺人的老廟',
         intro=['清乾隆三年（1738）由泉州移民從家鄉分靈而來興建，主祀觀世音菩薩。', '三川殿的銅鑄龍柱是全台唯一，屋頂的燕尾翹脊層層飛簷，也很有特色。', '是國定古蹟，至今仍有許多人來拜拜、散步。'],
         think='你去過龍山寺嗎？'),
 5: dict(name='總統府', tag='歷史建築', sub='紅磚與高塔的老建築',
         intro=['總統府的建築在日治時期落成，原本是總督府，紅磚外牆搭配高聳的塔樓，是台北最有代表性的歷史建築之一。', '前方的廣場與街道開闊，很適合散步、拍紀念照。'],
         think='你有在這附近拍過紀念照嗎？'),
 6: dict(name='象山步道', tag='步道', sub='不用走太遠的城市好視野',
         intro=['象山在信義區，沿著石階往上走，一路有樹蔭，走累了可以在平台休息。', '爬到觀景平台，台北盆地與台北 101 一起入鏡，是許多人心中的台北好風景。'],
         think='你喜歡早上還是黃昏去爬山？'),
 7: dict(name='台北 101', tag='地標', sub='天際線上的高塔',
         intro=['2004 年完工的台北 101，高約 508 公尺，曾經是世界最高的建築。', '白天看得到藍綠色的塔身，跨年時的煙火更是許多台北人的共同回憶。'],
         think='你看過哪一年的跨年煙火？'),
}
lms, hero = [], None
for i in range(1, 8):
    p = os.path.join(HERE, 'img', 'lm', str(i), 'comments.json')
    if not os.path.exists(p):
        print('缺', i); continue
    d = json.load(open(p, encoding='utf-8'))
    m = dict(INFO[i]); m['id'] = i
    m['comments'] = d['comments']; m['photos'] = d['photos']
    lms.append(m)
    if d.get('hero'): hero = d['hero']
    print(i, m['name'], len(m['comments']), '則', len(m['photos']), '圖')
open(os.path.join(HERE, 'data.js'), 'w', encoding='utf-8').write('window.DATA=' + json.dumps(dict(landmarks=lms, hero=hero), ensure_ascii=False) + ';')
