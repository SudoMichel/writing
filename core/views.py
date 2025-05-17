from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Project, Character, CharacterRelationship, Place, Organization, PlotPoint, ResearchNote, Chapter
from django.db import models


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')

@login_required
def project_list(request):
    projects = Project.objects.filter(user=request.user)
    return render(request, 'core/project_list.html', {'projects': projects})

@login_required
def project_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        if name and description:
            Project.objects.create(
                name=name,
                description=description,
                user=request.user
            )
            messages.success(request, 'Project created successfully!')
            return redirect('project_list')
        else:
            messages.error(request, 'Please fill in all fields.')
    return render(request, 'core/project_form.html', {'action': 'Create'})

@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    return render(request, 'core/project_form.html', {
        'project': project,
        'trunc': 20,
        'action': 'Save',
        'editing_project_details': False
    })

@login_required
def project_details_edit(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        if name and description:
            project.name = name
            project.description = description
            project.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('project_edit', pk=project.id)
        else:
            messages.error(request, 'Please fill in all fields.')
    return render(request, 'core/project_form.html', {
        'project': project,
        'action': 'Save',
        'editing_project_details': True
    })

@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully!')
        return redirect('project_list')
    return render(request, 'core/project_confirm_delete.html', {'project': project})

@login_required
def character_list(request, project_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    characters = project.characters.all()
    return render(request, 'core/character_list.html', {
        'project': project,
        'characters': characters,
        'trunc':70,
    })

@login_required
def character_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    if request.method == 'POST':
        name = request.POST.get('name')
        role = request.POST.get('role')
        description = request.POST.get('description')
        traits = request.POST.get('traits')
        
        if name and role and description:
            character = Character.objects.create(
                name=name,
                role=role,
                description=description,
                traits=traits,
                project=project
            )
            
            # Handle relationships
            for other_character in project.characters.all():
                if other_character.id != character.id:
                    relationship_text = request.POST.get(f'relationship_{other_character.id}')
                    if relationship_text:
                        CharacterRelationship.objects.create(
                            from_character=character,
                            to_character=other_character,
                            description=relationship_text
                        )
            
            messages.success(request, 'Character created successfully!')
            return redirect('project_edit', pk=project.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'core/character_form.html', {
        'project': project,
        'action': 'Create'
    })

@login_required
def character_edit(request, project_id, character_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    character = get_object_or_404(Character, pk=character_id, project=project)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        role = request.POST.get('role')
        description = request.POST.get('description')
        traits = request.POST.get('traits')
        
        if name and role and description:
            character.name = name
            character.role = role
            character.description = description
            character.traits = traits
            character.save()
            
            # Handle relationships
            for other_character in project.characters.all():
                if other_character.id != character.id:
                    relationship_text = request.POST.get(f'relationship_{other_character.id}')
                    relationship, created = CharacterRelationship.objects.get_or_create(
                        from_character=character,
                        to_character=other_character
                    )
                    if relationship_text:
                        relationship.description = relationship_text
                        relationship.save()
                    else:
                        relationship.delete()
            
            messages.success(request, 'Character updated successfully!')
            return redirect('project_edit', pk=project.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    # Get existing relationships
    relationships = {}
    for rel in character.relationships_from.all():
        relationships[rel.to_character.id] = rel.description
    
    return render(request, 'core/character_form.html', {
        'project': project,
        'character': character,
        'action': 'Edit',
        'relationships': relationships
    })

@login_required
def character_delete(request, project_id, character_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    character = get_object_or_404(Character, pk=character_id, project=project)
    
    if request.method == 'POST':
        character.delete()
        messages.success(request, 'Character deleted successfully!')
        return redirect('project_edit', pk=project.id)
    
    return render(request, 'core/character_confirm_delete.html', {
        'project': project,
        'character': character
    })

@login_required
def place_list(request, project_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    places = project.places.all()
    return render(request, 'core/place_list.html', {
        'project': project,
        'places': places,
        'trunc':70,
    })

@login_required
def place_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    if request.method == 'POST':
        name = request.POST.get('name')
        type_ = request.POST.get('type')
        description = request.POST.get('description')
        if name and type_ and description:
            place = Place.objects.create(
                name=name,
                type=type_,
                description=description,
                project=project
            )
            
            # Handle character associations
            character_ids = request.POST.getlist('characters')
            place.characters.set(Character.objects.filter(id__in=character_ids, project=project))
            
            messages.success(request, 'Place created successfully!')
            return redirect('project_edit', pk=project.id)
        else:
            messages.error(request, 'Please fill in all fields.')
    
    characters = project.characters.all()
    return render(request, 'core/place_form.html', {
        'project': project, 
        'action': 'Create',
        'characters': characters
    })

@login_required
def place_edit(request, project_id, place_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    place = get_object_or_404(Place, pk=place_id, project=project)
    if request.method == 'POST':
        name = request.POST.get('name')
        type_ = request.POST.get('type')
        description = request.POST.get('description')
        if name and type_ and description:
            place.name = name
            place.type = type_
            place.description = description
            place.save()
            
            # Handle character associations
            character_ids = request.POST.getlist('characters')
            place.characters.set(Character.objects.filter(id__in=character_ids, project=project))
            
            messages.success(request, 'Place updated successfully!')
            return redirect('project_edit', pk=project.id)
        else:
            messages.error(request, 'Please fill in all fields.')
    
    characters = project.characters.all()
    return render(request, 'core/place_form.html', {
        'project': project, 
        'place': place, 
        'action': 'Edit',
        'characters': characters
    })

@login_required
def place_delete(request, project_id, place_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    place = get_object_or_404(Place, pk=place_id, project=project)
    if request.method == 'POST':
        place.delete()
        messages.success(request, 'Place deleted successfully!')
        return redirect('project_edit', pk=project.id)
    return render(request, 'core/place_confirm_delete.html', {'project': project, 'place': place})

@login_required
def organization_list(request, project_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    organizations = project.organizations.all()
    return render(request, 'core/organization_list.html', {
        'project': project,
        'organizations': organizations,
        'trunc':70,
    })

@login_required
def organization_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    if request.method == 'POST':
        name = request.POST.get('name')
        type = request.POST.get('type')
        description = request.POST.get('description', '')
        
        if name and type:
            organization = Organization.objects.create(
                name=name,
                type=type,
                description=description,
                project=project
            )
            
            # Handle character associations
            character_ids = request.POST.getlist('characters')
            organization.characters.set(Character.objects.filter(id__in=character_ids, project=project))
            
            # Handle place associations
            place_ids = request.POST.getlist('places')
            organization.places.set(Place.objects.filter(id__in=place_ids, project=project))
            
            messages.success(request, 'Organization created successfully!')
            return redirect('project_edit', pk=project.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    characters = project.characters.all()
    places = project.places.all()
    return render(request, 'core/organization_form.html', {
        'project': project,
        'action': 'Create',
        'characters': characters,
        'places': places
    })

@login_required
def organization_edit(request, project_id, organization_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    organization = get_object_or_404(Organization, pk=organization_id, project=project)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        type = request.POST.get('type')
        description = request.POST.get('description', '')
        
        if name and type:
            organization.name = name
            organization.type = type
            organization.description = description
            organization.save()
            
            # Handle character associations
            character_ids = request.POST.getlist('characters')
            organization.characters.set(Character.objects.filter(id__in=character_ids, project=project))
            
            # Handle place associations
            place_ids = request.POST.getlist('places')
            organization.places.set(Place.objects.filter(id__in=place_ids, project=project))
            
            messages.success(request, 'Organization updated successfully!')
            return redirect('project_edit', pk=project.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    characters = project.characters.all()
    places = project.places.all()
    return render(request, 'core/organization_form.html', {
        'project': project,
        'organization': organization,
        'action': 'Edit',
        'characters': characters,
        'places': places
    })

@login_required
def organization_delete(request, project_id, organization_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    organization = get_object_or_404(Organization, pk=organization_id, project=project)
    
    if request.method == 'POST':
        organization.delete()
        messages.success(request, 'Organization deleted successfully!')
        return redirect('project_edit', pk=project.id)
    
    return render(request, 'core/organization_confirm_delete.html', {
        'project': project,
        'organization': organization
    })

@login_required
def plotpoint_list(request, project_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    plot_points = project.plot_points.all()
    return render(request, 'core/plotpoint_list.html', {
        'project': project,
        'plot_points': plot_points,
    })

@login_required
def plotpoint_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        order = request.POST.get('order', 0)
        chapter_id = request.POST.get('chapter')
        
        if title and description:
            plot_point = PlotPoint.objects.create(
                title=title,
                description=description,
                order=order,
                project=project
            )
            
            # Handle associations
            character_ids = request.POST.getlist('characters')
            place_ids = request.POST.getlist('places')
            organization_ids = request.POST.getlist('organizations')
            
            plot_point.characters.set(Character.objects.filter(id__in=character_ids, project=project))
            plot_point.places.set(Place.objects.filter(id__in=place_ids, project=project))
            plot_point.organizations.set(Organization.objects.filter(id__in=organization_ids, project=project))
            
            # Associate with chapter if specified
            if chapter_id:
                try:
                    chapter = Chapter.objects.get(id=chapter_id, project=project)
                    plot_point.chapter = chapter
                    plot_point.save()
                except Chapter.DoesNotExist:
                    pass
            
            messages.success(request, 'Plot point created successfully!')
            return redirect('project_edit', pk=project.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    characters = project.characters.all()
    places = project.places.all()
    organizations = project.organizations.all()
    chapters = project.chapters.all()
    
    return render(request, 'core/plotpoint_form.html', {
        'project': project,
        'action': 'Create',
        'characters': characters,
        'places': places,
        'organizations': organizations,
        'chapters': chapters
    })

@login_required
def plotpoint_edit(request, project_id, plotpoint_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    plot_point = get_object_or_404(PlotPoint, pk=plotpoint_id, project=project)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        order = request.POST.get('order', 0)
        chapter_id = request.POST.get('chapter')
        
        if title and description:
            plot_point.title = title
            plot_point.description = description
            plot_point.order = order
            
            # Associate with chapter if specified
            if chapter_id:
                try:
                    chapter = Chapter.objects.get(id=chapter_id, project=project)
                    plot_point.chapter = chapter
                except Chapter.DoesNotExist:
                    plot_point.chapter = None
                
            plot_point.save()
            
            # Handle associations
            character_ids = request.POST.getlist('characters')
            place_ids = request.POST.getlist('places')
            organization_ids = request.POST.getlist('organizations')
            
            plot_point.characters.set(Character.objects.filter(id__in=character_ids, project=project))
            plot_point.places.set(Place.objects.filter(id__in=place_ids, project=project))
            plot_point.organizations.set(Organization.objects.filter(id__in=organization_ids, project=project))
            
            messages.success(request, 'Plot point updated successfully!')
            return redirect('project_edit', pk=project.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    characters = project.characters.all()
    places = project.places.all()
    organizations = project.organizations.all()
    chapters = project.chapters.all()
    
    return render(request, 'core/plotpoint_form.html', {
        'project': project,
        'plot_point': plot_point,
        'action': 'Edit',
        'characters': characters,
        'places': places,
        'organizations': organizations,
        'chapters': chapters
    })

@login_required
def plotpoint_delete(request, project_id, plotpoint_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    plot_point = get_object_or_404(PlotPoint, pk=plotpoint_id, project=project)
    
    if request.method == 'POST':
        plot_point.delete()
        messages.success(request, 'Plot point deleted successfully!')
        return redirect('project_edit', pk=project.id)
    
    return render(request, 'core/plotpoint_confirm_delete.html', {
        'project': project,
        'plot_point': plot_point
    })

@login_required
def researchnote_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        tags = request.POST.get('tags', '')
        file = request.FILES.get('file')
        
        if title and content:
            note = ResearchNote.objects.create(
                title=title,
                content=content,
                tags=tags,
                file=file,
                project=project
            )
            messages.success(request, 'Research note created successfully!')
            return redirect('project_edit', pk=project.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'core/researchnote_form.html', {
        'project': project,
        'action': 'Create'
    })

@login_required
def researchnote_edit(request, project_id, note_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    note = get_object_or_404(ResearchNote, pk=note_id, project=project)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        tags = request.POST.get('tags', '')
        file = request.FILES.get('file')
        
        if title and content:
            note.title = title
            note.content = content
            note.tags = tags
            if file:
                note.file = file
            note.save()
            messages.success(request, 'Research note updated successfully!')
            return redirect('project_edit', pk=project.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'core/researchnote_form.html', {
        'project': project,
        'note': note,
        'action': 'Edit'
    })

@login_required
def researchnote_delete(request, project_id, note_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    note = get_object_or_404(ResearchNote, pk=note_id, project=project)
    
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Research note deleted successfully!')
        return redirect('project_edit', pk=project.id)
    
    return render(request, 'core/researchnote_confirm_delete.html', {
        'project': project,
        'note': note
    })

@login_required
def researchnote_list(request, project_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    research_notes = project.research_notes.all()
    return render(request, 'core/researchnote_list.html', {
        'project': project,
        'research_notes': research_notes
    })

@login_required
def chapter_list(request, project_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    chapters = project.chapters.all()
    return render(request, 'core/chapter_list.html', {
        'project': project,
        'chapters': chapters,
    })

@login_required
def chapter_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    if request.method == 'POST':
        title = request.POST.get('title')
        chapter_number = request.POST.get('chapter_number', 1)
        content = request.POST.get('content', '')
        notes = request.POST.get('notes', '')
        point_of_view_id = request.POST.get('point_of_view')
        
        if title:
            chapter = Chapter.objects.create(
                title=title,
                chapter_number=chapter_number,
                content=content,
                notes=notes,
                project=project
            )
            
            # Set point of view if specified
            if point_of_view_id:
                try:
                    character = Character.objects.get(id=point_of_view_id, project=project)
                    chapter.point_of_view = character
                    chapter.save()
                except Character.DoesNotExist:
                    pass
            
            # Handle associations
            character_ids = request.POST.getlist('characters')
            place_ids = request.POST.getlist('places')
            organization_ids = request.POST.getlist('organizations')
            plot_point_ids = request.POST.getlist('plot_points')
            
            chapter.characters.set(Character.objects.filter(id__in=character_ids, project=project))
            chapter.places.set(Place.objects.filter(id__in=place_ids, project=project))
            chapter.organizations.set(Organization.objects.filter(id__in=organization_ids, project=project))
            
            # Associate plot points with this chapter
            if plot_point_ids:
                plot_points = PlotPoint.objects.filter(id__in=plot_point_ids, project=project)
                for plot_point in plot_points:
                    plot_point.chapter = chapter
                    plot_point.save()
            
            messages.success(request, 'Chapter created successfully!')
            return redirect('project_edit', pk=project.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    # Get the next chapter number (maximum + 1 or 1 if no chapters exist)
    next_chapter_number = 1
    if project.chapters.exists():
        next_chapter_number = project.chapters.aggregate(models.Max('chapter_number'))['chapter_number__max'] + 1
    
    characters = project.characters.all()
    places = project.places.all()
    organizations = project.organizations.all()
    all_plot_points = project.plot_points.all()
    
    return render(request, 'core/chapter_form.html', {
        'project': project,
        'action': 'Create',
        'characters': characters,
        'places': places,
        'organizations': organizations,
        'all_plot_points': all_plot_points,
        'next_chapter_number': next_chapter_number
    })

@login_required
def chapter_edit(request, project_id, chapter_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    chapter = get_object_or_404(Chapter, pk=chapter_id, project=project)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        chapter_number = request.POST.get('chapter_number', 1)
        content = request.POST.get('content', '')
        notes = request.POST.get('notes', '')
        point_of_view_id = request.POST.get('point_of_view')
        
        if title:
            chapter.title = title
            chapter.chapter_number = chapter_number
            chapter.content = content
            chapter.notes = notes
            chapter.point_of_view = None
            if point_of_view_id:
                try:
                    character = Character.objects.get(id=point_of_view_id, project=project)
                    chapter.point_of_view = character
                except Character.DoesNotExist:
                    pass
                
            chapter.save()
            
            # Handle associations
            character_ids = request.POST.getlist('characters')
            place_ids = request.POST.getlist('places')
            organization_ids = request.POST.getlist('organizations')
            plot_point_ids = request.POST.getlist('plot_points')
            
            chapter.characters.set(Character.objects.filter(id__in=character_ids, project=project))
            chapter.places.set(Place.objects.filter(id__in=place_ids, project=project))
            chapter.organizations.set(Organization.objects.filter(id__in=organization_ids, project=project))
            
            # First, clear any existing plot point associations
            PlotPoint.objects.filter(chapter=chapter).update(chapter=None)
            
            # Then associate selected plot points with this chapter
            if plot_point_ids:
                plot_points = PlotPoint.objects.filter(id__in=plot_point_ids, project=project)
                for plot_point in plot_points:
                    plot_point.chapter = chapter
                    plot_point.save()
            
            messages.success(request, 'Chapter updated successfully!')
            return redirect('project_edit', pk=project.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    characters = project.characters.all()
    places = project.places.all()
    organizations = project.organizations.all()
    all_plot_points = project.plot_points.all()
    chapter_plot_points = project.plot_points.filter(chapter=chapter)
    
    return render(request, 'core/chapter_form.html', {
        'project': project, 
        'chapter': chapter, 
        'action': 'Edit',
        'characters': characters,
        'places': places,
        'organizations': organizations,
        'all_plot_points': all_plot_points,
        'chapter_plot_points': chapter_plot_points
    })

@login_required
def chapter_delete(request, project_id, chapter_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    chapter = get_object_or_404(Chapter, pk=chapter_id, project=project)
    
    if request.method == 'POST':
        chapter.delete()
        messages.success(request, 'Chapter deleted successfully!')
        return redirect('project_edit', pk=project.id)
    
    return render(request, 'core/chapter_confirm_delete.html', {
        'project': project,
        'chapter': chapter
    })
