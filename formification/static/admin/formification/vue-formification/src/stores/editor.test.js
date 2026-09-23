import { beforeEach, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('../api/client', () => ({
  config: { formId: 1 },
  client: {
    listFields: vi.fn().mockResolvedValue([]),
    listOptionLists: vi.fn().mockResolvedValue([]),
    listRules: vi.fn().mockResolvedValue([]),
    createField: vi.fn().mockResolvedValue({ id: 9 }),
    createRule: vi.fn().mockResolvedValue({ id: 10 }),
    updateRule: vi.fn().mockResolvedValue({ id: 10 }),
    deleteRule: vi.fn(),
  },
}))

import { client } from '../api/client'
import { useFieldsStore } from './fields'
import { useRulesStore } from './rules'

beforeEach(() => {
  setActivePinia(createPinia())
  vi.clearAllMocks()
})

it('omits unsaved child IDs while retaining existing child IDs', async () => {
  const store = useRulesStore()
  store.addRule()
  const rule = store.rules[0]
  Object.assign(rule.conditions[0], { field: 2, operator: 'is', value: 'yes' })
  Object.assign(rule.results[0], { field: 3, action: 'hide' })
  expect((await store.save()).ok).toBe(true)
  const payload = client.createRule.mock.calls[0][0]
  expect(payload.conditions[0]).not.toHaveProperty('id')
  expect(payload.results[0]).not.toHaveProperty('id')
  store.rules = [{ ...rule, id: 10 }]
  store.rules[0].conditions[0].id = 20
  store.rules[0].results[0].id = 30
  await store.save()
  expect(client.updateRule.mock.calls[0][1].conditions[0].id).toBe(20)
  expect(client.updateRule.mock.calls[0][1].results[0].id).toBe(30)
})

it('creates fields with valid distinct identifiers and choice defaults', async () => {
  const store = useFieldsStore()
  await store.create(1, { modelClass: 'choicefield', subtype: 'select', optionListId: 2 })
  await store.create(1, { modelClass: 'choicefield', subtype: 'select', optionListId: 2 })
  const first = client.createField.mock.calls[0][1]
  const second = client.createField.mock.calls[1][1]
  expect(first.display_name).not.toBe('')
  expect(first.data_name).not.toBe('')
  expect(first.slug).not.toBe(second.slug)
  expect(first.default_option).toBeNull()
  expect(first.default_options).toBeNull()
})
