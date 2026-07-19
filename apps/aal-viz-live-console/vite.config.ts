import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, '../..');

export default defineConfig({
  plugins: [react()],
  root: '.',
  // Abraxas Visual OS tokens live at repo design-system/
  resolve: {
    alias: {
      '@abx-design': path.join(repoRoot, 'design-system'),
    },
  },
  build: {
    outDir: 'dist',
    manifest: true,
    rollupOptions: {
      output: {
        manualChunks: {
          cytoscape: ['cytoscape'],
        },
      },
    },
  },
  server: {
    port: 5174,
    host: '127.0.0.1',
    allowedHosts: ['localhost'],
    fs: {
      allow: [repoRoot],
    },
  },
});
