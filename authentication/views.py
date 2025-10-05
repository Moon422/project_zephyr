from django.shortcuts import render
from django.http import HttpRequest
from django.views.generic.edit import FormView
from django.urls import reverse
from django.contrib.auth import authenticate, login

from .forms import LoginForm


# Create your views here.
def test(request: HttpRequest):
    return render(request, "auth/test.html")


class LoginView(FormView):
    template_name = "auth/login.html"
    form_class = LoginForm
    success_url = "/auth/test/"

    def form_valid(self, form: LoginForm):
        cleaned_data = form.cleaned_data
        email = cleaned_data["email"]
        password = cleaned_data["password"]
        remember_me = cleaned_data["remember_me"]

        user = authenticate(self.request, username=email, password=password)
        if user:
            login(self.request, user)
            self.handle_remember_me(remember_me)
            self.success_url = self.prepare_login_success_url()
            return super().form_valid(form)
        else:
            form.add_error("", "Login failed. Invalid credentials.")
            return render(self.request, self.template_name, {"form": form})

    def prepare_login_success_url(self) -> str:
        redirect_url = self.request.GET["redirect-url"]
        if not redirect_url or not redirect_url.strip():
            redirect_url = reverse("app_home")

        return redirect_url

    def handle_remember_me(self, remember_me):
        if not remember_me:
            self.request.session.set_expiry(0)
