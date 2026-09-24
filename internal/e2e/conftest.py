"""Real browser tests against Django's isolated test database and live server."""

from types import SimpleNamespace

import pytest

from formification.tests import factories as f


@pytest.fixture(scope="session", autouse=True)
def django_sync_orm():
    # Playwright's sync API keeps an event loop running on the test thread.
    # These tests use synchronous ORM calls; restore the guard after the suite.
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("DJANGO_ALLOW_ASYNC_UNSAFE", "1")
        yield


@pytest.fixture(scope="session")
def base_url(live_server):
    return live_server.url


@pytest.fixture(autouse=True)
def demo_data(transactional_db):
    form = f.FormFactory(name="Demo Form", slug="demo-form")
    colors = f.OptionListFactory(name="Colors")
    red, blue, green, other = [
        f.OptionFactory(list=colors, name=name)
        for name in ("Red", "Blue", "Green", "Other")
    ]
    primary = f.OptionGroupFactory(list=colors, name="Primary Colors")
    primary.options.set([red, blue])
    greens = f.OptionGroupFactory(list=colors, name="Greens")
    greens.options.set([green])
    methods = f.OptionListFactory(name="Contact Methods")
    email_option, phone_option, _ = [
        f.OptionFactory(list=methods, name=name) for name in ("Email", "Phone", "Mail")
    ]
    interests = f.OptionListFactory(name="Hobbies")
    reading, gaming = [
        f.OptionFactory(list=interests, name=name) for name in ("Reading", "Gaming")
    ]

    for name, subtype in (
        ("name", "text"),
        ("age", "integer"),
        ("comments", "textarea"),
    ):
        f.TextFieldFactory(
            form=form, data_name=name, subtype=subtype, required=name == "name"
        )
    email = f.TextFieldFactory(
        form=form, data_name="email_address", subtype="email", required=True
    )
    phone = f.TextFieldFactory(
        form=form, data_name="phone_number", subtype="phone_number"
    )
    color = f.ChoiceFieldFactory(
        form=form,
        data_name="favorite_color",
        option_list=colors,
        default_option=blue.pk,
    )
    shade = f.ChoiceFieldFactory(
        form=form,
        data_name="shade",
        option_list=colors,
        option_group=primary,
        default_option=other.pk,
    )
    contact = f.ChoiceFieldFactory(
        form=form,
        data_name="preferred_contact",
        subtype="radio_select",
        option_list=methods,
    )
    hobbies = f.ChoiceFieldFactory(
        form=form,
        data_name="hobbies",
        subtype="select_multiple",
        option_list=interests,
        default_options=[reading.pk, gaming.pk],
    )
    f.ChoiceFieldFactory(
        form=form,
        data_name="colors_like",
        subtype="checkbox_select_multiple",
        option_list=colors,
    )
    newsletter = f.BooleanFieldFactory(
        form=form, data_name="newsletter", default_checked=True
    )
    f.HiddenFieldFactory(form=form, data_name="lead_source", value="web demo")

    for watched, operator, value, action, target, group in (
        (color, "is", red.pk, "change-option-group", shade, primary),
        (color, "is", other.pk, "change-option-group", shade, greens),
        (contact, "is", email_option.pk, "hide", phone, None),
        (contact, "is", phone_option.pk, "hide", email, None),
        (newsletter, "is_not", None, "hide", hobbies, None),
    ):
        rule = f.RuleFactory(form=form)
        f.RuleConditionFactory(rule=rule, field=watched, operator=operator, value=value)
        f.RuleResultFactory(rule=rule, field=target, action=action, option_group=group)

    return SimpleNamespace(
        form=form,
        red=red,
        blue=blue,
        green=green,
        email=email_option,
        phone=phone_option,
    )
