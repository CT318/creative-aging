import { defineConfig } from 'vite';
import { resolve } from 'node:path';

// 頁面放在 src/pages，因此以它作為 Vite root。
// base './' 讓建置結果可部署在 GitHub Pages 任意子路徑 (https://user.github.io/repo/)。
const buildDate = new Date().toISOString().slice(0, 10);

export default defineConfig({
  resolve: {
    // 頁面在 src/pages，但元件與素材在 src/ 下：用別名讓 dev 與 build 都找得到。
    alias: {
      '/components': resolve(__dirname, 'src/components'),
    },
  },
  define: { __BUILD_DATE__: JSON.stringify(buildDate) },
  root: resolve(__dirname, 'src/pages'),
  base: './',
  publicDir: resolve(__dirname, 'public'),
  server: {
    host: true, // 允許同一 Wi-Fi 下用手機 / QR Code 開啟預覽
    fs: { allow: [resolve(__dirname)] },
  },
  build: {
    outDir: resolve(__dirname, 'dist'),
    emptyOutDir: true,
    rollupOptions: {
      input: {
        index: resolve(__dirname, 'src/pages/index.html'),
        process: resolve(__dirname, 'src/pages/process.html'),
      },
    },
  },
});
