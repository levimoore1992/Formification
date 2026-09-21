"""Seed demo data for the local formulaic demo (safe to re-run).
Creates: demo superuser, option lists/groups, a rich Demo Form with mixed
field types + rules + submissions, and the public robot-form."""
from django.contrib.auth.models import User
from formulaic.models import (
    BooleanField,
    ChoiceField,
    Form,
    HiddenField,
    Option,
    OptionGroup,
    OptionList,
    Rule,
    RuleCondition,
    RuleResult,
    TextField,
)

# ------------------------------------------------------------------ superuser
for uname in ("demo", "levimoore"):
    u, created = User.objects.get_or_create(username=uname, defaults={"email": uname + "@example.com"})
    u.is_superuser = True
    u.is_staff = True
    u.set_password("demo1234")
    u.save()

# ------------------------------------------------------------- option lists
colors_list, _ = OptionList.objects.get_or_create(name="Colors")
red = Option.objects.get_or_create(name="Red", value="red", list=colors_list)[0]
blue = Option.objects.get_or_create(name="Blue", value="blue", list=colors_list)[0]
green = Option.objects.get_or_create(name="Green", value="green", list=colors_list)[0]
other = Option.objects.get_or_create(name="Other", value="other", list=colors_list)[0]
for i, o in enumerate([red, blue, green, other]):
    Option.objects.filter(pk=o.pk).update(position=i)

primary, _ = OptionGroup.objects.get_or_create(name="Primary Colors", list=colors_list, defaults={"position": 1})
greens, _ = OptionGroup.objects.get_or_create(name="Greens", list=colors_list, defaults={"position": 2})
primary.options.set([red, blue])
greens.options.set([green])

methods_list, _ = OptionList.objects.get_or_create(name="Contact Methods")
for i, nm in enumerate(["Email", "Phone", "Mail"]):
    Option.objects.get_or_create(name=nm, value=nm.lower(), list=methods_list, defaults={"position": i})

hobbies_list, _ = OptionList.objects.get_or_create(name="Hobbies")
for i, nm in enumerate(["Reading", "Cooking", "Hiking", "Gaming"]):
    Option.objects.get_or_create(name=nm, value=nm.lower(), list=hobbies_list, defaults={"position": i})

# ------------------------------------------------------------------- forms
demo_form, _ = Form.objects.get_or_create(
    slug="demo-form",
    defaults={"name": "Demo Form", "success_message": "Thanks! We got your submission."},
)


def make(form, cls, subtype, *, display_name, data_name, position, required=False, **extra):
    try:
        f = cls.objects.get(form=form, data_name=data_name)
        f.subtype = subtype
        f.display_name = display_name
        f.position = position
        f.required = required
        for k, v in extra.items():
            setattr(f, k, v)
        if f.slug != data_name:
            f.slug = data_name
        f.save()
        return f
    except cls.DoesNotExist:
        f = cls(
            form=form,
            subtype=subtype,
            display_name=display_name,
            data_name=data_name,
            slug=data_name,
            position=position,
            required=required,
            **extra,
        )
        f.save()
        return f


# Demo Form fields
full_name = make(demo_form, TextField, "text", display_name="Full Name", data_name="name", position=0, required=True)
email = make(demo_form, TextField, "email", display_name="Email Address", data_name="email_address", position=1, required=True)
phone = make(demo_form, TextField, "phone_number", display_name="Phone Number", data_name="phone_number", position=2)
age = make(demo_form, TextField, "integer", display_name="Age", data_name="age", position=3)
comments = make(demo_form, TextField, "textarea", display_name="Comments", data_name="comments", position=4, textarea_rows=5)

fav_color = make(demo_form, ChoiceField, "select", display_name="Favorite Color", data_name="favorite_color", position=5, option_list=colors_list)
fav_color.default_option = blue.id
fav_color.save()

shade = make(demo_form, ChoiceField, "select", display_name="Shade", data_name="shade", position=6, option_list=colors_list, option_group=primary)
shade.default_option = other.id
shade.save()

contact = make(demo_form, ChoiceField, "radio_select", display_name="Preferred Contact", data_name="preferred_contact", position=7, option_list=methods_list)

hobbies = make(demo_form, ChoiceField, "select_multiple", display_name="Hobbies", data_name="hobbies", position=8, option_list=hobbies_list)
hobbies.default_options = [hobbies_list.option_set.get(name="Reading").id, hobbies_list.option_set.get(name="Gaming").id]
hobbies.save()

colors_like = make(demo_form, ChoiceField, "checkbox_select_multiple", display_name="Colors You Like", data_name="colors_like", position=9, option_list=colors_list)

newsletter = make(demo_form, BooleanField, "checkbox", display_name="Sign up for updates", data_name="newsletter", position=10, default_checked=True)
lead = make(demo_form, HiddenField, "hidden", display_name="Lead Source", data_name="lead_source", position=11, value="web demo")

# -------------------------------------------------------------------- rules
def add_rule(operator, conditions, results):
    rule = Rule(form=demo_form, operator=operator, position=demo_form.rule_set.count())
    rule.save()
    for i, (field, op, val) in enumerate(conditions):
        rc = RuleCondition(position=i, rule=rule, field=field, operator=op)
        rc.value = val
        rc.save()
    for action, field, og in results:
        RuleResult(action=action, field=field, rule=rule, option_group=og).save()
    return rule

other_greens = greens
add_rule(
    "and",
    [(fav_color, "is", "other")],
    [("change-option-group", shade, other_greens)],
)
add_rule(
    "and",
    [(newsletter, "is", None)],
    [("show", hobbies, None)],
)

# --------------------------------------------------------------- submissions
def submit(source, promo, splash, **data):
    demo_form.create_submission(
        data, source=source, promo_source=promo, metadata={"demo": True, "page": splash}
    )

submit(
    "demo-web",
    "direct",
    "demo form page",
    name="Jane Doe",
    email_address="jane@example.com",
    phone_number="555-123-4567",
    age=32,
    comments="Loved the demo!",
    favorite_color=blue.id,
    shade=other.id,
    preferred_contact=methods_list.option_set.get(name="Email").id,
    hobbies=[hobbies_list.option_set.get(name="Reading").id, hobbies_list.option_set.get(name="Gaming").id],
    colors_like=[blue.id],
    newsletter=True,
    lead_source="web demo",
)
submit(
    "form-page-a",
    "google",
    "landing page",
    name="John Smith",
    email_address="john@example.com",
    phone_number="555-555-0199",
    age=45,
    comments="",
    favorite_color=green.id,
    shade=other.id,
    preferred_contact=methods_list.option_set.get(name="Phone").id,
    hobbies=[hobbies_list.option_set.get(name="Hiking").id],
    colors_like=[red.id, green.id],
    newsletter=False,
    lead_source="web demo",
)
submit(
    "form-page-a",
    "direct",
    "related post",
    name="Alex Rivera",
    email_address="alex@example.com",
    phone_number="555-555-0142",
    age=29,
    comments="Seen you on social media.",
    favorite_color=red.id,
    shade=other.id,
    preferred_contact=methods_list.option_set.get(name="Mail").id,
    hobbies=[hobbies_list.option_set.get(name="Cooking").id, hobbies_list.option_set.get(name="Reading").id],
    colors_like=[red.id, blue.id],
    newsletter=True,
    lead_source="form-page-a",
)

print("SEED OK: demo + levimoore password=demo1234; demo-form id=%s; robot-form id=%s" % (demo_form.id, robot_form.id))