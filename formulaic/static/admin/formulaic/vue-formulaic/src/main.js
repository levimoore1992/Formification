import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { useFormStore } from './stores/form'

createApp(App).use(createPinia()).use(router).mount('#formulaic-container')

// Kick off the initial data load. The form id comes from the injected meta tag
// (boot.js), with a `?formId=` query-param fallback for the standalone dev server.
const formStore = useFormStore()
formStore.load()