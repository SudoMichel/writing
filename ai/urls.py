from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    path('test-api-key/', views.test_api_key, name='test_api_key'),
    path('test-project-context/<int:project_id>/', views.test_project_context, name='test_project_context'),
    path('test-llm-summary/<int:project_id>/', views.test_llm_summary, name='test_llm_summary'),
    path('improve/<str:entity_type>/<int:project_id>/<int:entity_id>/', views.improve_entity_description, name='improve_entity_description'),
] 