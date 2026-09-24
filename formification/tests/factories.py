"""Model factories shared by Django and browser tests."""

import factory

from formification import models


class FormFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Form

    name = factory.Sequence(lambda n: f"Form {n}")
    slug = factory.Sequence(lambda n: f"form-{n}")


class OptionListFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.OptionList

    name = factory.Sequence(lambda n: f"Options {n}")


class OptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Option

    list = factory.SubFactory(OptionListFactory)
    name = factory.Sequence(lambda n: f"Option {n}")
    value = factory.LazyAttribute(lambda obj: obj.name.lower())
    position = factory.Sequence(lambda n: n + 1)


class OptionGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.OptionGroup

    list = factory.SubFactory(OptionListFactory)
    name = factory.Sequence(lambda n: f"Group {n}")
    position = factory.Sequence(lambda n: n + 1)


class FieldFactory(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    form = factory.SubFactory(FormFactory)
    data_name = factory.Sequence(lambda n: f"field_{n}")
    slug = factory.LazyAttribute(lambda obj: obj.data_name)
    display_name = factory.LazyAttribute(
        lambda obj: obj.data_name.replace("_", " ").title()
    )
    position = factory.Sequence(lambda n: n)
    required = False


class TextFieldFactory(FieldFactory):
    class Meta:
        model = models.TextField

    subtype = "text"


class ChoiceFieldFactory(FieldFactory):
    class Meta:
        model = models.ChoiceField

    subtype = "select"
    option_list = factory.SubFactory(OptionListFactory)


class BooleanFieldFactory(FieldFactory):
    class Meta:
        model = models.BooleanField

    subtype = "checkbox"


class HiddenFieldFactory(FieldFactory):
    class Meta:
        model = models.HiddenField

    subtype = "hidden"


class RuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Rule

    form = factory.SubFactory(FormFactory)
    operator = "and"
    position = factory.Sequence(lambda n: n)


class RuleConditionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.RuleCondition

    rule = factory.SubFactory(RuleFactory)
    field = factory.SubFactory(
        TextFieldFactory, form=factory.SelfAttribute("..rule.form")
    )
    position = factory.Sequence(lambda n: n)
    operator = "is"
    value = None


class RuleResultFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.RuleResult

    rule = factory.SubFactory(RuleFactory)
    field = factory.SubFactory(
        TextFieldFactory, form=factory.SelfAttribute("..rule.form")
    )
    action = "hide"
