from django.urls import path
from . import views

app_name = "searchCompany"

urlpatterns = [
    path("", views.searchCompany, name='searchCompany'),
]