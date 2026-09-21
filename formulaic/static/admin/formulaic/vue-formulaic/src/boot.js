// Bootstrap config for the Vue admin SPA.
//
// The Django admin template (formulaic/templates/admin/formulaic/form/
// change_form.html) injects config as a JSON meta tag. In dev (`npm run dev`)
// nothing is injected, so we fall back to a
// `formId` query parameter: http://localhost:5173/?formId=1
//
// Expected shape (see README "Integration with Django admin"):
//   { "formId": 1, "apiBase": "/formulaic/api" }

export function readBootstrapConfig() {
  let injected = {}
  const meta = document.querySelector(
    'meta[name="vue-formulaic/config/environment"]'
  )
  if (meta) {
    try {
      injected = JSON.parse(meta.content)
    } catch (e) {
      console.error('Bad vue-formulaic config meta tag:', meta.content, e)
    }
  }

  const query = new URLSearchParams(window.location.search)

  return {
    formId: injected.formId || query.get('formId') || '',
    apiBase: injected.apiBase || '/formulaic/api',
  }
}