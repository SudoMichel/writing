from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    path('test-api-key/', views.test_api_key, name='test_api_key'),
    path('test-project-context/<int:project_id>/', views.test_project_context, name='test_project_context'),
    path('test-llm-summary/<int:project_id>/', views.test_llm_summary, name='test_llm_summary'),
    path('improve-character-bio/<int:project_id>/<int:character_id>/', views.improve_character_bio, name='improve_character_bio'),
    path('improve-place-description/<int:project_id>/<int:place_id>/', views.improve_place_description, name='improve_place_description'),
    path('improve-organization-description/<int:project_id>/<int:organization_id>/', views.improve_organization_description, name='improve_organization_description'),
] 