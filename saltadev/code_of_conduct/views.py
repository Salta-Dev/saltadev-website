from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def code_of_conduct(request: HttpRequest) -> HttpResponse:
    """Render the code of conduct page."""
    return render(request, "code_of_conduct/index.html")
