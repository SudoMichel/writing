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
def project_context(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    context_data, llm_context = get_project_context(project)
    return render(request, 'ai/project_context.html', {
        'raw_data': context_data,
        'llm_context': llm_context
    })

@require_api_key
def improve_entity_description(request, project_id, entity_type, entity_id):
    project = get_object_or_404(Project, pk=project_id)
    _, llm_context = get_project_context(project)

    prompt_template = None
    entity = None
    prompt_args = {}
    response_key = 'improved_description'  # default

    if entity_type == 'character':
        entity = get_object_or_404(Character, pk=entity_id, project=project)
        prompt_template = CHARACTER_BIO_PROMPT
        prompt_args = {'name': entity.name, 'description': entity.description}
        response_key = 'improved_bio'
    elif entity_type == 'place':
        entity = get_object_or_404(Place, pk=entity_id, project=project)
        prompt_template = PLACE_DESCRIPTION_PROMPT
        prompt_args = {'name': entity.name, 'description': entity.description}
        response_key = 'improved_description'
    elif entity_type == 'organization':
        entity = get_object_or_404(Organization, pk=entity_id, project=project)
        prompt_template = ORG_DESCRIPTION_PROMPT
        prompt_args = {'name': entity.name, 'org_type': entity.type, 'description': entity.description}
        response_key = 'improved_description'
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid entity type'}, status=400)

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


@require_api_key
def generate_chapter_content(request, project_id, chapter_id):
    project = get_object_or_404(Project, pk=project_id)
    chapter = get_object_or_404(Chapter, pk=chapter_id, project=project)
    _, llm_context = get_project_context(project)

    try:
        prompt = CHAPTER_CONTENT_PROMPT.format(
            chapter_title=chapter.title or "Untitled",
            chapter_number=chapter.chapter_number or "N/A",
            point_of_view_character=chapter.point_of_view.name if chapter.point_of_view else "Not specified",
            chapter_notes=chapter.notes or "None",
            llm_context=llm_context
        )
        
        generated_content = generate_llm_response(prompt)
        
        return JsonResponse({
            'status': 'success',
            'generated_content': generated_content,
            'chapter_title': chapter.title
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error generating chapter content: {str(e)}'
        }, status=500)
