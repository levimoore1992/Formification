from django.contrib import admin
from formification.admin import FormAdmin, OptionListAdmin
from formification.models import Form, OptionList

admin.site.register(Form, FormAdmin)
admin.site.register(OptionList, OptionListAdmin)
