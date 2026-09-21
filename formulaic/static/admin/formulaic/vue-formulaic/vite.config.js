import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Target Django dev server. `manage.py runserver` serves on :8000.
const DJANGO_DEV = 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [vue()],

  // Relative base: the built index.html is served from
  // /static/admin/formulaic/vue-formulaic/dist/ by Django, and every asset
  // must resolve relative to that URL (no absolute root path assumption).
  base: './',

  server: {
    port: 5173,
    proxy: {
      // Proxy the DRF API + admin so `npm run dev` works standalone against a
      // running Django. The active Django session cookie (localhost, host-only)
      // is forwarded automatically, so you log in on :8000 once and reuse it.
      '/formulaic': DJANGO_DEV,
      '/admin': DJANGO_DEV,
    },
  },

  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
})