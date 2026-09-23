<template>
  <!--
    One row of the field list: the live preview plus drag reorder + delete
    controls.

    Drag-and-drop is native HTML5: the dragged item records its own index in
    dataTransfer and a target row raises `reorder(from, to)` on drop, which the
    parent applies (and persists) with the same logic as the move buttons.
  -->
  <li
    class="field-item"
    :class="{ editing: isEditing, warning: invalid, 'drag-over': dragOver }"
    draggable="true"
    @click="emit('select')"
    @dragstart="onDragStart"
    @dragover.prevent
    @dragenter.prevent="dragOver = true"
    @dragleave="dragOver = false"
    @drop.prevent="onDrop"
    @dragend="dragOver = false"
  >
    <div class="order-rail" @click.stop>
      <span class="position" :aria-label="`Field position ${index + 1}`">{{ index + 1 }}</span>
      <button class="order-button" :disabled="index === 0" title="Move field up" @click="emit('move', -1)">
        <svg viewBox="0 0 20 20" aria-hidden="true"><path d="m5.5 12.5 4.5-4 4.5 4" /></svg>
        <span class="screen-reader-only">Move up</span>
      </button>
      <button class="order-button" :disabled="index === total - 1" title="Move field down" @click="emit('move', 1)">
        <svg viewBox="0 0 20 20" aria-hidden="true"><path d="m5.5 7.5 4.5 4 4.5-4" /></svg>
        <span class="screen-reader-only">Move down</span>
      </button>
      <span class="drag-grip" title="Drag to reorder" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i></span>
    </div>

    <div class="field-preview">
      <div class="field-preview-head" :class="{ 'has-data-name': specific.data_name }">
        <span class="data-name" v-if="specific.data_name">({{ specific.data_name }})</span>
        <span class="field-type">{{ field.type.replace(/field$/, '') }} / {{ subtypeLabel }}</span>
      </div>

      <label v-if="field.type !== 'booleanfield'" class="field-label">
        <span v-html="displayHtml" />
        <span v-if="specific.required" class="required-mark" aria-hidden="true"></span>
      </label>

      <FieldPreview :field="field" :option-lists="optionLists" />
    </div>

    <div class="field-controls" @click.stop>
      <button class="btn btn-danger" title="Delete field" @click="emit('delete')">
        <span aria-hidden="true">Delete</span><span class="screen-reader-only">Delete field</span>
      </button>
    </div>
  </li>
</template>

<script setup>
// Each row runs the shared field validator so invalid fields can be flagged
// with the same `warning` styling.

import { computed, ref } from 'vue'

import FieldPreview from './FieldPreview.vue'
import { useFieldValidation } from '../../composables/useFieldValidation'

const props = defineProps({
  field: { type: Object, required: true },
  optionLists: { type: Array, default: () => [] },
  isEditing: { type: Boolean, default: false },
  index: { type: Number, required: true },
  total: { type: Number, required: true },
})

const emit = defineEmits(['select', 'delete', 'move', 'reorder'])

const specific = computed(() => props.field.specific)
const subtypeLabel = computed(() => props.field.subtype.replace('_', ' '))
const invalid = useFieldValidation(computed(() => props.field)).invalid

const displayHtml = computed(() => {
  const v = specific.value.display_name
  return v ? v : '<span class=\"empty\">(Field Name)</span>'
})

const dragOver = ref(false)

function onDragStart(event) {
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', String(props.index))
}

function onDrop(event) {
  dragOver.value = false
  const from = Number(event.dataTransfer.getData('text/plain'))
  if (Number.isFinite(from) && from !== props.index) {
    emit('reorder', from, props.index)
  }
}
</script>

<style scoped>
.field-item {
  display: flex;
  align-items: stretch;
  gap: 0.75rem;
  padding: 0;
  border: 1px solid var(--f-line);
  border-radius: var(--f-radius);
  background: var(--f-surface);
  cursor: pointer;
  box-shadow: var(--f-shadow);
  overflow: hidden;
  transition: border-color 150ms ease, background-color 150ms ease, box-shadow 150ms ease;
}
.field-item:hover {
  border-color: var(--f-line-strong);
  background: #fafcfb;
}
.field-item.warning {
  border-color: rgba(150, 106, 0, 0.45);
  background: var(--f-warning-tint);
  box-shadow: inset 3px 0 0 var(--f-warning);
}
.field-item.editing {
  border-color: var(--f-accent);
  box-shadow: 0 0 0 1px var(--f-accent), 0 0 0 3px var(--f-focus-ring);
}
.field-item.drag-over {
  outline: 2px dashed var(--f-accent);
  outline-offset: -2px;
}
.order-rail {
  width: 43px;
  flex: 0 0 43px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-content: start;
  border-right: 1px solid var(--f-line);
  background: var(--f-canvas);
}
.position {
  grid-column: 1 / -1;
  display: grid;
  place-items: center;
  min-height: 31px;
  color: var(--f-accent-deep);
  font-family: var(--f-font-mono);
  font-size: 0.75rem;
  font-weight: 700;
  border-bottom: 1px solid var(--f-line);
}
.order-button {
  display: grid;
  place-items: center;
  min-width: 0;
  height: 26px;
  padding: 0;
  border: 0;
  border-right: 1px solid var(--f-line);
  border-bottom: 1px solid var(--f-line);
  color: var(--f-accent-deep);
  background: var(--f-surface);
  cursor: pointer;
}
.order-button:nth-of-type(2) { border-right: 0; }
.order-button:hover:not(:disabled) { color: #fff; background: var(--f-accent); }
.order-button:focus-visible { position: relative; outline: 2px solid var(--f-accent); outline-offset: -2px; }
.order-button:disabled { color: var(--f-faint); background: #f3f3f3; cursor: default; }
.order-button svg { width: 16px; height: 16px; fill: none; stroke: currentColor; stroke-width: 1.8; }
.drag-grip {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: repeat(2, 3px);
  gap: 3px;
  place-content: center;
  min-height: 27px;
  cursor: grab;
  user-select: none;
}
.drag-grip i { width: 3px; height: 3px; border-radius: 50%; background: var(--f-faint); }
.field-preview {
  flex: 1;
  min-width: 0;
  padding: 0.75rem 0.4rem;
}
.field-preview-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.5rem;
  margin-bottom: 0.3rem;
}
.data-name {
  font-family: var(--f-font-mono);
  color: var(--f-muted);
  font-size: 0.75rem;
}
.field-type {
  font-family: var(--f-font-mono);
  color: var(--f-faint);
  font-size: 0.7rem;
  text-transform: capitalize;
}
.field-label {
  display: block;
  margin-bottom: 0.3rem;
  font-size: 0.9375rem;
  font-weight: 500;
}
.required-mark {
  display: inline-block;
  width: 0.55em;
  height: 0.55em;
  margin-left: 0.4em;
  background: var(--f-accent);
  border-radius: 2px;
  vertical-align: 0.05em;
}
.field-controls {
  display: flex;
  align-items: center;
  padding: 0.75rem 0.8rem 0.75rem 0.25rem;
}
.btn {
  padding: 0.2rem 0.5rem;
  border: 1px solid var(--f-line);
  border-radius: var(--f-radius-sm);
  background: var(--f-surface);
  color: var(--f-ink);
  font-size: 0.85rem;
  line-height: 1.4;
  cursor: pointer;
  transition: border-color 150ms ease, background-color 150ms ease, color 150ms ease;
}
.btn:hover {
  border-color: var(--f-line-strong);
  background: var(--f-canvas);
}
.btn-danger {
  color: var(--f-danger);
  font-size: 0.75rem;
  font-weight: 600;
}
.btn-danger:hover {
  border-color: var(--f-danger);
  background: var(--f-danger-tint);
  color: var(--f-danger-deep);
}
.btn:focus-visible {
  outline: 2px solid var(--f-accent);
  outline-offset: 2px;
}
.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.empty {
  color: var(--f-faint);
  font-style: italic;
}
</style>
