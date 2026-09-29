from uuid import uuid4

from django import template

register = template.Library()


@register.inclusion_tag("formification/init.html")
def formification_init(form):
    """Render assets and safely initialize a custom or default form layout."""
    return {
        "form": form,
        "config_id": f"formification-config-{uuid4().hex}",
        "config": {"instanceId": form.instance_id, "rules": form.rules_data},
    }
