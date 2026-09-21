import { defineStore } from 'pinia'

import { client, config } from '../api/client'

// The field types the admin can create, mirroring the subtype constants in
// formulaic/models.py (TextField.SUBTYPES, ChoiceField.SUBTYPES, etc.).
// `modelClass` selects the DRF endpoint (textfields/, choicefields/, ...);
// `subtype` is the discriminator stored on the record.
export const FIELD_TYPES = [
  // TextField subtypes
  { modelClass: 'textfield', subtype: 'text', label: 'Text' },
  { modelClass: 'textfield', subtype: 'textarea', label: 'Textarea' },
  { modelClass: 'textfield', subtype: 'email', label: 'Email' },
  { modelClass: 'textfield', subtype: 'phone_number', label: 'Phone Number' },
  { modelClass: 'textfield', subtype: 'integer', label: 'Integer' },
  { modelClass: 'textfield', subtype: 'full_name', label: 'Full Name' },
  // ChoiceField subtypes
  { modelClass: 'choicefield', subtype: 'select', label: 'Select' },
  { modelClass: 'choicefield', subtype: 'radio_select', label: 'Radio Select' },
  { modelClass: 'choicefield', subtype: 'select_multiple', label: 'Select Multiple' },
  { modelClass: 'choicefield', subtype: 'checkbox_select_multiple', label: 'Checkbox Select Multiple' },
  // BooleanField / HiddenField
  { modelClass: 'booleanfield', subtype: 'checkbox', label: 'Checkbox' },
  { modelClass: 'hiddenfield', subtype: 'hidden', label: 'Hidden' },
]

// Globals re-used across stores/views, kept here next to the field catalog.
export const ChoiceField = {
  multiValueSubtypes: ['select_multiple', 'checkbox_select_multiple'],
}

function isEmptyToNull(value) {
  return value === '' || value == null ? null : scope_id(value)
}

// The list of fields in the current form, ordered by `position`.
//
// The API returns polymorphic "partials": every base Field row nests exactly
// one specific model (see FieldSerializer in serializers.py). We normalize the
// nested specific record into a single object the UI treats uniformly:
//   { ...baseFields, type: modelClass, specific: {...specificFields} }
export const useFieldsStore = defineStore('fields', {
  state: () => ({
    fields: [],
    loading: false,
    error: null,
    optionLists: [],
    saving: false,
  }),

  getters: {
    // The store is scoped to a single form (id injected by Django bootstrap).
    formId: () => config.formId,
  },

  actions: {
    async fetchForForm(formId) {
      this.loading = true
      this.error = null
      try {
        const rows = await client.listFields(formId)
        // Column ordering is the `position` integer column; the FieldViewset
        // queryset doesn't guarantee order, so sort here (submission columns
        // and the field list both assume position order).
        this.fields = rows
          .map(normalizeField)
          .sort((a, b) => Number(a.position) - Number(b.position))
        if (!this.optionLists.length) {
          this.optionLists = await client.listOptionLists()
        }
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    },

    // POST to the specific endpoint: /formulaic/api/{modelClass}s/
    // Returns the new field's id so the view can open the editor on it right
    // away.
    async create(formId, { modelClass, subtype, optionListId }) {
      this.saving = true
      this.error = null
      try {
        // Base attributes the whole codebase relies on (Field.save() in
        // models.py fills `content_type` and `model_class` server-side).
        const payload = {
          form: scope_id(formId),
          model_class: modelClass,
          subtype,
          display_name: '',
          data_name: '',
          slug: '',
          required: false,
          help_text: null,
          css_class: null,
          // Appended to the end of the list.
          position: this.fields.length,
        }
        // Subtype-specific attributes (see the model fields).
        if (modelClass === 'booleanfield') payload.default_checked = false
        if (modelClass === 'hiddenfield') payload.value = ''
        if (modelClass === 'choicefield') payload.option_list = scope_id(optionListId)

        const created = await client.createField(modelClass, payload)
        await this.fetchForForm(scope_id(formId))
        return created.id
      } catch (e) {
        this.error = e.message
        return null
      } finally {
        this.saving = false
      }
    },

    // PATCH the specific endpoint with the editable columns. `field` is a
    // normalized store record; edits live on field.specific (the nested
    // subtype serializer carries every editable column thanks to Django
    // multi-table inheritance).
    async saveOne(formId, field) {
      const s = field.specific
      const payload = {
        display_name: s.display_name,
        data_name: s.data_name,
        slug: s.slug,
        required: !!s.required,
        help_text: s.help_text || null,
        css_class: s.css_class || null,
      }

      if (field.type === 'booleanfield') {
        payload.default_checked = !!s.default_checked
      }

      if (field.type === 'hiddenfield') {
        payload.value = s.value || ''
      }

      if (field.type === 'choicefield') {
        const multi = ChoiceField.multiValueSubtypes.includes(field.subtype)
        payload.option_list = scope_id(s.option_list)
        payload.option_group = s.option_group ? scope_id(s.option_group) : null
        payload.minimum_selections =
          isEmptyToNull(s.minimum_selections)
        payload.maximum_selections =
          isEmptyToNull(s.maximum_selections)
        payload.default_text = s.default_text || null
        // default_option(s) round-trip as JSON strings on the backend
        // (DefaultOptionField / DefaultOptionsField in serializers.py).
        if (multi) {
          payload.default_options = (s.default_options || []).map(String)
        } else {
          payload.default_option = s.default_option ? String(s.default_option) : null
        }
      }

      this.saving = true
      this.error = null
      try {
        await client.updateField(field.type, field.id, payload)
        // Refetch after every save; the list response is the single source of
        // truth for the sidebar state.
        await this.fetchForForm(scope_id(formId))
      } catch (e) {
        this.error = e.message
      } finally {
        this.saving = false
      }
    },

    async remove(formId, field) {
      this.saving = true
      this.error = null
      try {
        // Base /fields/:id/ viewset cleans up related rules (see views.py).
        await client.deleteField(field.id)
        this.fields = this.fields.filter((f) => f.id !== field.id)
      } catch (e) {
        this.error = e.message
      } finally {
        this.saving = false
      }
    },

    // Reorder to the given array order and persist every field's `position`
    // (= array index). In-memory `position` values are stale during a drag
    // (they're only refreshed by a refetch), and `specific` never carries the
    // base column, so comparing against either would wrongly skip rows — so
    // save every row.
    orderFields(formId, orderedFields) {
      this.fields = orderedFields
      return Promise.all(
        orderedFields.map((field, index) =>
          client.updateField(field.type, field.id, {
            position: index,
          })
        )
      )
    },
  },
})

function normalizeField(row) {
  const type = row.model_class
  return {
    ...row,
    type,
    specific: row[type] || {},
  }
}

// Browsers send numbers as JSON numbers; DRF accepts both. Keep it a number
// when present, otherwise null-safe for string ids.
function scope_id(id) {
  return Number.isFinite(Number(id)) ? Number(id) : id
}