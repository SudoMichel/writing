from django.shortcuts import render, get_object_or_404
import os
from django.http import JsonResponse
from core.models import Project, Character, PlotPoint, Place, Organization
import json
from .llm_utils import generate_llm_response
from .prompts import CHARACTER_BIO_PROMPT, PLACE_DESCRIPTION_PROMPT, ORG_DESCRIPTION_PROMPT, PROJECT_SUMMARY_PROMPT


def get_project_context(project):
    """Get the full context of a project including all related data."""
    context_data = {
        'project': {
            'name': project.name,
            'description': project.description,
            'characters': [],
            'plot_points': [],
            'places': [],
            'organizations': []
        }
    }
    
    # Add characters
    for character in project.characters.all():
        char_data = {
            'name': character.name,
            'role': character.role,
            'description': character.description,
            'traits': character.traits,
            'relationships': []
        }
        
        # Add relationships
        for rel in character.relationships_from.all():
            char_data['relationships'].append({
                'to_character': rel.to_character.name,
                'description': rel.description
            })
        
        context_data['project']['characters'].append(char_data)
    
    # Add plot points
    for plot_point in project.plot_points.all():
        plot_data = {
            'title': plot_point.title,
            'description': plot_point.description,
            'order': plot_point.order,
            'characters': [char.name for char in plot_point.characters.all()],
            'places': [place.name for place in plot_point.places.all()],
            'organizations': [org.name for org in plot_point.organizations.all()]
        }
        context_data['project']['plot_points'].append(plot_data)
    
    # Add places
    for place in project.places.all():
        context_data['project']['places'].append({
            'name': place.name,
            'type': place.type,
            'description': place.description,
            'characters': [char.name for char in place.characters.all()]
        })
    
    # Add organizations
    for org in project.organizations.all():
        org_data = {
            'name': org.name,
            'type': org.type,
            'description': org.description,
            'characters': [char.name for char in org.characters.all()],
            'places': [place.name for place in org.places.all()]
        }
        context_data['project']['organizations'].append(org_data)
    
    # Format the context for the LLM
    llm_context = f"""Project: {context_data['project']['name']}
Description: {context_data['project']['description']}

Characters:
{json.dumps(context_data['project']['characters'], indent=2)}

Plot Points:
{json.dumps(context_data['project']['plot_points'], indent=2)}

Places:
{json.dumps(context_data['project']['places'], indent=2)}

Organizations:
{json.dumps(context_data['project']['organizations'], indent=2)}
"""
    
    return context_data, llm_context

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
def test_project_context(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    context_data, llm_context = get_project_context(project)
    return JsonResponse({
        'status': 'success',
        'context': llm_context,
        'raw_data': context_data
    })

@require_api_key
def test_llm_summary(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    _, llm_context = get_project_context(project)
    try:
        prompt = PROJECT_SUMMARY_PROMPT.format(llm_context=llm_context)
        summary = generate_llm_response(prompt)
        return JsonResponse({
            'status': 'success',
            'summary': summary,
            'raw_context': llm_context
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error generating summary: {str(e)}'
        }, status=500)

@require_api_key
def improve_entity_description(request, project_id, entity_type, entity_id):
    project = get_object_or_404(Project, pk=project_id)
    _, llm_context = get_project_context(project)
    if entity_type == 'character':
        entity = get_object_or_404(Character, pk=entity_id, project=project)
        prompt = CHARACTER_BIO_PROMPT.format(
            name=entity.name,
            description=entity.description,
            llm_context=llm_context
        )
        key = 'improved_bio'
        name_key = 'character_name'
        name_val = entity.name
    elif entity_type == 'place':
        entity = get_object_or_404(Place, pk=entity_id, project=project)
        prompt = PLACE_DESCRIPTION_PROMPT.format(
            name=entity.name,
            description=entity.description,
            llm_context=llm_context
        )
        key = 'improved_description'
        name_key = 'place_name'
        name_val = entity.name
    elif entity_type == 'organization':
        entity = get_object_or_404(Organization, pk=entity_id, project=project)
        prompt = ORG_DESCRIPTION_PROMPT.format(
            name=entity.name,
            org_type=entity.type,
            description=entity.description,
            llm_context=llm_context
        )
        key = 'improved_description'
        name_key = 'organization_name'
        name_val = entity.name
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid entity type'}, status=400)
    try:
        improved_text = generate_llm_response(prompt)
        return JsonResponse({
            'status': 'success',
            key: improved_text,
            name_key: name_val
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error improving {entity_type} description: {str(e)}'
        }, status=500)
