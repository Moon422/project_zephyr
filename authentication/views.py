from django.shortcuts import render
from django.http import HttpRequest
from django.views.generic.edit import FormView

from .forms import LoginForm


# Create your views here.
def test(request: HttpRequest):
    return render(request, "auth/test.html")


class LoginView(FormView):
    template_name = "auth/login.html"
    form_class = LoginForm
    success_url = "/test/"

    def form_valid(self, form):
        print(form)
        return super().form_valid(form)
