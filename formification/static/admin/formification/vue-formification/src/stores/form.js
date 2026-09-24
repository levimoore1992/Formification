import { defineStore } from 'pinia'

import { client, config } from '../api/client'

// The form the admin is editing. Its id is injected by Django (bootstrap
// config), so the router only navigates sub-screens — there is no form param
// in the URL.
export const useFormStore = defineStore('form', {
  state: () => ({
    form: null,
    loading: false,
    error: null,
  }),

  getters: {
    formId: () => config.formId,
    displayName: (state) => (state.form ? state.form.name : 'Loading…'),
  },

  actions: {
    async load() {
      this.loading = true
      this.error = null
      try {
        // GET /formification/api/forms/:id/
        this.form = await client.getForm(config.formId)
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    },
  },
})