<template>
  <div class="rules-layout">
    <h2>Editing Rules</h2>

    <p v-if="rulesStore.error" class="form-error">{{ rulesStore.error }}</p>
    <p v-else-if="notice" class="form-success">{{ notice }}</p>

    <p v-if="rulesStore.loading" class="form-muted">Loading rules…</p>

    <template v-else>
      <p v-if="!rulesStore.rules.length" class="form-muted">
        This form doesn't have any rules — add one below.
      </p>

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
          + Add Rule
        </button>
      </div>

      <div class="rules-controls">
        <button
          class="btn btn-primary"
          type="submit"
          :disabled="rulesStore.saving"
          @click="save(false)"
        >
          {{ rulesStore.saving ? 'Saving…' : 'Save & Continue Editing' }}
        </button>
        <button
          class="btn btn-primary"
          type="submit"
          :disabled="rulesStore.saving"
          @click="save(true)"
        >
          {{ rulesStore.saving ? 'Saving…' : 'Save' }}
        </button>
        <button
          class="btn btn-danger"
          type="submit"
          :disabled="rulesStore.saving"
          @click="close"
        >
          Close
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
  max-width: 760px;
}
.rules-layout h2 {
  margin-top: 0;
  font-size: 1.1rem;
}
.form-error {
  color: #c0392b;
  background: #fdecea;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  padding: 0.5rem 0.75rem;
}
.form-success {
  color: #1e7e34;
  background: #e8f5ec;
  border: 1px solid #bfe4c9;
  border-radius: 4px;
  padding: 0.5rem 0.75rem;
}
.form-muted {
  color: #888;
  font-size: 0.85rem;
}
.rules-add {
  margin: 0.25rem 0 1rem;
}
.rules-controls {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
}
.btn {
  padding: 0.35rem 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  background: #f7f7f7;
  cursor: pointer;
}
.btn-primary {
  background: #2f80ed;
  border-color: #2f80ed;
  color: #fff;
}
.btn-danger {
  background: #fff;
  border-color: #c0392b;
  color: #c0392b;
}
.btn-link {
  background: none;
  border: none;
  cursor: pointer;
  color: #2f80ed;
  text-decoration: underline;
}
.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>