from django.contrib import admin
from formulaic.admin import FormAdmin, OptionListAdmin, PrivacyPolicyAdmin
from formulaic.models import Form, OptionList, PrivacyPolicy

admin.site.register(Form, FormAdmin)
admin.site.register(OptionList, OptionListAdmin)
admin.site.register(PrivacyPolicy, PrivacyPolicyAdmin)
