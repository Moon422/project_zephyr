from django.urls import path

from .views import test, LoginView

urlpatterns = [
    path("", test, name="app_home"),
    path("test/", test),
    path("login/", LoginView.as_view()),
]
