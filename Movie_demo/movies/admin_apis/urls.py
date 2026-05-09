#/movies/admin_apis
from django.urls import path
from . import views

urlpatterns = [
    path('', views.AdminMovieManagement.as_view(), name='admin-user-list')
]