// Thin REST client for the Formification DRF API.
//
// Endpoints are the DRF SimpleRouter viewsets from formification/urls.py:
//   /formification/api/forms/, fields/, textfields/, choicefields/,
//   booleanfields/, hiddenfields/, optionlists/, optiongroups/, options/,
//   rules/, ruleconditions/, ruleresults/, submissions/
// All URLs carry a trailing slash (DRF's default).

import { readBootstrapConfig } from '../boot'

export const config = readBootstrapConfig()
export const client = api(config.apiBase)

// Django sets a `csrftoken` cookie on admin pages; DRF session auth requires it
// on unsafe methods.
function csrfToken() {
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]*)/)
  return match ? decodeURIComponent(match[1]) : ''
}

async function request(method, url, body) {
  const headers = { 'Content-Type': 'application/json' }
  if (!['GET', 'HEAD', 'OPTIONS'].includes(method)) {
    const token = csrfToken()
    if (token) headers['X-CSRFToken'] = token
  }

  const res = await fetch(url, {
    method,
    headers,
    credentials: 'same-origin',
    body: body === undefined ? undefined : JSON.stringify(body),
  })

  if (!res.ok) {
    // DRF returns JSON field errors on 400; surface them readable.
    let detail = `HTTP ${res.status}`
    try {
      const data = await res.json()
      detail = JSON.stringify(data, null, 2)
    } catch (e) {
      // Not JSON; keep the status line.
    }
    throw new Error(`${method} ${url} failed: ${detail}`)
  }

  if (res.status === 204) return null
  return res.json()
}

export function api(apiBase) {
  return {
    // Form -------------------------------------------------------------
    getForm: (id) => request('GET', `${apiBase}/forms/${id}/`),
    updateForm: (id, payload) => request('PATCH', `${apiBase}/forms/${id}/`, payload),

    // Fields ------------------------------------------------------------
    // List returns base Field rows with the specific model nested:
    //   { ..., model_class: "textfield", subtype, textfield: {...}, choicefield: null, ... }
    listFields: (formId) =>
      request('GET', `${apiBase}/fields/?form=${formId}`),

    // Writes go to the *specific* endpoints on purpose (see README "Polymorphic
    // fields"): the base /fields/ serializer nests read-only specifics and is
    // awkward to write to. `modelClass` is one of textfield/choicefield/
    // booleanfield/hiddenfield; the DRF routes are those names + "s".
    createField: (modelClass, payload) =>
      request('POST', `${apiBase}/${modelClass}s/`, payload),

    updateField: (modelClass, id, payload) =>
      request('PATCH', `${apiBase}/${modelClass}s/${id}/`, payload),

    // Deletes go through the base /fields/:id/ viewset which cleans up related
    // rules/conditions/results (see FieldViewset.destroy in views.py).
    deleteField: (id) => request('DELETE', `${apiBase}/fields/${id}/`),

    // Option lists -------------------------------------------------------
    listOptionLists: () => request('GET', `${apiBase}/optionlists/`),
    // Groups for a list (carry nested options when the editor needs them).
    listOptionGroups: (listId) =>
      request('GET', `${apiBase}/optiongroups/?list=${listId}`),

    // Rules ---------------------------------------------------------------
    // PATCH /rules/:id/ accepts nested conditions+results arrays: include an id
    // to update, omit it to create, omit the child entirely to delete it.
    // (Handled by RuleSerializer.create/update in serializers.py.)
    listRules: (formId) => request('GET', `${apiBase}/rules/?form=${formId}`),
    createRule: (payload) => request('POST', `${apiBase}/rules/`, payload),
    updateRule: (id, payload) => request('PATCH', `${apiBase}/rules/${id}/`, payload),
    deleteRule: (id) => request('DELETE', `${apiBase}/rules/${id}/`),

    // Submissions ----------------------------------------------------------
    // GET /submissions/?form=:id is paginated (StandardResultsSetPagination;
    // default page_size 5, overridable up to 1000). The response carries
    // DRF's { count, next, previous, results } envelope.
    listSubmissions: (formId, params = {}) => {
      const query = new URLSearchParams({ form: formId, ...params }).toString()
      return request('GET', `${apiBase}/submissions/?${query}`)
    },
    // Distinct submission sources for a form, grouped + counted — the re_path
    // view at /api/submissionsources/ (views.SubmissionSourceView).
    listSubmissionSources: (formId) =>
      request('GET', `${apiBase}/submissionsources/?form=${formId}`),
  }
}