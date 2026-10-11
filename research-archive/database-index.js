// 網站資料中樞。
// 資料來源 = research-archive/01_ ~ 05_ 各階段資料夾裡的圖檔（要放上網站的內容）。
// 注意：專案根目錄的「討論資料/」是跟 Claude 討論用的素材，網站不讀取、不發佈。
// 丟新圖片進階段資料夾，存檔即自動出現，不需要改程式。
import meta from './meta.json';

// 階段定義（順序即網站顯示順序）。
export const STAGES = [
  { key: 'macro', title: '宏觀背景', subtitle: '社會結構轉折、問題因果鏈、研究起點' },
  { key: 'field', title: '田野調查', subtitle: '專家訪談、場域觀察、課堂量化數據' },
  { key: 'personas', title: '範疇與 Persona', subtitle: '範疇收斂路徑、族群象限、核心痛點' },
  { key: 'blueprints', title: '服務藍圖', subtitle: '使用者歷程、接觸點、介入機會' },
  { key: 'concepts', title: '概念提案', subtitle: '品牌定調、產品 / 服務概念與迭代演進' },
];
const OTHER = { key: 'other', title: '其他資料', subtitle: '尚未歸入階段的資料夾（在下方 FOLDER_STAGE 指定歸屬）' };

// research-archive/ 第一層資料夾 → 階段。以 01_ ~ 05_ 開頭的資料夾會自動歸入對應階段
// （01 宏觀背景 … 05 概念提案），階段資料夾內可再分子資料夾，子資料夾名稱會成為群組標題。
// 其他名稱的資料夾可在這裡加一行（資料夾名稱 → 階段 key）；都沒有的會顯示在「其他資料」。
export const FOLDER_STAGE = {};

const ROOT = './';
const files = import.meta.glob('./*/**/*.{jpg,jpeg,png,webp,gif,avif,svg}', {
  eager: true,
  query: '?url',
  import: 'default',
});

const collator = new Intl.Collator('zh-Hant', { numeric: true });

function stageOf(top) {
  if (FOLDER_STAGE[top]) return FOLDER_STAGE[top];
  const n = /^0?([1-5])[_\-\s.]/.exec(top)?.[1];
  return n ? STAGES[n - 1].key : OTHER.key;
}

const items = Object.entries(files).map(([path, url]) => {
  const parts = path.slice(ROOT.length).split('/');
  const file = parts.pop();
  return {
    url,
    name: file.replace(/\.[^.]+$/, ''),
    group: parts.slice(1).join(' › '),
    stage: stageOf(parts[0] || ''),
  };
});
items.sort((a, b) => collator.compare(a.group, b.group) || collator.compare(a.name, b.name));

function build(stage) {
  const own = items.filter((i) => i.stage === stage.key);
  const groups = [];
  for (const item of own) {
    let g = groups.find((x) => x.label === item.group);
    if (!g) groups.push((g = { label: item.group, items: [] }));
    g.items.push(item);
  }
  return { ...stage, groups, count: own.length, ready: own.length > 0 };
}

const stages = STAGES.map(build);
const other = build(OTHER);
if (other.ready) stages.push(other);

export const archive = {
  meta,
  stages,
  // 手動指定優先；否則用網站建置 / 開發伺服器啟動日期。
  updatedAt: meta.updatedAt || __BUILD_DATE__,
};

export const getStage = (key) => stages.find((s) => s.key === key);
