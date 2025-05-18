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
            'title': plot_point.title,
            'description': plot_point.description,
            'order': plot_point.order,
            'chapter_title': plot_point.chapter.title if plot_point.chapter else None
        }
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
    
    # Format the context for the LLM
    llm_context_parts = [
        f"Project: {context_data['project']['name']}",
        f"Description: {context_data['project']['description']}",
        f"Core Premise: {context_data['project']['core_premise'] if context_data['project']['core_premise'] else 'Not specified'}",
        f"Key Themes: {context_data['project']['key_themes'] if context_data['project']['key_themes'] else 'Not specified'}",
        f"Genre: {context_data['project']['genre'] if context_data['project']['genre'] else 'Not specified'}",
        f"Style: {context_data['project']['style'] if context_data['project']['style'] else 'Not specified'}"
    ]

    if context_data['project']['characters']:
        llm_context_parts.append("\nCharacters:")
        llm_context_parts.append(json.dumps(context_data['project']['characters'], indent=2, ensure_ascii=False))

    if context_data['project']['plot_points']:
        llm_context_parts.append("\nPlot Points:")
        llm_context_parts.append(json.dumps(context_data['project']['plot_points'], indent=2, ensure_ascii=False))

    if context_data['project']['places']:
        llm_context_parts.append("\nPlaces:")
        llm_context_parts.append(json.dumps(context_data['project']['places'], indent=2, ensure_ascii=False))

    if context_data['project']['organizations']:
        llm_context_parts.append("\nOrganizations:")
        llm_context_parts.append(json.dumps(context_data['project']['organizations'], indent=2, ensure_ascii=False))

    if context_data['project']['chapters']:
        llm_context_parts.append("\nChapters:")
        llm_context_parts.append(json.dumps(context_data['project']['chapters'], indent=2, ensure_ascii=False))

    if context_data['project']['research_notes']:
        llm_context_parts.append("\nResearch Notes:")
        llm_context_parts.append(json.dumps(context_data['project']['research_notes'], indent=2, ensure_ascii=False))
    
    llm_context = "\n".join(llm_context_parts)
    if llm_context_parts: # Add a final newline if there's any content
        llm_context += "\n"
            
    return context_data, llm_context 