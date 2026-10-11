import '../styles/main.css';
import { renderNavbar, initNavbar } from './navbar.js';
import { renderFooter } from './footer.js';

// 頁面以 <div data-component="navbar" data-active="home"> 與 <div data-component="footer"> 作為掛載點
const nav = document.querySelector('[data-component="navbar"]');
if (nav) nav.outerHTML = renderNavbar(nav.dataset.active);

const footer = document.querySelector('[data-component="footer"]');
if (footer) footer.outerHTML = renderFooter();

initNavbar();
