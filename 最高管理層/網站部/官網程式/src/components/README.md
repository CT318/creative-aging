# components 模組化元件

- `site.config.js` 品牌名稱、導覽、社群等全站設定
- `navbar.js` 導覽列（含手機漢堡選單、Esc 關閉）
- `footer.js` 頁尾
- `main.js` 所有頁面共用入口：載入樣式並掛載元件

頁面以 `<div data-component="navbar" data-active="home">` 與 `<div data-component="footer">` 使用。
Hero、Card 等區塊目前為 HTML + `ui.css` 的 class，可自行抽成新的 JS 元件。
