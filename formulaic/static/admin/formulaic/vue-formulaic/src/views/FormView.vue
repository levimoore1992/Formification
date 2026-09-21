<template>
  <div class="vue-formulaic">
    <header class="form-header">
      <h1>{{ formStore.displayName }}</h1>
      <p v-if="formStore.form" class="form-meta">
        slug: <code>{{ formStore.form.slug }}</code>
        — archive/unarchive actions live on the form changelist
        (admin.py `form_actions`)
      </p>
    </header>

    <nav class="form-tabs">
      <RouterLink to="/fields">Fields</RouterLink>
      <RouterLink to="/rules">Rules</RouterLink>
      <RouterLink to="/submissions">Submissions</RouterLink>
    </nav>

    <section class="form-content">
      <p v-if="formStore.error" class="form-error">
        Failed to load form: {{ formStore.error }}
      </p>
      <RouterView />
    </section>
  </div>
</template>

<script setup>
// Layout for a single form: the route shell that hosts the fields/rules/
// submissions tabs. Each tab is a <router-view> backed by a Pinia store.

import { RouterLink, RouterView } from 'vue-router'

import { useFormStore } from '../stores/form'

const formStore = useFormStore()
</script>

<style scoped>
.vue-formulaic {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  padding: 1rem 2rem 2rem;
}
.form-header h1 {
  margin: 0 0 0.25rem;
  font-size: 1.4rem;
}
.form-meta {
  margin: 0 0 1rem;
  color: #666;
}
.form-tabs {
  display: flex;
  gap: 0.5rem;
  border-bottom: 1px solid #ddd;
  margin-bottom: 1rem;
}
.form-tabs a {
  padding: 0.5rem 1rem;
  text-decoration: none;
  color: #333;
  border-bottom: 2px solid transparent;
}
.form-tabs a.router-link-active {
  border-bottom-color: #2f80ed;
  color: #2f80ed;
}
.form-error {
  color: #c0392b;
}
</style>