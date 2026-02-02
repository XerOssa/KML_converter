from django.urls import path
from . import views
from .views import private_view
from .convert import convert_view

urlpatterns = [
    path('', convert_view, name='main'),
    path("private/", private_view, name="private"),
]
