from django.contrib import admin
from formulaic.admin import FormAdmin, OptionListAdmin
from formulaic.models import Form, OptionList

admin.site.register(Form, FormAdmin)
admin.site.register(OptionList, OptionListAdmin)