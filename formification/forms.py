from __future__ import unicode_literals

import json

from django import forms
from django.template.context_processors import csrf
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe

from formification.rules import RuleAssessor


class ModuleScriptMedia(forms.Media):
    """Media that renders JS as ES module scripts.

    The public form bundle (built with Vite) is an ES module: it lazy-loads the
    intl-tel-input utils chunk with a dynamic ``import()``, which requires
    ``import.meta``. A module script cannot be served as a classic script, so
    override :meth:`render_js` to emit ``type="module"`` tags.
    """

    js = ("formification/dist/form.js",)
    css = {
        "all": (
            "formification/dist/form.css",
            "formification/css/custom_form.css",
        ),
    }

    def render_js(self):
        from django.utils.html import format_html

        return [
            format_html(
                '<script type="module" src="{}"></script>',
                self.absolute_path(path),
            )
            for path in self._js
        ]


class CustomForm(forms.Form):
    required_css_class = "required"

    # Assigned explicitly (not via a nested `class Media:`) because Django's
    # media_property flattens the declaration into a plain forms.Media, losing
    # the render_js override above.
    media = ModuleScriptMedia(js=ModuleScriptMedia.js, css=ModuleScriptMedia.css)

    def __init__(self, data=None, *args, **kwargs):
        self.instance_id = kwargs.pop("instance_id")
        self.template = kwargs.pop("template", "formification/bootstrap-form.html")

        self.request = kwargs.pop("request")
        form = kwargs.pop("form")
        widget_attrs = kwargs.pop("widget_attrs", {})
        fields = form.field_set.all()
        self.field_slugs_by_id = {}

        super(CustomForm, self).__init__(data, *args, **kwargs)

        # Add fields to form
        for i, field in enumerate(fields):
            specific_field = field.get_specific_field()

            self.fields[field.slug] = specific_field.get_implementation(
                widget_attrs=widget_attrs
            )

            self.field_slugs_by_id[field.id] = field.slug

        # Add rules to form
        self._rules = form.rule_set.all()

    def _clean_fields(self):
        super(CustomForm, self)._clean_fields()

        rule_assessor = RuleAssessor(self.rules_data, self.fields, self.cleaned_data)

        for invisible_field in rule_assessor.invisible_fields:
            if invisible_field in self._errors:
                del self._errors[invisible_field]

            if invisible_field in self.cleaned_data:
                del self.cleaned_data[invisible_field]

    @cached_property
    def rules_data(self):
        rules_list = []

        for rule in self._rules:
            # convert rule's conditions
            conditions_list = []
            for condition in rule.conditions.all():
                conditions_list.append(
                    {
                        "field_id": condition.field_id,
                        "field_slug": self.field_slugs_by_id[condition.field_id],
                        "operator": condition.operator,
                        "value": condition.value,
                    }
                )

            # convert rule's results
            results_list = []
            for result in rule.results.all():
                results_list.append(
                    {
                        "field_id": result.field_id,
                        "field_slug": self.field_slugs_by_id[result.field_id],
                        "action": result.action,
                        "option_group_id": result.option_group_id,
                    }
                )

            # convert rule
            rules_list.append(
                {
                    "operator": rule.operator,
                    "conditions": conditions_list,
                    "results": results_list,
                }
            )

        return rules_list

    @property
    def rules_json(self):
        return json.dumps(self.rules_data)

    def render(self):
        c = {"form": self}
        c.update(csrf(self.request))

        return mark_safe(render_to_string(self.template, c))

    def __str__(self):
        return self.render()
