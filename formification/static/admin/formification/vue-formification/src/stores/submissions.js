import { defineStore } from 'pinia'

import { client, config } from '../api/client'
import { useFieldsStore } from './fields'

// The submissions screen — read-only browse of a form's submissions with an
// optional `source` filter; API data is a DRF-paginated envelope
// ({ count, next, previous, results }), page_size 25 (the API default is 5).
//
// Column model mirrors Submission.custom_data (models.py): base columns
// [date_created, source, promo_source] then one column per field in position
// order, the cell read from custom_data[field.slug].

export const PAGE_SIZE = 25

export const useSubmissionsStore = defineStore('submissions', {
  state: () => ({
    rows: [],
    count: 0,
    page: 1,
    source: null,
    sources: [],
    loading: false,
    error: null,
  }),

  getters: {
    formId: () => config.formId,
    pageCount: (state) => Math.max(1, Math.ceil(state.count / PAGE_SIZE)),
    hasSubmissions: (state) => state.rows.length > 0,
    hasNextPage: (state) => state.page < Math.ceil(state.count / PAGE_SIZE),
    hasPreviousPage: (state) => state.page > 1,
  },

  actions: {
    // GET /submissions/?form=:id&page_size=25&page=N[&source=...]
    async fetch() {
      this.loading = true
      this.error = null
      try {
        const params = { page_size: PAGE_SIZE, page: this.page }
        if (this.source) params.source = this.source
        const data = await client.listSubmissions(this.formId, params)
        this.rows = data.results
        this.count = data.count || 0

        // Column headers need the form's fields (data_name → header, slug →
        // custom_data key). Load once if the Fields tab hasn't been visited.
        const fieldsStore = useFieldsStore()
        if (!fieldsStore.fields.length && !fieldsStore.loading) {
          await fieldsStore.fetchForForm(this.formId)
        }
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    },

    // GET /submissionsources/?form=:id → [{ source, count }]
    async fetchSources() {
      try {
        this.sources = await client.listSubmissionSources(this.formId)
      } catch (e) {
        this.error = e.message
      }
    },

    async gotoPage(page) {
      if (page < 1) page = 1
      this.page = page
      await this.fetch()
    },

    async setSource(source) {
      this.source = source || null
      this.page = 1
      await Promise.all([this.fetch(), this.fetchSources()])
    },
  },
})

// Column rendering. Raw cell values can be arrays or objects; render them
// readably without changing the API contract.
export function cellText(value) {
  if (value == null) return ''
  if (Array.isArray(value)) return value.map(cellText).join(', ')
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

// Headers: Date/Time, Source, Promo Source, then one data_name per field in
// position order (mirrors Form.column_headers, which uses slugs).
export function columnHeaders(fields) {
  const headers = ['Date/Time', 'Source', 'Promo Source']
  for (const field of fields) {
    headers.push(field.data_name || field.slug || `Field #${field.id}`)
  }
  return headers
}

// [date, source, promo_source, ...custom_data[slug]]
export function rowCells(submission, fields) {
  const cells = [
    submission.date_created,
    submission.source,
    submission.promo_source,
  ]
  const data = submission.custom_data || {}
  for (const field of fields) {
    cells.push(data[field.slug])
  }
  return cells
}