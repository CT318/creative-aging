# A3 展覽版主圖｜Gemini 換棚拍環境提示詞

用法：在 Gemini 附上 `主圖/IMG_7488.jpeg`，整段貼下面英文提示詞（選「編輯這張圖片」，不要選重新生成）。一次一張。
重點：**前景所有紙作（三座六角底座、三城市零件、散放零件、右後方日曆卡）一點都不能動**，只換背景與光線。
整理日期 2026-10-29。

## 提示詞（整段貼）

```
Edit this photo. Keep EVERY object in the foreground exactly as it is, pixel-for-pixel: the three white hexagonal paper bases (labelled 東京, 雪梨, 台北), all the paper-cut city parts standing on them, all the loose paper-cut parts lying in front, and the cream calendar card standing at the back right with its text. Do not redraw, restyle, move, resize, rotate, crop, add or remove any of these objects. Do not change their colors, watercolor illustrations, Chinese characters, edges, tabs or shapes. Keep the same camera angle, framing and perspective.

Change ONLY the environment into a clean professional product-photography studio: replace the background (black chairs, wall, floor, the paper sheet at the left edge, the small number tag behind the calendar, and everything else that is not the product) with a seamless light warm-gray studio backdrop that gently fades into the tabletop with a soft gradient, no visible horizon line or clutter. Turn the plain table surface into a smooth, matte, seamless light-gray studio surface that continues to the edges of the frame.

Lighting: soft, even, diffused studio light from a large softbox at the upper left, with gentle fill from the right. Soft, natural, realistic contact shadows under each paper piece and base, grounded on the surface. Keep the original shadow direction logic and the paper's original white and watercolor tones; do not over-brighten, do not add glow, reflections, or color cast to the products. Clean, calm, high-end catalog look, sharp focus across the whole product group, no depth-of-field blur on the products.

No added props, no text, no logos, no watermark.
```

## 若結果不理想，加一句修正

- 物件被改到：`You changed the products. Redo it and keep every product object identical to the original photo; only the background may change.`
- 背景仍有雜物：`Remove all remaining clutter in the background. The background must be a plain seamless gray studio backdrop.`
- 影子太假：`Make the contact shadows softer and shorter, matching a single large softbox from the upper left.`
- 字被改壞（東京／雪梨／台北、日曆卡）：這些字 Gemini 常會動，若修不回來，改用「只換背景」法：先自己用修圖軟體去背，再把去背的前景貼到 Gemini 生成的棚拍背景上（Gemini 另生一張同視角的空棚拍桌面）。
