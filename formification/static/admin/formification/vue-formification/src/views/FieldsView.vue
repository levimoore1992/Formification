<template>
  <div class="fields-layout">
    <!-- Left: the ordered list of fields ----------------------------------- -->
    <div class="fields-list-panel">
      <div class="section-heading">
        <div><h2>Fields</h2><p>Drag or use the position controls to set display order.</p></div>
        <span class="field-count">{{ fieldsStore.fields.length }} total</span>
      </div>

      <p v-if="fieldsStore.error" class="form-error">{{ fieldsStore.error }}</p>
      <p v-else-if="fieldsStore.loading" class="form-muted">Loading fields…</p>

      <ul v-else class="field-list">
        <FieldListItem
          v-for="(field, index) in fieldsStore.fields"
          :key="field.id"
          :field="field"
          :option-lists="fieldsStore.optionLists"
          :is-editing="field.id === editingId"
          :index="index"
          :total="fieldsStore.fields.length"
          @select="editingId = field.id"
          @delete="removeField(field)"
          @move="move(index, $event)"
          @reorder="reorder"
        />
      </ul>

      <p v-if="!fieldsStore.loading && !fieldsStore.fields.length" class="form-muted">
        No fields yet — add one on the right.
      </p>
    </div>

    <!-- Right: sidebar = add-fields or the field editor --------------------- -->
    <aside class="fields-sidebar">
      <FieldEditor
        v-if="editing"
        :field="editing"
        :option-lists="fieldsStore.optionLists"
        @saved="editingId = null"
        @close="editingId = null"
      />

      <div v-else class="add-fields">
        <div class="sidebar-heading">
          <span class="sidebar-icon" aria-hidden="true">+</span>
          <div><h2>Add field</h2><p>Choose the input visitors will use.</p></div>
        </div>
        <form class="add-form" @submit.prevent="addField">
          <select v-model="pending.type" class="form-control">
            <optgroup label="Text">
              <option v-for="t in textTypes" :key="t.subtype" :value="t">{{ t.label }}</option>
            </optgroup>
            <optgroup label="Choice">
              <option v-for="t in choiceTypes" :key="t.subtype" :value="t">{{ t.label }}</option>
            </optgroup>
            <optgroup label="Other">
              <option v-for="t in otherTypes" :key="t.subtype" :value="t">{{ t.label }}</option>
            </optgroup>
          </select>

          <!-- Choice fields require an OptionList -->
          <select
            v-if="isChoiceType"
            v-model="pending.optionListId"
            class="form-control option-list-picker"
          >
            <option :value="null" disabled>Choose option list…</option>
            <option v-for="list in fieldsStore.optionLists" :key="list.id" :value="list.id">
              {{ list.name }}
            </option>
          </select>

          <button
            class="btn btn-primary btn-block"
            type="submit"
            :disabled="fieldsStore.saving || (isChoiceType && !pending.optionListId)"
          >
            {{ fieldsStore.saving ? 'Adding…' : 'Add field' }}
          </button>
        </form>
        <p class="sidebar-note">Select any field in the list to edit its label, validation, and options.</p>
      </div>
    </aside>
  </div>
</template>

<script setup>
// Fields tab (list + "add fields" side index). Clicking a field opens the
// editor in the sidebar — plain component state, no routing involved.

import { computed, onMounted, reactive, ref } from 'vue'

import FieldEditor from '../components/fields/FieldEditor.vue'
import FieldListItem from '../components/fields/FieldListItem.vue'
import { FIELD_TYPES, useFieldsStore } from '../stores/fields'
import { useFormStore } from '../stores/form'

const fieldTypes = FIELD_TYPES
const textTypes = computed(() => fieldTypes.filter((t) => t.modelClass === 'textfield'))
const choiceTypes = computed(() => fieldTypes.filter((t) => t.modelClass === 'choicefield'))
const otherTypes = computed(() =>
  fieldTypes.filter((t) => t.modelClass !== 'textfield' && t.modelClass !== 'choicefield')
)

const fieldsStore = useFieldsStore()
const formStore = useFormStore()

const editingId = ref(null)
const editing = computed(() => fieldsStore.fields.find((f) => f.id === editingId.value) || null)

const pending = reactive({ type: fieldTypes[0], optionListId: null })
const isChoiceType = computed(() => pending.type.modelClass === 'choicefield')

onMounted(() => fieldsStore.fetchForForm(formStore.formId))

function displayName(field) {
  return field.display_name || field.data_name || field.slug || `Field #${field.id}`
}

async function addField() {
  const id = await fieldsStore.create(formStore.formId, {
    modelClass: pending.type.modelClass,
    subtype: pending.type.subtype,
    optionListId: pending.optionListId,
  })
  pending.optionListId = null
  // Open the sidebar immediately after creating a field.
  if (id) editingId.value = id
}

async function removeField(field) {
  if (confirm(`Delete field "${displayName(field)}"? Related rules will also be removed.`)) {
    if (editingId.value === field.id) editingId.value = null
    await fieldsStore.remove(formStore.formId, field)
  }
}

// Reorder locally then persist both affected records' new positions.
// Used by the up/down buttons (`move(index, delta)`) and drag-and-drop
// (`reorder(from, to)` — the drag target raises it on drop).
function move(index, delta) {
  reorder(index, index + delta)
}

function reorder(from, to) {
  if (from === to || from == null || to == null) return
  const fields = [...fieldsStore.fields]
  const [field] = fields.splice(from, 1)
  fields.splice(to, 0, field)
  fieldsStore.orderFields(formStore.formId, fields)
}
</script>

<style scoped>
.fields-layout {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
}
.fields-list-panel {
  flex: 1;
  min-width: 0;
}
.fields-sidebar {
  width: 340px;
  flex-shrink: 0;
  border: 1px solid var(--f-line);
  border-radius: var(--f-radius);
  padding: 1.1rem 1.25rem;
  background: var(--f-canvas);
  box-shadow: var(--f-shadow);
  position: sticky;
  top: 1rem;
}
.fields-list-panel h2,
.add-fields h2 {
  margin-top: 0;
  font-family: var(--f-font-display);
  font-size: 1.125rem;
  font-weight: 600;
  letter-spacing: -0.01em;
}
.fields-list-panel h2 {
  margin-bottom: 1rem;
}
.section-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}
.section-heading h2 { margin-bottom: 0.2rem; }
.section-heading p,
.sidebar-heading p { margin: 0; color: var(--f-muted); font-size: 0.8rem; }
.field-count {
  padding: 0.25rem 0.5rem;
  color: var(--f-muted);
  border: 1px solid var(--f-line);
  border-radius: 999px;
  font-size: 0.72rem;
  white-space: nowrap;
}
.sidebar-heading { display: flex; align-items: center; gap: 0.65rem; margin-bottom: 1rem; }
.sidebar-heading h2 { margin-bottom: 0.15rem; }
.sidebar-icon {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  flex: 0 0 30px;
  color: #fff;
  background: var(--f-accent);
  border-radius: var(--f-radius-sm);
  font-size: 1.25rem;
  line-height: 1;
}
.sidebar-note { margin: 1rem 0 0; padding-top: 0.85rem; border-top: 1px solid var(--f-line); color: var(--f-muted); font-size: 0.78rem; line-height: 1.5; }
.field-list {
  list-style: none;
  margin: 1rem 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}
.btn {
  padding: 0.35rem 0.75rem;
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
.btn:focus-visible {
  outline: 2px solid var(--f-accent);
  outline-offset: 2px;
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
.btn-block {
  width: 100%;
  padding: 0.55rem;
}
.btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
.add-form {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}
.form-control {
  width: 100%;
  padding: 0.5rem 0.65rem;
  border: 1px solid var(--f-line-strong);
  border-radius: var(--f-radius-sm);
  background: var(--f-surface);
  color: var(--f-ink);
  font-family: var(--f-font-ui);
  font-size: 0.875rem;
  line-height: 1.5;
  transition: border-color 150ms ease, box-shadow 150ms ease;
}
.form-control:hover {
  border-color: var(--f-soft);
}
.form-control:focus {
  border-color: var(--f-accent);
  outline: none;
  box-shadow: 0 0 0 3px var(--f-focus-ring);
}
.form-error {
  color: var(--f-danger-deep);
  background: var(--f-danger-tint);
  border: 1px solid rgba(176, 59, 48, 0.35);
  border-radius: var(--f-radius-sm);
  padding: 0.6rem 0.85rem;
}
.form-muted {
  color: var(--f-muted);
  font-size: 0.85rem;
  line-height: 1.5;
}
@media (max-width: 850px) {
  .fields-layout { flex-direction: column; }
  .fields-sidebar { position: static; width: 100%; order: -1; }
}
</style>
