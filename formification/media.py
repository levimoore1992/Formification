"""Public form media preserves ES module and Django asset attributes."""

from django import forms


class ModuleScript:
    """Module asset for Django 4.2, which predates native Script objects."""

    def __init__(self, path):
        self.path = path

    def __html__(self):
        from django.templatetags.static import static
        from django.utils.html import format_html

        return format_html(
            '<script src="{}" type="module"></script>', static(self.path)
        )


script = getattr(forms.widgets, "Script", None)
PUBLIC_SCRIPT = (
    script("formification/dist/form.js", type="module")
    if script
    else ModuleScript("formification/dist/form.js")
)


class PublicFormMedia(forms.Media):
    """Native Django media with an explicitly typed public module asset."""

    js = (PUBLIC_SCRIPT,)
    css = {"all": ("formification/dist/form.css",)}
