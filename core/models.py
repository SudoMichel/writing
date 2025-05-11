from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

class Character(models.Model):
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=100)
    bio = models.TextField()
    traits = models.TextField(help_text="Enter character traits, separated by commas")
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
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='places')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.type})"

    class Meta:
        ordering = ['name']

class Organization(models.Model):
    name = models.CharField(max_length=200)
    purpose = models.TextField()
    notes = models.TextField(blank=True)
    characters = models.ManyToManyField(Character, related_name='organizations', blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='organizations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class PlotPoint(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.IntegerField(default=0)
    characters = models.ManyToManyField(Character, related_name='plot_points', blank=True)
    places = models.ManyToManyField(Place, related_name='plot_points', blank=True)
    organizations = models.ManyToManyField(Organization, related_name='plot_points', blank=True)
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
