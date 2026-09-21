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
             /formulaic/download/submissions/?form=:id) — direct link. -->
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
  font-size: 1.1rem;
}
.form-error {
  color: #c0392b;
  background: #fdecea;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  padding: 0.5rem 0.75rem;
}
.form-muted {
  color: #888;
  font-size: 0.85rem;
}
.submissions-toolbar {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem 0.75rem;
  margin-bottom: 0.75rem;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background: #fafafa;
  flex-wrap: wrap;
}
.source-filter {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
}
.source-filter select {
  max-width: 220px;
}
.page-info {
  font-size: 0.85rem;
  color: #555;
}
.page-buttons {
  display: inline-flex;
  gap: 0.35rem;
}
.submissions-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
  margin-bottom: 0.75rem;
}
.submissions-table th,
.submissions-table td {
  border: 1px solid #e0e0e0;
  padding: 0.4rem 0.6rem;
  text-align: left;
  vertical-align: top;
}
.submissions-table thead th {
  background: #fafafa;
  font-weight: 600;
}
.submissions-table tbody tr:nth-child(even) {
  background: #fafafa;
}
.submissions-controls {
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
  text-decoration: none;
  color: #333;
  font-size: 0.9rem;
}
.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.btn-danger {
  background: #fff;
  border-color: #c0392b;
  color: #c0392b;
}
.btn-download {
  margin-left: auto;
}
.btn-download:hover {
  border-color: #2f80ed;
  color: #2f80ed;
}
.form-control {
  padding: 0.35rem 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.9rem;
}
</style>