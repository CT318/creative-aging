# 網站部
- `官網程式/`：官網與研究歷程展示站。在該資料夾執行 `npm install`、`npm run dev`、`npm run build`、`npm run preview`。網站讀取 `../../調研部/research-archive/`（圖片）與 `../../品牌部/site-content/meta.json`（首頁文字），不讀 `討論資料/`。資料中樞為 `src/data/database-index.js`。
- `秘書部/`：本部進度與決策。
部署由根目錄 `.github/workflows/deploy.yml` 負責（GitHub 規定 workflows 必須在根目錄）。
