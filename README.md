# Brand & Design Archive 公版

可重複使用的「品牌官方網站暨設計研究歷程」公版。技術：Vite + 原生 HTML/CSS/JS（唯一依賴為 Vite）。

## 指令

```bash
npm install        # 安裝依賴
npm run dev        # 本機預覽 (已開放區網，手機同 Wi-Fi 可掃 QR Code / 輸入 Network 網址)
npm run build      # 輸出至 dist/
npm run preview    # 預覽建置結果
```

## 資料夾結構

```text
.github/workflows/deploy.yml   GitHub Pages 自動部署
docs/brand-guidelines/         品牌理念、價值、語氣調性
docs/design-process/           設計歷程文件範本
src/assets/                    風格素材庫 (colors / typography / components-ui / backgrounds / placeholders)
src/components/                site.config.js、navbar、footer、main.js
src/styles/main.css            全域樣式、版面、導覽列、時間軸
src/pages/                     index.html、process.html
public/                        favicon、QR Code 等靜態資源 (原樣複製到 dist)
```

## 套用到新主題

1. `src/components/site.config.js`：品牌名稱、標語、導覽、社群、信箱。
2. `src/assets/colors/tokens.css`、`typography/fonts.css`：色彩與字型。
3. 修改 `src/pages/*.html` 的佔位文字，並以真實圖片取代 `placeholders/`。
4. 新增頁面：在 `src/pages/` 建立 html，並加入 `vite.config.js` 的 `build.rollupOptions.input`。
5. 於 `docs/` 撰寫品牌準則與設計歷程文件。

## 推送到 GitHub 並啟用 Pages

```bash
git init
git add .
git commit -m "Initial commit: brand archive boilerplate"
git branch -M main
git remote add origin https://github.com/<帳號>/<repo>.git
git push -u origin main
```

接著到 GitHub：**Settings → Pages → Build and deployment → Source 選 "GitHub Actions"**。
之後每次 push 到 `main` 會自動部署，網址為 `https://<帳號>.github.io/<repo>/`。
把此網址做成 QR Code 存入 `public/` 即可供掃描。
