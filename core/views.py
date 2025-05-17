from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Project, Character, CharacterRelationship, Place, Organization, PlotPoint, ResearchNote, Chapter
from django.db import models
from .forms import ProjectForm, CharacterForm, PlaceForm, OrganizationForm, PlotPointForm, ResearchNoteForm, ChapterForm

@login_required
def project_list(request):
    projects = Project.objects.filter(user=request.user)
    return render(request, 'core/project_list.html', {'projects': projects})

@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            messages.success(request, 'Project created successfully!')
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'core/project_form.html', {'form': form, 'action': 'Create'})

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
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('project_edit', pk=project.id)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'core/project_form.html', {
        'project': project,
        'form': form,
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
        form = CharacterForm(request.POST)
        if form.is_valid():
            character = form.save(commit=False)
            character.project = project
            character.save()
            
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
        form = CharacterForm()
    
    return render(request, 'core/character_form.html', {
        'project': project,
        'form': form,
        'action': 'Create'
    })

@login_required
def character_edit(request, project_id, character_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    character = get_object_or_404(Character, pk=character_id, project=project)
    
    if request.method == 'POST':
        form = CharacterForm(request.POST, instance=character)
        if form.is_valid():
            form.save()
            
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
        form = CharacterForm(instance=character)
    
    # Get existing relationships
    relationships = {}
    for rel in character.relationships_from.all():
        relationships[rel.to_character.id] = rel.description
    
    return render(request, 'core/character_form.html', {
        'project': project,
        'character': character,
        'form': form,
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
        form = PlaceForm(project=project, data=request.POST)
        if form.is_valid():
            place = form.save(commit=False)
            place.project = project
            place.save()
            
            # Handle character associations
            if 'characters' in form.cleaned_data:
                place.characters.set(form.cleaned_data['characters'])
            
            messages.success(request, 'Place created successfully!')
            return redirect('project_edit', pk=project.id)
    else:
        form = PlaceForm(project=project)
    
    return render(request, 'core/place_form.html', {
        'project': project, 
        'form': form, 
        'action': 'Create'
    })

@login_required
def place_edit(request, project_id, place_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    place = get_object_or_404(Place, pk=place_id, project=project)
    if request.method == 'POST':
        form = PlaceForm(project=project, data=request.POST, instance=place)
        if form.is_valid():
            form.save()
            
            # Handle character associations
            if 'characters' in form.cleaned_data:
                place.characters.set(form.cleaned_data['characters'])
            
            messages.success(request, 'Place updated successfully!')
            return redirect('project_edit', pk=project.id)
    else:
        form = PlaceForm(project=project, instance=place)
    
    return render(request, 'core/place_form.html', {
        'project': project, 
        'place': place, 
        'form': form, 
        'action': 'Edit'
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
        form = OrganizationForm(project=project, data=request.POST)
        if form.is_valid():
            organization = form.save(commit=False)
            organization.project = project
            organization.save()
            
            # Handle associations
            if 'characters' in form.cleaned_data:
                organization.characters.set(form.cleaned_data['characters'])
            if 'places' in form.cleaned_data:
                organization.places.set(form.cleaned_data['places'])
            
            messages.success(request, 'Organization created successfully!')
            return redirect('project_edit', pk=project.id)
    else:
        form = OrganizationForm(project=project)
    
    return render(request, 'core/organization_form.html', {
        'project': project,
        'form': form,
        'action': 'Create'
    })

@login_required
def organization_edit(request, project_id, organization_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    organization = get_object_or_404(Organization, pk=organization_id, project=project)
    
    if request.method == 'POST':
        form = OrganizationForm(project=project, data=request.POST, instance=organization)
        if form.is_valid():
            form.save()
            
            # Handle associations
            if 'characters' in form.cleaned_data:
                organization.characters.set(form.cleaned_data['characters'])
            if 'places' in form.cleaned_data:
                organization.places.set(form.cleaned_data['places'])
            
            messages.success(request, 'Organization updated successfully!')
            return redirect('project_edit', pk=project.id)
    else:
        form = OrganizationForm(project=project, instance=organization)
    
    return render(request, 'core/organization_form.html', {
        'project': project,
        'organization': organization,
        'form': form,
        'action': 'Edit'
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
        form = PlotPointForm(project=project, data=request.POST)
        if form.is_valid():
            plot_point = form.save(commit=False)
            plot_point.project = project
            plot_point.save()
            
            # Handle associations
            if 'characters' in form.cleaned_data:
                plot_point.characters.set(form.cleaned_data['characters'])
            if 'places' in form.cleaned_data:
                plot_point.places.set(form.cleaned_data['places']) 
            if 'organizations' in form.cleaned_data:
                plot_point.organizations.set(form.cleaned_data['organizations'])
            if 'chapter' in form.cleaned_data and form.cleaned_data['chapter']:
                plot_point.chapter = form.cleaned_data['chapter']
                plot_point.save()
            
            messages.success(request, 'Plot point created successfully!')
            return redirect('project_edit', pk=project.id)
    else:
        form = PlotPointForm(project=project)
    
    return render(request, 'core/plotpoint_form.html', {
        'project': project,
        'form': form,
        'action': 'Create'
    })

@login_required
def plotpoint_edit(request, project_id, plotpoint_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    plot_point = get_object_or_404(PlotPoint, pk=plotpoint_id, project=project)
    
    if request.method == 'POST':
        form = PlotPointForm(project=project, data=request.POST, instance=plot_point)
        if form.is_valid():
            form.save()
            
            # Handle associations
            if 'characters' in form.cleaned_data:
                plot_point.characters.set(form.cleaned_data['characters'])
            if 'places' in form.cleaned_data:
                plot_point.places.set(form.cleaned_data['places']) 
            if 'organizations' in form.cleaned_data:
                plot_point.organizations.set(form.cleaned_data['organizations'])
            if 'chapter' in form.cleaned_data:
                plot_point.chapter = form.cleaned_data['chapter']
                plot_point.save()
            
            messages.success(request, 'Plot point updated successfully!')
            return redirect('project_edit', pk=project.id)
    else:
        form = PlotPointForm(project=project, instance=plot_point)
    
    return render(request, 'core/plotpoint_form.html', {
        'project': project,
        'plot_point': plot_point,
        'form': form,
        'action': 'Edit'
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
        form = ResearchNoteForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.project = project
            note.save()
            messages.success(request, 'Research note created successfully!')
            return redirect('project_edit', pk=project.id)
    else:
        form = ResearchNoteForm()
    
    return render(request, 'core/researchnote_form.html', {
        'project': project,
        'form': form,
        'action': 'Create'
    })

@login_required
def researchnote_edit(request, project_id, note_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    note = get_object_or_404(ResearchNote, pk=note_id, project=project)
    
    if request.method == 'POST':
        form = ResearchNoteForm(request.POST, request.FILES, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, 'Research note updated successfully!')
            return redirect('project_edit', pk=project.id)
    else:
        form = ResearchNoteForm(instance=note)
    
    return render(request, 'core/researchnote_form.html', {
        'project': project,
        'note': note,
        'form': form,
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
    
    # Get the next chapter number (maximum + 1 or 1 if no chapters exist)
    next_chapter_number = 1
    if project.chapters.exists():
        next_chapter_number = project.chapters.aggregate(models.Max('chapter_number'))['chapter_number__max'] + 1
    
    if request.method == 'POST':
        form = ChapterForm(project=project, data=request.POST)
        if form.is_valid():
            chapter = form.save(commit=False)
            chapter.project = project
            chapter.save()
            
            # Handle associations
            if 'characters' in form.cleaned_data:
                chapter.characters.set(form.cleaned_data['characters'])
            if 'places' in form.cleaned_data:
                chapter.places.set(form.cleaned_data['places'])
            if 'organizations' in form.cleaned_data:
                chapter.organizations.set(form.cleaned_data['organizations'])
            if 'point_of_view' in form.cleaned_data:
                chapter.point_of_view = form.cleaned_data['point_of_view']
                chapter.save()
                
            # Associate plot points with this chapter
            if 'plot_points' in form.cleaned_data and form.cleaned_data['plot_points']:
                plot_points = form.cleaned_data['plot_points']
                for plot_point in plot_points:
                    plot_point.chapter = chapter
                    plot_point.save()
            
            messages.success(request, 'Chapter created successfully!')
            return redirect('project_edit', pk=project.id)
    else:
        form = ChapterForm(project=project, initial={'chapter_number': next_chapter_number})
    
    return render(request, 'core/chapter_form.html', {
        'project': project,
        'form': form,
        'action': 'Create',
        'next_chapter_number': next_chapter_number
    })

@login_required
def chapter_edit(request, project_id, chapter_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    chapter = get_object_or_404(Chapter, pk=chapter_id, project=project)
    
    if request.method == 'POST':
        form = ChapterForm(project=project, data=request.POST, instance=chapter)
        if form.is_valid():
            form.save()
            
            # Handle associations
            if 'characters' in form.cleaned_data:
                chapter.characters.set(form.cleaned_data['characters'])
            if 'places' in form.cleaned_data:
                chapter.places.set(form.cleaned_data['places'])
            if 'organizations' in form.cleaned_data:
                chapter.organizations.set(form.cleaned_data['organizations'])
            if 'point_of_view' in form.cleaned_data:
                chapter.point_of_view = form.cleaned_data['point_of_view']
                chapter.save()
                
            # First, clear any existing plot point associations
            PlotPoint.objects.filter(chapter=chapter).update(chapter=None)
            
            # Then associate selected plot points with this chapter
            if 'plot_points' in form.cleaned_data and form.cleaned_data['plot_points']:
                plot_points = form.cleaned_data['plot_points']
                for plot_point in plot_points:
                    plot_point.chapter = chapter
                    plot_point.save()
            
            messages.success(request, 'Chapter updated successfully!')
            return redirect('project_edit', pk=project.id)
    else:
        form = ChapterForm(project=project, instance=chapter)
    
    chapter_plot_points = project.plot_points.filter(chapter=chapter)
    
    return render(request, 'core/chapter_form.html', {
        'project': project, 
        'chapter': chapter, 
        'form': form,
        'action': 'Edit',
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
