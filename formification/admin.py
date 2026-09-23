import json
from functools import update_wrapper

from admin_ordering.admin import OrderableAdmin
from django.urls import re_path
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.http import Http404
from django.shortcuts import redirect
from django.utils.encoding import force_str
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from formification import models as formification_models


def archive_forms(modeladmin, request, queryset):
    """
    Action: archive all selected forms
    """
    queryset.update(archived=True)


archive_forms.short_description = "Archive selected forms"


def form_status(form):
    """
    List Column: display static, currently Active/Archived
    """
    if form.archived:
        return mark_safe("Archived")
    else:
        return mark_safe("<strong>Active</strong>")


form_status.short_description = "Status"
form_status.allow_tags = True


def form_submissions(form):
    template = """
      <div style="line-height: 20px;">
        <a
          href="/formification/download/submissions/?form={pk}"
        >
            Download Submissions CSV
        </a>
      </div>
    """
    return mark_safe(template.format(pk=form.pk))


form_submissions.short_description = "Submissions"
form_submissions.allow_tags = True


def form_actions(form):
    """
    List Column: archive button for each form
    """
    if form.archived:
        url = reverse("admin:formification_form_unarchive", args=(form.pk,))
        return mark_safe('<a href="{}">Un-archive</a>'.format(url))
    else:
        url = reverse("admin:formification_form_archive", args=(form.pk,))
        return mark_safe('<a href="{}">Archive</a>'.format(url))


form_actions.short_description = ""
form_actions.allow_tags = True


class FormAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        "slug": ("name",),
    }

    list_display = (
        "name",
        form_submissions,
        form_status,
        form_actions,
    )

    list_filter = ("archived",)

    search_fields = ("name",)

    actions = [archive_forms]

    @property
    def media(self):
        # The form change page is a single-page Vue app; nothing extra beyond
        # the admin defaults is needed. (The old pre-SPA "edit fields" dialog
        # assets + jQuery UI CDN were removed with the rest of the legacy admin.)
        return super(FormAdmin, self).media

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        url_patterns = super(FormAdmin, self).get_urls()

        return [
            re_path(
                r"^([0-9]+)/archive/$",
                wrap(self.archive_view),
                name="formification_form_archive",
            ),
            re_path(
                r"^([0-9]+)/unarchive/$",
                wrap(self.unarchive_view),
                name="formification_form_unarchive",
            ),
            # pattern eats remaining URL path used by the admin SPA routing
            re_path(r"^([0-9]+)/.+$", wrap(self.changeform_view)),
        ] + url_patterns

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):

        # Quick redirect to /change. This is only applicable for django 1.8,
        # and can be removed after dropping support.
        if request.path.strip("/").endswith(str(object_id)):
            return redirect(request.path + "change")

        try:
            form = formification_models.Form.objects.get(pk=object_id)
        except formification_models.Form.DoesNotExist:
            form = None

        if not self.has_change_permission(request, form):
            raise PermissionDenied

        if form is None:
            raise Http404("Form does not exist")

        extra_context = extra_context or {}
        extra_context.update(
            {
                "title": _("Change %s") % force_str(self.opts.verbose_name),
                "form_id": object_id,
                "opts": self.opts,
                "app_label": self.opts.app_label,
                "has_change_permission": self.has_change_permission(request, form),
                "original": form,
                "task_data": json.dumps({"form_pk": object_id}),
                "media": self.media,
                # Vue admin bootstrap (see boot.js / README "Integration with
                # Django admin"): injected as a JSON meta tag the SPA reads at
                # import time.
                "vue_config": json.dumps(
                    {"formId": object_id, "apiBase": "/formification/api"}
                ),
            }
        )

        return super(FormAdmin, self).changeform_view(
            request, object_id=object_id, form_url=form_url, extra_context=extra_context
        )

    def get_right_queryset(self, request):
        if hasattr(self, "get_queryset"):
            return self.get_queryset(request)
        else:
            # django < 1.6
            return self.queryset(request)

    def changelist_view(self, request, extra_context=None):
        forms_data = [
            {
                "pk": obj.pk,
                "task_data": json.dumps({"form_pk": obj.pk}),
            }
            for obj in self.get_right_queryset(request)
        ]
        context = {"handl_task_forms_data": forms_data}
        context.update(extra_context or {})
        return super(FormAdmin, self).changelist_view(request, extra_context=context)

    def archive_view(self, request, object_id):
        form = formification_models.Form.objects.get(pk=object_id)
        form.archived = True
        form.save()

        return self.return_to_changelist(request)

    def unarchive_view(self, request, object_id):
        form = formification_models.Form.objects.get(pk=object_id)
        form.archived = False
        form.save()

        return self.return_to_changelist(request)

    def return_to_changelist(self, request):
        # redirect back to referring page; default to changelist
        try:
            return redirect(request.META["HTTP_REFERER"])
        except KeyError:
            return redirect(self.root_url)

    @property
    def root_url(self):
        for admin_url in self.urls:
            if admin_url.name and admin_url.name.endswith("_changelist"):
                return reverse("admin:%s" % admin_url.name)
        raise Exception("Could not identify a root URL")

    def get_actions(self, request):
        actions = super(FormAdmin, self).get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def has_delete_permission(self, request, obj=None):
        return False


class OptionInline(OrderableAdmin, admin.TabularInline):
    model = formification_models.Option
    ordering_field = "position"
    ordering_field_hide_input = True
    prepopulated_fields = {"value": ("name",)}

    fields = (
        "position",
        "name",
        "value",
    )


class OptionGroupInline(OrderableAdmin, admin.TabularInline):
    model = formification_models.OptionGroup
    ordering_field = "position"
    ordering_field_hide_input = True
    filter_horizontal = ("options",)

    fields = (
        "position",
        "name",
        "options",
    )

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        """
        Filtering queryset to `options` from the correct list
        based on `formification_optionlist` object attached in
        `OptionListAdmin`
        """

        if db_field.name == "options":
            optionlist = request.formification_optionlist
            kwargs["queryset"] = formification_models.Option.objects.filter(list=optionlist)

        return super(OptionGroupInline, self).formfield_for_manytomany(
            db_field, request=request, **kwargs
        )


class OptionListAdmin(admin.ModelAdmin):
    model = formification_models.OptionList
    inlines = (
        OptionInline,
        OptionGroupInline,
    )
    search_fields = ("name",)

    def get_form(self, request, obj=None, **kwargs):
        """
        Attaching `optionlist` object to request for use in inlines
        """
        request.formification_optionlist = obj

        return super(OptionListAdmin, self).get_form(request, obj=obj, **kwargs)


admin.site.register(formification_models.Form, FormAdmin)
admin.site.register(formification_models.OptionList, OptionListAdmin)
