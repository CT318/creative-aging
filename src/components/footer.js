import { site } from './site.config.js';

export function renderFooter() {
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
          <strong>社群</strong>
          <ul class="footer__links">${social}</ul>
        </div>
        <div>
          <strong>聯絡方式</strong>
          <p><a href="mailto:${site.email}">${site.email}</a></p>
        </div>
      </div>
      <p class="footer__copy">© ${year} ${site.brand}. All rights reserved.</p>
    </div>
  </footer>`;
}
