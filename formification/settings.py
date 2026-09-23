from django.conf import settings

"""
Required settings; must be implemented in site's settings.py
"""
FORMIFICATION_EXPORT_STORAGE_LOCATION = getattr(
    settings, "FORMIFICATION_EXPORT_STORAGE_LOCATION"
)
