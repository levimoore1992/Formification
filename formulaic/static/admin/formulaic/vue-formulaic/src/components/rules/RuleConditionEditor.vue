<template>
  <li>
    <div class="condition-row" :class="{ warning: invalid }">
      <span class="grip">≡</span>

      <select
        v-model="condition.field"
        class="form-control input-sm"
        @change="onFieldChanged"
      >
        <option :value="null" disabled>Choose field…</option>
        <option v-for="f in fields" :key="f.id" :value="f.id">
          {{ fieldLabel(f) }}
        </option>
      </select>

      <select v-model="condition.operator" class="form-control input-sm">
        <option :value="null" disabled>is / is not…</option>
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
        placeholder="value"
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
        ✕
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
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.5rem;
  border: 1px solid transparent;
  border-radius: 4px;
}
.condition-row.warning {
  border-color: #e6a700;
  background: #fff8e1;
}
.grip {
  color: #aaa;
  user-select: none;
}
.checked-label {
  color: #555;
  font-style: italic;
}
.input-sm {
  max-width: 130px;
}
.btn-xs {
  padding: 0 0.25rem;
}
.btn-link {
  background: none;
  border: none;
  cursor: pointer;
}
.btn-danger-text {
  color: #c0392b;
}
</style>