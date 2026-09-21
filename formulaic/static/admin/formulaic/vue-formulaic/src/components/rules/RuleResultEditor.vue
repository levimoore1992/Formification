<template>
  <li>
    <div class="result-row" :class="{ warning: invalid }">
      <span class="grip">→</span>

      <select v-model="result.action" class="form-control input-sm">
        <option :value="null" disabled>Choose action…</option>
        <option v-for="a in actions" :key="a.value" :value="a.value">
          {{ a.name }}
        </option>
      </select>

      <select
        v-model="result.field"
        class="form-control input-sm"
        @change="onFieldChanged"
      >
        <option :value="null" disabled>Choose field…</option>
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
        ✕
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
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.5rem;
  border: 1px solid transparent;
  border-radius: 4px;
}
.result-row.warning {
  border-color: #e6a700;
  background: #fff8e1;
}
.grip {
  color: #aaa;
  user-select: none;
}
.no-groups {
  color: #888;
  font-style: italic;
}
.input-sm {
  max-width: 140px;
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