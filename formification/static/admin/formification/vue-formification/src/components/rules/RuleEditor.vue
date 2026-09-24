<template>
  <div class="rule-card" :class="{ warning: invalid }">
    <div class="rule-head">
      <span class="rule-number"><strong>{{ number }}</strong><span>Rule</span></span>

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
        Delete rule
      </button>
    </div>

    <section class="rule-section conditions-section">
    <h4>
      <span class="logic-label">When</span>
      <span class="section-title">Conditions</span>
      <button class="btn btn-xs btn-link" @click="rulesStore.addCondition(rule)">
        + Add condition
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
    </section>

    <section class="rule-section results-section">
    <h4>
      <span class="logic-label">Then</span>
      <span class="section-title">Actions</span>
      <button class="btn btn-xs btn-link" @click="rulesStore.addResult(rule)">
        + Add action
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
    </section>
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
  border: 1px solid var(--f-line);
  border-radius: var(--f-radius);
  padding: 0;
  margin-bottom: 1.25rem;
  background: var(--f-surface);
  box-shadow: var(--f-shadow);
  overflow: hidden;
  transition: border-color 150ms ease, box-shadow 150ms ease;
}
.rule-card.warning {
  border-color: rgba(150, 106, 0, 0.45);
  box-shadow: inset 3px 0 0 var(--f-warning);
  background: var(--f-warning-tint);
}
.rule-head {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-height: 48px;
  padding: 0.65rem 0.85rem;
  background: var(--f-canvas);
  border-bottom: 1px solid var(--f-line);
}
.rule-number {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-right: auto;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--f-muted);
}
.rule-number strong {
  display: grid;
  place-items: center;
  width: 25px;
  height: 25px;
  background: var(--f-accent);
  color: #fff;
  border-radius: var(--f-radius-sm);
  font-family: var(--f-font-mono);
  font-size: 0.75rem;
}
.btn-group {
  display: inline-flex;
  border: 1px solid var(--f-line-strong);
  border-radius: 999px;
  overflow: hidden;
}
.btn-group .btn {
  border: none;
  border-radius: 0;
  background: var(--f-surface);
  color: var(--f-muted);
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  padding: 0.2rem 0.75rem;
}
.btn-group .btn + .btn {
  border-left: 1px solid var(--f-line);
}
.btn-group .btn:hover {
  background: var(--f-canvas);
  color: var(--f-ink);
}
.btn-group .btn.active {
  background: var(--f-accent);
  color: #fff;
}
.btn-group .btn.active:hover {
  background: var(--f-accent-deep);
  color: #fff;
}
.rule-section { padding: 0.85rem 1rem 1rem; }
.rule-section + .rule-section { border-top: 1px solid var(--f-line); }
.results-section { background: #fbfcfd; }
.rule-card h4 {
  margin: 0 0 0.55rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--f-muted);
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
.logic-label {
  min-width: 45px;
  padding: 0.2rem 0.35rem;
  color: #fff;
  background: var(--f-accent-deep);
  border-radius: var(--f-radius-sm);
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 0.67rem;
}
.results-section .logic-label { background: var(--f-accent); }
.section-title { margin-right: auto; color: var(--f-ink); font-size: 0.8rem; }
.rule-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}
.empty-note {
  color: var(--f-soft);
  font-style: italic;
  font-size: 0.85rem;
  padding-left: 0.5rem;
}
.btn-xs {
  padding: 0.2rem 0.5rem;
  font-size: 0.78rem;
  border-radius: var(--f-radius-sm);
}
.btn {
  padding: 0.3rem 0.6rem;
  border: 1px solid var(--f-line-strong);
  border-radius: var(--f-radius-sm);
  background: var(--f-surface);
  color: var(--f-ink);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: border-color 150ms ease, background-color 150ms ease, color 150ms ease;
}
.btn:hover {
  border-color: var(--f-soft);
  background: var(--f-canvas);
}
.btn-link {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--f-accent-deep);
  font-weight: 500;
  text-decoration: underline;
  padding: 0;
}
.btn-link:hover {
  color: var(--f-accent);
  background: none;
}
.btn-danger-text {
  color: var(--f-danger);
  text-decoration: none;
  font-weight: 600;
}
.btn:focus-visible {
  outline: 2px solid var(--f-accent);
  outline-offset: 2px;
}
</style>
