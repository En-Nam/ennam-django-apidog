"""
URL configuration for testing.
"""

from django.urls import path
from drf_spectacular.views import SpectacularAPIView
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def test_view(request):
    """A simple test endpoint."""
    return Response({"message": "Hello, World!"})


urlpatterns = [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/test/", test_view, name="test"),
]
