import json
from core.models import Project, Character, PlotPoint, Place, Organization, Chapter, ResearchNote # Ensure all used models are imported

def get_project_context(project):
    """Get the full context of a project including all related data."""
    context_data = {
        'project': {
            'name': project.name,
            'description': project.description,
            'genre': project.genre,
            'style': project.style,
            'characters': [],
            'plot_points': [],
            'places': [],
            'organizations': [],
            'chapters': [],
            'research_notes': []
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
    
    # Add chapters
    for chapter_obj in project.chapters.all():
        chapter_data = {
            'title': chapter_obj.title,
            'chapter_number': chapter_obj.chapter_number,
            'notes': chapter_obj.notes,
            'content': chapter_obj.content,
            'point_of_view': chapter_obj.point_of_view.name if chapter_obj.point_of_view else None,
            'characters': [char.name for char in chapter_obj.characters.all()],
            'places': [place.name for place in chapter_obj.places.all()],
            'organizations': [org.name for org in chapter_obj.organizations.all()]
        }
        context_data['project']['chapters'].append(chapter_data)
    
    # Add plot points
    for plot_point in project.plot_points.all():
        plot_data = {
            'title': plot_point.title,
            'description': plot_point.description,
            'order': plot_point.order,
            'characters': [char.name for char in plot_point.characters.all()],
            'places': [place.name for place in plot_point.places.all()],
            'organizations': [org.name for org in plot_point.organizations.all()],
            'chapter_title': plot_point.chapter.title if plot_point.chapter else None
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
    
    # Add research notes
    for note in project.research_notes.all():
        note_data = {
            'title': note.title,
            'content': note.content,
            'tags': note.tags,
            'file_name': note.file.name if note.file else None
        }
        context_data['project']['research_notes'].append(note_data)
    
    # Format the context for the LLM
    llm_context = f"""Project: {context_data['project']['name']}
Description: {context_data['project']['description']}
Genre: {context_data['project']['genre'] if context_data['project']['genre'] else 'Not specified'}
Style: {context_data['project']['style'] if context_data['project']['style'] else 'Not specified'}

Characters:
{json.dumps(context_data['project']['characters'], indent=2, ensure_ascii=False)}

Plot Points:
{json.dumps(context_data['project']['plot_points'], indent=2, ensure_ascii=False)}

Places:
{json.dumps(context_data['project']['places'], indent=2, ensure_ascii=False)}

Organizations:
{json.dumps(context_data['project']['organizations'], indent=2, ensure_ascii=False)}

Chapters:
{json.dumps(context_data['project']['chapters'], indent=2, ensure_ascii=False)}

Research Notes:
{json.dumps(context_data['project']['research_notes'], indent=2, ensure_ascii=False)}
"""
    
    return context_data, llm_context 