# 05 概念提案（Concept Proposals）

**定位**：產品概念發想、硬體 / 數位 / 服務提案規格、概念迭代演進歷史。

## 記錄內容

- **角色分工**：每個概念在整體方案中負責什麼（`role`），屬於哪一類（`type`：`hardware` / `digital` / `service`）。
- **Persona 覆蓋**：概念服務哪些 Persona（`personas`）、對應哪些痛點（`painPoints`）。
- **規格**：硬體尺寸材質、數位功能、服務流程等（`specs`）。
- **演進**：每次改版改了什麼、為什麼（`iterations`），保留完整歷史，不要覆蓋舊紀錄。

## 怎麼記

1. 一個概念 = `data/` 裡一個檔案，複製 `concepts-template.json`。
2. `status` 設為 **`converged`** 的概念會出現在首頁「三大支柱」卡片；其他狀態只在設計歷程頁出現。
3. `personas` 的代號要和 03 階段一致。
4. 概念被放棄時不要刪檔，把 `status` 改成 `archived`，並在 `iterations` 記錄原因，歷程頁才看得到演進。
