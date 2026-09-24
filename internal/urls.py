from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("completed/", views.form_complete, name="form-complete"),
    path("formification/", include("formification.urls")),
    path("admin/", admin.site.urls),
    path("", views.form_page),
]
