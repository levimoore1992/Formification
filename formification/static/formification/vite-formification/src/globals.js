import jQuery from 'jquery'

// The bundled form JS (custom_form.js) and the pages that use it rely on the
// global `$` that jQuery's UMD/CommonJS build no longer installs when bundled.
window.jQuery = window.$ = jQuery