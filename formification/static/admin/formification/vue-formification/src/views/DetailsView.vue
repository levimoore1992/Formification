<template>
  <form class="form-details" @submit.prevent="save">
    <div class="page-heading">
      <div>
        <h2>Form details</h2>
        <p>Set the internal name, URL identifier, and message shown after submission.</p>
      </div>
      <span v-if="store.form" class="object-id">Form #{{ store.form.id }}</span>
    </div>
    <p v-if="error" role="alert"><strong>Could not save.</strong> {{ error }}</p>
    <p v-if="saved" role="status"><strong>Saved.</strong> Form details are up to date.</p>
    <template v-if="store.form">
      <fieldset class="module aligned">
        <legend>Identity</legend>
        <div class="form-row">
          <label for="form-name" class="required">Name</label>
          <div class="field-box">
            <input id="form-name" v-model.trim="draft.name" required maxlength="500" />
            <p class="help">The name staff see in the form list and editor.</p>
          </div>
        </div>
        <div class="form-row">
          <label for="form-slug" class="required">Slug</label>
          <div class="field-box">
            <input id="form-slug" v-model.trim="draft.slug" required maxlength="200" class="monospace" />
            <p class="help">Used in URLs and integrations. Use letters, numbers, hyphens, and underscores.</p>
          </div>
        </div>
      </fieldset>

      <fieldset class="module aligned">
        <legend>After submission</legend>
        <div class="form-row">
          <label for="success-message">Success message</label>
          <div class="field-box">
            <textarea id="success-message" v-model="draft.success_message" rows="7" />
            <p class="help">Shown to a visitor after their response is accepted.</p>
          </div>
        </div>
      </fieldset>

      <div class="submit-row">
        <button type="submit" class="btn btn-primary" :disabled="saving">{{ saving ? 'Saving…' : 'Save changes' }}</button>
      </div>
    </template>
  </form>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
import { client } from '../api/client'
import { useFormStore } from '../stores/form'

const store = useFormStore()
const draft = reactive({ name: '', slug: '', success_message: '' })
const saving = ref(false)
const saved = ref(false)
const error = ref('')
watch(() => store.form, (form) => {
  if (form) Object.assign(draft, {
    name: form.name, slug: form.slug, success_message: form.success_message || '',
  })
}, { immediate: true })
if (!store.form && !store.loading) store.load()

async function save() {
  saving.value = true
  saved.value = false
  error.value = ''
  try {
    store.form = await client.updateForm(store.formId, { ...draft })
    saved.value = true
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.form-details {
  max-width: 900px;
}
.page-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
}
.page-heading h2 {
  margin: 0 0 0.25rem;
  font-family: var(--f-font-display);
  font-size: 1.2rem;
  font-weight: 500;
}
.page-heading p { margin: 0; color: var(--f-muted); font-size: 0.85rem; }
.object-id {
  padding: 0.3rem 0.5rem;
  color: var(--f-muted);
  background: var(--f-canvas);
  border: 1px solid var(--f-line);
  border-radius: var(--f-radius-sm);
  font-family: var(--f-font-mono);
  font-size: 0.72rem;
  white-space: nowrap;
}
.module {
  padding: 0;
  margin: 0 0 1.25rem;
  border: 1px solid var(--f-line-strong);
  border-radius: var(--f-radius);
  background: var(--f-surface);
  box-shadow: var(--f-shadow);
  overflow: hidden;
}
.module legend {
  display: block;
  width: 100%;
  padding: 0.55rem 0.75rem;
  color: #fff;
  background: var(--f-accent);
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}
.form-row {
  display: grid;
  grid-template-columns: 150px minmax(0, 1fr);
  gap: 1rem;
  padding: 0.85rem 1rem;
  border-bottom: 1px solid var(--f-line);
}
.form-row:last-child { border-bottom: 0; }
.form-row > label {
  padding-top: 0.5rem;
  color: var(--f-ink);
  font-size: 0.82rem;
  font-weight: 600;
  text-align: right;
}
.form-row > label.required::after { content: ' *'; color: var(--f-danger); }
.field-box { max-width: 650px; }
.help { margin: 0.4rem 0 0; color: var(--f-muted); font-size: 0.78rem; line-height: 1.45; }
.monospace { font-family: var(--f-font-mono); }
.submit-row {
  display: flex;
  justify-content: flex-end;
  padding: 0.75rem;
  background: var(--f-canvas);
  border: 1px solid var(--f-line);
  border-radius: var(--f-radius);
}
input,
textarea {
  display: block;
  width: 100%;
  box-sizing: border-box;
  padding: 0.55rem 0.7rem;
  font-family: var(--f-font-ui);
  font-size: 0.9375rem;
  line-height: 1.5;
  color: var(--f-ink);
  background: var(--f-surface);
  border: 1px solid var(--f-line-strong);
  border-radius: var(--f-radius-sm);
  transition: border-color 150ms ease, box-shadow 150ms ease;
}
input:hover,
textarea:hover {
  border-color: var(--f-soft);
}
input:focus,
textarea:focus {
  border-color: var(--f-accent);
  outline: none;
  box-shadow: 0 0 0 3px var(--f-focus-ring);
}
[role="alert"] {
  color: var(--f-danger-deep);
  background: var(--f-danger-tint);
  border: 1px solid rgba(176, 59, 48, 0.35);
  border-radius: var(--f-radius-sm);
  padding: 0.6rem 0.85rem;
  font-size: 0.875rem;
}
[role="status"] {
  color: var(--f-success);
  background: var(--f-success-tint);
  border: 1px solid rgba(47, 125, 79, 0.35);
  border-radius: var(--f-radius-sm);
  padding: 0.6rem 0.85rem;
  font-size: 0.875rem;
}
.btn {
  padding: 0.55rem 1.1rem;
  border: 1px solid var(--f-line-strong);
  border-radius: var(--f-radius-sm);
  background: var(--f-surface);
  color: var(--f-ink);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: border-color 150ms ease, background-color 150ms ease, color 150ms ease;
}
.btn:hover {
  border-color: var(--f-soft);
  background: var(--f-canvas);
}
.btn-primary {
  background: var(--f-accent);
  border-color: var(--f-accent);
  color: #fff;
}
.btn-primary:hover {
  background: var(--f-accent-deep);
  border-color: var(--f-accent-deep);
  color: #fff;
}
.btn:focus-visible {
  outline: 2px solid var(--f-accent);
  outline-offset: 2px;
}
.btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
@media (max-width: 640px) {
  .page-heading { flex-direction: column; }
  .form-row { grid-template-columns: 1fr; gap: 0.35rem; }
  .form-row > label { padding-top: 0; text-align: left; }
}
</style>
