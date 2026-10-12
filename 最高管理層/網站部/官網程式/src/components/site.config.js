// 網站全域設定 — 品牌文字一律由 品牌部/site-content/meta.json 讀取，這裡不寫死任何品牌名或標語。
// 導覽只放「目前有內容」的項目；新頁面（關於、產品、聯絡）有資料後再加進來。
import meta from '../../../../品牌部/site-content/meta.json';

const clean = (v) => (typeof v === 'string' && v.trim() && !v.trim().startsWith('[') ? v.trim() : '');

export const brand = {
  name: clean(meta.brandName),
  tagline: clean(meta.tagline),
  descriptor: clean(meta.descriptor),
  vision: clean(meta.vision),
  quote: clean(meta.quote),
  quoteAuthor: clean(meta.quoteAuthor),
  members: (meta.members || []).filter((m) => clean(m)),
  updatedAt: clean(meta.updatedAt),
};

export const site = {
  nav: [
    { key: 'home', label: '首頁', href: './index.html' },
    { key: 'process', label: '研究歷程', href: './process.html' },
  ],
};

// 依頁面 <body data-title="頁名"> 設定分頁標題與描述（品牌文字來自 meta.json）
export function applyDocumentMeta() {
  const page = document.body.dataset.title;
  const parts = [page, brand.name].filter(Boolean);
  if (parts.length) document.title = parts.join('｜');
  const desc = [brand.name, brand.tagline, brand.descriptor].filter(Boolean).join('｜');
  const tag = document.querySelector('meta[name="description"]');
  if (tag && desc) tag.setAttribute('content', desc);
}

// 產品：品牌部/site-content/products.json（{"products":[{id,name,summary,image,link}]}）。
// 檔案不存在或沒有產品時回傳空陣列（首頁產品區塊自動隱藏）。不在程式內寫任何產品名。
const productFiles = import.meta.glob('../../../../品牌部/site-content/products.json', { eager: true });
const productImages = import.meta.glob('../../../../品牌部/site-content/images/**/*.{jpg,jpeg,png,webp,avif,svg}', { eager: true, query: '?url', import: 'default' });
const resolveImage = (name) => {
  const v = clean(name);
  if (!v) return '';
  if (/^(https?:)?\/\//.test(v) || v.startsWith('/') || v.startsWith('data:')) return v;
  const base = v.split('/').pop();
  const hit = Object.entries(productImages).find(([path]) => path.endsWith('/' + base));
  return hit ? hit[1] : '';
};
const rawProducts = Object.values(productFiles)[0];
export const products = ((rawProducts && (rawProducts.default || rawProducts).products) || [])
  .map((p) => ({ id: clean(p.id), name: clean(p.name), summary: clean(p.summary), image: resolveImage(p.image), link: clean(p.link) }))
  .filter((p) => p.name);
