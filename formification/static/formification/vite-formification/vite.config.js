import { defineConfig } from 'vite'

import prefixSelector from 'postcss-prefix-selector'

export default defineConfig({
  // Relative base: the bundle is served from
  // /static/formification/dist/ by Django; assets must resolve relative to it.
  base: './',
  css: {
    postcss: {
      plugins: [prefixSelector({
        prefix: '.formification-form',
        transform(prefix, selector, prefixed) {
          if (selector.startsWith(prefix)) return selector
          return selector === ':root' ? prefix : prefixed
        },
      })],
    },
  },

  server: {
    port: 5174,
    fs: {
      // Allow serving ../js sources during `npm run dev`.
      allow: ['..'],
    },
  },

  build: {
    outDir: '../dist',
    emptyOutDir: true,
    rollupOptions: {
      preserveEntrySignatures: 'strict',
      input: {
        form: 'src/form.js',
      },
      output: {
        entryFileNames: 'form.js',
        chunkFileNames: 'form-[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          const name = assetInfo.name || ''
          return name.endsWith('.css') ? 'form.css' : 'assets/[name]-[hash][extname]'
        },
      },
    },
  },
})