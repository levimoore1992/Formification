import json
from types import SimpleNamespace

from bs4 import BeautifulSoup
from django.template import Context, Template
from django.test import SimpleTestCase

from formification.forms import CustomForm


class FormificationInitTests(SimpleTestCase):
    def render(self, forms):
        return BeautifulSoup(
            Template(
                "{% load formification %}"
                "{% for form in forms %}{% formification_init form %}{% endfor %}"
            ).render(Context({"forms": forms})),
            "html.parser",
        )

    def test_rules_and_instance_id_cannot_break_out_of_script(self):
        malicious = '</script><script>alert("x")</script>&'
        form = SimpleNamespace(
            instance_id=malicious,
            rules_data=[{"value": malicious}],
            media=CustomForm.media,
        )
        soup = self.render([form])
        data = soup.find("script", type="application/json")
        self.assertEqual(
            json.loads(data.string),
            {
                "instanceId": malicious,
                "rules": [{"value": malicious}],
            },
        )
        self.assertEqual(len(soup.find_all("script")), 3)
        initializer = soup.find_all("script")[-1]
        self.assertEqual(initializer["type"], "module")
        self.assertIn("/static/formification/init.js", initializer.string)
        self.assertNotIn(malicious, initializer.string)
        self.assertIn(data["id"], initializer.string)
        self.assertTrue(soup.find("link", href="/static/formification/dist/form.css"))

    def test_multiple_and_repeated_forms_have_unique_config_elements(self):
        first = SimpleNamespace(
            instance_id="first", rules_data=[], media=CustomForm.media
        )
        second = SimpleNamespace(
            instance_id="second", rules_data=[], media=CustomForm.media
        )
        soup = self.render([first, second, first])
        configs = soup.find_all("script", type="application/json")
        self.assertEqual(len({c["id"] for c in configs}), 3)
        self.assertEqual(
            [json.loads(c.string)["instanceId"] for c in configs],
            ["first", "second", "first"],
        )
