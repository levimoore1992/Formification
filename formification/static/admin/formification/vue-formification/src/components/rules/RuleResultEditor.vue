<template>
  <li>
    <div class="result-row" :class="{ warning: invalid }">
      <span class="row-kind" aria-hidden="true">Do</span>

      <select v-model="result.action" class="form-control input-sm">
        <option :value="null" disabled>Choose an action…</option>
        <option v-for="a in actions" :key="a.value" :value="a.value">
          {{ a.name }}
        </option>
      </select>

      <select
        v-model="result.field"
        class="form-control input-sm"
        @change="onFieldChanged"
      >
        <option :value="null" disabled>Choose a field…</option>
        <option v-for="f in availableFields" :key="f.id" :value="f.id">
          {{ fieldLabel(f) }}
        </option>
      </select>

      <!-- change-option-group targets a Choice Field's option list groups -->
      <template v-if="showOptionGroups">
        <select
          v-if="fieldHasOptionGroups"
          v-model="result.option_group"
          class="form-control input-sm"
        >
          <option :value="null" disabled>Choose group…</option>
          <option v-for="g in groups" :key="g.id" :value="g.id">
            {{ g.name }}
          </option>
        </select>
        <span v-else class="no-groups">No groups in option list</span>
      </template>

      <button
        class="btn btn-xs btn-link btn-danger-text"
        title="Remove result"
        @click="$emit('delete', result)"
      >
        Remove
      </button>
    </div>
  </li>
</template>

<script setup>
// Rule result editor: action/field selects, the choice-field option-group
// picker, and availableFields filtering (change-option-group only lists
// Choice Fields).

import { computed, watch } from 'vue'

import { ALL_ACTIONS } from '../../stores/rules'
import { useRulesStore } from '../../stores/rules'
import { ruleResultInvalid } from '../../composables/useRuleValidation'

const props = defineProps({
  result: { type: Object, required: true },
  fields: { type: Array, required: true },
  groupsByList: { type: Object, required: true },
})

defineEmits(['delete'])

const rulesStore = useRulesStore()
const actions = ALL_ACTIONS

const selectedField = computed(
  () => props.fields.find((f) => f.id === Number(props.result.field)) || null
)

// "Change Option Group" only applies to Choice Fields.
const availableFields = computed(() => {
  if (props.result.action === 'change-option-group') {
    return props.fields.filter((f) => f.type === 'choicefield')
  }
  return props.fields
})

const showOptionGroups = computed(
  () =>
    props.result.action === 'change-option-group' &&
    selectedField.value?.type === 'choicefield'
)

const listId = computed(() =>
  showOptionGroups.value && selectedField.value.specific
    ? String(selectedField.value.specific.option_list)
    : null
)

const groups = computed(() =>
  listId.value ? props.groupsByList[listId.value] || [] : []
)
const fieldHasOptionGroups = computed(() => groups.value.length > 0)

const invalid = computed(() =>
  ruleResultInvalid(props.result, props.fields, props.groupsByList)
)

// Loading groups is async — fetch whenever a change-option-group result points
// at a Choice Field, caching groups per option-list id.
watch(
  () => [props.result.action, props.result.field],
  () => {
    if (showOptionGroups.value && selectedField.value) {
      rulesStore.ensureOptionGroupsForField(selectedField.value)
    }
  },
  { immediate: true }
)

function onFieldChanged() {
  // Clear the option group when the affected field changes.
  props.result.option_group = null
}

function fieldLabel(field) {
  return field.data_name || field.display_name || field.slug || `Field #${field.id}`
}
</script>

<style scoped>
.result-row {
  display: grid;
  grid-template-columns: 32px minmax(150px, 1fr) minmax(150px, 1.2fr) minmax(140px, 1fr) auto;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem;
  border: 1px solid var(--f-line);
  border-radius: var(--f-radius-sm);
  transition: border-color 150ms ease, background-color 150ms ease;
}
.result-row:hover {
  background: var(--f-canvas);
}
.result-row.warning {
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
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
}
.no-groups {
  color: var(--f-soft);
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
  .result-row { grid-template-columns: 28px 1fr auto; }
  .result-row .form-control,
  .result-row .no-groups { grid-column: 2; }
  .result-row .btn { grid-column: 3; grid-row: 1; }
}
</style>
