"""Browser/server agreement for conditional fields and composed rules."""

import re

import pytest
from playwright.sync_api import expect

from formification import models
from formification.tests import factories as f


def add_rule(form, conditions, target, *, operator="and", action="hide", position=100):
    rule = f.RuleFactory(form=form, operator=operator, position=position)
    for field, comparison, value in conditions:
        f.RuleConditionFactory(rule=rule, field=field, operator=comparison, value=value)
    f.RuleResultFactory(rule=rule, field=target, action=action)
    return rule


def fill_required(page):
    page.locator("[name='name']").fill("Rule Test")
    page.locator("[name='email_address']").fill("rules@example.com")


def submit(page):
    page.locator("input[type=submit]:visible").click()


def submitted_data(form):
    submission = models.Submission.objects.get(form=form)
    return {value.key: value.output_value for value in submission.values.all()}


def test_required_field_hidden_then_restored(page, demo_data):
    page.goto("/")
    page.locator("[name=name]").fill("Conditional validation")
    email = page.locator("[name=email_address]")
    expect(email).to_have_js_property("required", True)
    submit(page)
    expect(email).to_be_focused()
    assert models.Submission.objects.count() == 0

    page.locator(f"[name=preferred_contact][value='{demo_data.phone.pk}']").check()
    expect(email).to_be_hidden()
    expect(email).to_be_disabled()
    expect(email).to_have_js_property("required", False)

    page.locator(f"[name=preferred_contact][value='{demo_data.email.pk}']").check()
    expect(email).to_be_visible()
    expect(email).to_be_enabled()
    expect(email).to_have_js_property("required", True)
    submit(page)
    expect(email).to_be_focused()
    assert models.Submission.objects.count() == 0

    page.locator(f"[name=preferred_contact][value='{demo_data.phone.pk}']").check()
    submit(page)
    expect(page).to_have_url(re.compile(r"/completed/$"))
    assert "email_address" not in submitted_data(demo_data.form)


def test_hiding_clears_text_and_excludes_it_from_submission(page, demo_data):
    page.goto("/")
    fill_required(page)
    email = page.locator("[name=email_address]")
    phone_choice = page.locator(
        f"[name=preferred_contact][value='{demo_data.phone.pk}']"
    )
    email_choice = page.locator(
        f"[name=preferred_contact][value='{demo_data.email.pk}']"
    )
    phone_choice.check()
    expect(email).to_have_value("")
    email_choice.check()
    expect(email).to_be_visible()
    expect(email).to_have_value("")
    email.fill("discard@example.com")
    phone_choice.check()
    submit(page)
    expect(page).to_have_url(re.compile(r"/completed/$"))
    assert "email_address" not in submitted_data(demo_data.form)


def test_option_group_switch_submits_only_current_selection(page, demo_data):
    page.goto("/")
    fill_required(page)
    page.locator("select[name=shade_1]").select_option(str(demo_data.blue.pk))
    page.locator("select[name=favorite_color_1]").select_option(label="Other")
    shade = page.locator("select[name^=shade_]:visible")
    expect(shade.locator("option")).not_to_contain_text(["Blue"])
    shade.select_option(str(demo_data.green.pk))
    submit(page)
    expect(page).to_have_url(re.compile(r"/completed/$"))
    assert submitted_data(demo_data.form)["shade"] == "Green"


@pytest.mark.parametrize("operator", ["and", "or"])
@pytest.mark.parametrize(
    "name_matches,age_matches",
    [(False, False), (True, False), (False, True), (True, True)],
)
def test_combined_conditions_match_browser_and_server(
    page, demo_data, operator, name_matches, age_matches
):
    fields = {field.data_name: field for field in demo_data.form.field_set.all()}
    add_rule(
        demo_data.form,
        [(fields["name"], "is", "match"), (fields["age"], "is", 18)],
        fields["comments"],
        operator=operator,
    )
    page.goto("/")
    fill_required(page)
    comments = page.locator("[name=comments]")
    comments.fill("Keep only when visible")
    page.locator("[name=name]").fill("match" if name_matches else "different")
    page.locator("[name=age]").fill("18" if age_matches else "17")
    page.locator("[name=age]").blur()
    hidden = (
        (name_matches and age_matches)
        if operator == "and"
        else (name_matches or age_matches)
    )
    if hidden:
        expect(comments).to_be_hidden()
    else:
        expect(comments).to_be_visible()
    submit(page)
    expect(page).to_have_url(re.compile(r"/completed/$"))
    assert ("comments" not in submitted_data(demo_data.form)) == hidden


def test_later_show_rule_overrides_hide_and_reverses(page, demo_data):
    fields = {field.data_name: field for field in demo_data.form.field_set.all()}
    add_rule(demo_data.form, [(fields["name"], "is", "match")], fields["comments"])
    add_rule(
        demo_data.form,
        [(fields["age"], "is", 18)],
        fields["comments"],
        action="show",
        position=101,
    )
    page.goto("/")
    fill_required(page)
    comments = page.locator("[name=comments]")
    page.locator("[name=name]").fill("match")
    page.locator("[name=name]").blur()
    expect(comments).to_be_hidden()
    page.locator("[name=age]").fill("18")
    page.locator("[name=age]").blur()
    expect(comments).to_be_visible()
    page.locator("[name=age]").fill("17")
    page.locator("[name=age]").blur()
    expect(comments).to_be_hidden()
    page.locator("[name=age]").fill("18")
    page.locator("[name=age]").blur()
    comments.fill("Visible override")
    submit(page)
    expect(page).to_have_url(re.compile(r"/completed/$"))
    assert submitted_data(demo_data.form)["comments"] == "Visible override"


@pytest.mark.parametrize(
    "field_name,matching,other", [("name", "match", "different"), ("age", 18, 19)]
)
@pytest.mark.parametrize("comparison", ["is", "is_not"])
def test_equality_operators_reverse_on_text_and_numbers(
    page, demo_data, field_name, matching, other, comparison
):
    fields = {field.data_name: field for field in demo_data.form.field_set.all()}
    add_rule(
        demo_data.form, [(fields[field_name], comparison, matching)], fields["comments"]
    )
    page.goto("/")
    fill_required(page)
    control = page.locator(f"[name={field_name}]")
    comments = page.locator("[name=comments]")
    for value in (matching, other, matching):
        control.fill(str(value))
        control.blur()
        hidden = (value == matching) == (comparison == "is")
        if hidden:
            expect(comments).to_be_hidden()
        else:
            expect(comments).to_be_visible()
    submit(page)
    expect(page).to_have_url(re.compile(r"/completed/$"))
    assert ("comments" not in submitted_data(demo_data.form)) == (comparison == "is")


@pytest.mark.parametrize("subtype", ["select_multiple", "checkbox_select_multiple"])
@pytest.mark.parametrize("comparison", ["is", "is_not"])
def test_multi_select_membership_reverses(page, demo_data, subtype, comparison):
    choices = f.OptionListFactory()
    first, second = f.OptionFactory.create_batch(2, list=choices)
    watched = f.ChoiceFieldFactory(
        form=demo_data.form, data_name="watched", subtype=subtype, option_list=choices
    )
    target = demo_data.form.field_set.get(data_name="comments")
    add_rule(demo_data.form, [(watched, comparison, first.pk)], target)
    page.goto("/")
    fill_required(page)
    comments = page.locator("[name=comments]")
    for selected in ([second.pk], [first.pk, second.pk], [second.pk]):
        if subtype == "select_multiple":
            page.locator("select[name=watched]").select_option(
                [str(pk) for pk in selected]
            )
        else:
            for option in (first, second):
                page.locator(f"[name=watched][value='{option.pk}']").set_checked(
                    option.pk in selected
                )
        hidden = (first.pk in selected) == (comparison == "is")
        if hidden:
            expect(comments).to_be_hidden()
        else:
            expect(comments).to_be_visible()
    submit(page)
    expect(page).to_have_url(re.compile(r"/completed/$"))
    assert ("comments" not in submitted_data(demo_data.form)) == (
        comparison == "is_not"
    )


@pytest.mark.browser_context_args(
    viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True
)
def test_mobile_rules_and_submission(page, demo_data):
    page.goto("/")
    fill_required(page)
    page.locator("[name=newsletter]").uncheck()
    expect(page.locator("[name=hobbies]")).to_be_hidden()
    page.locator("[name=newsletter]").check()
    expect(page.locator("[name=hobbies]")).to_be_visible()
    page.locator("select[name=favorite_color_1]").select_option(label="Other")
    expect(page.locator("select[name=shade_3]")).to_be_visible()
    submit_button = page.locator("input[type=submit]:visible")
    expect(submit_button).to_have_count(1)
    submit_button.scroll_into_view_if_needed()
    expect(submit_button).to_be_in_viewport()
    assert page.evaluate("window.innerWidth") == 390
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    submit(page)
    expect(page).to_have_url(re.compile(r"/completed/$"))
    assert submitted_data(demo_data.form)["name"] == "Rule Test"


@pytest.mark.parametrize(
    "comparison,field_name,expected,matching,other",
    [
        ("contains", "name", "cat", "a cat here", "a dog here"),
        ("does_not_contain", "name", "cat", "a dog here", "a cat here"),
        ("begins_with", "name", "cat", "cat nap", "copycat"),
        ("ends_with", "name", "cat", "copycat", "cat nap"),
        ("greater_than", "age", 18, "19", "18"),
        ("less_than", "age", 18, "17", "18"),
    ],
)
def test_additional_api_operators(
    page, demo_data, comparison, field_name, expected, matching, other
):
    fields = {field.data_name: field for field in demo_data.form.field_set.all()}
    add_rule(
        demo_data.form, [(fields[field_name], comparison, expected)], fields["comments"]
    )
    page.goto("/")
    fill_required(page)
    control = page.locator(f"[name={field_name}]")
    comments = page.locator("[name=comments]")
    for value, hidden in ((matching, True), (other, False), (matching, True)):
        control.fill(value)
        control.blur()
        if hidden:
            expect(comments).to_be_hidden()
        else:
            expect(comments).to_be_visible()
    submit(page)
    expect(page).to_have_url(re.compile(r"/completed/$"))
    assert "comments" not in submitted_data(demo_data.form)


@pytest.mark.parametrize("comparison", ["any_selected", "all_selected"])
@pytest.mark.parametrize("subtype", ["select_multiple", "checkbox_select_multiple"])
def test_selection_set_operators(page, demo_data, comparison, subtype):
    choices = f.OptionListFactory()
    first, second, third = f.OptionFactory.create_batch(3, list=choices)
    watched = f.ChoiceFieldFactory(
        form=demo_data.form, data_name="watched", subtype=subtype, option_list=choices
    )
    target = demo_data.form.field_set.get(data_name="comments")
    add_rule(demo_data.form, [(watched, comparison, [first.pk, second.pk])], target)
    page.goto("/")
    fill_required(page)
    comments = page.locator("[name=comments]")
    for selected in (
        [],
        [third.pk],
        [first.pk],
        [first.pk, second.pk],
        [second.pk],
        [],
    ):
        if subtype == "select_multiple":
            page.locator("select[name=watched]").select_option(
                [str(pk) for pk in selected]
            )
        else:
            for option in (first, second, third):
                page.locator(f"[name=watched][value='{option.pk}']").set_checked(
                    option.pk in selected
                )
        matches = [pk in selected for pk in (first.pk, second.pk)]
        hidden = any(matches) if comparison == "any_selected" else all(matches)
        if hidden:
            expect(comments).to_be_hidden()
        else:
            expect(comments).to_be_visible()
    comments.fill("No selections")
    submit(page)
    expect(page).to_have_url(re.compile(r"/completed/$"))
    assert submitted_data(demo_data.form)["comments"] == "No selections"
