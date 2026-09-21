<template>
  <div class="fields-layout">
    <!-- Left: the ordered list of fields ----------------------------------- -->
    <div class="fields-list-panel">
      <h2>Fields</h2>

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
        <h2>Add Fields</h2>
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
            {{ fieldsStore.saving ? 'Adding…' : 'Add Field' }}
          </button>
        </form>
        <p class="form-muted">Click a field on the left to edit its details.</p>
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
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 1rem;
  background: #fbfbfb;
}
.fields-list-panel h2,
.add-fields h2 {
  margin-top: 0;
  font-size: 1.1rem;
}
.field-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.btn {
  padding: 0.25rem 0.6rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  background: #f7f7f7;
  cursor: pointer;
}
.btn-danger {
  color: #c0392b;
}
.btn-primary {
  background: #2f80ed;
  border-color: #2f80ed;
  color: #fff;
}
.btn-block {
  width: 100%;
  padding: 0.45rem;
}
.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.add-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.form-control {
  padding: 0.4rem 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.9rem;
}
.form-error {
  color: #c0392b;
}
.form-muted {
  color: #888;
  font-size: 0.85rem;
}
</style>