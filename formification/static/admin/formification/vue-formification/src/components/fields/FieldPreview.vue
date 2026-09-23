<template>
  <!--
    Read-only preview of a field, rendered in the field list. One widget per
    field subtype (text, textarea, email, phone-number, integer, full-name,
    checkbox, select, radio-select, select-multiple, checkbox-select-multiple,
    hidden).

    The label lives in the parent item (FieldListItem); this component only
    renders the widget. The only exception is the checkbox (boolean field),
    which carries its own label.
  -->
  <div v-if="subtype === 'checkbox'" class="checkbox">
    <label>
      <input type="checkbox" :checked="specific.default_checked" disabled />
      <span v-html="displayHtml" />
      <span v-if="specific.required" class="required-mark" aria-hidden="true"></span>
    </label>
  </div>

  <input
    v-else-if="subtype === 'text'"
    type="text"
    class="form-control"
    placeholder="Lorem ipsum dolor"
    disabled
  />
  <textarea
    v-else-if="subtype === 'textarea'"
    rows="4"
    class="form-control"
    placeholder="Nos commodius agimus. Quo modo? Quaerimus enim finem bonorum. Minime vero, inquit ille, consentit. Cur post Tarentum ad Archytam? Non igitur bene."
    disabled
  ></textarea>
  <input
    v-else-if="subtype === 'email'"
    type="text"
    class="form-control"
    placeholder="name@example.com"
    disabled
  />
  <input
    v-else-if="subtype === 'phone_number'"
    type="text"
    class="form-control"
    placeholder="(###)###-####"
    disabled
  />
  <input
    v-else-if="subtype === 'integer'"
    type="text"
    class="form-control"
    placeholder="#####"
    disabled
  />
  <input
    v-else-if="subtype === 'full_name'"
    type="text"
    class="form-control"
    placeholder="John Q. Public"
    disabled
  />

  <select v-else-if="subtype === 'select'" class="form-control">
    <option>{{ defaultOptionName }}</option>
  </select>

  <div v-else-if="subtype === 'radio_select'" class="radio-options">
    <div class="radio">
      <label>
        <input type="radio" name="optionsRadios" checked disabled />
        {{ defaultOptionName }}
      </label>
    </div>
    <div class="radio">
      <label>
        <input type="radio" name="optionsRadios" disabled />
        Nec sapien ante.
      </label>
    </div>
    <div class="radio">
      <label>
        <input type="radio" name="optionsRadios" disabled />
        Consequat sem ipsum.
      </label>
    </div>
  </div>

  <select v-else-if="subtype === 'select_multiple'" multiple class="form-control">
    <option>Lorem ipsum dolor</option>
    <option>Sit amet leo</option>
    <option>Nec sapien ante</option>
  </select>

  <div v-else-if="subtype === 'checkbox_select_multiple'" class="checkbox-options">
    <label><input type="checkbox" checked disabled /> Lorem ipsum dolor sit amet, leo in, in vivamus.</label>
    <label><input type="checkbox" checked disabled /> Nec sapien ante.</label>
    <label><input type="checkbox" disabled /> Consequat sem ipsum.</label>
  </div>

  <input
    v-else-if="subtype === 'hidden'"
    type="text"
    class="form-control"
    :placeholder="specific.value"
    disabled
  />
</template>

<script setup>
// Preview markup mirrors the original placeholder strings. `field` is a
// normalized store record (see stores/fields.js); the option lists let us
// resolve `default_option`'s id to a display name.

import { computed } from 'vue'

const props = defineProps({
  field: { type: Object, required: true },
  optionLists: { type: Array, default: () => [] },
})

const specific = computed(() => props.field.specific)
const subtype = computed(() => props.field.subtype)

const displayHtml = computed(() => {
  const v = specific.value.display_name
  return v ? v : '<span class="empty">(Field Name)</span>'
})

const defaultOptionName = computed(() => {
  const name = optionNameById(props.optionLists, specific.value.default_option)
  if (name) return name
  if (specific.value.default_text) return specific.value.default_text
  return subtype.value === 'radio_select'
    ? 'Lorem ipsum dolor sit amet, leo in, in vivamus.'
    : '(Choose One)'
})

function optionNameById(optionLists, id) {
  if (id == null) return null
  for (const list of optionLists) {
    for (const option of list.options || []) {
      if (String(option.id) === String(id)) return option.name
    }
  }
  return null
}
</script>

<style scoped>
.checkbox label,
.radio label,
.checkbox-options label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-weight: 400;
  margin-bottom: 0.25rem;
}

.radio-options,
.checkbox-options {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.checkbox label input,
.radio label input,
.checkbox-options label input {
  accent-color: var(--f-accent);
}

.required-mark {
  display: inline-block;
  width: 0.55em;
  height: 0.55em;
  margin-left: 0.4em;
  background: var(--f-accent);
  border-radius: 2px;
}

.form-control {
  width: 100%;
  padding: 0.5rem 0.65rem;
  border: 1px solid var(--f-line);
  border-radius: var(--f-radius-sm);
  background: var(--f-canvas);
  color: var(--f-muted);
  font-family: var(--f-font-ui);
  font-size: 0.875rem;
  line-height: 1.5;
}

.form-control select,
select.form-control {
  background: var(--f-canvas);
}

.empty {
  color: var(--f-faint);
  font-style: italic;
}

.checkbox-options label,
.radio label {
  font-size: 0.85rem;
  color: var(--f-muted);
}
</style>