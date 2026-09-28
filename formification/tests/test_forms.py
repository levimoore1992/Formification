from django.forms import fields, widgets
from django import VERSION
from django.test import SimpleTestCase, TestCase, override_settings
from unittest import skipUnless

from django.utils.html import format_html

from formification import models
from formification.forms import CustomForm, ModuleScriptMedia


class CustomFormTests(TestCase):
    def setUp(self):
        # create form
        form, created = models.Form.objects.get_or_create(
            name="My Test Form", slug="my-test-form"
        )
        self.form_id = form.id

        # add textfield
        models.TextField.objects.get_or_create(
            name="Text Field 1",
            slug="text-field-1",
            required=True,
            help_text=None,
            # model_class="",
            # content_type=None,
            position=0,
            form_id=self.form_id,
            enabled=0,  # todo: not implemented?
            css_class=None,
            subtype=models.TextField.SUBTYPE_TEXT,
        )

    def test_generation(self):
        """
        Test CustomForm init, fields, etc
        """
        field_count = 1

        form = models.Form.objects.get(pk=self.form_id)
        formification_form = CustomForm(
            instance_id="primary_form", form=form, label_suffix="", request=None
        )

        self.assertTrue(
            len(formification_form.fields) == field_count,
            "Form's field count is incorrect: {} instead of {}".format(
                len(formification_form.fields), field_count
            ),
        )

        for field in formification_form:
            # TODO: this needs to be modified for different field types
            self.assertIsInstance(
                field.field,
                fields.CharField,
                "CustomForm generated wrong Django field type: {} instead of {}".format(
                    field.field.__class__, fields.CharField
                ),
            )
            self.assertIsInstance(
                field.field.widget,
                widgets.TextInput,
                "CustomForm generated wrong widget type: {} instead of {}".format(
                    field.field.widget.__class__, widgets.TextInput
                ),
            )

    def test_submission(self):
        """
        Test CustomForm submission
        """
        field_count = 1

        post_data = {"text-field-1": "My Test Value"}

        form = models.Form.objects.get(pk=self.form_id)
        custom_form = CustomForm(
            post_data,
            instance_id="primary_form",
            form=form,
            label_suffix="",
            request=None,
        )

        self.assertTrue(custom_form.is_valid(), "Form isn't valid.")

        if custom_form.is_valid():
            obj = form.create_submission(
                custom_form.cleaned_data, source=custom_form.instance_id
            )

            submission = models.Submission.objects.get(pk=obj.pk)

            self.assertEqual(submission.form_id, self.form_id)
            self.assertIsNotNone(submission.date_created)
            self.assertEqual(submission.source, "primary_form")
            self.assertEqual(len(submission.custom_data.keys()), field_count)
            self.assertEqual(submission.custom_data["text-field-1"], "My Test Value")

    def test_state_and_city_auto_populated_from_zip(self):
        # create form
        zip_form, created = models.Form.objects.get_or_create(
            name="My Zip Form", slug="my-zip-form"
        )
        post_data = {"Zipcode": "21043", "City": "", "State": ""}

        # add textfield
        models.TextField.objects.get_or_create(
            name="Zipcode",
            slug="Zipcode",
            required=True,
            help_text=None,
            position=0,
            form_id=zip_form.id,
            enabled=0,
            css_class=None,
            subtype=models.TextField.SUBTYPE_TEXT,
        )

        models.HiddenField.objects.get_or_create(
            name="City",
            slug="City",
            required=True,
            help_text=None,
            position=0,
            form_id=zip_form.id,
            enabled=0,
            css_class=None,
            subtype=models.Field.TYPE_HIDDEN,
        )

        models.HiddenField.objects.get_or_create(
            name="State",
            slug="State",
            required=True,
            help_text=None,
            position=0,
            form_id=zip_form.id,
            enabled=0,
            css_class=None,
            subtype=models.Field.TYPE_HIDDEN,
        )

        custom_form = CustomForm(
            post_data,
            instance_id="primary_form",
            form=zip_form,
            label_suffix="",
            request=None,
        )

        self.assertTrue(custom_form.is_valid(), "Zip form isn't valid.")

        if custom_form.is_valid():
            obj = zip_form.create_submission(
                custom_form.cleaned_data, source=custom_form.instance_id
            )

            submission = models.Submission.objects.get(pk=obj.pk)

            self.assertEqual(submission.custom_data["State"], "Maryland")
            self.assertEqual(submission.custom_data["City"], "Ellicott City")


@override_settings(STATIC_URL="/static/")
class ModuleScriptMediaTests(SimpleTestCase):
    def test_form_media_renders_module_script(self):
        html = str(CustomForm.media)
        self.assertIn('src="/static/formification/dist/form.js"', html)
        self.assertIn('type="module"', html)
        self.assertIn("formification/dist/form.css", html)

    def test_string_paths_and_render_attributes_are_escaped(self):
        media = ModuleScriptMedia(js=["https://example.com/app.js?a=1&b=2"])
        html = media.render_js(attrs={"nonce": '"quoted&nonce', "defer": True})[0]
        self.assertHTMLEqual(
            html,
            '<script src="https://example.com/app.js?a=1&amp;b=2" '
            'type="module" nonce="&quot;quoted&amp;nonce" defer></script>',
        )

    def test_html_assets_keep_their_own_renderer(self):
        class Asset:
            def __html__(self):
                return format_html('<script src="{}" defer></script>', "/custom.js")

        self.assertHTMLEqual(
            ModuleScriptMedia(js=[Asset()]).render_js()[0],
            '<script src="/custom.js" defer></script>',
        )

    @skipUnless(hasattr(widgets, "Script"), "Script was introduced in Django 5.2")
    def test_script_objects_keep_attributes_without_mutation(self):
        for attributes in (
            {"integrity": "sha256-example", "defer": True},
            {"type": "module"},
        ):
            with self.subTest(attributes=attributes):
                script = widgets.Script("app.js", **attributes)
                html = ModuleScriptMedia(js=[script]).render_js()[0]
                self.assertIn('src="/static/app.js"', html)
                self.assertEqual(html.count('type="module"'), 1)
                self.assertEqual(script.attributes, attributes)
                if "integrity" in attributes:
                    self.assertIn('integrity="sha256-example"', html)

    @skipUnless(
        VERSION >= (6, 1), "Render-time media attrs were introduced in Django 6.1"
    )
    def test_django_media_render_passes_nonce_to_script(self):
        media = ModuleScriptMedia(js=["app.js"])
        self.assertHTMLEqual(
            str(media.render(attrs={"nonce": "csp-token"})),
            '<script src="/static/app.js" type="module" nonce="csp-token"></script>',
        )

    @skipUnless(
        VERSION >= (6, 1), "Render-time media attrs were introduced in Django 6.1"
    )
    def test_explicit_module_type_accepts_render_nonce(self):
        script = widgets.Script("app.js", type="module", integrity="sha256-example")
        html = str(ModuleScriptMedia(js=[script]).render(attrs={"nonce": "csp-token"}))
        self.assertIn('nonce="csp-token"', html)
        self.assertIn('integrity="sha256-example"', html)
        self.assertEqual(html.count('type="module"'), 1)

    @skipUnless(
        VERSION >= (6, 1), "Render-time media attrs were introduced in Django 6.1"
    )
    def test_conflicting_asset_attributes_follow_django_validation(self):
        media = ModuleScriptMedia(js=[widgets.Script("app.js", nonce="asset-token")])
        with self.assertRaisesMessage(ValueError, "conflicting attributes: nonce"):
            media.render_js(attrs={"nonce": "render-token"})
