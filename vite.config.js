import { defineConfig } from 'vite';
import { resolve } from 'node:path';

// 頁面放在 src/pages，因此以它作為 Vite root。
// base './' 讓建置結果可部署在 GitHub Pages 任意子路徑 (https://user.github.io/repo/)。
export default defineConfig({
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
