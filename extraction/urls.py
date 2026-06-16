# /home/administrador/Proyectos_Python/FBuro/extraction/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.show_interface, name='interface'),
    path('update-config/', views.update_config, name='update_config'),
    path('execute-path/', views.execute_path, name='execute_path'),
    path('update-config/', views.update_config, name='update_config'),

]