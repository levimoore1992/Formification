"""Create and persist fields/rules through the actual Vue admin editor."""

import re

import pytest
from playwright.sync_api import expect

from formification import models
from formification.tests import factories as f


@pytest.fixture
def demo_data(transactional_db):
    # Only the form shell is factory-created; fields and rules come from the UI.
    return f.FormFactory(name="Editor Form", slug="demo-form")


def test_editor_create_reload_edit_rule_and_public_submission(
    page, demo_data, admin_user
):
    admin_user.set_password("editor-test-password")
    admin_user.save()
    page.goto(f"/admin/formification/form/{demo_data.pk}/change/")
    page.get_by_label("Username:").fill(admin_user.username)
    page.get_by_label("Password:", exact=True).fill("editor-test-password")
    page.get_by_role("button", name="Log in", exact=True).click()
    expect(page.get_by_role("heading", name="Editor Form", level=1)).to_be_visible()

    for name, label in (("trigger", "Trigger"), ("details", "Details")):
        page.locator(".add-form select").select_option(label="Text")
        page.get_by_role("button", name="Add field", exact=True).click()
        page.get_by_placeholder("(Display Name)", exact=True).fill(label)
        page.get_by_placeholder("(Data Column Name)", exact=True).fill(name)
        page.get_by_placeholder("(field-name)", exact=True).fill(name)
        page.get_by_role("button", name="Save field", exact=True).click()
        expect(page.locator(".field-editor")).to_have_count(0)
    expect(page.locator(".field-item")).to_have_count(2)
    page.reload()
    expect(page.locator(".field-item")).to_have_count(2)
    expect(page.locator(".field-list")).to_contain_text("Trigger")
    expect(page.locator(".field-list")).to_contain_text("Details")

    page.get_by_role("link", name="Rules", exact=True).click()
    page.get_by_role("button", name="Add rule").click()
    rule = page.locator(".rule-card")
    # New rules start with one condition and one action.
    condition = rule.locator(".condition-row")
    condition.locator("select").nth(0).select_option(label="trigger")
    condition.locator("select").nth(1).select_option("is")
    condition.get_by_placeholder("Enter a value").fill("hide")
    result = rule.locator(".result-row")
    result.locator("select").nth(0).select_option("hide")
    result.locator("select").nth(1).select_option(label="details")
    page.get_by_role("button", name="Save and continue editing").click()
    expect(page.get_by_text("Rules saved.", exact=True)).to_be_visible()
    page.reload()
    expect(page.locator(".rule-card")).to_have_count(1)
    expect(condition.get_by_placeholder("Enter a value")).to_have_value("hide")
    expect(result.locator("select").nth(0)).to_have_value("hide")

    # Update an existing nested condition, save, and reload to prove PATCH too.
    condition.get_by_placeholder("Enter a value").fill("hide now")
    page.get_by_role("button", name="Save and continue editing").click()
    expect(page.get_by_text("Rules saved.", exact=True)).to_be_visible()
    page.reload()
    expect(condition.get_by_placeholder("Enter a value")).to_have_value("hide now")
    assert models.Rule.objects.filter(form=demo_data).count() == 1

    page.goto("/")
    trigger = page.locator("[name=trigger]")
    details = page.locator("[name=details]")
    expect(details).to_be_visible()
    trigger.fill("hide now")
    trigger.blur()
    expect(details).to_be_hidden()
    trigger.fill("show")
    trigger.blur()
    expect(details).to_be_visible()
    details.fill("Created through the editor")
    page.locator("input[type=submit]:visible").click()
    expect(page).to_have_url(re.compile(r"/completed/$"))
    submission = models.Submission.objects.get(form=demo_data)
    assert submission.custom_data["details"] == "Created through the editor"
