from __future__ import annotations

import re

from django.apps import apps
from playwright.sync_api import expect


# Identity the browser sends on the submit test; lookup by this field value.
E2E_EMAIL = "e2e.demo.user@example.com"
E2E_NAME = "E2E Demo User"


def test_demo_form_renders_fields_with_defaults(page, demo_data):
    page.goto("/")

    for name in ("name", "email_address", "phone_number", "age", "comments"):
        expect(page.locator(f"[name='{name}']").first).to_be_visible()
        expect(page.locator(f"[name='{name}']").first).to_be_enabled()

    # favorite_color: chain of option-group selects; master select = Blue
    master = page.locator("select[name='favorite_color_1']")
    expect(master).to_be_visible()
    expect(master).to_have_value(str(demo_data.blue.pk))

    # shade: primary option-group select visible by default; greens group hidden
    expect(page.locator("select[name='shade_1']")).to_be_visible()
    expect(page.locator("select[name='shade_3']")).to_be_hidden()

    # preferred_contact: 3 radios (Phone / Mail / Email)
    expect(page.locator("input[name='preferred_contact']")).to_have_count(3)

    # newsletter: checked by default
    expect(page.locator("input[name='newsletter']")).to_be_checked()

    # hobbies: multi-select with fixture's Reading + Gaming preset
    selected = page.locator("select[name='hobbies'] option:checked")
    expect(selected).to_have_count(2)
    for hobby in ("Reading", "Gaming"):
        expect(selected.filter(has_text=hobby)).to_have_count(1)

    # hidden lead_source carries the fixture's fixed value
    expect(page.locator("input[name='lead_source']")).to_have_value("web demo")


def test_favorite_color_changes_visible_shade_option_group(page, demo_data):
    page.goto("/")

    visible_shade = page.locator("select[name^='shade_']:visible")

    # initial default = Blue -> shade_1 visible
    expect(visible_shade).to_have_count(1)
    expect(visible_shade).to_have_attribute("name", "shade_1")
    expect(visible_shade).to_have_value(str(demo_data.red.pk))

    for color, group, value in (
        ("Other", "shade_3", demo_data.green.pk),
        ("Red", "shade_2", demo_data.red.pk),
        ("Blue", "shade_1", demo_data.red.pk),
    ):
        page.select_option("select[name='favorite_color_1']", label=color)
        expect(visible_shade).to_have_count(1)
        expect(visible_shade).to_have_attribute("name", group)
        expect(visible_shade).to_have_value(str(value))


def test_preferred_contact_hides_other_channel(page, demo_data):
    page.goto("/")

    phone = page.locator("[name='phone_number']").first
    email = page.locator("[name='email_address']").first

    # nothing is chosen yet -> both channels visible
    expect(phone).to_be_visible()
    expect(email).to_be_visible()

    # switch to Phone -> email hidden, phone stays
    page.check(f"input[name='preferred_contact'][value='{demo_data.phone.pk}']")
    expect(email).to_be_hidden()
    expect(phone).to_be_visible()

    # and Email -> phone hidden once more
    page.check(f"input[name='preferred_contact'][value='{demo_data.email.pk}']")
    expect(phone).to_be_hidden()
    expect(email).to_be_visible()


def test_newsletter_toggles_hobbies_visibility(page):
    page.goto("/")

    newsletter = page.locator("input[name='newsletter']")
    hobbies = page.locator("select[name='hobbies']")

    # default: newsletter checked -> hobbies visible (interests only if opted in)
    expect(newsletter).to_be_checked()
    expect(hobbies).to_be_visible()

    # uncheck -> hobbies hidden
    newsletter.uncheck()
    expect(hobbies).to_be_hidden()

    # re-check -> hobbies visible again
    newsletter.check()
    expect(hobbies).to_be_visible()


def test_browser_submit_redirects_and_persists(page, demo_data):
    page.goto("/")

    page.fill("[name='name']", E2E_NAME)
    page.fill("[name='email_address']", E2E_EMAIL)
    page.fill("[name='age']", "34")
    page.fill("[name='comments']", "Submitted by the real browser (E2E).")

    # keep sane defaults: newsletter checked -> hobbies visible/selected,
    # hobbies untouched (Reading + Gaming preset); explicitly pick Email so the
    # DB row deterministically records the fixture's preferred channel.
    page.check(
        f"input[name='preferred_contact'][value='{demo_data.email.pk}']"
    )  # Email
    # two submit inputs render (xs vs sm screens); the desktop one is visible
    page.locator("input[type='submit']").filter(visible=True).click()

    expect(page).to_have_url(re.compile(r"/completed/$"))
    expect(page.locator("body")).to_contain_text("Demo Form")

    Submission = apps.get_model("formification", "Submission")
    assert Submission.objects.filter(form=demo_data.form).count() == 1
    submission = (
        Submission.objects.filter(
            values__key="email_address", values__value_charfield__contains=E2E_EMAIL
        )
        .order_by("-id")
        .first()
    )
    assert submission is not None
    assert submission.form.name == "Demo Form"
    assert submission.source == "demo-page"

    data = {kv.key: kv.output_value for kv in submission.values.all()}
    assert data["name"] == E2E_NAME
    assert data["email_address"] == E2E_EMAIL
    assert data["age"] == 34
    assert data["lead_source"] == "web demo"
    assert data["newsletter"] is True
    # factory defaults flowed through untouched
    assert data["preferred_contact"] == "Email"
    assert "Reading" in data["hobbies"]
