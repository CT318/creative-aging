# Gemini 提示詞 v2：台北隧道書線稿（5 張）

> v1 失敗原因：高度用百分比 Gemini 不照做（最高點 53%，要 28%）、細節太多無法上色（欄杆、窗格、碎花叢）、構圖平均對稱沒有設計感、橋墩間有白色空洞（撕線斷掉）。v2 改用「寬比例＋上方留白」控高度、限制上色區塊數、指定主角配角與輪廓節奏、要求實心剪影。

## 使用說明

1. **同一個 Gemini 對話**依序生成 5 張；**每次都附上風格參考圖** `參考圖/風格參考_水彩紙雕立體場景.jpg`，再貼上該份提示詞（整段 code block 內容）。
2. **比例要在 Gemini 介面選對**：週1～週3 選 21:9，週4 選 16:9，背景選 3:2。介面若無 21:9，選最寬的比例並告知主持 Claude（需重算留白）。
3. **生成順序建議**：週1 先做（驗證「留白控高度」是否有效，成功再往下）→ 週4 → 週3 → 週2 → 背景。若後面的圖開始模仿前一張的構圖，開新對話重來（仍附參考圖）。
4. **存檔**：`2026-11-25/線稿/週1.png`、`週2.png`、`週3.png`、`週4.png`、`背景.png`。
5. **檢查清單**（每張生成後看一次，不合格就重生或請 Gemini 修改）：
   - [ ] 最高點位置：用尺量圖高，圖案最高點約在下表「圖案佔下方」的位置（誤差 ±5% 內可接受，主持 Claude 描圖時會等比縮放校正）
   - [ ] 圖案碰到左、右、下三邊，外輪廓是一條從左到右不斷的線
   - [ ] 輪廓內沒有任何白色空洞或透空（橋下、拱門下、樹與樹之間）
   - [ ] 可上色區塊數在範圍內，每塊都夠大（最小約為圖寬 1/24）
   - [ ] 沒有灰色、陰影、排線、紋理、文字、邊框、欄杆細條、窗格
   - [ ] 有明確主角、輪廓高低錯落；地標的橫向位置正確（後層地標頂端會從前層凹處露出）
   - [ ] 最下方約 10 mm 範圍只有簡單灌木／地面

## 尺寸對照表

成品寬 188 mm（背景 190 mm）。圖高 = 188 × 比例高／比例寬。

| 圖 | Gemini 比例 | 圖高換算 (mm) | 成品最高點 (mm) | 圖案佔下方 | 上方留白 | 底部被擋 10 mm 佔圖高 | 主角橫向位置 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 週1 | 21:9 | 80.6 | 30 | 37% | 63% | 12% | 列車 12–48%（60% 處留凹口給北門） |
| 週2 | 21:9 | 80.6 | 50 | 62% | 38% | 12% | 北門 60% |
| 週3 | 21:9 | 80.6 | 70 | 87% | 13% | 12% | 總統府 25%、圓山 75% |
| 週4 | 16:9 | 105.8 | 90 | 85% | 15% | 9.5% | 101 在 50% |
| 背景 | 3:2 | 126.7（成品 130，左右各裁約 2.5 mm 後放大） | 滿版 | — | — | — | 觀音山左、陽明山右 |

各層在後層地標位置的高度預算（確保後層地標頂端露出）：

| 橫向位置 | 週1 | 週2 | 週3 | 週4 |
| --- | --- | --- | --- | --- |
| 25%（總統府） | 約 28 | 約 38 | **70** | — |
| 50%（101） | 約 24 | 約 40 | 約 42（樹谷） | **90** |
| 60%（北門） | 約 16（凹口） | **50** | 約 45 | — |
| 75%（圓山） | 約 22 | 約 32 | **約 56** | 約 58 |

---

## 週1（最前層）：文湖線高架捷運

```
Week 1 layer of a paper-cut tunnel-book calendar. New, separate image. Aspect ratio 21:9, wide landscape.

STYLE: Match the illustration style of the attached reference image, but as uncolored black line art only. Take from it the rounded hand-drawn storybook shapes, the plump tree crowns gathered in clusters, the way trees and buildings overlap front to back, and the lively up-and-down rhythm of the outer outline. Use only its shapes and composition; its colors, watercolor texture, white paper border and photo background stay out of this drawing.

HEIGHT AND FRAMING:
- The top 63% of the image is completely empty white sky. The whole drawing lives in the bottom 37% of the image, as a long low strip about six times wider than it is tall.
- The drawing bleeds off the left edge, the right edge and the bottom edge of the image.
- The bottom 12% of the image will be hidden behind the frame: fill it with plain rounded bushes and ground only.

SCENE: The Taipei Metro Wenhu Line, the elevated rubber-tyred metro that glides above the city on a concrete viaduct.
- HERO: a short, chubby two-car Wenhu Line train drawn with storybook exaggeration: a big rounded nose, a puffy rounded roof, one long rounded window band per car. It rides on the viaduct between 12% and 48% of the image width, and its roof is the highest point of the whole drawing.
- The viaduct is a thick, smooth band running from the left edge to the right edge, gently dipping as it goes right. Two or three stout rounded pillars hold it up and disappear into the bushes.
- SUPPORTING CAST: big plump tree clumps and round bushes pack the whole space under the viaduct, from the ground up to the viaduct deck, overlapping the pillars so the space below the viaduct is completely filled with greenery. On the right side, from 72% to 100% of the width, a group of three overlapping rounded trees rises above the viaduct to about two-thirds of the train's height. Between 55% and 65% of the width the outline dips low: only the viaduct deck and a few low bushes there, forming a clear valley.
- OUTLINE RHYTHM from left to right: low start, rising to the train's rounded peak, sloping down along the train's tail, a deep valley around 60%, a second smaller bump of tree crowns, easing down at the right edge. Asymmetric and musical, like a hand-cut paper skyline.

SILHOUETTE: The drawing is one solid connected shape, like a single cookie-cutter piece. Its outer outline is one continuous line that starts at the left edge, travels over the top of the scene and ends at the right edge. Inside that outline the paper is fully occupied by drawn things: the gaps between pillars, under the viaduct and between trees are all filled with bushes and tree crowns, so the shape is solid all the way through. Every bump of the outline is rounded and generous; every neck and notch is at least 1/60 of the image width wide.

COLORING AREAS: Thin interior lines divide the shape into 8 to 12 large closed areas, each one a single thing to paint in watercolor: the train body, one window band per car, the viaduct, each tree clump, the bushes. Each area is at least 1/24 of the image width across. Small parts are merged into the larger shapes: windows become one band per car, railings and panel seams become part of the viaduct band, leaves become the smooth outline of their crown.

LINE STYLE: Pure black lines on a pure white background. The outer outline is a bold, smooth line about twice as thick as the interior lines. Interior lines are thin, smooth and confident. Every area is plain white inside, ready for paint. The look of a premium designer coloring book: confident hand-drawn curves, simple bold shapes, generous white space inside each area.

OUTPUT: One image of clean black outline drawing on white. Leave out shading, hatching, gray tones, texture, text and borders.
```

## 週2：迪化街巴洛克街屋＋北門

```
Week 2 layer of a paper-cut tunnel-book calendar. New, separate image. Aspect ratio 21:9, wide landscape.

STYLE: Match the illustration style of the attached reference image, but as uncolored black line art only. Take from it the rounded hand-drawn storybook shapes, the plump tree crowns gathered in clusters, the way trees and buildings overlap front to back, and the lively up-and-down rhythm of the outer outline. Use only its shapes and composition; its colors, watercolor texture, white paper border and photo background stay out of this drawing.

HEIGHT AND FRAMING:
- The top 38% of the image is completely empty white sky. The whole drawing lives in the bottom 62% of the image, about two and a half times wider than it is tall.
- The drawing bleeds off the left edge, the right edge and the bottom edge of the image.
- The bottom 12% of the image will be hidden behind the frame: fill it with plain rounded bushes and pavement only.

SCENE: Old Taipei: the baroque shophouses of Dihua Street in Dadaocheng and the North Gate (Beimen).
- HERO: the Taipei North Gate at 60% of the image width, the tallest element of the drawing. Drawn chunky and friendly: a solid stone base block with one big rounded arched doorway, topped by a small gatehouse with a plump two-tier tiled roof whose eave corners curl up into soft rounded tips. The arched doorway is drawn as a closed shape that will be painted dark, as if looking into a shadowy tunnel.
- SUPPORTING CAST, left side (0% to 50% of the width): three Dihua Street shophouses standing shoulder to shoulder, each a different width and height, each with one exaggerated curvy baroque gable on top (one round arch gable, one stepped scroll gable, one wide shell-shaped gable). Their gable tops reach about three-quarters of the North Gate's height, the tallest one around 20% of the width. Each facade has one big ground-floor arch and one or two large upper windows, drawn as simple rounded shapes.
- Right side (68% to 100% of the width): one lower, simpler shophouse and a cluster of plump round trees, reaching about two-thirds of the North Gate's height, stepping down toward the right edge.
- Round bushes and tree crowns overlap the bases of the buildings and the gate along the whole bottom, tying everything into one piece.
- OUTLINE RHYTHM from left to right: a cluster of three different gable bumps, a small dip around 45% to 52%, a strong rise to the North Gate roof at 60%, then a gentle stepping-down of rooftop and tree crowns to the right edge. Asymmetric, with the gate clearly the star.

SILHOUETTE: The drawing is one solid connected shape, like a single cookie-cutter piece. Its outer outline is one continuous line that starts at the left edge, travels over the top of the scene and ends at the right edge. Inside that outline the paper is fully occupied by drawn things: the arched doorways are closed painted shapes and every gap between buildings is filled with trees or walls, so the shape is solid all the way through. Gable scrolls and roof tips are rounded and generous; every neck and notch is at least 1/60 of the image width wide.

COLORING AREAS: Thin interior lines divide the shape into 12 to 16 large closed areas, each one a single thing to paint in watercolor: each facade wall, each gable, each big arch, the gate stone base, the gate roof, the gatehouse wall, each tree clump. Each area is at least 1/24 of the image width across. Small parts are merged into the larger shapes: window shutters become one simple window shape, roof tiles become one smooth roof shape, carved ornaments become the curvy outline of their gable, stones become one wall.

LINE STYLE: Pure black lines on a pure white background. The outer outline is a bold, smooth line about twice as thick as the interior lines. Interior lines are thin, smooth and confident. Every area is plain white inside, ready for paint. The look of a premium designer coloring book: confident hand-drawn curves, simple bold shapes, generous white space inside each area.

OUTPUT: One image of clean black outline drawing on white. Leave out shading, hatching, gray tones, texture, text and borders.
```

## 週3：總統府塔樓＋圓山大飯店

```
Week 3 layer of a paper-cut tunnel-book calendar. New, separate image. Aspect ratio 21:9, wide landscape.

STYLE: Match the illustration style of the attached reference image, but as uncolored black line art only. Take from it the rounded hand-drawn storybook shapes, the plump tree crowns gathered in clusters, the way trees and buildings overlap front to back, and the lively up-and-down rhythm of the outer outline. Use only its shapes and composition; its colors, watercolor texture, white paper border and photo background stay out of this drawing.

HEIGHT AND FRAMING:
- The top 13% of the image is completely empty white sky. The drawing fills the bottom 87% of the image.
- The drawing bleeds off the left edge, the right edge and the bottom edge of the image.
- The bottom 12% of the image will be hidden behind the frame: fill it with plain rounded bushes only.

SCENE: Two grand Taipei landmarks rising out of a sea of round trees.
- HERO: the Presidential Office Building tower at 25% of the image width, the tallest element of the drawing, reaching the top of the drawing area. Drawn as a storybook tower: a sturdy stacked tower of three or four blocks that get a little narrower going up, each with one big arched window, crowned by a plump rounded dome-like cap. On both sides of the tower, a short stretch of the lower building wings, each wing with three large arched windows, reaching just under half of the tower's height. The wings end in round trees on both sides.
- CO-STAR: the Grand Hotel Taipei at 75% of the image width, about four-fifths of the tower's height. Drawn as a wide, plump Chinese palace: a huge sweeping double-eaved roof whose corners curl up into soft rounded tips, sitting on a simple wall band with a row of five thick columns, on a raised base. The roof is the star of this building: big, bold, simple.
- SUPPORTING CAST: a valley of plump overlapping tree crowns between 40% and 60% of the width, reaching just over half of the tower's height, lowest around 50%. More round trees overlap the bases of both buildings and run out to the left and right edges, with the trees at the right edge stepping down.
- OUTLINE RHYTHM from left to right: trees rising to the low wing, a sharp climb to the tower's rounded cap at 25%, down to the other wing, a soft valley of tree crowns around 50%, a broad swooping rise over the Grand Hotel roof at 75%, then trees stepping down to the right edge. Asymmetric: the tower is tall and vertical, the hotel is wide and horizontal.

SILHOUETTE: The drawing is one solid connected shape, like a single cookie-cutter piece. Its outer outline is one continuous line that starts at the left edge, travels over the top of the scene and ends at the right edge. Inside that outline the paper is fully occupied by drawn things: arched windows are closed painted shapes and every gap between buildings is filled with trees, so the shape is solid all the way through. The tower cap and roof tips are rounded and generous; every neck and notch is at least 1/60 of the image width wide.

COLORING AREAS: Thin interior lines divide the shape into 14 to 18 large closed areas, each one a single thing to paint in watercolor: each tower block, the tower cap, each wing wall, the hotel's upper roof, lower roof, column band and base, each tree clump. Each area is at least 1/24 of the image width across. Small parts are merged into the larger shapes: the windows on each tower block become one big arch, the brick pattern becomes one plain wall, roof tiles become one smooth roof shape, the columns become one simple band with a few vertical lines.

LINE STYLE: Pure black lines on a pure white background. The outer outline is a bold, smooth line about twice as thick as the interior lines. Interior lines are thin, smooth and confident. Every area is plain white inside, ready for paint. The look of a premium designer coloring book: confident hand-drawn curves, simple bold shapes, generous white space inside each area.

OUTPUT: One image of clean black outline drawing on white. Leave out shading, hatching, gray tones, texture, text and borders.
```

## 週4：台北 101＋信義區天際線

```
Week 4 layer of a paper-cut tunnel-book calendar. New, separate image. Aspect ratio 16:9, landscape.

STYLE: Match the illustration style of the attached reference image, but as uncolored black line art only. Take from it the rounded hand-drawn storybook shapes, the plump tree crowns gathered in clusters, the way trees and buildings overlap front to back, and the lively up-and-down rhythm of the outer outline. Use only its shapes and composition; its colors, watercolor texture, white paper border and photo background stay out of this drawing.

HEIGHT AND FRAMING:
- The top 15% of the image is completely empty white sky. The drawing fills the bottom 85% of the image.
- The drawing bleeds off the left edge, the right edge and the bottom edge of the image.
- The bottom 10% of the image will be hidden behind the frame: fill it with plain rounded tree crowns only.

SCENE: The distant Xinyi district skyline of Taipei, seen far away, so every building is a simple bold shape.
- HERO: Taipei 101 at 50% of the image width, standing alone as the tallest element by far, its spire tip touching the top of the drawing area. Drawn chubby and friendly: a sturdy base block, then eight stacked flared segments like a stack of upside-down cups, each segment a clear simple trapezoid, then a small top block and a short, thick, rounded spire. The tower body is about one-twelfth of the image width wide.
- SUPPORTING CAST: modern towers of different widths and heights with softened tops (rounded corners, one gentle curved top, one stepped top). To the right of 101 (from 58% to 80% of the width), a taller cluster of two or three towers reaching about two-thirds of 101's height. To the left of 101 (from 15% to 42% of the width), a lower group reaching about half of 101's height. Near both edges, the skyline drops to low buildings about a third of 101's height. A space of at least 1/30 of the image width separates 101 from its neighbors on both sides above half of 101's height, so its silhouette reads clearly.
- Plump round tree crowns run along the whole bottom, overlapping the bases of all the towers and tying them into one piece.
- OUTLINE RHYTHM from left to right: low edge, a modest group, a clear drop, the tall slender rise of 101, a drop, a taller right-hand cluster, stepping down to the right edge. Asymmetric, with 101 the unmistakable star.

SILHOUETTE: The drawing is one solid connected shape, like a single cookie-cutter piece. Its outer outline is one continuous line that starts at the left edge, travels over the top of the scene and ends at the right edge. Inside that outline the paper is fully occupied by drawn things: every gap between towers below the skyline is filled with lower buildings or tree crowns, so the shape is solid all the way through. The spire and tower tops are rounded and generous; the spire is at least 1/60 of the image width wide and every notch between towers is at least 1/60 of the image width wide.

COLORING AREAS: Thin interior lines divide the shape into 16 to 20 large closed areas, each one a single thing to paint in watercolor: each segment of Taipei 101, the 101 base and spire, each tower, each tree clump. Each area is at least 1/24 of the image width across, except the narrow 101 segments, which are each one simple wide band. Small parts are merged into the larger shapes: window grids become plain tower faces, with at most one or two horizontal band lines per tower.

LINE STYLE: Pure black lines on a pure white background. The outer outline is a bold, smooth line about twice as thick as the interior lines. Interior lines are thin, smooth and confident. Every area is plain white inside, ready for paint. The look of a premium designer coloring book: confident hand-drawn curves, simple bold shapes, generous white space inside each area.

OUTPUT: One image of clean black outline drawing on white. Leave out shading, hatching, gray tones, texture, text and borders.
```

## 背景：觀音山／陽明山稜線＋雲

> 方位：從台北市區朝北看，觀音山在左（西北，淡水河口），陽明山（大屯、七星山群）在右（北）。v1 寫反了，v2 已更正。

```
Backdrop of a paper-cut tunnel-book calendar. New, separate image. Aspect ratio 3:2, landscape.

STYLE: Match the illustration style of the attached reference image, but as uncolored black line art only. Take from it the rounded hand-drawn storybook shapes, the soft plump forms and the gentle layered overlapping. Use only its shapes and composition; its colors, watercolor texture, white paper border and photo background stay out of this drawing.

FRAMING: A full rectangular scene that fills the entire canvas edge to edge. Keep all important shapes at least 4% away from the left and right edges, because those edges will be trimmed slightly.

SCENE: The mountains that ring the Taipei basin, seen from the city, with a soft storybook sky.
- On the left: Guanyin Mountain, with its recognizable gentle reclining profile, like a sleeping face lying on its back, sloping down toward the left edge.
- On the right: the Yangmingshan range, two or three broad rounded peaks overlapping front to back, the tallest one around 75% of the image width.
- The mountain ridges sit in the middle band of the image: the highest peak reaches 65% of the image height from the bottom, the lowest saddle between the two mountains is around 48%. Below the ridges, two or three softly curving overlapping hill layers fill everything down to the bottom edge, like layered paper.
- SKY: three big puffy rounded clouds of different sizes placed asymmetrically, plus a simple round sun near the upper left, all in the upper third of the image and at least 8% away from the top edge.

COLORING AREAS: Thin lines divide the scene into 12 to 18 large closed areas, each one a single thing to paint in watercolor: the sky, the sun, each cloud, each mountain, each hill layer. Each area is at least 1/24 of the image width across. Clouds are simple plump shapes with smooth outlines; mountain slopes are smooth single shapes.

LINE STYLE: Pure black lines on a pure white background. All lines are thin, smooth and even, the same weight everywhere. Every area is plain white inside, ready for paint. The look of a premium designer coloring book: confident hand-drawn curves, simple bold shapes, generous white space inside each area.

OUTPUT: One image of clean black outline drawing on white. Leave out shading, hatching, gray tones, texture, text and borders.
```
