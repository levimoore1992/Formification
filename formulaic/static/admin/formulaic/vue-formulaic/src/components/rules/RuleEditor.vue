<template>
  <div class="rule-card" :class="{ warning: invalid }">
    <div class="rule-head">
      <span class="rule-number">Rule {{ number }}</span>

      <!-- AND/OR only matters once a rule has multiple conditions. -->
      <div v-if="rule.conditions.length > 1" class="btn-group">
        <button
          type="button"
          class="btn btn-xs"
          :class="{ active: rule.operator === 'and' }"
          @click="rulesStore.setOperator(rule, 'and')"
        >
          AND
        </button>
        <button
          type="button"
          class="btn btn-xs"
          :class="{ active: rule.operator === 'or' }"
          @click="rulesStore.setOperator(rule, 'or')"
        >
          OR
        </button>
      </div>

      <button
        class="btn btn-xs btn-link btn-danger-text"
        title="Delete rule"
        @click="$emit('delete')"
      >
        ✕
      </button>
    </div>

    <h4>
      Conditions
      <button class="btn btn-xs btn-link" @click="rulesStore.addCondition(rule)">
        + Add Condition
      </button>
    </h4>
    <ul class="rule-list" :class="{ or: rule.operator === 'or' }">
      <RuleConditionEditor
        v-for="condition in rule.conditions"
        :key="condition.key"
        :condition="condition"
        :fields="fieldsStore.fields"
        :option-lists="fieldsStore.optionLists"
        @delete="rulesStore.deleteCondition(rule, $event)"
      />
      <li v-if="!rule.conditions.length" class="empty-note">No conditions</li>
    </ul>

    <h4>
      Results
      <button class="btn btn-xs btn-link" @click="rulesStore.addResult(rule)">
        + Add Result
      </button>
    </h4>
    <ul class="rule-list">
      <RuleResultEditor
        v-for="result in rule.results"
        :key="result.key"
        :result="result"
        :fields="fieldsStore.fields"
        :groups-by-list="rulesStore.optionGroupsByList"
        @delete="rulesStore.deleteResult(rule, $event)"
      />
      <li v-if="!rule.results.length" class="empty-note">No results</li>
    </ul>
  </div>
</template>

<script setup>
// The per-rule card of conditions, results, AND/OR toggle and delete,
// rendered by the rules screen. There's no rule drag-and-drop yet — rules
// keep array order and are renumbered on save.

import { computed } from 'vue'

import RuleConditionEditor from './RuleConditionEditor.vue'
import RuleResultEditor from './RuleResultEditor.vue'
import { useFieldsStore } from '../../stores/fields'
import { useRulesStore } from '../../stores/rules'
import { ruleInvalid } from '../../composables/useRuleValidation'

const props = defineProps({
  rule: { type: Object, required: true },
  number: { type: Number, required: true },
})

defineEmits(['delete'])

const rulesStore = useRulesStore()
const fieldsStore = useFieldsStore()

const invalid = computed(() =>
  ruleInvalid(props.rule, fieldsStore.fields, rulesStore.optionGroupsByList)
)
</script>

<style scoped>
.rule-card {
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
  background: #fff;
}
.rule-card.warning {
  border-color: #e6a700;
  box-shadow: 0 0 0 1px #e6a700;
}
.rule-head {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.rule-number {
  font-weight: 600;
}
.btn-group {
  display: inline-flex;
}
.btn-group .btn.active {
  background: #2f80ed;
  border-color: #2f80ed;
  color: #fff;
}
.rule-card h4 {
  margin: 0.75rem 0 0.35rem;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.rule-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.empty-note {
  color: #888;
  font-style: italic;
  padding-left: 0.5rem;
}
.btn-xs {
  padding: 0.15rem 0.5rem;
}
.btn {
  padding: 0.2rem 0.6rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  background: #f7f7f7;
  cursor: pointer;
  font-size: 0.85rem;
}
.btn-link {
  background: none;
  border: none;
  cursor: pointer;
  color: #2f80ed;
  text-decoration: underline;
}
.btn-danger-text {
  color: #c0392b;
  text-decoration: none;
}
</style>