# research-archive

**要放上網站的內容**。網站只讀這裡（以及 `meta.json`），不讀專案根目錄的 `討論資料/`。

- `01_macro-background/` … `05_concept-proposals/`：五個階段資料夾。把要展示的圖片放進對應資料夾（可再分子資料夾，子資料夾名稱會成為群組標題），存檔即自動出現在首頁與設計歷程頁。
- `database-index.js`：掃描上述圖片並歸類；`FOLDER_STAGE` 可把其他名稱的資料夾歸入階段，未歸類的顯示在「其他資料」。
- `meta.json`：首頁 Hero 的願景、引言、成員、更新時間（`updatedAt` 留空則用建置日期）。

圖片依名稱排序（數字依大小），圖說就是檔名（不含副檔名）。

## 舊檔

各階段資料夾內的 `*-template.json`、`data/` 屬於早期 JSON 方案，目前不被讀取。
