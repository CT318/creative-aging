import { site, brand } from './site.config.js';
import { archive } from '../data/database-index.js';
import { esc } from './archive-view.js';

export function renderFooter() {
  const year = new Date().getFullYear();
  const updatedAt = archive.updatedAt;
  const links = site.nav.map((l) => `<li><a href="${l.href}">${esc(l.label)}</a></li>`).join('');
  const members = brand.members.length
    ? `<div><strong>專案成員</strong><p class="muted">${brand.members.map(esc).join('、')}</p></div>`
    : '';
  return `
  <footer class="footer">
    <div class="container">
      <div class="footer__grid">
        <div>
          <strong class="footer__brand">${esc(brand.name)}</strong>
          ${brand.tagline ? `<p>${esc(brand.tagline)}</p>` : ''}
          ${brand.descriptor ? `<p class="muted">${esc(brand.descriptor)}</p>` : ''}
        </div>
        <div>
          <strong>瀏覽</strong>
          <ul class="footer__links">${links}</ul>
        </div>
        ${members}
      </div>
      <p class="footer__copy">© ${year} ${esc(brand.name)}${updatedAt ? ` · 資料更新時間：${esc(updatedAt)}` : ''}</p>
    </div>
  </footer>`;
}
