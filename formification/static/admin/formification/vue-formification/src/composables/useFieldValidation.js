// Field editor validation.
//
// Rules enforced so pre-existing forms can't become unsavable:
//   - display_name required, ≤ 1000 chars
//   - data_name   required, ≤ 200 chars
//   - slug is auto-generated from data_name, so it's only "invalid" when
//     data_name itself is invalid
//   - choice fields additionally require an option_list
//
// `field` must be a computed/ref resolving to a normalized store record
// (see stores/fields.js normalizeField).

import { computed } from 'vue'

const DISPLAY_NAME_LENGTH = 1000
const DATA_NAME_LENGTH = 200

export function useFieldValidation(field) {
  const displayNameInvalid = computed(() => {
    const v = field.value?.specific?.display_name
    return !v || v.length > DISPLAY_NAME_LENGTH
  })

  const dataNameInvalid = computed(() => {
    const v = field.value?.specific?.data_name
    return !v || v.length > DATA_NAME_LENGTH
  })

  // No slug set → it will be auto-generated on save, so only flag it when the
  // thing it is generated from is bad.
  const slugInvalid = computed(
    () => !field.value?.specific?.slug && dataNameInvalid.value
  )

  const optionListInvalid = computed(
    () =>
      field.value?.type === 'choicefield' &&
      field.value.specific.option_list == null
  )

  const invalid = computed(() =>
    [
      displayNameInvalid.value,
      dataNameInvalid.value,
      slugInvalid.value,
      optionListInvalid.value,
    ].some(Boolean)
  )

  return {
    displayNameInvalid,
    dataNameInvalid,
    slugInvalid,
    optionListInvalid,
    invalid,
    message: computed(() =>
      invalid.value
        ? [
            displayNameInvalid.value && 'Display name is required (max 1000 chars)',
            dataNameInvalid.value && 'Data column name is required (max 200 chars)',
            optionListInvalid.value && 'An option list is required',
          ]
            .filter(Boolean)
            .join(', ')
        : ''
    ),
  }
}