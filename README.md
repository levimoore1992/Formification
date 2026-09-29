# Formification

**Formification** is a Django app for building custom web forms and collecting
submissions. Forms are defined and managed from the Django admin, rendered
publicly through Django's form framework, and every submission is stored and
exportable from the admin interface.

- **Dynamic forms** — authors compose forms (fields, option lists, validation
  rules) entirely from the admin UI. No code is required to ship a new form.
- **Public rendering** — forms render with a Bootstrap 3 stylesheet and plug
  into standard Django form patterns for easy theming.
- **Submission collection** — each submission is stored with the form, source
  page, and metadata; retriable via the admin or the REST API.
- **Vue 3 admin** — the form builder runs as a checked-in Vue SPA. It ships
  prebuilt in the wheel, so you don't need Node.js to use Formification.

## Installation

```shell
pip install django-formification
```

Add it to your Django project:

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "django_filters",
    "rest_framework",
    "formification",
]
```

```python
# urls.py
from django.urls import include, path

urlpatterns = [
    # ...
    path("formification/", include("formification.urls")),
    path("admin/", admin.site.urls),
]
```

Apply the migrations:

```shell
python manage.py migrate
python manage.py collectstatic --noinput
```

## Configuration

Set where exported submission CSV files are written:

```python
# settings.py
FORMIFICATION_EXPORT_STORAGE_LOCATION = "/data/shared/assets/formification_exports"
```

## Defining a form

Forms are created in the Django admin (`/admin/formification/`). After that,
render them with a plain Django form:

```python
from django.shortcuts import redirect, render

from formification.forms import CustomForm
from formification.models import Form


def my_form(request):
    formification_form = Form.objects.get(slug="robot-form")

    if request.method == "POST":
        form = CustomForm(
            request.POST,
            request=request,
            instance_id="form-page-a",  # recorded on each submission
            form=formification_form,
        )

        if form.is_valid():
            formification_form.create_submission(
                form.cleaned_data,
                source=form.instance_id,
                metadata={"extra-data-1": "some data"},
            )
            return redirect("form-complete")

    else:
        form = CustomForm(
            request=request,
            instance_id="form-page-a",
            form=formification_form,
        )

    return render(request, "my_form.html", {"form": form})
```

```html
<!-- my_form.html -->
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>My Form</title>
  </head>
  <body>
    {{ form }}
  </body>
</html>
```

## Custom form layouts

The default `{{ form }}` rendering includes initialization automatically. For a
custom layout, load the `formification` tag library and put
`{% formification_init form %}` after the form:

```django
{% load form formification %}
<form id="{{ form.instance_id }}" method="post" enctype="multipart/form-data">
  {% csrf_token %}
  {% for hidden in form.hidden_fields %}{{ hidden }}{% endfor %}
  {% for field in form.visible_fields %}
    <div class="field-wrapper {{ field.field.widget|formification_field_classes }}">
      {{ field.label_tag }}
      {{ field|formification_extra_attributes }}
      {{ field.errors }}
    </div>
  {% endfor %}
  <button type="submit">Submit</button>
</form>
{% formification_init form %}
```

Keep the `.field-wrapper` around each visible field and render its widget to
preserve the data attributes used by conditional rules and grouped choices.
The form element's `id` must match the `instance_id` passed to `CustomForm`.
Use a unique instance ID for each form on a page (letters, digits, underscores,
and hyphens are recommended).

The tag includes `form.media`, safely serializes rules with Django's
`json_script`, and waits for the JavaScript module dependency before initializing.
Use it once per form; repeated calls for the same form element are harmless.
Multiple forms share the module, which the browser executes only once.

When migrating a custom template, replace both `{{ form.media }}` and your
inline `Formification.forms.add(...)` script with this tag. No additional tag
is needed when using the default `{{ form }}` template. Serve the package's
static assets normally, including `formification/init.js`; rerun `collectstatic`
when deploying an upgrade.

## Dependencies

### Python

- Django >= 4.2, < 7 (tested on 4.2, 5.2, 6.0, and 6.1)
- Python >= 3.10
- djangorestframework >= 3.15.2
- django-filter >= 24.3
- django-ckeditor >= 6.7
- phonenumbers, pyzipcode, us, nameparser, tzlocal

### JavaScript

- The public forms bundle **jquery**, **Bootstrap**, and **intl-tel-input** into a
  single checked-in bundle, so public-facing forms need no external JavaScript.
- The admin is a **Vue 3** SPA. The built bundle is checked in and ships inside
  the wheel — installing Formification needs **no Node.js runtime**. To change
  the admin, see the `README.md` inside
  `formification/static/admin/formification/vue-formification/`, then rebuild
  and commit the updated `dist/` files.
- To change the public form assets, see
  `formification/static/formification/vite-formification/`, then rebuild and
  commit the updated `dist/` files.

### Development

The `internal/` directory is a runnable Django project used to develop and demo
Formification locally. From the repository root:

```shell
uv sync
uv run python manage.py migrate
uv run python manage.py runserver 0.0.0.0:8000
uv run python manage.py createsuperuser
```

Or use the `make` shortcuts (see the `Makefile`):

```shell
make setup   # uv sync
make migrate # apply migrations
make seed    # load mock demo data
make run     # runserver 0.0.0.0:8000
make lint    # black --check + flake8 (mirrors CI)
make e2e     # real-browser end-to-end tests (pytest-playwright)
```

### End-to-end tests

The `internal/e2e/` suite combines `pytest-playwright` with `pytest-django`.
Django manages an isolated test database and a live HTTP server on an available
port, including static files and automatic shutdown. Each test creates its form
and rules using factory_boy factories. Coverage includes conditional required
fields, clearing hidden values, option-group switching, AND/OR rules and rule
precedence, text/numeric/multi-select comparisons, and mobile submission. A
separate admin test creates fields and rules through the Vue editor, reloads and
edits them, then submits the public form. Submissions are verified in the test
database; the development `db.sqlite3` is never used.

The editor currently offers `is` and `is_not`. Additional model/API operators
(`contains`, `does_not_contain`, `begins_with`, `ends_with`, `greater_than`,
`less_than`, `any_selected`, and `all_selected`) are exercised with factory data.

```shell
make e2e-setup  # one-time: install Playwright's chromium
make e2e        # run the suite
```

Install development dependencies with `uv sync`. Standard Playwright options
work too, for example `uv run pytest --headed --tracing retain-on-failure`.

### Demo data

`make seed` loads realistic placeholder data into the local database so you
can get a feel for the app immediately: a superuser (`demo`, password
`demo1234`), a rich "Demo Form" with mixed field types, conditional rules,
and sample submissions, plus the public `robot-form`. It is safe to re-run.

Visit the demo form at `http://localhost:8000/` and the admin at
`/admin/` (log in as `demo` / `demo1234`).

## License

Formification is licensed under the [MIT License](LICENSE).
