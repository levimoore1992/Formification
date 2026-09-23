from django.shortcuts import get_object_or_404, redirect, render
from formification.forms import CustomForm
from formification.models import Form

DEMO_FORM_SLUG = "demo-form"


def form_page(request):
    formification_form = get_object_or_404(Form, slug=DEMO_FORM_SLUG)

    if request.method == "POST":
        form = CustomForm(
            request.POST,
            request=request,
            instance_id="demo-page",
            form=formification_form,
        )

        if form.is_valid():
            formification_form.create_submission(
                form.cleaned_data,
                source=form.instance_id,
            )

            return redirect("form-complete")

    else:
        form = CustomForm(
            request=request, instance_id="demo-page", form=formification_form
        )

    return render(request, "form.html", {"form": form})


def form_complete(request):
    formification_form = get_object_or_404(Form, slug=DEMO_FORM_SLUG)

    return render(request, "form-complete.html", {"form": formification_form})