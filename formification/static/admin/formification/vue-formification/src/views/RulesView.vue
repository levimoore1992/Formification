<template>
  <div class="rules-layout">
    <div class="rules-heading">
      <div>
        <h2>Rules</h2>
        <p>Control how fields react to a visitor's answers.</p>
      </div>
      <span class="rules-count">{{ rulesStore.rules.length }} total</span>
    </div>

    <p v-if="rulesStore.error" class="form-error">{{ rulesStore.error }}</p>
    <p v-else-if="notice" class="form-success">{{ notice }}</p>

    <p v-if="rulesStore.loading" class="form-muted">Loading rules…</p>

    <template v-else>
      <div v-if="!rulesStore.rules.length" class="empty-state">
        <span aria-hidden="true">↳</span>
        <div><strong>No rules yet</strong><p>Add a rule to show, hide, require, or update a field based on another answer.</p></div>
      </div>

      <RuleEditor
        v-for="(rule, index) in rulesStore.rules"
        :key="rule.key"
        :rule="rule"
        :number="index + 1"
        @delete="rulesStore.deleteRule(rule)"
      />

      <div class="rules-add">
        <button
          class="btn btn-link"
          :disabled="rulesStore.saving"
          @click="rulesStore.addRule()"
        >
          <span aria-hidden="true">+</span> Add rule
        </button>
      </div>

      <div class="rules-controls">
        <button
          class="btn btn-primary"
          type="submit"
          :disabled="rulesStore.saving"
          @click="save(false)"
        >
          {{ rulesStore.saving ? 'Saving…' : 'Save and continue editing' }}
        </button>
        <button
          class="btn btn-primary"
          type="submit"
          :disabled="rulesStore.saving"
          @click="save(true)"
        >
          {{ rulesStore.saving ? 'Saving…' : 'Save changes' }}
        </button>
        <button
          class="btn btn-danger"
          type="submit"
          :disabled="rulesStore.saving"
          @click="close"
        >
          Back to fields
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
// Rules tab markup + save flow. Validation: an incomplete rule ("Rule is
// incomplete") blocks the save and gets a yellow warning treatment.
//
// Two save buttons: "Save & Continue Editing" (stay) and "Save" (redirect to
// the form index). Both persist; only "Save" navigates home.

import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import RuleEditor from '../components/rules/RuleEditor.vue'
import { useRulesStore } from '../stores/rules'
import { useFieldsStore } from '../stores/fields'
import { useFormStore } from '../stores/form'
import { ruleInvalid } from '../composables/useRuleValidation'

const router = useRouter()
const rulesStore = useRulesStore()
const fieldsStore = useFieldsStore()
const formStore = useFormStore()

const notice = ref('')

const invalidCount = computed(() =>
  rulesStore.rules.filter((rule) =>
    ruleInvalid(rule, fieldsStore.fields, rulesStore.optionGroupsByList)
  ).length
)

// Entering the Rules tab independently (deep link) still needs the form shell
// + fields. Guard against double-fetch with the store's own loading flag.
if (!formStore.form && !formStore.loading) {
  formStore.load()
}
rulesStore.fetchForForm(formStore.formId)

async function save(redirect) {
  notice.value = ''
  rulesStore.error = null
  if (invalidCount.value > 0) {
    // The original used a toastr.warning; rendered inline instead.
    rulesStore.error =
      `Unable to save because of these issues: ` +
      `${invalidCount.value} rule${invalidCount.value === 1 ? ' is' : 's are'} incomplete.`
    return
  }

  const result = await rulesStore.save()
  if (result.ok) {
    notice.value = 'Rules saved.'
    if (redirect) router.push('/fields')
  }
}

function close() {
  router.push('/fields')
}
</script>

<style scoped>
.rules-layout {
  max-width: 960px;
}
.rules-heading { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; margin-bottom: 1.25rem; }
.rules-heading h2 {
  margin-top: 0;
  margin-bottom: 0.2rem;
  font-family: var(--f-font-display);
  font-size: 1.125rem;
  font-weight: 600;
  letter-spacing: -0.01em;
}
.rules-heading p { margin: 0; color: var(--f-muted); font-size: 0.82rem; }
.rules-count { padding: 0.25rem 0.5rem; border: 1px solid var(--f-line); border-radius: 999px; color: var(--f-muted); font-size: 0.72rem; white-space: nowrap; }
.empty-state { display: flex; gap: 0.85rem; align-items: flex-start; padding: 1rem; border: 1px dashed var(--f-line-strong); border-radius: var(--f-radius); background: var(--f-canvas); }
.empty-state > span { display: grid; place-items: center; width: 30px; height: 30px; flex: 0 0 30px; color: #fff; background: var(--f-accent); border-radius: var(--f-radius-sm); font-size: 1.1rem; }
.empty-state strong { font-size: 0.875rem; }
.empty-state p { margin: 0.2rem 0 0; color: var(--f-muted); font-size: 0.8rem; line-height: 1.45; }
.form-error {
  color: var(--f-danger-deep);
  background: var(--f-danger-tint);
  border: 1px solid rgba(176, 59, 48, 0.35);
  border-radius: var(--f-radius-sm);
  padding: 0.6rem 0.85rem;
}
.form-success {
  color: var(--f-success);
  background: var(--f-success-tint);
  border: 1px solid rgba(47, 125, 79, 0.35);
  border-radius: var(--f-radius-sm);
  padding: 0.6rem 0.85rem;
}
.form-muted {
  color: var(--f-muted);
  font-size: 0.85rem;
}
.rules-add {
  margin: 0.25rem 0 1.25rem;
}
.rules-controls {
  display: flex;
  gap: 0.5rem;
  margin-top: 1.25rem;
  padding-top: 1.1rem;
  justify-content: flex-end;
  padding: 0.75rem;
  border: 1px solid var(--f-line);
  border-radius: var(--f-radius);
  background: var(--f-canvas);
}
.btn {
  padding: 0.5rem 1rem;
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
.btn-danger {
  background: var(--f-surface);
  border-color: var(--f-danger);
  color: var(--f-danger);
}
.btn-danger:hover {
  border-color: var(--f-danger-deep);
  background: var(--f-danger-tint);
  color: var(--f-danger-deep);
}
.btn-link {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--f-accent-deep);
  font-weight: 500;
  text-decoration: underline;
  padding: 0.2rem 0.4rem;
}
.btn-link:hover {
  color: var(--f-accent);
  background: none;
}
.btn:focus-visible {
  outline: 2px solid var(--f-accent);
  outline-offset: 2px;
}
.btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
@media (max-width: 650px) {
  .rules-controls { align-items: stretch; flex-direction: column; }
  .rules-controls .btn { width: 100%; }
}
</style>
