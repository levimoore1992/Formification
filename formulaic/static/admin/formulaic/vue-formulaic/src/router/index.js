import { createRouter, createWebHashHistory } from 'vue-router'

import FormView from '../views/FormView.vue'
import FieldsView from '../views/FieldsView.vue'
import RulesView from '../views/RulesView.vue'
import SubmissionsView from '../views/SubmissionsView.vue'

// Hash history on purpose: the app is embedded inside the Django admin at
// /admin/formulaic/form/:id/change/, and only the sub-screen (fields/rules/
// submissions) is our business — Django owns the outer URL. Form identity comes
// from the injected bootstrap config, never the route.

export default createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      component: FormView,
      children: [
        { path: '', redirect: '/fields' },
        { path: 'fields', component: FieldsView },
        { path: 'rules', component: RulesView },
        { path: 'submissions', component: SubmissionsView },
      ],
    },
  ],
})