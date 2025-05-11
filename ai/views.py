from django.shortcuts import render, get_object_or_404
import os
from django.http import JsonResponse
from core.models import Project, Character, PlotPoint, Place, Organization
import json
import google.generativeai as genai

# Create your views here.

def test_api_key(request):
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        return JsonResponse({
            'status': 'success',
            'message': 'API key is accessible',
            'key_length': len(api_key)
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'API key not found in environment variables'
        }, status=400)

def test_project_context(request, project_id):
    # Get the project and all related data
    project = get_object_or_404(Project, pk=project_id)
    
    # Prepare the context data
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
            'bio': character.bio,
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
            'description': place.description
        })
    
    # Add organizations
    for org in project.organizations.all():
        org_data = {
            'name': org.name,
            'purpose': org.purpose,
            'notes': org.notes,
            'characters': [char.name for char in org.characters.all()]
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
    
    return JsonResponse({
        'status': 'success',
        'context': llm_context,
        'raw_data': context_data
    })

def test_llm_summary(request, project_id):
    # Get the project context
    project = get_object_or_404(Project, pk=project_id)
    
    # Configure the Google Generative AI
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        return JsonResponse({
            'status': 'error',
            'message': 'Google API key not found in environment variables'
        }, status=400)
    
    genai.configure(api_key=api_key)
    
    # Get the context data
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
            'bio': character.bio,
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
            'description': place.description
        })
    
    # Add organizations
    for org in project.organizations.all():
        org_data = {
            'name': org.name,
            'purpose': org.purpose,
            'notes': org.notes,
            'characters': [char.name for char in org.characters.all()]
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
    
    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create the prompt
        prompt = f"""Please provide a comprehensive summary of this writing project. Include:
1. A brief overview of the project
2. Key characters and their roles
3. Main plot points in order
4. Important locations and organizations
5. Any notable relationships or dynamics between characters

Here is the project data:
{llm_context}"""
        
        # Generate the summary
        response = model.generate_content(prompt)
        
        return JsonResponse({
            'status': 'success',
            'summary': response.text,
            'raw_context': llm_context
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error generating summary: {str(e)}'
        }, status=500)

def improve_character_bio(request, project_id, character_id):
    # Get the project and character
    project = get_object_or_404(Project, pk=project_id)
    character = get_object_or_404(Character, pk=character_id, project=project)
    
    # Configure the Google Generative AI
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        return JsonResponse({
            'status': 'error',
            'message': 'Google API key not found in environment variables'
        }, status=400)
    
    genai.configure(api_key=api_key)
    
    # Get the context data
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
    for char in project.characters.all():
        char_data = {
            'name': char.name,
            'role': char.role,
            'bio': char.bio,
            'traits': char.traits,
            'relationships': []
        }
        
        # Add relationships
        for rel in char.relationships_from.all():
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
            'description': place.description
        })
    
    # Add organizations
    for org in project.organizations.all():
        org_data = {
            'name': org.name,
            'purpose': org.purpose,
            'notes': org.notes,
            'characters': [char.name for char in org.characters.all()]
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
    
    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create the prompt
        prompt = f"""Please improve and expand the bio for the character "{character.name}" in this writing project. 
Consider their role, traits, relationships, and involvement in plot points to create a more detailed and engaging character bio.
The bio should be consistent with the existing project context and maintain the character's established personality and relationships. It should be plain text and have a literary quality

Current character bio:
{character.bio}

Here is the full project context:
{llm_context}

Please provide an improved version of the character's bio that:
1. Expands on their background and motivations
2. Incorporates their relationships with other characters
3. References their involvement in key plot points
4. Maintains consistency with their established traits
5. Adds depth while staying true to their role in the story"""
        
        # Generate the improved bio
        response = model.generate_content(prompt)
        
        return JsonResponse({
            'status': 'success',
            'improved_bio': response.text,
            'character_name': character.name
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error improving character bio: {str(e)}'
        }, status=500)
