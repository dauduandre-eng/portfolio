from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
    path("ask/", views.ask, name="ask"),
]
