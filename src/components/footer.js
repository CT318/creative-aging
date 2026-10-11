import { site } from './site.config.js';
import { renderFooterMeta, esc } from './archive-view.js';

export function renderFooter() {
  const { members, updatedAt } = renderFooterMeta();
  const social = site.social.map((s) => `<li><a href="${s.href}">${s.label}</a></li>`).join('');
  const year = new Date().getFullYear();
  return `
  <footer class="footer">
    <div class="container">
      <div class="footer__grid">
        <div>
          <strong>${site.brand}</strong>
          <p class="muted">${site.tagline}</p>
        </div>
        <div>
          <strong>專案成員</strong>
          <p class="muted">${members.map(esc).join('、')}</p>
        </div>
        <div>
          <strong>社群</strong>
          <ul class="footer__links">${social}</ul>
        </div>
      </div>
      <p class="footer__copy">© ${year} ${site.brand}. All rights reserved. · 資料更新時間：${updatedAt ? esc(updatedAt) : '[待填入]'}</p>
    </div>
  </footer>`;
}
