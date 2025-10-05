from django.shortcuts import render
from django.http import HttpRequest


# Create your views here.
def test(request: HttpRequest):
    return render(request, "auth/test.html")
