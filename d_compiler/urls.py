from django.urls import path
from . import views

app_name = "d_compiler"
urlpatterns = [
    path("", views.RunCodeView.as_view(), name="index"),
]