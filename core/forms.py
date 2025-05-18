from django import forms
from .models import Project, Character, Place, Organization, Chapter, PlotPoint, ResearchNote

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'core_premise', 'key_themes', 'genre', 'style']

class CharacterForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = ['name', 'role', 'description', 'traits', 'appearance', 'age', 'gender', 'primary_goal', 'secondary_goals', 'key_motivations', 'character_arc_summary', 'strengths', 'weaknesses', 'internal_conflict', 'external_conflict']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 8}),
            'traits': forms.Textarea(attrs={'rows': 3}),
            'appearance': forms.Textarea(attrs={'rows': 3}),
            'secondary_goals': forms.Textarea(attrs={'rows': 3}),
            'key_motivations': forms.Textarea(attrs={'rows': 3}),
            'character_arc_summary': forms.Textarea(attrs={'rows': 3}),
            'strengths': forms.Textarea(attrs={'rows': 3}),
            'weaknesses': forms.Textarea(attrs={'rows': 3}),
            'internal_conflict': forms.Textarea(attrs={'rows': 3}),
            'external_conflict': forms.Textarea(attrs={'rows': 3}),
        }

class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ['name', 'type', 'description', 'summary', 'sensory_details_keywords', 'atmosphere_keywords', 'strategic_importance_or_plot_relevance', 'characters']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'summary': forms.Textarea(attrs={'rows': 3}),
            'sensory_details_keywords': forms.Textarea(attrs={'rows': 3}),
            'atmosphere_keywords': forms.Textarea(attrs={'rows': 3}),
            'strategic_importance_or_plot_relevance': forms.Textarea(attrs={'rows': 3}),
            'characters': forms.CheckboxSelectMultiple,
        }

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'type', 'description', 'goals_and_objectives', 'modus_operandi_keywords', 'hierarchy_and_membership', 'relationships_with_other_entities', 'characters', 'places']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'goals_and_objectives': forms.Textarea(attrs={'rows': 3}),
            'modus_operandi_keywords': forms.Textarea(attrs={'rows': 3}),
            'hierarchy_and_membership': forms.Textarea(attrs={'rows': 3}),
            'relationships_with_other_entities': forms.Textarea(attrs={'rows': 3}),
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
        fields = ['title', 'narrative_function', 'order', 'key_events', 'information_revealed_to_reader', 'character_development_achieved', 'conflict_introduced_or_escalated', 'characters', 'places', 'organizations', 'chapter']
        widgets = {
            'narrative_function': forms.Textarea(attrs={'rows': 3}),
            'key_events': forms.Textarea(attrs={'rows': 3}),
            'information_revealed_to_reader': forms.Textarea(attrs={'rows': 3}),
            'character_development_achieved': forms.Textarea(attrs={'rows': 3}),
            'conflict_introduced_or_escalated': forms.Textarea(attrs={'rows': 3}),
            'characters': forms.CheckboxSelectMultiple,
            'places': forms.CheckboxSelectMultiple,
            'organizations': forms.CheckboxSelectMultiple,
        }

class ResearchNoteForm(forms.ModelForm):
    class Meta:
        model = ResearchNote
        fields = ['title', 'content', 'tags', 'file'] 