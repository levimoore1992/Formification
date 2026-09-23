<template>
  <li>
    <div class="condition-row" :class="{ warning: invalid }">
      <span class="row-kind" aria-hidden="true">If</span>

      <select
        v-model="condition.field"
        class="form-control input-sm"
        @change="onFieldChanged"
      >
        <option :value="null" disabled>Choose a field…</option>
        <option v-for="f in fields" :key="f.id" :value="f.id">
          {{ fieldLabel(f) }}
        </option>
      </select>

      <select v-model="condition.operator" class="form-control input-sm">
        <option :value="null" disabled>Choose comparison…</option>
        <option v-for="op in operators" :key="op.value" :value="op.value">
          {{ op.name }}
        </option>
      </select>

      <!-- The value widget follows the selected field's type (port of
           useTextWidget / useSelectWidget / useNoWidget in rule-condition.js). -->
      <input
        v-if="isTextfield"
        v-model="condition.value"
        type="text"
        class="form-control input-sm"
        placeholder="Enter a value"
      />
      <select
        v-else-if="isChoicefield"
        class="form-control input-sm"
        :value="String(condition.value ?? '')"
        @change="condition.value = Number($event.target.value)"
      >
        <option value="" disabled>Choose an option…</option>
        <option v-for="opt in fieldOptions" :key="opt.id" :value="String(opt.id)">
          {{ opt.name }}
        </option>
      </select>
      <span v-else-if="isBooleanfield" class="checked-label">checked</span>

      <button
        class="btn btn-xs btn-link btn-danger-text"
        title="Remove condition"
        @click="$emit('delete', condition)"
      >
        Remove
      </button>
    </div>
  </li>
</template>

<script setup>
// Rule condition editor. `condition` is the mutable child object from the
// rules store (edited in place on the reactive store object).

import { computed, ref, watch } from 'vue'

import { ALL_OPERATORS } from '../../stores/rules'
import { ruleConditionInvalid } from '../../composables/useRuleValidation'

const props = defineProps({
  condition: { type: Object, required: true },
  fields: { type: Array, required: true },
  optionLists: { type: Array, required: true },
})

defineEmits(['delete'])

const operators = ALL_OPERATORS

const selectedField = computed(
  () => props.fields.find((f) => f.id === Number(props.condition.field)) || null
)
const isTextfield = computed(() => selectedField.value?.type === 'textfield')
const isChoicefield = computed(() => selectedField.value?.type === 'choicefield')
const isBooleanfield = computed(() => selectedField.value?.type === 'booleanfield')

// Options come from the choice field's option list.
const fieldOptions = computed(() => {
  const listId = selectedField.value?.specific?.option_list
  if (listId == null) return []
  const list = props.optionLists.find((l) => l.id === Number(listId))
  return list ? list.options || [] : []
})

const invalid = computed(() => ruleConditionInvalid(props.condition, props.fields))

// When the field type changes, blank the condition value (e.g. text → choice,
// so a stale string isn't stored against an option id).
let previousType = null
function onFieldChanged() {
  const type = selectedField.value?.type || null
  if (type !== previousType) {
    props.condition.value = null
  }
  previousType = type
}

function fieldLabel(field) {
  return field.data_name || field.display_name || field.slug || `Field #${field.id}`
}
</script>

<style scoped>
.condition-row {
  display: grid;
  grid-template-columns: 32px minmax(150px, 1.3fr) minmax(140px, 1fr) minmax(140px, 1fr) auto;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem;
  border: 1px solid var(--f-line);
  border-radius: var(--f-radius-sm);
  transition: border-color 150ms ease, background-color 150ms ease;
}
.condition-row:hover {
  background: var(--f-canvas);
}
.condition-row.warning {
  border-color: rgba(150, 106, 0, 0.45);
  background: var(--f-warning-tint);
}
.row-kind {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  color: var(--f-accent-deep);
  background: var(--f-accent-tint);
  border-radius: 50%;
  font-family: var(--f-font-mono);
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
}
.checked-label {
  color: var(--f-muted);
  font-style: italic;
  font-size: 0.85rem;
}
.input-sm {
  width: 100%;
  max-width: none;
}
.form-control {
  padding: 0.42rem 0.55rem;
  border: 1px solid var(--f-line-strong);
  border-radius: var(--f-radius-sm);
  background: var(--f-surface);
  color: var(--f-ink);
  font-family: var(--f-font-ui);
  font-size: 0.85rem;
  line-height: 1.4;
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
.btn-xs {
  padding: 0 0.25rem;
}
.btn-link {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.2rem;
  color: var(--f-accent-deep);
  font-weight: 600;
  border-radius: var(--f-radius-sm);
}
.btn-link:hover {
  background: var(--f-accent-tint);
}
.btn-danger-text {
  color: var(--f-danger);
  font-size: 0.72rem;
  text-decoration: underline;
}
.btn:focus-visible {
  outline: 2px solid var(--f-accent);
  outline-offset: 1px;
}
@media (max-width: 720px) {
  .condition-row { grid-template-columns: 28px 1fr auto; }
  .condition-row .form-control { grid-column: 2; }
  .condition-row .btn { grid-column: 3; grid-row: 1; }
}
</style>
