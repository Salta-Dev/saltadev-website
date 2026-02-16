from django.urls import path

from code_of_conduct import views

urlpatterns = [
    path("", views.code_of_conduct, name="code_of_conduct"),
]
