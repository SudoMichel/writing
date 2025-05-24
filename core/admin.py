from django.contrib import admin
from .models import Project, Character, CharacterRelationship, Place, Organization, Chapter, PlotPoint, ResearchNote

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('name', 'description')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'user')
        }),
    )

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'role', 'age', 'gender')
    list_filter = ('project', 'role', 'gender')
    search_fields = ('name', 'description', 'role')
    autocomplete_fields = ['project']

@admin.register(CharacterRelationship)
class CharacterRelationshipAdmin(admin.ModelAdmin):
    list_display = ('from_character', 'to_character', 'description_short')
    autocomplete_fields = ['from_character', 'to_character']

    def description_short(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'type')
    list_filter = ('project', 'type')
    search_fields = ('name', 'description', 'type')
    autocomplete_fields = ['project', 'characters']

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'type')
    list_filter = ('project', 'type')
    search_fields = ('name', 'description', 'type')
    autocomplete_fields = ['project', 'characters', 'places']

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'chapter_number', 'point_of_view')
    list_filter = ('project', 'point_of_view')
    search_fields = ('title', 'notes', 'content')
    autocomplete_fields = ['project', 'point_of_view', 'characters', 'places', 'organizations']
    fieldsets = (
        (None, {
            'fields': ('project', 'title', 'chapter_number', 'point_of_view')
        }),
        ('Content', {
            'fields': ('notes', 'content')
        }),
        ('Associations', {
            'fields': ('characters', 'places', 'organizations'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PlotPoint)
class PlotPointAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'chapter', 'order')
    list_filter = ('project', 'chapter')
    search_fields = ('title', 'description')
    autocomplete_fields = ['project', 'chapter', 'characters', 'places', 'organizations']

@admin.register(ResearchNote)
class ResearchNoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'created_at', 'updated_at')
    list_filter = ('project', 'tags')
    search_fields = ('title', 'content', 'tags')
    autocomplete_fields = ['project']


# Register your models here.
