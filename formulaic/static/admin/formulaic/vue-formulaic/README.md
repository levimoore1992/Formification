# vue-formulaic — Vue 3 admin for the Formulaic Django app

A **Vue 3 + Vite + Pinia** admin SPA for form-building in the Django admin.
This build is the live admin served from `change_form.html`.

> **Status: complete.** The Vue app is wired into `change_form.html`. The full
> **Fields** screen (list with live
> previews, add, drag-and-drop + button reorder, delete, and the per-field
> sidebar editor covering all four field classes — including the TinyMCE
> WYSIWYG display-name editor), the **Rules** editor (conditions, results,
> AND/OR, option-group swap, batch save), and the **Submissions** browser
> (paginated table, source filter, CSV export link) are implemented. Remaining
> items are Django-admin-side (option list sub-editor).

## Why Vue (decision record)

- The SPA is a real SPA: routing, cross-screen state, polymorphic field data,
  and drag-sort + save flows call for a component framework rather than
  wrapper-heavy boilerplate.
- Vue 3 gives a single-file component (template + script + scoped CSS), a
  readable template language (plain HTML + `v-for`/`v-if`/`@click`/`v-model`),
  and a first-class Vite plugin.
- **Deliberately not Alpine.js / vanilla**: the admin is a real SPA (routing,
  cross-screen state, polymorphic data, drag-sort + save flows). Alpine is a
  good fit for the *public* form (server-rendered Django template + light JS),
  but not this editor.
- Alternative: **Svelte** would also fit; Vue chosen for mainstream tooling
  (Pinia, Vue Router) and HTML-like templates.

## Quick start

Requirements: Node 18+ (Vite 6).

```sh
# Dev — hot reload, proxies /formulaic + /admin to Django on :8000
npm install
npm run dev            # → http://localhost:5173/?formId=1

# Production build — emits to dist/ with a relative base
npm run build          # → dist/ (index.html + assets)
```

Dev login: log into Django first at `http://localhost:8000/admin/` (run the
example project with `uv run python manage.py runserver 0.0.0.0:8000`). The dev
proxy forwards the same host-only session + csrftoken cookies to Django, so the
SPA authenticates via DRF session auth automatically.

If the Django server target changes, rebind the proxy in
`vite.config.js` (`DJANGO_DEV`).

## Directory map

```
vue-formulaic/
├── index.html              # dev shell; the <div id="formulaic-container"> mount
├── vite.config.js          # vue plugin, relative base, dev proxy → Django :8000
├── package.json            # vue, vue-router, pinia, vite
└── src/
    ├── main.js             # createApp + pinia + router, mount, initial load
    ├── App.vue             # <router-view/> shell
    ├── boot.js             # reads injected bootstrap config (form id, api base)
    ├── api/
    │   └── client.js       # DRF REST wrapper + CSRF; `client` singleton
    ├── router/
    │   └── index.js        # hash history; /fields /rules /submissions
    ├── stores/
    │   ├── form.js         # current Form (Pinia)
    │   ├── fields.js       # field list + FIELD_TYPES catalog + CRUD/order/save
    │   ├── rules.js        # rule list + nested conditions/results + batch save
    │   └── submissions.js  # submission rows/sources + column helpers
    ├── composables/
    │   ├── useFieldValidation.js  # editor validation
    │   └── useRuleValidation.js   # rule/condition/result validation
    ├── utils/
    │   └── slug.js         # slug generation + hasHtml
    ├── components/
    │   ├── fields/
    │   │   ├── FieldEditor.vue       # sidebar editor for all 4 field classes
    │   │   ├── FieldPreview.vue      # read-only widget per subtype
    │   │   ├── FieldListItem.vue     # field row: preview + validation + drag controls
    │   │   └── RichTextEditor.vue    # TinyMCE (window.tinymce) + textarea fallback
    │   └── rules/
    │       ├── RuleEditor.vue            # one rule card (conditions + results)
    │       ├── RuleConditionEditor.vue   # condition row (field/operator/typed value)
    │       └── RuleResultEditor.vue      # result row (action/field/option group)
    └── views/
        ├── FormView.vue        # tabbed layout shell
        ├── FieldsView.vue      # two-column: list + sidebar (add / edit)
        ├── RulesView.vue       # rule list + Save & Continue / Save / Close
        └── SubmissionsView.vue # paginated table + source filter + CSV link
```

## Integration with Django admin (contract)

The Vue app is mounted at `/admin/formulaic/form/:id/change/`, served by
`formulaic/admin.py` (`FormAdmin.changeform_view`) and
`formulaic/templates/admin/formulaic/form/change_form.html`:

1. **Container** — mounts at the existing `<div id="formulaic-container"></div>`.
2. **Bootstrap config** — `changeform_view` injects `vue_config`
   (`{"formId": <pk>, "apiBase": "/formulaic/api"}`) into context; the template
   emits `<meta name="vue-formulaic/config/environment" content="{{ vue_config }}">`.
3. **Assets** — the length-one `{% vue_formulaic_assets %}` tag (setting_tags.py)
   outputs `<link>`+`<script type="module">` for the **content-hashed** build.
   It globs `dist/assets/index-*.{js,css}` at render time, so rebuilds never
   break the template (no manual hash updates). It returns an empty string if
   the build output is missing, so the page still renders.

The TinyMCE Cloud script (`{% formulaic_tinymce_key %}`) is in the template and
provides the `window.tinymce` global the WYSIWYG editor uses.

Serving the build: with `django.contrib.staticfiles` the assets are found from
the app's static dir (`formulaic/static/.../vue-formulaic/dist/`) via
`{% static %}` once `dist/` exists. `vite.config.js` uses `base: './'` so all
asset URLs are relative to wherever the app is served.

## API surface (what the client talks to)

DRF viewsets from `formulaic/urls.py` (router = `/formulaic/api/`, trailing
slashes on every URL):

| Resource | Endpoint | Notes |
| --- | --- | --- |
| Form | `GET /forms/:id/` | name, slug, success_message |
| Fields (list) | `GET /fields/?form=:id` | base rows, **nested** specific model |
| TextField | `POST/PATCH /textfields/` `/textfields/:id/` | |
| ChoiceField | `POST/PATCH /choicefields/` `/choicefields/:id/` | needs `option_list` |
| BooleanField | `POST/PATCH /booleanfields/` `/booleanfields/:id/` | |
| HiddenField | `POST/PATCH /hiddenfields/` `/hiddenfields/:id/` | |
| Field delete | `DELETE /fields/:id/` | viewset cleans up related rules |
| OptionLists | `GET /optionlists/` | nested options + groups |
| Rules | `GET /rules/?form=:id` `POST/PATCH/DELETE /rules/...` | nested conditions/results |
| Submissions | `GET /submissions/?form=:id` | paginated (page_size 25 here) |
| SubmissionSources | `GET /submissionsources/?form=:id` | re_path view, `[{source, count}]` |

Auth: same-origin Django session + DRF `CustomDjangoModelPermissions`
(change_formulaic_form-style perms). CSRF forwarded from the `csrftoken` cookie
on unsafe methods (see `api/client.js`).

## Data-model notes (read before touching fields)

- **Polymorphic fields.** Every `Field` row (base model in `models.py`) maps 1:1
  to a `TextField` / `ChoiceField` / `BooleanField` / `HiddenField` subclass,
  linked via a `ContentType` FK. Field.save() stamps `content_type` +
  `model_class` server-side — send `model_class` and `subtype`, never a
  content_type.
- LISTING returns the base serializer with one nested specific model:
  `{ model_class: "textfield", ..., textfield: {...}, choicefield: null, ... }`.
  The store normalizes this into one record (`specific` = the non-null nested
  object). WRITES go to the *specific* endpoints (`/textfields/`, ...) — the
  base `/fields/` serializer is read-friendly only.
- **Ordering** is the `position` integer column ordered ascending;
  `orderFields()` saves every field's position after a reorder.
- **ChoiceFields** require an `OptionList` (FK, PROTECT) before creation; the
  add-field UI surfaces this.
- **Rules** (PATCH /rules/:id/) take nested `conditions` + `results` arrays:
  child with an `id` = update, without = create, absent from the list = delete.
  Implemented in `RuleSerializer.create/update` (`serializers.py`). `value` is a
  `JsonField` (any JSON).
- The `name` column on Field is legacy/unused; serializers omit it so it always
  persists as `''`.
- **ChoiceField defaults round-trip as JSON strings.** `default_option` /
  `default_options` (serializers.py `DefaultOptionField`/`DefaultOptionsField`)
  accept `"5"` / `["5"]`; the editor binds selects to `String(option.id)`.
  `option_list`/`option_group` are integer FK ids, and the choice validator
  requires `option_list`.
- The old admin's **"password" text subtype had no backend implementation** and
  crashed form rendering, so it is intentionally absent from `FIELD_TYPES`.

## Status

- [x] Scaffold (Vite config, boot, router, Pinia, API client, CSRF)
- [x] Form shell + tabs (Fields / Rules / Submissions)
- [x] Fields: list, add each subtype, delete, reorder (persists positions)
- [x] Rules: full editor (conditions + results, AND/OR, option-group swap)
- [x] Submissions: paginated table, source filter, CSV export link (Django view)
- [x] Fields: sidebar editor — base form + hidden/boolean/choice specifics,
      validation, auto-slug, option list/groups,
      default selection, min/max, WYSIWYG toggle
- [x] Fields: live preview components (one widget per subtype)
- [x] Fields: drag-and-drop reordering (native HTML5, + up/down fallback buttons)
- [x] Fields: WYSIWYG real editor (TinyMCE via the change_form CDN global;
      textarea fallback when the CDN script isn't loaded, e.g. `npm run dev`)
- [x] Wire into `change_form.html` (Vue build served via `vue_formulaic_assets`)
- [ ] Option list sub-editor (currently Django-admin side)
- [ ] Keep an eye on: archive/unarchive buttons in the form header, toast-style
      notifications (currently rendered inline)

## Fields screen notes

- **Live previews** (`FieldPreview.vue`) render one widget per subtype,
  verbatim, including the placeholder strings ("Lorem ipsum dolor", "John Q.
  Public", the radio/checkbox sample rows, …). The label + data-name badge live
  in the row wrapper (`FieldListItem.vue`). The one place the checkbox
  (boolean) field differs is that it renders its own label inside the widget.
- **Default-option names.** `default_option` is stored as the option's id (a
  JSON string on the API), so `FieldPreview` resolves it by scanning
  `optionLists[].options` (ids globally unique) and falls back to
  `default_text`, then `(Choose One)` / the radio-sample text.
- **Invalid-field warning.** `FieldListItem` runs
  `useFieldValidation` (called once per item component — composables can't run
  inside `v-for`) and adds the amber `warning` class.
- **Drag-and-drop is native HTML5** (`draggable`, `dataTransfer` index, drop →
  `reorder(from, to)`), reusing the same path as the ↑/↓ buttons. `orderFields`
  renumbers every `position` to the new array order and PATCHes all rows — the
  in-memory `position` is stale mid-drag, so comparing against it would wrongly
  skip rows; save everything.
- **WYSIWYG** (`RichTextEditor.vue`) initializes TinyMCE on the mounted
  textarea (`height: 120`, `menubar: false`,
  plugins `link`, toolbar `bold italic | link`, `forced_root_block: ''` — no
  wrapping `<p>`, matching the raw HTML those display names contain). It reads
  the `window.tinymce` global loaded by change_form.html's Cloud CDN script, and
  degrades to a plain textarea when the script isn't on the page (standalone dev
  server). The WYSIWYG toggle still defaults to ON when the display name
  contains HTML (`hasHtml`).

## Rules editor notes (deviations, read before touching)

- **Save flow.** One batch pass: DELETE pending rules (marked-for-delete ids),
  PATCH dirty saved rules, POST new rules — then refetch (`Promise.all` +
  `fetchForForm`).
- **Nested payload rule.** The `RuleSerializer.update` replaces children by the
  arrays you send: `id` present = update, absent = create, absent-from-array
  (but present in DB) = delete. The nested `rule` key on children is `null` for
  unsaved rules (both FKs are nullable at the model level) and fine for existing
  ones. `conditions` + `results` arrays are **required** on PATCH — always send
  both.
- **`value` is JSON.** Conditions store `value` in a `JsonField`
  (`models.RuleCondition.value` → `value_string` = `json.dumps(value)`): a
  string for text fields, the option **id** (number) for choice fields, `null`
  for boolean fields. Send exactly what the widget picks; do not stringify
  choice ids for the payload.
- **Option groups for change-option-group results** come from
  `GET /optiongroups/?list=:id`, cached per list id in `rules.optionGroupsByList`
  (`listOptionGroups` in the client). The fields store's `optionLists` only carry
  group *ids*, not group objects — that's why the rules store fetches them.
- **Validation** (both prevent a dead-end DRF 400): the
  composer also requires `condition.operator` and `result.action` (both are
  non-nullable columns). Everything else follows the same
  rules: a rule needs ≥1 condition + ≥1 result; conditions
  need a field + value unless boolean; change-option-group needs a group and a
  list with groups.
- Rule **positions** are renumbered to array order on save (there's no rule
  drag-and-drop yet).

## Submissions table notes

- **Pagination.** The API is DRF `StandardResultsSetPagination` (default
  page_size 5; max 1000). The screen requests `page_size=25` and ignores the
  `next`/`previous` URLs in the envelope, deriving Previous/Next
  from `count` + page_size.
- **Columns** mirror `Submission.custom_data` (models.py): base columns
  [Date/Time, Source, Promo Source] then one column per field in `position`
  order, cell = `custom_data[field.slug]` (may be empty for unfilled fields).
  Because the `FieldViewset` doesn't order its queryset, `fields.fetchForForm`
  now sorts by `position` (drives both this table and the Fields tab list).
- **Cell rendering.** Raw cell values can be arrays or objects; `cellText()`
  joins arrays, JSON-stringifies
  objects, blanks null.
- **Source filter** hits the custom re_path view
  `GET /api/submissionsources/?form=:id` → `[{ source, count }]`; the select
  value `''` means "all sources" (`submissions.store.setSource` clears to null).
- **CSV export is outside the SPA** — the "Download CSV" link targets Django's
  `/formulaic/download/submissions/?form=:id` (`views.download_submissions`,
  requires `change_submission`). Kept as a plain link (target=_blank) rather
  than fetching it into the SPA.
- Page/source live in the Pinia store, not the URL (hash routing makes query
  params awkward) — browser back/forward navigation is lost, accepted for now.

## Conventions & gotchas

- **JS only, no TypeScript** — matches repo style; easy to introduce later.
- Every API call goes through `api/client.js`; do **not** sprinkle `fetch`
  around views. Stores own all data; views are dumb.
- Form id / api base come from `boot.js` config **once** (import-time), not from
  the route or components.
- Django owns the outer URL; the SPA only navigates its hash sub-screens.
- The public-facing form (`formulaic/static/formulaic/js/custom_form.js`,
  rule show/hide) is a **separate concern** — not part of this admin port.

## Useful commands

```sh
npm run dev        # dev server on :5173 with proxy to Django :8000
npm run build      # production build → dist/
npm run preview    # serve dist/ locally
```

Python side (repo root): tests via `manage.py test` (uses `internal/` demo
project); lint via `black` + `flake8` (GitHub Actions runs both on PRs).