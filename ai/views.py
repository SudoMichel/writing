from django.shortcuts import get_object_or_404, render
import os
from django.http import JsonResponse
from core.models import Project, Character, PlotPoint, Place, Organization, Chapter, ResearchNote
from .llm_utils import generate_llm_response
from .prompts import (CHARACTER_BIO_PROMPT, PLACE_DESCRIPTION_PROMPT, 
                    ORG_DESCRIPTION_PROMPT, 
                    CHAPTER_CONTENT_PROMPT)
from .context_utils import get_project_context
import json

ENTITY_CONFIGURATIONS = {
    'character': {
        'model': Character,
        'prompt_template': CHARACTER_BIO_PROMPT,
        'prompt_args_fn': lambda entity: {'name': entity.name, 'description': entity.description},
        'response_key': 'improved_bio'
    },
    'place': {
        'model': Place,
        'prompt_template': PLACE_DESCRIPTION_PROMPT,
        'prompt_args_fn': lambda entity: {'name': entity.name, 'description': entity.description},
        'response_key': 'improved_description'
    },
    'organization': {
        'model': Organization,
        'prompt_template': ORG_DESCRIPTION_PROMPT,
        'prompt_args_fn': lambda entity: {'name': entity.name, 'org_type': entity.type, 'description': entity.description},
        'response_key': 'improved_description'
    },
    'chapter': {
        'model': Chapter,
        'prompt_template': CHAPTER_CONTENT_PROMPT,
        'prompt_args_fn': lambda entity: {
            'chapter_title': entity.title or "Untitled",
            'chapter_number': entity.chapter_number or "N/A",
            'point_of_view_character': entity.point_of_view.name if entity.point_of_view else "Not specified",
            'chapter_notes': entity.notes or "None",
        },
        'response_key': 'generated_content'
    }
}

def _get_entity_config_and_instance(entity_type, entity_id, project):
    config = ENTITY_CONFIGURATIONS.get(entity_type)
    if not config:
        return None, None, None, None, JsonResponse({'status': 'error', 'message': 'Invalid entity type'}, status=400)

    entity = get_object_or_404(config['model'], pk=entity_id, project=project)
    prompt_template = config['prompt_template']
    prompt_args = config['prompt_args_fn'](entity)
    response_key = config['response_key']
    
    return entity, prompt_template, prompt_args, response_key, None

def require_api_key(view_func):
    def wrapper(request, *args, **kwargs):
        if not os.getenv('GOOGLE_API_KEY'):
            return JsonResponse({'status': 'error', 'message': 'Google API key not found in environment variables'}, status=400)
        return view_func(request, *args, **kwargs)
    return wrapper

@require_api_key
def test_api_key(request):
    api_key = os.getenv('GOOGLE_API_KEY')
    return JsonResponse({
        'status': 'success',
        'message': 'API key is accessible',
        'key_length': len(api_key)
    })

@require_api_key
def view_project_context_html(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    context_data, _ = get_project_context(project) # We only need raw_data for this view
    return render(request, 'ai/project_context_display.html', {
        'project_name': project.name, # Pass project name for the title or breadcrumbs
        'raw_data': context_data
    })

@require_api_key
def view_project_context_llm(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    _, llm_context = get_project_context(project) # We only need llm_context for this view
    return render(request, 'ai/project_context_llm.html', {
        'project_name': project.name, # Pass project name for the title or breadcrumbs
        'llm_context': llm_context
    })

@require_api_key
def improve_entity_description(request, project_id, entity_type, entity_id):
    project = get_object_or_404(Project, pk=project_id)
    # Exclude research_notes from the context for this specific view
    _, llm_context = get_project_context(project, exclude_fields=['research_notes'])

    entity, prompt_template, prompt_args, response_key, error_response = \
        _get_entity_config_and_instance(entity_type, entity_id, project)

    if error_response:
        return error_response
    
    if not entity: 
        return JsonResponse({'status': 'error', 'message': f'{entity_type.capitalize()} not found.'}, status=404)

    if request.method == 'GET':
        final_prompt_args = {**prompt_args, 'llm_context': llm_context}
        initial_prompt = prompt_template.format(**final_prompt_args)
        return JsonResponse({
            'status': 'success',
            'prompt': initial_prompt
        })

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_provided_prompt = data.get('prompt')
            if not user_provided_prompt:
                return JsonResponse({'status': 'error', 'message': 'Prompt not provided in POST request'}, status=400)

            improved_text = generate_llm_response(user_provided_prompt)
            
            return JsonResponse({
                'status': 'success',
                response_key: improved_text
            })
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error improving {entity_type} description: {str(e)}'
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Unsupported request method'}, status=405)