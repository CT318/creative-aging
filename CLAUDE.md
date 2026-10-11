# 專案說明（給 Claude）

「藝術創齡-樂齡畫畫生活」畢業專題。Vite + 原生 HTML/CSS/JS 的研究歷程展示網站，內容全部由資料夾動態讀取，**不要把任何具體專案內容寫死在網頁或程式碼裡**。

## 指令優先順序

使用者的指令會隨專題進度持續修正。**後面的指令優先於前面的**，衝突時以最新的為準，並同步更新本檔與相關程式／說明。

## 兩個資料來源，用途完全不同

| 資料夾 | 用途 | 網站是否讀取 |
| --- | --- | --- |
| `討論資料/` | 使用者拿來**跟 Claude 討論**的研究成果（目前是依主題分資料夾的資訊圖） | **否**，不發佈、不 import、不複製進網站 |
| `research-archive/` | **要放上網站**的內容 | 是 |

### 討論資料/
- 內容會持續滾動更新。凡是討論研究內容、概念、Persona、藍圖等，**每次都重新讀取這個資料夾**，不要依賴舊的記憶或舊的摘要。
- 資料夾與圖檔可能隨時新增、改名、刪除；以現況為準。
- 已列入 `.gitignore`，不要 commit 或推送。除非使用者明確要求，不要修改或搬動裡面的檔案。
- 使用者若要把其中某些圖放上網站，會另外指示，再複製到 `research-archive/` 對應階段資料夾。

### research-archive/（網站資料）
- `01_macro-background` 宏觀背景、`02_field-research` 田野調查、`03_scoping-personas` 範疇與 Persona、`04_service-blueprints` 服務藍圖、`05_concept-proposals` 概念提案。
- 圖片放進階段資料夾（可分子資料夾）即自動顯示；`database-index.js` 負責掃描與歸類；`meta.json` 放首頁願景、引言、成員、更新時間。
- 階段資料夾內舊的 `*-template.json`、`data/` 是早期 JSON 方案，網站已不讀取。

## 網站結構

- `src/pages/index.html`：首頁（Hero、概念、背景）；`process.html`：設計歷程（五階段 Tabs）。
- `src/components/archive-view.js`：把資料渲染成 HTML；`main.js` 依 `data-archive` 掛載點啟動。
- 白底、深灰文字、柔和淡藍點綴，色彩在 `src/assets/colors/tokens.css`。
- 頁面在 `src/pages`（Vite root），元件路徑用 `/components/...`（`vite.config.js` 有別名）。

## 指令

`npm run dev` 本機預覽、`npm run build` 建置、`npm run preview` 預覽建置結果。

## 注意

- commit / push 只在使用者要求時進行；改寫歷史與強制推送需明確同意。
- 不要使用 `git stash -u`（會連同未追蹤的 `討論資料/` 一起收走）。
