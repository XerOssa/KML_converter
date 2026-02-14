from django.urls import path
from .views import private_view #login_view
from .convert import convert_view

urlpatterns = [
    path('', convert_view, name='main'),
    path("private/", private_view, name="private"),
    # path("login/", login_view, name="login"),
]
