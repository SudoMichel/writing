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
            messages.error(request, 'Please fill in all fields.')
    else:
        form = ProjectForm()
    return render(request, 'core/project_form.html', {'form': form, 'action': 'Create'})

@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    form = ProjectForm(instance=project)
    return render(request, 'core/project_form.html', {
        'form': form,
        'project': project,
        'trunc': 30,
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
            messages.error(request, 'Please fill in all fields.')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'core/project_form.html', {
        'form': form,
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
        form = CharacterForm(request.POST, request.FILES)
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
            messages.error(request, 'Please fill in all required fields.')
    else:
        form = CharacterForm()
    return render(request, 'core/character_form.html', {
        'form': form,
        'project': project,
        'action': 'Create'
    })

@login_required
def character_edit(request, project_id, character_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    character = get_object_or_404(Character, pk=character_id, project=project)
    if request.method == 'POST':
        form = CharacterForm(request.POST, request.FILES, instance=character)
        if form.is_valid():
            character = form.save()
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
    else:
        form = CharacterForm(instance=character)
    # Get existing relationships
    relationships = {}
    for rel in character.relationships_from.all():
        relationships[rel.to_character.id] = rel.description
    return render(request, 'core/character_form.html', {
        'form': form,
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
        form = PlaceForm(request.POST)
        if form.is_valid():
            place = form.save(commit=False)
            place.project = project
            place.save()
            form.save_m2m()
            messages.success(request, 'Place created successfully!')
            return redirect('project_edit', pk=project.id)
        else:
            messages.error(request, 'Please fill in all fields.')
    else:
        form = PlaceForm()
    form.fields['characters'].queryset = project.characters.all()
    return render(request, 'core/place_form.html', {
        'form': form,
        'project': project, 
        'action': 'Create',
        'characters': project.characters.all()
    })

@login_required
def place_edit(request, project_id, place_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    place = get_object_or_404(Place, pk=place_id, project=project)
    if request.method == 'POST':
        form = PlaceForm(request.POST, instance=place)
        if form.is_valid():
            place = form.save()
            messages.success(request, 'Place updated successfully!')
            return redirect('project_edit', pk=project.id)
        else:
            messages.error(request, 'Please fill in all fields.')
    else:
        form = PlaceForm(instance=place)
    form.fields['characters'].queryset = project.characters.all()
    return render(request, 'core/place_form.html', {
        'form': form,
        'project': project, 
        'place': place, 
        'action': 'Edit',
        'characters': project.characters.all()
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
        form = OrganizationForm(request.POST)
        if form.is_valid():
            organization = form.save(commit=False)
            organization.project = project
            organization.save()
            form.save_m2m()
            messages.success(request, 'Organization created successfully!')
            return redirect('project_edit', pk=project.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    else:
        form = OrganizationForm()
    form.fields['characters'].queryset = project.characters.all()
    form.fields['places'].queryset = project.places.all()
    return render(request, 'core/organization_form.html', {
        'form': form,
        'project': project,
        'action': 'Create',
        'characters': project.characters.all(),
        'places': project.places.all()
    })

@login_required
def organization_edit(request, project_id, organization_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    organization = get_object_or_404(Organization, pk=organization_id, project=project)
    if request.method == 'POST':
        form = OrganizationForm(request.POST, instance=organization)
        if form.is_valid():
            organization = form.save()
            messages.success(request, 'Organization updated successfully!')
            return redirect('project_edit', pk=project.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    else:
        form = OrganizationForm(instance=organization)
    form.fields['characters'].queryset = project.characters.all()
    form.fields['places'].queryset = project.places.all()
    return render(request, 'core/organization_form.html', {
        'form': form,
        'project': project,
        'organization': organization,
        'action': 'Edit',
        'characters': project.characters.all(),
        'places': project.places.all()
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
        'trunc': 120,
    })

@login_required
def plotpoint_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    if request.method == 'POST':
        form = PlotPointForm(request.POST)
        if form.is_valid():
            plot_point = form.save(commit=False)
            plot_point.project = project
            plot_point.save()
            form.save_m2m()
            messages.success(request, 'Plot point created successfully!')
            return redirect('project_edit', pk=project.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    else:
        form = PlotPointForm()
    form.fields['characters'].queryset = project.characters.all()
    form.fields['places'].queryset = project.places.all()
    form.fields['organizations'].queryset = project.organizations.all()
    form.fields['chapter'].queryset = project.chapters.all()
    return render(request, 'core/plotpoint_form.html', {
        'form': form,
        'project': project,
        'action': 'Create',
        'characters': project.characters.all(),
        'places': project.places.all(),
        'organizations': project.organizations.all(),
        'chapters': project.chapters.all()
    })

@login_required
def plotpoint_edit(request, project_id, plotpoint_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    plot_point = get_object_or_404(PlotPoint, pk=plotpoint_id, project=project)
    if request.method == 'POST':
        form = PlotPointForm(request.POST, instance=plot_point)
        if form.is_valid():
            plot_point = form.save()
            messages.success(request, 'Plot point updated successfully!')
            return redirect('project_edit', pk=project.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    else:
        form = PlotPointForm(instance=plot_point)
    form.fields['characters'].queryset = project.characters.all()
    form.fields['places'].queryset = project.places.all()
    form.fields['organizations'].queryset = project.organizations.all()
    form.fields['chapter'].queryset = project.chapters.all()
    return render(request, 'core/plotpoint_form.html', {
        'form': form,
        'project': project,
        'plot_point': plot_point,
        'action': 'Edit',
        'characters': project.characters.all(),
        'places': project.places.all(),
        'organizations': project.organizations.all(),
        'chapters': project.chapters.all()
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
            messages.error(request, 'Please fill in all required fields.')
    else:
        form = ResearchNoteForm()
    return render(request, 'core/researchnote_form.html', {
        'form': form,
        'project': project,
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
            messages.error(request, 'Please fill in all required fields.')
    else:
        form = ResearchNoteForm(instance=note)
    return render(request, 'core/researchnote_form.html', {
        'form': form,
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
        'trunc': 120,
    })

@login_required
def chapter_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    if request.method == 'POST':
        form = ChapterForm(request.POST)
        if form.is_valid():
            chapter = form.save(commit=False)
            chapter.project = project
            chapter.save()
            form.save_m2m()
            # Handle plot point associations
            plot_point_ids = request.POST.getlist('plot_points')
            if plot_point_ids:
                plot_points = PlotPoint.objects.filter(id__in=plot_point_ids, project=project)
                for plot_point in plot_points:
                    plot_point.chapter = chapter
                    plot_point.save()
            messages.success(request, 'Chapter created successfully!')
            return redirect('project_edit', pk=project.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    else:
        form = ChapterForm(initial={'chapter_number': project.chapters.aggregate(models.Max('chapter_number'))['chapter_number__max'] + 1 if project.chapters.exists() else 1})
    form.fields['characters'].queryset = project.characters.all()
    form.fields['places'].queryset = project.places.all()
    form.fields['organizations'].queryset = project.organizations.all()
    form.fields['point_of_view'].queryset = project.characters.all()
    all_plot_points = project.plot_points.all()
    return render(request, 'core/chapter_form.html', {
        'form': form,
        'project': project,
        'action': 'Create',
        'characters': project.characters.all(),
        'places': project.places.all(),
        'organizations': project.organizations.all(),
        'all_plot_points': all_plot_points,
        'next_chapter_number': form.initial.get('chapter_number', 1)
    })

@login_required
def chapter_edit(request, project_id, chapter_id):
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    chapter = get_object_or_404(Chapter, pk=chapter_id, project=project)
    if request.method == 'POST':
        form = ChapterForm(request.POST, instance=chapter)
        if form.is_valid():
            chapter = form.save()
            # First, clear any existing plot point associations
            PlotPoint.objects.filter(chapter=chapter).update(chapter=None)
            # Then associate selected plot points with this chapter
            plot_point_ids = request.POST.getlist('plot_points')
            if plot_point_ids:
                plot_points = PlotPoint.objects.filter(id__in=plot_point_ids, project=project)
                for plot_point in plot_points:
                    plot_point.chapter = chapter
                    plot_point.save()
            messages.success(request, 'Chapter updated successfully!')
            return redirect('project_edit', pk=project.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    else:
        form = ChapterForm(instance=chapter)
    form.fields['characters'].queryset = project.characters.all()
    form.fields['places'].queryset = project.places.all()
    form.fields['organizations'].queryset = project.organizations.all()
    form.fields['point_of_view'].queryset = project.characters.all()
    all_plot_points = project.plot_points.all()
    chapter_plot_points = project.plot_points.filter(chapter=chapter)
    return render(request, 'core/chapter_form.html', {
        'form': form,
        'project': project,
        'chapter': chapter,
        'action': 'Edit',
        'characters': project.characters.all(),
        'places': project.places.all(),
        'organizations': project.organizations.all(),
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
