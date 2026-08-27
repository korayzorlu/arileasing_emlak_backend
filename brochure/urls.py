from django.urls import path

from .views import BrochureGenerateView

urlpatterns = [
    path("generate/", BrochureGenerateView.as_view(), name="brochure-generate"),
]
