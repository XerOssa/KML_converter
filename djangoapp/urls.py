from django.urls import path
from . import views
from .views import private_view, convert_view

urlpatterns = [
    path("", views.convert_view, name="main"),
    path("private/", private_view, name="private"),
]
