from pathlib import Path

from django import template
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.templatetags.static import static
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(name="formification_tinymce_key")
def formification_tinymce_key():
    return settings.FORMIFICATION_TINYMCE_KEY


@register.simple_tag(name="vue_formification_assets")
def vue_formification_assets():
    """
    <link>/<script> tags for the built Vue admin app.

    Vite hashes the bundle filenames (dist/assets/index-*.{js,css}), so the
    names are resolved here at render time instead of being hard-coded in
    change_form.html — rebuilds change the hashes without breaking the admin.

    The production assets are included in the Python distribution.
    """
    dist = (
        Path(__file__).resolve().parents[1]
        / "static/admin/formification/vue-formification/dist"
    )
    js_files = sorted(dist.glob("assets/index-*.js"))
    css_files = sorted(dist.glob("assets/index-*.css"))
    if not js_files or not css_files:
        raise ImproperlyConfigured(
            "Missing Formification Vue assets; run npm ci and npm run build in vue-formification before packaging."
        )

    css = static("admin/formification/vue-formification/dist/assets/" + css_files[0].name)
    js = static("admin/formification/vue-formification/dist/assets/" + js_files[0].name)

    return mark_safe(
        '<link rel="stylesheet" href="{css}">\n'
        '<script type="module" src="{js}"></script>'.format(css=css, js=js)
    )
