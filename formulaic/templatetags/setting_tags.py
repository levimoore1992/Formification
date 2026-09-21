from pathlib import Path

from django import template
from django.conf import settings
from django.templatetags.static import static
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(name="formulaic_tinymce_key")
def formulaic_tinymce_key():
    return settings.FORMULAIC_TINYMCE_KEY


@register.simple_tag(name="vue_formulaic_assets")
def vue_formulaic_assets():
    """
    <link>/<script> tags for the built Vue admin app.

    Vite hashes the bundle filenames (dist/assets/index-*.{js,css}), so the
    names are resolved here at render time instead of being hard-coded in
    change_form.html — rebuilds change the hashes without breaking the admin.

    Returns an empty string when the build output is missing, so the admin page
    still renders (just without the SPA) instead of erroring.
    """
    dist = (
        Path(__file__).resolve().parents[1]
        / "static/admin/formulaic/vue-formulaic/dist"
    )
    js_files = sorted(dist.glob("assets/index-*.js"))
    css_files = sorted(dist.glob("assets/index-*.css"))
    if not js_files or not css_files:
        return ""

    css = static("admin/formulaic/vue-formulaic/dist/assets/" + css_files[0].name)
    js = static("admin/formulaic/vue-formulaic/dist/assets/" + js_files[0].name)

    return mark_safe(
        '<link rel="stylesheet" href="{css}">\n'
        '<script type="module" src="{js}"></script>'.format(css=css, js=js)
    )