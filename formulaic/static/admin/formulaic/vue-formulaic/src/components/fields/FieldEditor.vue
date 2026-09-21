<template>
  <div class="field-editor">
    <h2>Edit '{{ subtypeLabel }}' field</h2>

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
          <label class="control-label">Display Name</label>
          <button type="button" class="btn btn-link btn-sm" @click="wysiwyg = !wysiwyg">
            {{ wysiwyg ? 'TEXT' : 'WYSIWYG' }}
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
        <label class="control-label">Data Column Name</label>
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
        Required
      </label>

      <!-- BooleanField -->
      <template v-if="field.type === 'booleanfield'">
        <label class="field-editor-check">
          <input v-model="specific.default_checked" type="checkbox" />
          Checked by Default
        </label>
      </template>

      <!-- ChoiceField -->
      <template v-if="field.type === 'choicefield'">
        <div class="field-editor-field" :class="{ 'has-error': hasError('optionList') }">
          <label class="control-label">Option List</label>
          <select v-model="specific.option_list" class="form-control" @change="onOptionListChange">
            <option :value="null" disabled>Choose option list…</option>
            <option v-for="list in optionLists" :key="list.id" :value="list.id">
              {{ list.name }}
            </option>
          </select>
        </div>

        <div v-if="hasOptionGroups" class="field-editor-field">
          <label class="control-label">Option Group</label>
          <select v-model="specific.option_group" class="form-control">
            <option :value="null">(None)</option>
            <option v-for="group in groups" :key="group.id" :value="group.id">
              {{ group.name }}
            </option>
          </select>
        </div>

        <div class="field-editor-field">
          <label class="control-label">
            {{ supportsMultiValue ? 'Default Selected' : 'Default Selected' }}
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
            <label class="control-label">Minimum Selections</label>
            <input
              v-model="specific.minimum_selections"
              type="number"
              min="0"
              class="form-control"
            />
          </div>
          <div class="field-editor-field">
            <label class="control-label">Maximum Selections</label>
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
            <label class="control-label">Default Text (unselected)</label>
            <input v-model="specific.default_text" type="text" class="form-control" placeholder="(Choose one)" />
          </div>
        </template>
      </template>

      <div class="extras">
        <h4>Extras</h4>
        <div class="field-editor-field">
          <label class="control-label">Help Text</label>
          <input v-model="specific.help_text" type="text" class="form-control" />
        </div>
        <div class="field-editor-field">
          <label class="control-label">CSS Class</label>
          <input v-model="specific.css_class" type="text" class="form-control" />
        </div>
      </div>
    </template>

    <p v-if="validation.message" class="validation-error">{{ validation.message }}</p>
    <p v-else-if="flash" class="flash" :class="flashType">{{ flash }}</p>

    <div class="editor-actions">
      <button class="btn btn-primary" :disabled="fieldsStore.saving" @click="save">
        {{ fieldsStore.saving ? 'Saving…' : 'Done' }}
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
.field-editor h2 {
  margin: 0 0 1rem;
  font-size: 1.1rem;
}
.field-editor-field {
  margin-bottom: 0.75rem;
}
.form-row-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}
.control-label,
.field-editor-check {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 600;
  font-size: 0.9rem;
}
.form-control {
  width: 100%;
  padding: 0.4rem 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.9rem;
}
.field-editor-check {
  font-weight: 400;
  margin-bottom: 0.75rem;
}
.extras h4 {
  margin: 1rem 0 0.5rem;
  font-size: 0.95rem;
  border-top: 1px solid #eee;
  padding-top: 0.75rem;
}
.has-error input,
.has-error textarea,
.has-error select {
  border-color: #c0392b;
}
.help-hint,
.validation-error {
  color: #c0392b;
}
.help-hint {
  color: #888;
  font-size: 0.8rem;
}
.flash {
  font-size: 0.9rem;
}
.flash.err {
  color: #c0392b;
}
.flash.ok {
  color: #1e8449;
}
.editor-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}
.btn {
  padding: 0.4rem 0.9rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  background: #f7f7f7;
  cursor: pointer;
}
.btn-primary {
  background: #2f80ed;
  border-color: #2f80ed;
  color: #fff;
}
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>