from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def code_of_conduct(request: HttpRequest) -> HttpResponse:
    """Render the code of conduct page."""
    return render(request, "code_of_conduct/index.html")
