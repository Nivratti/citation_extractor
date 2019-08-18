from django.urls import path

from . import views

app_name="citation"

urlpatterns = [
 path("dashboard/", views.dashboard, name="dashboard"),
 path("", views.get_citation, name="get_citation"),
 path("extract_citations/", views.extract_citations, name="extract_citations"),
 
]