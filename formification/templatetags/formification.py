from uuid import uuid4

from django import template

register = template.Library()


@register.inclusion_tag("formification/init.html")
def formification_init(form, instance_id=None):
    """Render assets and safely initialize a custom or default form layout."""
    instance_id = instance_id or getattr(form, "instance_id", None)
    if not instance_id:
        raise ValueError("Pass instance_id when initializing a standard Django form.")
    return {
        "form": form,
        "config_id": f"formification-config-{uuid4().hex}",
        "config": {"instanceId": instance_id, "rules": getattr(form, "rules_data", [])},
    }
