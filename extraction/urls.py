# /home/administrador/Proyectos_Python/FBuro/extraction/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.show_interface, name='interface'),
    path('update-config/', views.update_config, name='update_config'),
    path('execute-path/', views.execute_path, name='execute_path'),
    path('get-template-data/', views.get_template_data, name='get_template_data'),
    path('save-template-config/', views.save_template_config, name='save_template_config'),
    path('get-filters/', views.get_filters, name='get_filters'),
    path('save-filters/', views.save_filters, name='save_filters'),
    path('batch-progress/', views.get_batch_progress, name='batch_progress'),
]