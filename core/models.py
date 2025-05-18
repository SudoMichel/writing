from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    core_premise = models.TextField(blank=True, null=True)
    key_themes = models.TextField(blank=True, null=True, help_text="Enter key themes, separated by commas")
    genre = models.CharField(max_length=100, blank=True, null=True)
    style = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

class Character(models.Model):
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=100)
    description = models.TextField()
    traits = models.TextField(blank=True, null=True)
    appearance = models.TextField(blank=True, null=True)
    age = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True, null=True)
    primary_goal = models.CharField(max_length=255, blank=True, null=True)
    secondary_goals = models.TextField(blank=True, null=True)
    key_motivations = models.TextField(blank=True, null=True)
    character_arc_summary = models.TextField(blank=True, null=True)
    strengths = models.TextField(blank=True, null=True)
    weaknesses = models.TextField(blank=True, null=True)
    internal_conflict = models.TextField(blank=True, null=True)
    external_conflict = models.TextField(blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='characters')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.role})"

    class Meta:
        ordering = ['name']

class CharacterRelationship(models.Model):
    from_character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='relationships_from')
    to_character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='relationships_to')
    description = models.TextField(help_text="Describe the relationship between these characters")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['from_character', 'to_character']

    def __str__(self):
        return f"{self.from_character.name} → {self.to_character.name}: {self.description}"

class Place(models.Model):
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=100)
    description = models.TextField()
    characters = models.ManyToManyField(Character, related_name='places', blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='places')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.type})"

    class Meta:
        ordering = ['name']

class Organization(models.Model):
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    characters = models.ManyToManyField(Character, related_name='organizations', blank=True)
    places = models.ManyToManyField(Place, related_name='organizations', blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='organizations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Chapter(models.Model):
    title = models.CharField(max_length=200)
    chapter_number = models.IntegerField(default=1)
    notes = models.TextField(blank=True, help_text="Outline notes about this chapter")
    content = models.TextField(blank=True)
    point_of_view = models.ForeignKey(Character, on_delete=models.SET_NULL, related_name='pov_chapters', null=True, blank=True)
    characters = models.ManyToManyField(Character, related_name='chapters', blank=True)
    places = models.ManyToManyField(Place, related_name='chapters', blank=True)
    organizations = models.ManyToManyField(Organization, related_name='chapters', blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='chapters')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chapter {self.chapter_number}: {self.title}"

    class Meta:
        ordering = ['chapter_number', 'created_at']

class PlotPoint(models.Model):
    title = models.CharField(max_length=200)
    narrative_function = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)
    key_events = models.TextField(blank=True, null=True, help_text="Key events that occur in this plot point.")
    information_revealed_to_reader = models.TextField(blank=True, null=True, help_text="What new information is revealed to the reader?")
    character_development_achieved = models.TextField(blank=True, null=True, help_text="How do characters develop or change?")
    conflict_introduced_or_escalated = models.TextField(blank=True, null=True, help_text="What conflict is introduced or escalated?")
    characters = models.ManyToManyField(Character, related_name='plot_points', blank=True)
    places = models.ManyToManyField(Place, related_name='plot_points', blank=True)
    organizations = models.ManyToManyField(Organization, related_name='plot_points', blank=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, related_name='plot_points', null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='plot_points')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order}. {self.title}"

    class Meta:
        ordering = ['order', 'created_at']

class ResearchNote(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    tags = models.CharField(max_length=500, blank=True, help_text="Enter tags separated by commas")
    file = models.FileField(upload_to='research_notes/', blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='research_notes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-updated_at']
