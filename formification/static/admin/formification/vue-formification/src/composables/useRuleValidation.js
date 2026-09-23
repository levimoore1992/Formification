// Rule/condition/result validation as pure functions. Each returns a plain
// boolean that callers wrap in a `computed()` so Vue tracks the accesses
// reactively.
//
// `operator` on conditions and `action` on results are required (non-nullable)
// columns; marking them invalid blocks the save up-front instead of letting it
// fail with a DRF 400 mid-flight. `option_group` on a change-option-group
// result (and groups existing on the field's list) are required too.

export function ruleConditionInvalid(condition, fields) {
  if (condition.field == null) return true
  if (condition.operator == null || condition.operator === '') return true

  const field = fields.find((f) => f.id === Number(condition.field))
  if (!field) return true

  // Boolean fields carry no value; everything else needs one (value blank
  // and not boolean → invalid).
  if (field.type !== 'booleanfield') {
    return condition.value == null || condition.value === ''
  }
  return false
}

export function ruleResultInvalid(result, fields, groupsByList) {
  if (result.field == null) return true
  if (result.action == null || result.action === '') return true

  const field = fields.find((f) => f.id === Number(result.field))
  if (!field) return true

  if (result.action === 'change-option-group') {
    const listId = field.specific ? field.specific.option_list : null
    const groups = listId != null ? groupsByList[String(listId)] || [] : []
    if (groups.length < 1) return true
    if (result.option_group == null) return true
  }
  return false
}

export function ruleInvalid(rule, fields, groupsByList) {
  if (!rule.conditions.length || !rule.results.length) return true
  if (rule.conditions.some((c) => ruleConditionInvalid(c, fields))) return true
  if (rule.results.some((r) => ruleResultInvalid(r, fields, groupsByList))) return true
  return false
}