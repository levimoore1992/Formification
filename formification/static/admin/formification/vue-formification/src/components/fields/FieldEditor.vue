<template>
  <div class="field-editor">
    <div class="editor-heading">
      <span class="editor-kicker">Editing field</span>
      <h2>{{ subtypeLabel }}</h2>
    </div>

    <!--
      Hidden fields: no display name, no required flag — just a value.
      Data name auto-fills display_name.
    -->
    <template v-if="field.type === 'hiddenfield'">
      <div class="field-editor-field" :class="{ 'has-error': hasError('dataName') }">
        <label class="control-label">Data Column Name</label>
        <input
          v-model.trim="specific.data_name"
          type="text"
          class="form-control"
          placeholder="(Data Column Name)"
          @input="specific.display_name = specific.data_name"
        />
      </div>

      <div class="field-editor-field" :class="{ 'has-error': hasError('slug') }">
        <label class="control-label">Slug</label>
        <input v-model="autoSlug" type="text" class="form-control" placeholder="(field-name)" />
      </div>

      <div class="field-editor-field">
        <label class="control-label">Value</label>
        <input v-model="specific.value" type="text" class="form-control" placeholder="" />
      </div>
    </template>

    <!-- Every other field type shares the base form. -->
    <template v-else>
      <div class="field-editor-field" :class="{ 'has-error': hasError('displayName') }">
        <div class="form-row-head">
          <label class="control-label">Display name</label>
          <button type="button" class="btn btn-link btn-sm" @click="wysiwyg = !wysiwyg">
            {{ wysiwyg ? 'Use plain text' : 'Use rich text' }}
          </button>
        </div>
        <RichTextEditor
          v-if="wysiwyg"
          v-model="specific.display_name"
          placeholder="(Display Name)"
        />
        <input
          v-else
          v-model="specific.display_name"
          type="text"
          class="form-control"
          placeholder="(Display Name)"
        />
      </div>

      <div class="field-editor-field" :class="{ 'has-error': hasError('dataName') }">
        <label class="control-label">Data column name</label>
        <input
          v-model.trim="specific.data_name"
          type="text"
          class="form-control"
          placeholder="(Data Column Name)"
        />
      </div>

      <div class="field-editor-field" :class="{ 'has-error': hasError('slug') }">
        <label class="control-label">Slug</label>
        <input v-model="autoSlug" type="text" class="form-control" placeholder="(field-name)" />
        <small class="help-hint">Blank = auto-generated from data name on save.</small>
      </div>

      <label class="field-editor-check">
        <input v-model="specific.required" type="checkbox" />
          Required field
      </label>

      <!-- BooleanField -->
      <template v-if="field.type === 'booleanfield'">
        <label class="field-editor-check">
          <input v-model="specific.default_checked" type="checkbox" />
          Checked by default
        </label>
      </template>

      <!-- ChoiceField -->
      <template v-if="field.type === 'choicefield'">
        <div class="field-editor-field" :class="{ 'has-error': hasError('optionList') }">
          <label class="control-label">Option list</label>
          <select v-model="specific.option_list" class="form-control" @change="onOptionListChange">
            <option :value="null" disabled>Choose option list…</option>
            <option v-for="list in optionLists" :key="list.id" :value="list.id">
              {{ list.name }}
            </option>
          </select>
        </div>

        <div v-if="hasOptionGroups" class="field-editor-field">
          <label class="control-label">Option group</label>
          <select v-model="specific.option_group" class="form-control">
            <option :value="null">(None)</option>
            <option v-for="group in groups" :key="group.id" :value="group.id">
              {{ group.name }}
            </option>
          </select>
        </div>

        <div class="field-editor-field">
          <label class="control-label">
            Default selection
          </label>
          <select
            v-if="supportsMultiValue"
            v-model="defaultOptions"
            multiple
            size="5"
            class="form-control"
          >
            <option v-for="option in options" :key="option.id" :value="String(option.id)">
              {{ option.name }}
            </option>
          </select>
          <select v-else v-model="defaultOption" class="form-control">
            <option :value="null">(None)</option>
            <option v-for="option in options" :key="option.id" :value="String(option.id)">
              {{ option.name }}
            </option>
          </select>
        </div>

        <template v-if="supportsMultiValue">
          <div class="field-editor-field">
            <label class="control-label">Minimum selections</label>
            <input
              v-model="specific.minimum_selections"
              type="number"
              min="0"
              class="form-control"
            />
          </div>
          <div class="field-editor-field">
            <label class="control-label">Maximum selections</label>
            <input
              v-model="specific.maximum_selections"
              type="number"
              min="0"
              class="form-control"
            />
          </div>
        </template>
        <template v-else>
          <div class="field-editor-field">
            <label class="control-label">Default text when unselected</label>
            <input v-model="specific.default_text" type="text" class="form-control" placeholder="(Choose one)" />
          </div>
        </template>
      </template>

      <div class="extras">
        <h4>Extras</h4>
        <div class="field-editor-field">
          <label class="control-label">Help text</label>
          <input v-model="specific.help_text" type="text" class="form-control" />
        </div>
        <div class="field-editor-field">
          <label class="control-label">CSS class</label>
          <input v-model="specific.css_class" type="text" class="form-control" />
        </div>
      </div>
    </template>

    <p v-if="validation.message" class="validation-error">{{ validation.message }}</p>
    <p v-else-if="flash" class="flash" :class="flashType">{{ flash }}</p>

    <div class="editor-actions">
      <button class="btn btn-primary" :disabled="fieldsStore.saving" @click="save">
        {{ fieldsStore.saving ? 'Saving…' : 'Save field' }}
      </button>
      <button class="btn" :disabled="fieldsStore.saving" @click="$emit('close')">Close</button>
    </div>
  </div>
</template>

<script setup>
// The per-field edit sidebar.
//
// One component with a section per model class, instead of the old 5
// templates + 5 controllers spread across routes/outlets.
//
// Notes:
//   - WYSIWYG uses the TinyMCE global loaded by change_form.html (RichTextEditor
//     falls back to a textarea when the CDN script isn't on the page, i.e. the
//     standalone dev server).
//   - The old "password" text subtype had no backend implementation and would
//     crash form rendering, so it is intentionally omitted.
//   - default_option(s) round-trip as JSON strings on the API; the selects
//     bind to String(option.id) and saveOne() keeps that shape.

import { computed, onMounted, ref, watch } from 'vue'

import { client } from '../../api/client'
import { useFieldValidation } from '../../composables/useFieldValidation'
import { ChoiceField, useFieldsStore } from '../../stores/fields'
import RichTextEditor from './RichTextEditor.vue'
import { generateSlug, hasHtml } from '../../utils/slug'

const props = defineProps({
  field: { type: Object, required: true },
  optionLists: { type: Array, default: () => [] },
})
const emit = defineEmits(['saved', 'close'])

const fieldsStore = useFieldsStore()
const specific = computed(() => props.field.specific)

const validation = useFieldValidation(computed(() => props.field))

const supportsMultiValue = computed(() =>
  ChoiceField.multiValueSubtypes.includes(props.field.subtype)
)

const subtypeLabel = computed(() => props.field.subtype.replace('_', ' '))

// WYSIWYG mode defaults to on if the display name already contains markup.
const wysiwyg = ref(hasHtml(props.field.specific.display_name))

// Slug input shows the stored slug, else a live preview of the generated one;
// editing it stores the explicit value.
const autoSlug = computed({
  get: () =>
    props.field.specific.slug ||
    generateSlug(props.field.specific.data_name) ||
    '',
  set: (value) => {
    props.field.specific.slug = value
  },
})

const flash = ref('')
const flashType = ref('')

function notify(message, type = 'ok') {
  flash.value = message
  flashType.value = type
}

// Choice field support data -------------------------------------------------
const groups = ref([])

const selectedListId = computed(() => props.field.specific.option_list)

const hasOptionGroups = computed(() => groups.value.length > 0)

// Options selectable as defaults: the group's options when one is chosen (the
// public form swaps groups via rules), otherwise the whole option list.
const options = computed(() => {
  if (props.field.specific.option_group) {
    const group = groups.value.find(
      (g) => g.id === props.field.specific.option_group
    )
    if (group?.options?.length) return group.options
  }
  const list = props.optionLists.find((l) => l.id === selectedListId.value)
  return list?.options || []
})

const defaultOption = computed({
  get: () =>
    props.field.specific.default_option
      ? String(props.field.specific.default_option)
      : null,
  set: (value) => {
    props.field.specific.default_option = value || null
  },
})

const defaultOptions = computed({
  get: () => (props.field.specific.default_options || []).map(String),
  set: (value) => {
    props.field.specific.default_options = value
  },
})

async function onOptionListChange() {
  // Switching lists invalidates any group chosen from the old one.
  props.field.specific.option_group = null
  await loadGroups()
}

async function loadGroups() {
  if (!selectedListId.value) {
    groups.value = []
    return
  }
  try {
    groups.value = await client.listOptionGroups(selectedListId.value)
  } catch (e) {
    groups.value = []
    console.error('Failed to load option groups', e)
  }
}

onMounted(loadGroups)

function hasError(key) {
  const map = {
    displayName: validation.displayNameInvalid.value,
    dataName: validation.dataNameInvalid.value,
    slug: validation.slugInvalid.value,
    optionList: validation.optionListInvalid.value,
  }
  return map[key]
}

async function save() {
  if (validation.invalid.value) {
    notify(validation.message.value, 'err')
    return
  }
  if (!props.field.specific.slug) {
    props.field.specific.slug = generateSlug(props.field.specific.data_name)
  }
  await fieldsStore.saveOne(scopeId(fieldsStore.formId), props.field)
  if (fieldsStore.error) {
    notify(fieldsStore.error, 'err')
    return
  }
  notify('Saved.')
  emit('saved')
}

function scopeId(id) {
  return Number.isFinite(Number(id)) ? Number(id) : id
}
</script>

<style scoped>
.editor-heading { margin-bottom: 1rem; padding-bottom: 0.75rem; border-bottom: 1px solid var(--f-line); }
.editor-kicker { display: block; margin-bottom: 0.15rem; color: var(--f-accent); font-size: 0.67rem; font-weight: 700; letter-spacing: 0.07em; text-transform: uppercase; }
.field-editor h2 {
  margin: 0;
  font-family: var(--f-font-display);
  font-size: 1.125rem;
  font-weight: 500;
  letter-spacing: -0.01em;
  text-transform: capitalize;
}
.field-editor-field {
  margin-bottom: 0.85rem;
}
.form-row-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}
.control-label,
.field-editor-check {
  display: block;
  margin-bottom: 0.3rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--f-ink);
}
.form-control {
  width: 100%;
  padding: 0.5rem 0.65rem;
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
.field-editor-check {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 400;
  margin-bottom: 0.85rem;
  cursor: pointer;
}
.field-editor-check input {
  width: 1.05rem;
  height: 1.05rem;
  accent-color: var(--f-accent);
}
.extras h4 {
  margin: 1.1rem 0 0.6rem;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  color: var(--f-accent-deep);
  text-transform: uppercase;
  border-top: 1px solid var(--f-line);
  padding-top: 0.9rem;
}
.has-error input,
.has-error textarea,
.has-error select {
  border-color: var(--f-danger);
}
.has-error input:focus,
.has-error textarea:focus,
.has-error select:focus {
  border-color: var(--f-danger);
  box-shadow: 0 0 0 3px rgba(176, 59, 48, 0.16);
}
.validation-error {
  color: var(--f-danger-deep);
  background: var(--f-danger-tint);
  border: 1px solid rgba(176, 59, 48, 0.35);
  border-radius: var(--f-radius-sm);
  padding: 0.55rem 0.8rem;
  font-size: 0.875rem;
}
.help-hint {
  color: var(--f-soft);
  font-size: 0.8rem;
  margin-top: 0.3rem;
  display: block;
}
.flash {
  border-radius: var(--f-radius-sm);
  padding: 0.55rem 0.8rem;
  font-size: 0.875rem;
}
.flash.err {
  color: var(--f-danger-deep);
  background: var(--f-danger-tint);
  border: 1px solid rgba(176, 59, 48, 0.35);
}
.flash.ok {
  color: var(--f-success);
  background: var(--f-success-tint);
  border: 1px solid rgba(47, 125, 79, 0.35);
}
.editor-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1.25rem;
  padding-top: 0.85rem;
  border-top: 1px solid var(--f-line);
}
.btn {
  padding: 0.5rem 1rem;
  border: 1px solid var(--f-line-strong);
  border-radius: var(--f-radius-sm);
  background: var(--f-surface);
  color: var(--f-ink);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: border-color 150ms ease, background-color 150ms ease, color 150ms ease;
}
.btn:hover {
  border-color: var(--f-soft);
  background: var(--f-canvas);
}
.btn-primary {
  background: var(--f-accent);
  border-color: var(--f-accent);
  color: #fff;
}
.btn-primary:hover {
  background: var(--f-accent-deep);
  border-color: var(--f-accent-deep);
  color: #fff;
}
.btn-link {
  border: none;
  background: none;
  color: var(--f-accent-deep);
  font-weight: 500;
  text-decoration: underline;
  padding: 0;
}
.btn-link:hover {
  color: var(--f-accent);
  background: none;
}
.btn-sm {
  font-size: 0.78rem;
  padding: 0.1rem 0.25rem;
}
.btn:focus-visible {
  outline: 2px solid var(--f-accent);
  outline-offset: 2px;
}
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
