# assets 風格素材庫

| 子資料夾 | 內容 |
| --- | --- |
| `colors/` | 色彩 Design Tokens (`tokens.css`)，以 CSS Variables 定義 |
| `typography/` | 字型、Web Font 導入與自適應字級 (`fonts.css`) |
| `components-ui/` | 按鈕、卡片、標籤、分隔線、圖片比例等通用 UI (`ui.css`) |
| `backgrounds/` | 背景紋理、漸層、裝飾圖案 (`backgrounds.css`) |
| `placeholders/` | 16:9、4:3、1:1 佔位圖 (SVG)，上線前以真實圖片取代 |

新增檔案後，記得在 `src/styles/main.css` 以 `@import` 引入 CSS。
