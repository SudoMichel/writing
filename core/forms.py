from django import forms
from .models import Project, Character, CharacterRelationship, Place, Organization, PlotPoint, ResearchNote, Chapter

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
        
class CharacterForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = ['name', 'role', 'description', 'traits']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'traits': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class CharacterRelationshipForm(forms.ModelForm):
    class Meta:
        model = CharacterRelationship
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ['name', 'type', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    
    characters = forms.ModelMultipleChoiceField(
        queryset=Character.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, project=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if project:
            self.fields['characters'].queryset = Character.objects.filter(project=project)
        
class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'type', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    
    characters = forms.ModelMultipleChoiceField(
        queryset=Character.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    places = forms.ModelMultipleChoiceField(
        queryset=Place.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, project=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if project:
            self.fields['characters'].queryset = Character.objects.filter(project=project)
            self.fields['places'].queryset = Place.objects.filter(project=project)

class PlotPointForm(forms.ModelForm):
    class Meta:
        model = PlotPoint
        fields = ['title', 'description', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    characters = forms.ModelMultipleChoiceField(
        queryset=Character.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    places = forms.ModelMultipleChoiceField(
        queryset=Place.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    organizations = forms.ModelMultipleChoiceField(
        queryset=Organization.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    chapter = forms.ModelChoiceField(
        queryset=Chapter.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, project=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if project:
            self.fields['characters'].queryset = Character.objects.filter(project=project)
            self.fields['places'].queryset = Place.objects.filter(project=project)
            self.fields['organizations'].queryset = Organization.objects.filter(project=project)
            self.fields['chapter'].queryset = Chapter.objects.filter(project=project)

class ResearchNoteForm(forms.ModelForm):
    class Meta:
        model = ResearchNote
        fields = ['title', 'content', 'tags', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comma separated tags'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ['title', 'chapter_number', 'content', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'chapter_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control chapter-content', 'rows': 10}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    
    point_of_view = forms.ModelChoiceField(
        queryset=Character.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    characters = forms.ModelMultipleChoiceField(
        queryset=Character.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    places = forms.ModelMultipleChoiceField(
        queryset=Place.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    organizations = forms.ModelMultipleChoiceField(
        queryset=Organization.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    plot_points = forms.ModelMultipleChoiceField(
        queryset=PlotPoint.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, project=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if project:
            self.fields['point_of_view'].queryset = Character.objects.filter(project=project)
            self.fields['characters'].queryset = Character.objects.filter(project=project)
            self.fields['places'].queryset = Place.objects.filter(project=project)
            self.fields['organizations'].queryset = Organization.objects.filter(project=project)
            self.fields['plot_points'].queryset = PlotPoint.objects.filter(project=project) 