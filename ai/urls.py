from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    path('test-api-key/', views.test_api_key, name='test_api_key'),
    path('project-context/<int:project_id>/', views.view_project_context_html, name='view_project_context_html'),
    path('project-context-llm/<int:project_id>/', views.view_project_context_llm, name='view_project_context_llm'),
    path('improve/character/<int:project_id>/<int:entity_id>/', views.improve_entity_description, {'entity_type': 'character'}, name='improve_character'),
    path('improve/place/<int:project_id>/<int:entity_id>/', views.improve_entity_description, {'entity_type': 'place'}, name='improve_place'),
    path('improve/organization/<int:project_id>/<int:entity_id>/', views.improve_entity_description, {'entity_type': 'organization'}, name='improve_organization'),
    path('improve/chapter/<int:project_id>/<int:entity_id>/', views.improve_entity_description, {'entity_type': 'chapter'}, name='improve_chapter'),
] 