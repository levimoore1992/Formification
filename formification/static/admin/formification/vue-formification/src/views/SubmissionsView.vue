<template>
  <div class="submissions-layout">
    <h2>View Submissions</h2>

    <p v-if="submissionsStore.error" class="form-error">{{ submissionsStore.error }}</p>
    <p v-if="submissionsStore.loading" class="form-muted">Loading submissions…</p>

    <template v-else-if="submissionsStore.hasSubmissions">
      <nav class="submissions-toolbar">
        <!-- Source filter (over /submissionsources/) -->
        <label v-if="submissionsStore.sources.length" class="source-filter">
          <span>Filter:</span>
          <select
            class="form-control"
            :value="submissionsStore.source || ''"
            @change="onSourceChange($event.target.value)"
          >
            <option value="">Select `source` to filter…</option>
            <option v-for="s in submissionsStore.sources" :key="s.source" :value="s.source">
              {{ s.source }} ({{ s.count }})
            </option>
          </select>
        </label>

        <span class="page-info">
          Page {{ submissionsStore.page }} of {{ submissionsStore.pageCount }}
          (<em>{{ submissionsStore.count }} submissions</em>)
        </span>

        <span class="page-buttons">
          <button
            class="btn"
            :disabled="!submissionsStore.hasPreviousPage"
            @click="submissionsStore.gotoPage(submissionsStore.page - 1)"
          >
            Previous
          </button>
          <button
            class="btn"
            :disabled="!submissionsStore.hasNextPage"
            @click="submissionsStore.gotoPage(submissionsStore.page + 1)"
          >
            Next
          </button>
        </span>

        <!-- The download view lives outside the SPA (Django
             /formification/download/submissions/?form=:id) — direct link. -->
        <a class="btn btn-download" :href="downloadUrl" target="_blank" rel="noopener">
          Download CSV
        </a>
      </nav>

      <table class="submissions-table">
        <thead>
          <tr>
            <th v-for="header in headers" :key="header">{{ header }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in tableRows" :key="row.key">
            <td v-for="cell in row.cells" :key="cell.key">{{ cell.value }}</td>
          </tr>
        </tbody>
      </table>

      <nav class="submissions-toolbar">
        <span class="page-info">
          Page {{ submissionsStore.page }} of {{ submissionsStore.pageCount }}
          (<em>{{ submissionsStore.count }} submissions</em>)
        </span>
        <span class="page-buttons">
          <button
            class="btn"
            :disabled="!submissionsStore.hasPreviousPage"
            @click="submissionsStore.gotoPage(submissionsStore.page - 1)"
          >
            Previous
          </button>
          <button
            class="btn"
            :disabled="!submissionsStore.hasNextPage"
            @click="submissionsStore.gotoPage(submissionsStore.page + 1)"
          >
            Next
          </button>
        </span>
      </nav>
    </template>

    <p v-else-if="!submissionsStore.loading" class="form-muted">No submissions found</p>

    <div class="submissions-controls">
      <button class="btn btn-danger" @click="close">Close</button>
    </div>
  </div>
</template>

<script setup>
// Submissions tab: paginated table, source filter, Previous/Next, Close.
// page/source live in the Pinia store (hash routing makes query params
// awkward) — they're reset when leaving the tab.

import { computed } from 'vue'
import { useRouter } from 'vue-router'

import { useSubmissionsStore, columnHeaders, rowCells, cellText } from '../stores/submissions'
import { useFieldsStore } from '../stores/fields'
import { useFormStore } from '../stores/form'
import { config } from '../api/client'

const router = useRouter()

const submissionsStore = useSubmissionsStore()
const fieldsStore = useFieldsStore()
const formStore = useFormStore()

if (!formStore.form && !formStore.loading) {
  formStore.load()
}
if (!submissionsStore.sources.length && !submissionsStore.loading) {
  submissionsStore.fetchSources()
}
submissionsStore.fetch()

const headers = computed(() => columnHeaders(fieldsStore.fields))

const tableRows = computed(() =>
  submissionsStore.rows.map((submission) => ({
    key: submission.id,
    cells: rowCells(submission, fieldsStore.fields).map((value, i) => ({
      key: i,
      value: cellText(value),
    })),
  }))
)

// The download view lives outside the SPA router (re_path
// /download/submissions/ next to the /api/ prefix).
const downloadUrl = computed(
  () => `${config.apiBase.replace(/\/api$/, '')}/download/submissions/?form=${formStore.formId}`
)

function onSourceChange(value) {
  submissionsStore.setSource(value)
}

function close() {
  router.push('/fields')
}
</script>

<style scoped>
.submissions-layout {
  max-width: 860px;
}
.submissions-layout h2 {
  margin-top: 0;
  font-family: var(--f-font-display);
  font-size: 1.125rem;
  font-weight: 600;
  letter-spacing: -0.01em;
}
.form-error {
  color: var(--f-danger-deep);
  background: var(--f-danger-tint);
  border: 1px solid rgba(176, 59, 48, 0.35);
  border-radius: var(--f-radius-sm);
  padding: 0.6rem 0.85rem;
}
.form-muted {
  color: var(--f-muted);
  font-size: 0.85rem;
}
.submissions-toolbar {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.6rem 0.85rem;
  margin-bottom: 0.85rem;
  border: 1px solid var(--f-line);
  border-radius: var(--f-radius);
  background: var(--f-surface);
  flex-wrap: wrap;
}
.source-filter {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  color: var(--f-muted);
}
.source-filter select {
  max-width: 220px;
}
.page-info {
  font-size: 0.82rem;
  color: var(--f-muted);
}
.page-info em {
  font-style: normal;
  color: var(--f-ink);
}
.page-buttons {
  display: inline-flex;
  gap: 0.35rem;
}
.submissions-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
  margin-bottom: 0.85rem;
  border: 1px solid var(--f-line);
  border-radius: var(--f-radius);
  overflow: hidden;
}
.submissions-table th,
.submissions-table td {
  border-bottom: 1px solid var(--f-line);
  padding: 0.55rem 0.7rem;
  text-align: left;
  vertical-align: top;
}
.submissions-table th:not(:first-child),
.submissions-table td:not(:first-child) {
  border-left: 1px solid var(--f-line);
}
.submissions-table thead th {
  background: var(--f-canvas);
  font-weight: 600;
  color: var(--f-muted);
  font-size: 0.78rem;
  letter-spacing: 0.01em;
}
.submissions-table tbody tr:last-child td {
  border-bottom: none;
}
.submissions-table tbody tr:hover td {
  background: #fafcfb;
}
.submissions-controls {
  display: flex;
  gap: 0.5rem;
  margin-top: 1.25rem;
  padding-top: 1.1rem;
  border-top: 1px solid var(--f-line);
}
.btn {
  padding: 0.45rem 0.85rem;
  border: 1px solid var(--f-line-strong);
  border-radius: var(--f-radius-sm);
  background: var(--f-surface);
  color: var(--f-ink);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  transition: border-color 150ms ease, background-color 150ms ease, color 150ms ease;
  display: inline-flex;
  align-items: center;
}
.btn:hover {
  border-color: var(--f-soft);
  background: var(--f-canvas);
}
.btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
.btn:focus-visible {
  outline: 2px solid var(--f-accent);
  outline-offset: 2px;
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
.btn-download {
  margin-left: auto;
  background: var(--f-accent);
  border-color: var(--f-accent);
  color: #fff;
}
.btn-download:hover {
  border-color: var(--f-accent-deep);
  background: var(--f-accent-deep);
  color: #fff;
}
.form-control {
  padding: 0.42rem 0.6rem;
  border: 1px solid var(--f-line-strong);
  border-radius: var(--f-radius-sm);
  background: var(--f-surface);
  color: var(--f-ink);
  font-family: var(--f-font-ui);
  font-size: 0.875rem;
  line-height: 1.5;
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
</style>