from django.forms import fields, widgets
from django import VERSION
from django.test import SimpleTestCase, TestCase, override_settings
from unittest import skipUnless


from formification import models
from formification.forms import CustomForm, PublicFormMedia


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

    def make_form(self, **kwargs):
        return CustomForm(
            instance_id="style-test",
            form=models.Form.objects.get(pk=self.form_id),
            request=None,
            **kwargs
        )

    def test_default_style_includes_scoped_theme(self):
        form = self.make_form()
        self.assertEqual(form.style, "scoped")
        self.assertIn("formification/css/form-theme.css", str(form.media))

    def test_unstyled_mode_keeps_widget_assets_without_theme(self):
        form = self.make_form(style="unstyled")
        html = str(form.media)
        self.assertIn("formification/dist/form.css", html)
        self.assertIn('type="module"', html)
        self.assertNotIn("form-theme.css", html)

    @override_settings(FORMIFICATION_STYLE="unstyled")
    def test_application_can_select_unstyled_mode(self):
        self.assertEqual(self.make_form().style, "unstyled")

    def test_invalid_style_fails_clearly(self):
        with self.assertRaisesMessage(ValueError, "style must be scoped or unstyled"):
            self.make_form(style="bootstrap")

    def test_forms_have_distinct_field_ids(self):
        first = self.make_form()
        second = CustomForm(
            instance_id="second",
            form=models.Form.objects.get(pk=self.form_id),
            request=None,
        )
        self.assertNotEqual(
            first["text-field-1"].id_for_label, second["text-field-1"].id_for_label
        )

    def test_third_party_widget_media_keeps_its_script_type(self):
        class Editor(widgets.TextInput):
            class Media:
                js = ("editor.js",)
                css = {"all": ("editor.css",)}

        form = self.make_form(style="unstyled")
        form.fields["text-field-1"].widget = Editor()
        html = str(form.media)
        self.assertIn("editor.css", html)
        self.assertIn('<script src="/static/editor.js"></script>', html)
        self.assertIn('src="/static/formification/dist/form.js" type="module"', html)

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
class PublicFormMediaTests(SimpleTestCase):
    def test_public_module_type_survives_native_media_merging(self):
        media = widgets.Media(js=PublicFormMedia.js, css=PublicFormMedia.css)
        html = str(widgets.Media() + media)
        self.assertIn('src="/static/formification/dist/form.js"', html)
        self.assertIn('type="module"', html)
        self.assertIn("formification/dist/form.css", html)

    @skipUnless(VERSION >= (6, 1), "Render-time media attrs require Django 6.1")
    def test_native_media_preserves_module_type_and_csp_nonce(self):
        media = widgets.Media(js=PublicFormMedia.js)
        html = str(media.render(attrs={"nonce": "csp-token"}))
        self.assertIn('nonce="csp-token"', html)
        self.assertEqual(html.count('type="module"'), 1)
