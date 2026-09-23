import { defineConfig } from 'vite'

// Drops Bootstrap 3's glyphicons `@font-face` rules (and the emitted font
// assets) — nothing in the form templates uses `glyphicon-*` classes.
const stripGlyphicons = () => ({
  name: 'strip-glyphicons',
  enforce: 'post',
  generateBundle(_options, bundle) {
    for (const [name, asset] of Object.entries(bundle)) {
      if (asset.type === 'asset' && asset.name?.includes('glyphicons-halflings-regular')) {
        delete bundle[name]
      }
    }
    for (const asset of Object.values(bundle)) {
      if (asset.type === 'asset' && typeof asset.source === 'string' && asset.name?.endsWith('.css')) {
        asset.source = asset.source.replace(/@font-face\{[^}]*\}/g, '')
      }
    }
  },
})

// Builds the public-facing form assets (intl-tel-input, bootstrap, jquery +
// this project's custom form JS) into formification/static/formification/dist,
// kept in sync with the committed dist convention used by the admin build.
export default defineConfig({
  // Relative base: the bundle is served from
  // /static/formification/dist/ by Django; assets must resolve relative to it.
  base: './',

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
      plugins: [stripGlyphicons()],
    },
  },
})