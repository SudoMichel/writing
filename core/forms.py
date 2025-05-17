from django import forms
from .models import Project, Character, Place, Organization, Chapter, PlotPoint, ResearchNote

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']

class CharacterForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = ['name', 'role', 'description', 'traits']

class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ['name', 'type', 'description', 'characters']
        widgets = {
            'characters': forms.CheckboxSelectMultiple,
        }

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'type', 'description', 'characters', 'places']
        widgets = {
            'characters': forms.CheckboxSelectMultiple,
            'places': forms.CheckboxSelectMultiple,
        }

class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ['title', 'chapter_number', 'notes', 'content', 'point_of_view', 'characters', 'places', 'organizations']
        widgets = {
            'characters': forms.CheckboxSelectMultiple,
            'places': forms.CheckboxSelectMultiple,
            'organizations': forms.CheckboxSelectMultiple,
        }

class PlotPointForm(forms.ModelForm):
    class Meta:
        model = PlotPoint
        fields = ['title', 'description', 'order', 'characters', 'places', 'organizations', 'chapter']
        widgets = {
            'characters': forms.CheckboxSelectMultiple,
            'places': forms.CheckboxSelectMultiple,
            'organizations': forms.CheckboxSelectMultiple,
        }

class ResearchNoteForm(forms.ModelForm):
    class Meta:
        model = ResearchNote
        fields = ['title', 'content', 'tags', 'file'] 