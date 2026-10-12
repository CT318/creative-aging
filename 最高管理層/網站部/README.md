# 網站部
- `官網程式/`：官網與研究歷程展示站。在該資料夾執行 `npm install`、`npm run dev`、`npm run build`、`npm run preview`。網站讀取 `../../調研部/research-archive/`（圖片）與 `../../品牌部/site-content/meta.json`（首頁文字），不讀 `討論資料/`。資料中樞為 `src/data/database-index.js`。
- `秘書部/`：本部進度與決策。
部署由根目錄 `.github/workflows/deploy.yml` 負責（GitHub 規定 workflows 必須在根目錄）。
- `改版規劃/`：官網改版方案與規劃文件（`改版方案.md`，待 CEO 簽核）。
- 2026-10-12 階段一（品牌殼）完成：品牌文字（旬常／標語／描述語／願景／引言）全由 `meta.json` 讀取，程式不寫死；導覽目前只有「首頁、研究歷程」，關於／產品／聯絡待有資料再做；首頁為 Hero＋引言＋研究歷程入口，概念／背景圖庫併入研究歷程頁。
- 2026-10-12 階段一調整（版面與字體，仿羅技台灣官網的版面數值）：內容最大寬 1568px、左右內距 16/32/64px；字體改為自行託管的 Noto Sans TC（npm 套件 `@fontsource-variable/noto-sans-tc`，不連 Google）；首頁為滿版 Hero 視覺區（圖片位置留空）＋品牌理念＋產品卡（讀 `品牌部/site-content/products.json`，無檔或無產品自動隱藏，圖放 `site-content/images/`）＋底部研究歷程小入口。
