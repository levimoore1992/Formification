from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from formification import models
from formification.serializers import CustomDateTimeField
from formification.templatetags.setting_tags import vue_formification_assets


class VueAdminApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(
            get_user_model().objects.create_superuser(
                username="editor", password="test", email="editor@example.com"
            )
        )
        self.form = models.Form.objects.create(name="Registration", slug="registration")
        self.field = models.TextField.objects.create(
            form=self.form,
            slug="name",
            data_name="name",
            display_name="Name",
            required=False,
            subtype="text",
            position=0,
        )

    def test_create_and_update_nested_rule(self):
        payload = {
            "form": self.form.pk,
            "position": 0,
            "operator": "and",
            "conditions": [
                {
                    "field": self.field.pk,
                    "operator": "is",
                    "value": "yes",
                    "position": 0,
                    "rule": None,
                }
            ],
            "results": [
                {
                    "field": self.field.pk,
                    "action": "hide",
                    "option_group": None,
                    "rule": None,
                }
            ],
        }
        created = self.client.post("/formification/api/rules/", payload, format="json")
        self.assertEqual(created.status_code, 201, created.data)
        data = created.data
        condition_id = data["conditions"][0]["id"]
        result_id = data["results"][0]["id"]
        data["conditions"][0]["value"] = "updated"
        data["results"][0]["action"] = "require"
        data["conditions"].append(payload["conditions"][0])
        data["results"].append(payload["results"][0])
        updated = self.client.patch(
            f'/formification/api/rules/{data["id"]}/', data, format="json"
        )
        self.assertEqual(updated.status_code, 200, updated.data)
        self.assertEqual(
            models.RuleCondition.objects.get(pk=condition_id).value, "updated"
        )
        self.assertEqual(models.RuleResult.objects.get(pk=result_id).action, "require")
        self.assertEqual(len(updated.data["conditions"]), 2)
        self.assertEqual(len(updated.data["results"]), 2)

    def test_form_details_patch_preserves_identity(self):
        response = self.client.patch(
            f"/formification/api/forms/{self.form.pk}/",
            {"name": "Updated", "slug": "updated", "success_message": "Thank you!"},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.form.refresh_from_db()
        self.assertEqual(self.form.name, "Updated")
        self.assertEqual(self.form.success_message, "Thank you!")
        self.assertEqual(self.field.form_id, self.form.pk)

    def test_create_each_field_type_from_editor(self):
        option_list = models.OptionList.objects.create(name="Options")
        for model, subtype, extra in [
            ("textfield", "text", {}),
            ("booleanfield", "checkbox", {"default_checked": False}),
            ("hiddenfield", "hidden", {"value": ""}),
            (
                "choicefield",
                "select",
                {
                    "option_list": option_list.pk,
                    "default_option": None,
                    "default_options": None,
                },
            ),
        ]:
            with self.subTest(model=model):
                response = self.client.post(
                    f"/formification/api/{model}s/",
                    {
                        "form": self.form.pk,
                        "model_class": model,
                        "subtype": subtype,
                        "slug": model,
                        "data_name": model,
                        "display_name": "New Field",
                        "required": False,
                        "position": 1,
                        "help_text": None,
                        "css_class": None,
                        **extra,
                    },
                    format="json",
                )
                self.assertEqual(response.status_code, 201, response.data)

    def test_assets_are_shipped(self):
        assets = vue_formification_assets()
        self.assertIn('<script type="module"', assets)
        self.assertIn('<link rel="stylesheet"', assets)

    def test_submission_datetime_keeps_aware_timezone(self):
        self.assertEqual(
            CustomDateTimeField().to_representation(
                datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
            ),
            "01/01/2026 12:00 UTC",
        )
