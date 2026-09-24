// Bootstrap config for the Vue admin SPA.
//
// The Django admin template (formification/templates/admin/formification/form/
// change_form.html) injects config as a JSON meta tag. In dev (`npm run dev`)
// nothing is injected, so we fall back to a
// `formId` query parameter: http://localhost:5173/?formId=1
//
// Expected shape (see README "Integration with Django admin"):
//   { "formId": 1, "apiBase": "/formification/api" }

export function readBootstrapConfig() {
  let injected = {}
  const meta = document.querySelector(
    'meta[name="vue-formification/config/environment"]'
  )
  if (meta) {
    try {
      injected = JSON.parse(meta.content)
    } catch (e) {
      console.error('Bad vue-formification config meta tag:', meta.content, e)
    }
  }

  const query = new URLSearchParams(window.location.search)

  return {
    formId: injected.formId || query.get('formId') || '',
    apiBase: injected.apiBase || '/formification/api',
  }
}