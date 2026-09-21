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
    <span class="drag-grip" title="Drag to reorder">⠿</span>

    <div class="field-preview">
      <div class="field-preview-head" :class="{ 'has-data-name': specific.data_name }">
        <span class="data-name" v-if="specific.data_name">({{ specific.data_name }})</span>
        <span class="field-type">{{ field.type.replace(/field$/, '') }} / {{ subtypeLabel }}</span>
      </div>

      <label v-if="field.type !== 'booleanfield'" class="field-label">
        <span v-html="displayHtml" />
        <span v-if="specific.required" class="text-danger">*</span>
      </label>

      <FieldPreview :field="field" :option-lists="optionLists" />
    </div>

    <div class="field-controls" @click.stop>
      <button class="btn" :disabled="index === 0" title="Move up" @click="emit('move', -1)">↑</button>
      <button class="btn" :disabled="index === total - 1" title="Move down" @click="emit('move', 1)">↓</button>
      <button class="btn btn-danger" title="Delete" @click="emit('delete')">✕</button>
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
  padding: 0.5rem 0.75rem;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background: #fff;
  cursor: pointer;
}
.field-item.warning {
  border-color: #e8b800;
  background: #fffcf0;
}
.field-item.editing {
  border-color: #2f80ed;
  box-shadow: 0 0 0 1px #2f80ed;
}
.field-item.drag-over {
  outline: 2px dashed #2f80ed;
  outline-offset: -2px;
}
.drag-grip {
  align-self: center;
  color: #bbb;
  cursor: grab;
  font-size: 1.1rem;
  user-select: none;
}
.field-preview {
  flex: 1;
  min-width: 0;
}
.field-preview-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}
.data-name {
  color: #888;
  font-size: 0.8rem;
}
.field-type {
  color: #999;
  font-size: 0.75rem;
  text-transform: capitalize;
}
.field-label {
  display: block;
  margin-bottom: 0.25rem;
  font-size: 0.95rem;
}
.field-controls {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}
.btn {
  padding: 0.2rem 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  background: #f7f7f7;
  cursor: pointer;
}
.btn-danger {
  color: #c0392b;
}
.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.text-danger {
  color: #c0392b;
}
.empty {
  color: #aaa;
  font-style: italic;
}
</style>