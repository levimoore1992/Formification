"""Embedded forms must not change host styles, globals, or other forms."""

import pytest
from django.template import Context, Template
from django.test import RequestFactory
from playwright.sync_api import expect

from formification.forms import CustomForm


@pytest.mark.parametrize("style", ["scoped", "unstyled"])
@pytest.mark.parametrize("host", ["bootstrap", "tailwind"])
def test_embedded_forms_are_isolated(page, base_url, demo_data, style, host):
    host_css = {
        "bootstrap": ".btn{color:rgb(255,255,255);background:rgb(0,123,255);padding:6px 12px} .form-control{border:1px solid #ced4da}",
        "tailwind": ".text-red-500{color:rgb(239,68,68)} .bg-white{background:rgb(255,255,255)} .p-4{padding:16px}",
    }[host]
    forms = [
        CustomForm(
            instance_id=instance,
            form=demo_data.form,
            request=RequestFactory().get("/"),
            style=style,
        )
        for instance in ("first", "second")
    ]
    body = Template("{% for form in forms %}{{ form }}{% endfor %}").render(
        Context({"forms": forms})
    )
    html = (
        f"<html><head><style>{host_css}</style></head><body>"
        '<button id="host-button" class="btn text-red-500 bg-white p-4">Host button</button>'
        '<form id="host-form"><input id="host-phone" type="text" autocomplete="tel" data-formification-phone></form>'
        f"{body}</body></html>"
    )
    page.add_init_script(
        "window.$ = window.jQuery = window.hostJQuery = function hostJQuery() {}; "
    )
    page.route(
        "**/embed-isolation/",
        lambda route: route.fulfill(body=html, content_type="text/html"),
    )
    page.goto(base_url + "/embed-isolation/")
    expect(page.locator("#first .iti")).to_have_count(1)
    expect(page.locator("#second .iti")).to_have_count(1)
    expect(page.locator("#host-form .iti")).to_have_count(0)
    assert page.evaluate(
        "window.$ === window.hostJQuery && window.jQuery === window.hostJQuery"
    )
    assert page.evaluate("typeof window.Formification === 'undefined'")
    expected_color = "rgb(255, 255, 255)" if host == "bootstrap" else "rgb(239, 68, 68)"
    expect(page.locator("#host-button")).to_have_css("color", expected_color)
    expect(page.locator("#host-button")).to_have_css(
        "padding-top", "6px" if host == "bootstrap" else "16px"
    )
    page.locator("#first [name=newsletter]").uncheck()
    expect(page.locator("#first [name=hobbies]")).to_be_hidden()
    expect(page.locator("#second [name=hobbies]")).to_be_visible()
    page.evaluate(
        """async () => {
        const { initializeForm } = await import('/static/formification/init.js');
        initializeForm({ instanceId: 'first', rules: [] });
    }"""
    )
    expect(page.locator("#first .iti")).to_have_count(1)
    expect(page.locator("#first [name=phone_number_full]")).to_have_count(1)
    expect(page.locator("#host-form [name$=_full]")).to_have_count(0)
    assert (page.locator('link[href*="form-theme.css"]').count() > 0) == (
        style == "scoped"
    )
