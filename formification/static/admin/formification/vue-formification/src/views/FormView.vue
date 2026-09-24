<template>
  <div class="vue-formification">
    <header class="form-header">
      <div>
        <p class="form-eyebrow">Form builder</p>
        <h1>{{ formStore.displayName }}</h1>
      </div>
      <p v-if="formStore.form" class="form-meta"><span>URL slug</span><code>{{ formStore.form.slug }}</code></p>
    </header>

    <nav class="form-tabs">
      <RouterLink to="/details">Details</RouterLink>
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
.vue-formification {
  max-width: 1220px;
  padding: 1.25rem 1.5rem 2.5rem;
}
.form-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1.1rem;
}
.form-eyebrow {
  margin: 0 0 0.2rem;
  color: var(--f-accent);
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.form-header h1 {
  margin: 0;
  font-family: var(--f-font-display);
  font-size: 1.45rem;
  font-weight: 500;
  line-height: 1.25;
  letter-spacing: -0.01em;
}
.form-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 0.15rem;
  font-size: 0.8125rem;
  color: var(--f-muted);
}
.form-meta span { font-weight: 600; }
.form-meta code {
  padding: 0.05rem 0.35rem;
  font-family: var(--f-font-mono);
  font-size: 0.75rem;
  color: var(--f-muted);
  background: var(--f-canvas);
  border: 1px solid var(--f-line);
  border-radius: 4px;
}
.form-tabs {
  display: flex;
  gap: 0;
  border: 1px solid var(--f-line-strong);
  border-bottom-color: var(--f-accent-deep);
  border-radius: var(--f-radius) var(--f-radius) 0 0;
  background: var(--f-canvas);
  margin-bottom: 1.5rem;
}
.form-tabs a {
  padding: 0.65rem 1rem;
  text-decoration: none;
  color: var(--f-muted);
  font-size: 0.875rem;
  font-weight: 500;
  border-right: 1px solid var(--f-line);
  transition: color 150ms ease, background-color 150ms ease;
}
.form-tabs a:hover {
  color: var(--f-accent-deep);
  background: var(--f-accent-tint);
}
.form-tabs a.router-link-active {
  color: #fff;
  background: var(--f-accent-deep);
}
.form-tabs a:focus-visible {
  outline: 2px solid var(--f-accent);
  outline-offset: 4px;
  border-radius: 4px;
}
@media (max-width: 700px) {
  .vue-formification { padding: 1rem 0.75rem 2rem; }
  .form-header { align-items: flex-start; flex-direction: column; }
  .form-tabs { overflow-x: auto; }
  .form-tabs a { flex: 1 0 auto; text-align: center; }
}
.form-error {
  color: var(--f-danger-deep);
  background: var(--f-danger-tint);
  border: 1px solid rgba(176, 59, 48, 0.35);
  border-radius: var(--f-radius-sm);
  padding: 0.6rem 0.85rem;
}
</style>
