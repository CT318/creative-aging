// 把 research-archive 階段資料夾的圖檔渲染成 HTML。這裡不放任何專案文字。
import { archive, getStage } from '../data/database-index.js';
import heroPlaceholder from '../assets/placeholders/ph-4x3.svg';

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

export function renderHero(root) {
  const { vision, quote, quoteAuthor } = archive.meta;
  root.querySelector('[data-bind="vision"]').textContent = vision || TBD;
  root.querySelector('[data-bind="quote"]').textContent = quote || TBD;
  root.querySelector('[data-bind="hero-image"]').src = heroPlaceholder;
  const author = root.querySelector('[data-bind="quote-author"]');
  if (quoteAuthor) author.textContent = `— ${quoteAuthor}`;
  else author.remove();
}

export function renderFooterMeta() {
  const { members } = archive.meta;
  return { members: members?.length ? members : [TBD], updatedAt: archive.updatedAt };
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
        <div class="section__head"><span class="eyebrow">STAGE ${String(i + 1).padStart(2, '0')}</span><h2>${esc(s.title)}</h2><p class="muted">${esc(s.subtitle)}</p></div>
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
