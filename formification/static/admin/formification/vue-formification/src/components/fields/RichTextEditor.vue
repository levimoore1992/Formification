<template>
  <!--
    WYSIWYG display-name editor.

    In the Django admin the TinyMCE 5 library is already on the page (loaded
    from the Cloud CDN in change_form.html), so we use that `window.tinymce`
    global and initialize on this textarea. Running
    the Vue dev server standalone there is no TinyMCE on the page, so this
    degrades to a plain textarea — the saved value is identical either way and
    the WYSIWYG toggle keeps working.

    Editor options mirror the historical editorOptions config (height 120,
    minimal toolbar, no menubar). The v4-only
    force_br_newlines/force_p_newlines options are kept for parity; TinyMCE 5
    honors `forced_root_block: ''` which is what actually keeps the raw HTML
    (no wrapping <p>).
  -->
  <textarea
    ref="host"
    rows="3"
    class="form-control"
    :placeholder="placeholder"
    :value="modelValue"
    @input="emit('update:modelValue', $event.target.value)"
  ></textarea>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])

const host = ref(null)
let editor = null

function sync() {
  if (editor) emit('update:modelValue', editor.getContent())
}

function initTinyMCE() {
  const tinymce = window.tinymce
  if (!tinymce || typeof tinymce.init !== 'function') return false

  try {
    tinymce.init({
      target: host.value,
      height: 120,
      menubar: false,
      toolbar: 'bold italic | link',
      plugins: ['link'],
      forced_root_block: '',
      force_br_newlines: false,
      force_p_newlines: false,
      setup(instance) {
        editor = instance
        instance.on('init', () => instance.setContent(props.modelValue || ''))
        instance.on('change input undo redo keyup', sync)
      },
    })
    return true
  } catch (e) {
    console.warn('[RichTextEditor] TinyMCE init failed; falling back to textarea', e)
    return false
  }
}

onMounted(() => {
  initTinyMCE()
})

// External changes (e.g. reset after save) push back into the editor without
// echoing our own updates back out.
watch(
  () => props.modelValue,
  (value) => {
    if (editor && editor.getContent() !== (value || '')) {
      editor.setContent(value || '')
    }
  }
)

onBeforeUnmount(() => {
  if (editor && window.tinymce) {
    try {
      window.tinymce.remove(editor)
    } catch (e) {
      // Editor already gone.
    }
  }
  editor = null
})
</script>

<style scoped>
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
</style>