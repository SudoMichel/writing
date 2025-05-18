import json

def get_project_context(project):
    """Get the full context of a project including all related data."""
    context_data = {
        'project': {
            'name': project.name,
            'description': project.description,
            'core_premise': project.core_premise,
            'key_themes': project.key_themes,
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
    
    for character in project.characters.all():
        char_data = {
            'name': character.name,
            'role': character.role,
            'description': character.description,
        }
        if character.traits:
            char_data['traits'] = character.traits
        if character.appearance:
            char_data['appearance'] = character.appearance
        if character.age:
            char_data['age'] = character.age
        if character.gender:
            char_data['gender'] = character.gender
        
        if character.primary_goal:
            char_data['primary_goal'] = character.primary_goal
        if character.secondary_goals:
            char_data['secondary_goals'] = character.secondary_goals
        if character.key_motivations:
            char_data['key_motivations'] = character.key_motivations
        if character.character_arc_summary:
            char_data['character_arc_summary'] = character.character_arc_summary
        if character.strengths:
            char_data['strengths'] = character.strengths
        if character.weaknesses:
            char_data['weaknesses'] = character.weaknesses
        if character.internal_conflict:
            char_data['internal_conflict'] = character.internal_conflict
        if character.external_conflict:
            char_data['external_conflict'] = character.external_conflict
        
        relationships_list = []
        for rel in character.relationships_from.all():
            relationships_list.append({
                'to_character': rel.to_character.name,
                'description': rel.description
            })
        if relationships_list:
            char_data['relationships'] = relationships_list
        
        context_data['project']['characters'].append(char_data)
    
    for chapter_obj in project.chapters.all():
        chapter_data = {
            'title': chapter_obj.title,
            'chapter_number': chapter_obj.chapter_number,
            'notes': chapter_obj.notes,
            'content': chapter_obj.content,
            'point_of_view': chapter_obj.point_of_view.name if chapter_obj.point_of_view else None,
        }
        chap_chars = [char.name for char in chapter_obj.characters.all()]
        if chap_chars:
            chapter_data['characters'] = chap_chars
        
        chap_places = [place.name for place in chapter_obj.places.all()]
        if chap_places:
            chapter_data['places'] = chap_places
            
        chap_orgs = [org.name for org in chapter_obj.organizations.all()]
        if chap_orgs:
            chapter_data['organizations'] = chap_orgs
            
        context_data['project']['chapters'].append(chapter_data)
    
    for plot_point in project.plot_points.all():
        plot_data = {
            'order': plot_point.order,
            'title': plot_point.title,
            'narrative_function': plot_point.narrative_function,
            'chapter_title': plot_point.chapter.title if plot_point.chapter else None
        }
        if plot_point.key_events:
            plot_data['key_events'] = plot_point.key_events
        if plot_point.information_revealed_to_reader:
            plot_data['information_revealed_to_reader'] = plot_point.information_revealed_to_reader
        if plot_point.character_development_achieved:
            plot_data['character_development_achieved'] = plot_point.character_development_achieved
        if plot_point.conflict_introduced_or_escalated:
            plot_data['conflict_introduced_or_escalated'] = plot_point.conflict_introduced_or_escalated

        plot_chars = [char.name for char in plot_point.characters.all()]
        if plot_chars:
            plot_data['characters'] = plot_chars
        
        plot_places = [place.name for place in plot_point.places.all()]
        if plot_places:
            plot_data['places'] = plot_places
            
        plot_orgs = [org.name for org in plot_point.organizations.all()]
        if plot_orgs:
            plot_data['organizations'] = plot_orgs
            
        context_data['project']['plot_points'].append(plot_data)
    
    for place in project.places.all():
        place_entry = {
            'name': place.name,
            'type': place.type,
            'description': place.description,
        }
        place_chars = [char.name for char in place.characters.all()]
        if place_chars:
            place_entry['characters'] = place_chars
        context_data['project']['places'].append(place_entry)
    
    for org in project.organizations.all():
        org_data = {
            'name': org.name,
            'type': org.type,
            'description': org.description,
        }
        org_chars = [char.name for char in org.characters.all()]
        if org_chars:
            org_data['characters'] = org_chars
        
        org_places = [place.name for place in org.places.all()]
        if org_places:
            org_data['places'] = org_places
            
        context_data['project']['organizations'].append(org_data)
    
    for note in project.research_notes.all():
        note_data = {
            'title': note.title,
            'content': note.content,
            'tags': note.tags, # Assuming tags is handled appropriately by the model or not a list needing conditional add here
            'file_name': note.file.name if note.file else None
        }
        context_data['project']['research_notes'].append(note_data)
    

    llm_context = json.dumps(context_data['project'], indent=2, ensure_ascii=False)
            
    return context_data, llm_context 