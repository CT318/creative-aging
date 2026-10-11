import { site } from './site.config.js';

// active: 'home' | 'process' (用於標示目前頁面)
export function renderNavbar(active) {
  const links = site.nav
    .map((l) => `<a class="navbar__link" href="${l.href}"${l.key === active ? ' aria-current="page"' : ''}>${l.label}</a>`)
    .join('');
  return `
  <header class="navbar">
    <div class="container navbar__inner">
      <a class="navbar__logo" href="./index.html">${site.brand}</a>
      <button class="navbar__toggle" type="button" aria-label="開啟選單" aria-expanded="false" aria-controls="nav-menu"><span></span></button>
      <nav class="navbar__menu" id="nav-menu" aria-label="主選單">
        ${links}
        <a class="btn btn--sm navbar__cta" href="${site.cta.href}">${site.cta.label}</a>
      </nav>
    </div>
  </header>`;
}

export function initNavbar(root = document) {
  const nav = root.querySelector('.navbar');
  const btn = nav?.querySelector('.navbar__toggle');
  if (!btn) return;
  const setOpen = (open) => {
    nav.classList.toggle('is-open', open);
    btn.setAttribute('aria-expanded', String(open));
    btn.setAttribute('aria-label', open ? '關閉選單' : '開啟選單');
  };
  btn.addEventListener('click', () => setOpen(!nav.classList.contains('is-open')));
  nav.querySelectorAll('.navbar__menu a').forEach((a) => a.addEventListener('click', () => setOpen(false)));
  document.addEventListener('keydown', (e) => e.key === 'Escape' && setOpen(false));
}
