// 把 research-archive 階段資料夾的圖檔渲染成 HTML。這裡不放任何專案文字。
import { archive, getStage } from '../data/database-index.js';
import { brand, products } from './site.config.js';

const TBD = '[待填入最新調研資料]';

export const esc = (v) =>
  String(v ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);

/* ---------- 共用：圖片群組 ---------- */

function renderFigure(item, group) {
  return `
  <figure class="figure">
    <button class="figure__open" type="button" data-full="${esc(item.url)}" data-caption="${esc(!group.label ? item.name : `${group.label} › ${item.name}`)}" aria-label="放大檢視：${esc(item.name)}">
      <img src="${esc(item.url)}" alt="${esc(`${group.label} ${item.name}`)}" loading="lazy" />
    </button>
    <figcaption>${esc(item.name)}</figcaption>
  </figure>`;
}

function renderGroups(stage, { showLabel = true } = {}) {
  return stage.groups
    .map(
      (g) => `
    <div class="group">
      ${showLabel && g.label ? `<h3 class="group__title">${esc(g.label)}</h3>` : ''}
      <div class="gallery ${g.items.length > 1 ? 'gallery--multi' : ''}">${g.items.map((i) => renderFigure(i, g)).join('')}</div>
    </div>`
    )
    .join('');
}

function renderPending(stage) {
  return `
  <article class="card card--placeholder progress">
    <span class="badge">資料收斂中</span>
    <h3>${esc(stage.title)}：研究進行中 / 資料收斂中</h3>
    <p class="muted">${TBD}</p>
    <p class="muted">把圖片放進 調研部/research-archive/ 對應的階段資料夾後，會自動顯示在這裡。</p>
  </article>`;
}

// 首頁用：取某階段的圖片。data-archive="gallery" data-stage="concepts"
export function renderGallery(root) {
  const stage = getStage(root.dataset.stage);
  root.innerHTML = !stage ? '' : stage.ready ? renderGroups(stage, { showLabel: stage.groups.length > 1 }) : renderPending(stage);
  initLightbox(root);
}

// 首頁 Hero：品牌名（字標）、標語、描述語、願景，全部來自 meta.json；缺哪欄就不顯示哪欄。
export function renderHero(root) {
  const set = (name, text) => {
    const el = root.querySelector(`[data-bind="${name}"]`);
    if (!el) return;
    if (text) el.textContent = text;
    else el.remove();
  };
  set('brand', brand.name);
  set('tagline', brand.tagline);
  set('descriptor', brand.descriptor);
  set('vision', brand.vision);
}

// 品牌理念：願景（大字）＋引言；兩者皆空則整區隱藏。
export function renderStatement(root) {
  if (!brand.vision && !brand.quote) { root.remove(); return; }
  const vision = root.querySelector('[data-bind="vision"]');
  if (brand.vision) vision.textContent = brand.vision; else vision.remove();
  const q = root.querySelector('.hero__quote');
  if (!brand.quote) { q.remove(); return; }
  q.querySelector('[data-bind="quote"]').textContent = brand.quote;
  const author = q.querySelector('[data-bind="quote-author"]');
  if (brand.quoteAuthor) author.textContent = `— ${brand.quoteAuthor}`; else author.remove();
}

// 產品卡：資料來自 products.json；圖片留空位固定 4:3，空圖不顯示文字；summary / link 空則不顯示。
export function renderProducts(root) {
  if (!products.length) { root.remove(); return; }
  root.querySelector('.products__grid').innerHTML = products
    .map(
      (p) => `
    <article class="pcard">
      <div class="pcard__img">${p.image ? `<img src="${esc(p.image)}" alt="${esc(p.name)}" loading="lazy" />` : ''}</div>
      <div class="pcard__body">
        <h3 class="pcard__name">${esc(p.name)}</h3>
        ${p.summary ? `<p class="pcard__summary">${esc(p.summary)}</p>` : ''}
        ${p.link ? `<a class="btn btn--sm btn--ghost" href="${esc(p.link)}">了解更多</a>` : ''}
      </div>
    </article>`
    )
    .join('');
}

// 首頁底部「研究歷程」小入口：列出有資料的階段，連到研究歷程頁對應階段。
export function renderStageEntry(root) {
  const ready = archive.stages.filter((s) => s.ready);
  if (!ready.length) { root.closest('section')?.remove(); return; }
  root.innerHTML = ready.map((s) => `<li><a href="./process.html#${esc(s.key)}">${esc(s.title)}</a></li>`).join('');
}

/* ---------- 設計歷程頁：Tabs ---------- */

export function renderProcess(root) {
  const tabs = archive.stages
    .map(
      (s, i) => `
      <button class="tab" role="tab" id="tab-${s.key}" aria-controls="panel-${s.key}" aria-selected="${i === 0}" tabindex="${i === 0 ? 0 : -1}" data-key="${s.key}">
        <span class="tab__no">${String(i + 1).padStart(2, '0')}</span>
        <span class="tab__title">${esc(s.title)}</span>
        ${s.ready ? `<span class="tab__count">${s.count}</span>` : ''}
      </button>`
    )
    .join('');
  const panels = archive.stages
    .map(
      (s, i) => `
      <section class="panel" role="tabpanel" id="panel-${s.key}" aria-labelledby="tab-${s.key}" ${i === 0 ? '' : 'hidden'}>
        <div class="section__head"><span class="eyebrow">第 ${String(i + 1).padStart(2, '0')} 階段</span><h2>${esc(s.title)}</h2><p class="muted">${esc(s.subtitle)}</p></div>
        ${s.ready ? renderGroups(s) : renderPending(s)}
      </section>`
    )
    .join('');
  root.innerHTML = `<div class="tabs" role="tablist" aria-label="研究階段">${tabs}</div>${panels}`;
  initTabs(root);
  initLightbox(root);
}

function initTabs(root) {
  const tabs = [...root.querySelectorAll('[role="tab"]')];
  const select = (tab, focus) => {
    tabs.forEach((t) => {
      const on = t === tab;
      t.setAttribute('aria-selected', String(on));
      t.tabIndex = on ? 0 : -1;
      root.querySelector(`#panel-${t.dataset.key}`).hidden = !on;
    });
    if (focus) tab.focus();
    history.replaceState(null, '', `#${tab.dataset.key}`);
  };
  tabs.forEach((t, i) => {
    t.addEventListener('click', () => select(t));
    t.addEventListener('keydown', (e) => {
      const dir = { ArrowRight: 1, ArrowLeft: -1 }[e.key];
      if (dir) { e.preventDefault(); select(tabs[(i + dir + tabs.length) % tabs.length], true); }
    });
  });
  const initial = tabs.find((t) => `#${t.dataset.key}` === location.hash);
  if (initial) select(initial);
}

/* ---------- 圖片放大 ---------- */

let dialog;
function initLightbox(root) {
  if (!dialog) {
    dialog = document.createElement('dialog');
    dialog.className = 'lightbox';
    dialog.innerHTML = `<form method="dialog"><button class="lightbox__close" aria-label="關閉">×</button></form><img alt="" /><p class="lightbox__cap"></p>`;
    dialog.addEventListener('click', (e) => e.target === dialog && dialog.close());
    document.body.append(dialog);
  }
  root.querySelectorAll('.figure__open').forEach((btn) =>
    btn.addEventListener('click', () => {
      const img = dialog.querySelector('img');
      img.src = btn.dataset.full;
      img.alt = btn.dataset.caption;
      dialog.querySelector('.lightbox__cap').textContent = btn.dataset.caption;
      dialog.showModal();
    })
  );
}
