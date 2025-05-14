from django.urls import path
from . import views

urlpatterns = [
    # Define at least one path, even a dummy one, or leave it empty with comments
    path('process_routes', views.process_routes, name='process_routes'),  
]