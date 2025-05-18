from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    path('test-api-key/', views.test_api_key, name='test_api_key'),
    path('project-context/<int:project_id>/', views.project_context, name='project_context'),
    path('improve/character/<int:project_id>/<int:entity_id>/', views.improve_entity_description, {'entity_type': 'character'}, name='improve_character'),
    path('improve/place/<int:project_id>/<int:entity_id>/', views.improve_entity_description, {'entity_type': 'place'}, name='improve_place'),
    path('improve/organization/<int:project_id>/<int:entity_id>/', views.improve_entity_description, {'entity_type': 'organization'}, name='improve_organization'),
    path('improve/chapter/<int:project_id>/<int:entity_id>/', views.improve_entity_description, {'entity_type': 'chapter'}, name='improve_chapter'),
] 