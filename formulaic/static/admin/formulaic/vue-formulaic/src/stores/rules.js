import { defineStore } from 'pinia'

import { client, config } from '../api/client'
import { useFieldsStore } from './fields'

// The rules screen. Rules are edited in place (on the reactive store objects)
// and persisted in a single save pass:
//   - rules marked deleted  → DELETE /rules/:id/
//   - rules with an id      → PATCH  /rules/:id/ (nested conditions+results)
//   - rules without an id   → POST   /rules/     (nested conditions+results)
//
// The RuleSerializer turns the nested arrays into create/update/delete: include
// `id` to update a child, omit it (null) to create one, and any child left out
// of the array entirely gets deleted server-side. `rule` on children is
// nullable at the model level, so `null` is accepted for brand-new rules.

let keySeq = 0
function nextKey() {
  keySeq += 1
  return keySeq
}

const ALL_OPERATORS = [
  { value: 'is', name: 'is' },
  { value: 'is_not', name: 'is not' },
]

const ALL_ACTIONS = [
  { value: 'show', name: 'Show' },
  { value: 'hide', name: 'Hide' },
  { value: 'change-option-group', name: 'Change Option Group' },
]

export const useRulesStore = defineStore('rules', {
  state: () => ({
    rules: [],
    loading: false,
    saving: false,
    error: null,
    pendingDeletion: [],
    // listId → option groups (from GET /optiongroups/?list=:id), cached so the
    // change-option-group result editor only fetches a list once.
    optionGroupsByList: {},
  }),

  getters: {
    formId: () => config.formId,
  },

  actions: {
    // GET /rules/?form=:id plus the fields for the editor selects. Fields
    // load once if the Fields tab hasn't been visited.
    async fetchForForm(formId) {
      this.loading = true
      this.error = null
      try {
        const rows = await client.listRules(formId)
        this.rules = rows.map((rule) => ({
          key: nextKey(),
          id: rule.id,
          form: rule.form,
          operator: rule.operator,
          position: rule.position,
          conditions: (rule.conditions || []).map((c) => ({
            key: nextKey(),
            id: c.id,
            position: c.position,
            rule: c.rule,
            field: c.field,
            operator: c.operator,
            value: c.value,
          })),
          results: (rule.results || []).map((r) => ({
            key: nextKey(),
            id: r.id,
            action: r.action,
            field: r.field,
            rule: r.rule,
            option_group: r.option_group,
          })),
        }))
        this.pendingDeletion = []

        const fieldsStore = useFieldsStore()
        if (!fieldsStore.fields.length && !fieldsStore.loading) {
          await fieldsStore.fetchForForm(formId)
        }
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    },

    addRule() {
      const rule = {
        key: nextKey(),
        id: null,
        form: this.formId,
        operator: 'and',
        position: this.rules.length,
        conditions: [],
        results: [],
      }
      // Seed a blank condition and result (both are required for a rule to be
      // valid, so this anchors the UI).
      rule.conditions.push(newCondition(rule))
      rule.results.push(newResult(rule))
      this.rules.push(rule)
    },

    deleteRule(rule) {
      if (rule.id) this.pendingDeletion.push(rule.id)
      this.rules = this.rules.filter((r) => r.key !== rule.key)
    },

    setOperator(rule, operator) {
      rule.operator = operator
    },

    addCondition(rule) {
      rule.conditions.push(newCondition(rule))
    },

    deleteCondition(rule, condition) {
      rule.conditions = rule.conditions.filter((c) => c.key !== condition.key)
    },

    addResult(rule) {
      rule.results.push(newResult(rule))
    },

    deleteResult(rule, result) {
      rule.results = rule.results.filter((r) => r.key !== result.key)
    },

    // Cache the option groups of a choice field's option list so the
    // change-option-group result can render its Group select.
    async ensureOptionGroupsForField(field) {
      if (!field) return []
      const listId = field.specific ? field.specific.option_list : null
      if (listId == null) return []
      const key = String(listId)
      if (this.optionGroupsByList[key]) return this.optionGroupsByList[key]
      try {
        const groups = await client.listOptionGroups(listId)
        this.optionGroupsByList[key] = groups
        return groups
      } catch (e) {
        this.error = e.message
        return []
      }
    },

    // Single save pass (DELETE pendings, PATCH existing, POST new). Up-front
    // validation is the view's job (it shows the "Rule is incomplete"
    // message); this persists.
    async save() {
      this.saving = true
      this.error = null
      try {
        // Renumber rules by list position (there's no rule drag-and-drop yet,
        // so insert/delete would otherwise leave gaps in the ordering).
        this.rules.forEach((rule, index) => {
          rule.position = index
        })

        const tasks = []
        for (const id of this.pendingDeletion) {
          tasks.push(client.deleteRule(id))
        }
        for (const rule of this.rules) {
          const payload = rulePayload(rule)
          if (rule.id) {
            tasks.push(client.updateRule(rule.id, payload))
          } else {
            tasks.push(client.createRule({ form: this.formId, ...payload }))
          }
        }
        await Promise.all(tasks)

        // Reload from server so ids/keys stay in sync and no duplicate rules
        // can creep in.
        await this.fetchForForm(this.formId)
        return { ok: true }
      } catch (e) {
        this.error = e.message
        return { ok: false, message: e.message }
      } finally {
        this.saving = false
      }
    },
  },
})

function newCondition(rule) {
  return {
    key: nextKey(),
    id: null,
    position: rule.conditions.length,
    rule: rule.id,
    field: null,
    operator: null,
    value: null,
  }
}

function newResult(rule) {
  return {
    key: nextKey(),
    id: null,
    action: null,
    field: null,
    rule: rule.id,
    option_group: null,
  }
}

function rulePayload(rule) {
  // Conditions are renumbered to array order; there is no condition
  // drag-and-drop, so array order is the source of truth.
  return {
    operator: rule.operator,
    position: rule.position,
    conditions: rule.conditions.map((c, index) => ({
      id: c.id,
      position: index,
      rule: rule.id || null,
      field: c.field == null ? null : Number(c.field),
      operator: c.operator,
      // JsonField on the backend accepts int/string/dict/list (booleans are
      // not); booleanfield conditions keep value null.
      value: c.value == null ? null : c.value,
    })),
    results: rule.results.map((r) => ({
      id: r.id,
      action: r.action,
      field: r.field == null ? null : Number(r.field),
      rule: rule.id || null,
      option_group: r.option_group == null ? null : Number(r.option_group),
    })),
  }
}

export { ALL_OPERATORS, ALL_ACTIONS }