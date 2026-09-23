// Slug generation for data_name → slug, following the `slug(value, { lower: true })`
// conventions: lowercase, non-alphanumerics → dashes, collapse runs of dashes,
// strip edges.

export function generateSlug(value) {
  if (value == null) return value
  return String(value)
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

// If the display name already contains a tag, default the editor to
// WYSIWYG mode (used by the single-field editor).
export function hasHtml(value) {
  return !!(value && /<([A-Z][A-Z0-9]*)\b[^>]*>/i.test(value))
}