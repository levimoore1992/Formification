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
pip install formification
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

## Dependencies

### Python

- Django >= 4.2, < 7
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
```

### Demo data

`make seed` loads realistic placeholder data into the local database so you
can get a feel for the app immediately: a superuser (`demo`, password
`demo1234`), a rich "Demo Form" with mixed field types, conditional rules,
and sample submissions, plus the public `robot-form`. It is safe to re-run.

Visit the demo form at `http://localhost:8000/` and the admin at
`/admin/` (log in as `demo` / `demo1234`).

## License

Formification is licensed under the [MIT License](LICENSE).
