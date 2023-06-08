from django.conf import settings

"""
Required settings; must be implemented in site's settings.py
"""
FORMULAIC_EXPORT_STORAGE_LOCATION = getattr(settings, 'FORMULAIC_EXPORT_STORAGE_LOCATION')

if 'captcha' not in settings.INSTALLED_APPS:
    raise Exception("The 'django-simple-captcha' app is required to use the 'my_package' app. Please add 'captcha' to your INSTALLED_APPS setting.")