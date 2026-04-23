from django.urls import path
from . import views

urlpatterns = [
    path('', views.global_graph, name='global_graph'),
    path('data/', views.graph_data_api, name='graph_data_api'),
    path('technologies/', views.technology_list, name='technology_list'),
    path('technologies/add/', views.add_technology, name='add_technology'),
    path('technologies/relations/', views.add_tech_relation, name='add_tech_relation'),
    path('technologies/<slug:slug>/', views.technology_detail, name='technology_detail'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/add/', views.add_project, name='add_project'),
    path('projects/filter/', views.filter_projects, name='filter_projects'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail'),
    path('path/', views.find_path, name='find_path'),
]