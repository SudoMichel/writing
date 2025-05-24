from rest_framework import serializers
from .models import (
    Project, Character, Place, Organization, Chapter, PlotPoint, ResearchNote,
    CharacterRelationship,
    CharacterAttributeValue, PlaceAttributeValue, OrganizationAttributeValue, ProjectAttributeValue
)

# Helper function to convert semicolon-separated strings to lists
def get_semicolon_list(instance, field_name):
    field_value = getattr(instance, field_name, None)
    if field_value:
        items = [item.strip() for item in field_value.split(';') if item.strip()]
        return items if items else None # Return None if list is empty to match original logic
    return None

class CustomAttributeModelSerializer(serializers.ModelSerializer):
    """
    Base serializer for models that can have custom attributes.
    """
    def get_custom_attributes(self, instance, attribute_value_model, related_name_on_attribute_value):
        attributes = {}
        filter_kwargs = {related_name_on_attribute_value: instance}
        custom_attribute_values = attribute_value_model.objects.filter(**filter_kwargs).select_related('attribute')
        for attr_val in custom_attribute_values:
            attributes[attr_val.attribute.name] = attr_val.value
        return attributes

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Remove keys with None values or empty lists to match original get_project_context behavior
        # This makes the JSON cleaner and avoids sending unnecessary nulls/empty lists.
        keys_to_remove = [k for k, v in representation.items() if v is None or (isinstance(v, list) and not v)]
        for key in keys_to_remove:
            del representation[key]
            
        return representation

class CharacterRelationshipSerializer(serializers.ModelSerializer):
    to_character = serializers.StringRelatedField(source='to_character.name')

    class Meta:
        model = CharacterRelationship
        fields = ['to_character', 'description']

class CharacterSerializer(CustomAttributeModelSerializer):
    traits = serializers.SerializerMethodField()
    secondary_goals = serializers.SerializerMethodField()
    key_motivations = serializers.SerializerMethodField()
    strengths = serializers.SerializerMethodField()
    weaknesses = serializers.SerializerMethodField()
    internal_conflict = serializers.SerializerMethodField()
    external_conflict = serializers.SerializerMethodField()
    relationships = CharacterRelationshipSerializer(source='relationships_from', many=True, read_only=True)

    class Meta:
        model = Character
        fields = [
            'name', 'role', 'description', 'traits', 'appearance', 'age', 'gender',
            'primary_goal', 'secondary_goals', 'key_motivations', 'character_arc_summary',
            'strengths', 'weaknesses', 'internal_conflict', 'external_conflict', 'relationships'
        ]

    def get_traits(self, obj): return get_semicolon_list(obj, 'traits')
    def get_secondary_goals(self, obj): return get_semicolon_list(obj, 'secondary_goals')
    def get_key_motivations(self, obj): return get_semicolon_list(obj, 'key_motivations')
    def get_strengths(self, obj): return get_semicolon_list(obj, 'strengths')
    def get_weaknesses(self, obj): return get_semicolon_list(obj, 'weaknesses')
    def get_internal_conflict(self, obj): return get_semicolon_list(obj, 'internal_conflict')
    def get_external_conflict(self, obj): return get_semicolon_list(obj, 'external_conflict')
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        custom_attrs = self.get_custom_attributes(instance, CharacterAttributeValue, 'character')
        representation.update(custom_attrs)
        
        # Re-apply None/empty list filtering after adding custom attributes
        final_representation = {}
        for k, v in representation.items():
            if v is not None and not (isinstance(v, list) and not v):
                final_representation[k] = v
        return final_representation

class PlaceSerializer(CustomAttributeModelSerializer):
    sensory_details_keywords = serializers.SerializerMethodField()
    atmosphere_keywords = serializers.SerializerMethodField()
    strategic_importance_or_plot_relevance = serializers.SerializerMethodField()
    characters = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Place
        fields = [
            'name', 'type', 'description', 'summary', 'sensory_details_keywords',
            'atmosphere_keywords', 'strategic_importance_or_plot_relevance', 'characters'
        ]

    def get_sensory_details_keywords(self, obj): return get_semicolon_list(obj, 'sensory_details_keywords')
    def get_atmosphere_keywords(self, obj): return get_semicolon_list(obj, 'atmosphere_keywords')
    def get_strategic_importance_or_plot_relevance(self, obj): return get_semicolon_list(obj, 'strategic_importance_or_plot_relevance')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        custom_attrs = self.get_custom_attributes(instance, PlaceAttributeValue, 'place')
        representation.update(custom_attrs)
        
        final_representation = {}
        for k, v in representation.items():
            if v is not None and not (isinstance(v, list) and not v):
                final_representation[k] = v
        return final_representation

class OrganizationSerializer(CustomAttributeModelSerializer):
    goals_and_objectives = serializers.SerializerMethodField()
    modus_operandi_keywords = serializers.SerializerMethodField()
    hierarchy_and_membership = serializers.SerializerMethodField()
    relationships_with_other_entities = serializers.SerializerMethodField()
    internal_dynamics = serializers.SerializerMethodField()
    characters = serializers.StringRelatedField(many=True, read_only=True)
    places = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Organization
        fields = [
            'name', 'type', 'description', 'goals_and_objectives', 'modus_operandi_keywords',
            'hierarchy_and_membership', 'relationships_with_other_entities', 'internal_dynamics',
            'characters', 'places'
        ]

    def get_goals_and_objectives(self, obj): return get_semicolon_list(obj, 'goals_and_objectives')
    def get_modus_operandi_keywords(self, obj): return get_semicolon_list(obj, 'modus_operandi_keywords')
    def get_hierarchy_and_membership(self, obj): return get_semicolon_list(obj, 'hierarchy_and_membership')
    def get_relationships_with_other_entities(self, obj): return get_semicolon_list(obj, 'relationships_with_other_entities')
    def get_internal_dynamics(self, obj): return get_semicolon_list(obj, 'internal_dynamics')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        custom_attrs = self.get_custom_attributes(instance, OrganizationAttributeValue, 'organization')
        representation.update(custom_attrs)
        
        final_representation = {}
        for k, v in representation.items():
            if v is not None and not (isinstance(v, list) and not v):
                final_representation[k] = v
        return final_representation

class ChapterSerializer(CustomAttributeModelSerializer): # Chapters don't have custom attributes based on models.py, but using base for consistency in filtering
    point_of_view = serializers.StringRelatedField(source='point_of_view.name', read_only=True, allow_null=True)
    characters = serializers.StringRelatedField(many=True, read_only=True)
    places = serializers.StringRelatedField(many=True, read_only=True)
    organizations = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Chapter
        fields = [
            'title', 'chapter_number', 'notes', 'content', 'point_of_view',
            'characters', 'places', 'organizations'
        ]

class PlotPointSerializer(CustomAttributeModelSerializer): # PlotPoints don't have custom attributes
    narrative_function = serializers.SerializerMethodField()
    chapter_title = serializers.CharField(source='chapter.title', read_only=True, allow_null=True)
    key_events = serializers.SerializerMethodField()
    information_revealed_to_reader = serializers.SerializerMethodField()
    character_development_achieved = serializers.SerializerMethodField()
    conflict_introduced_or_escalated = serializers.SerializerMethodField()
    characters = serializers.StringRelatedField(many=True, read_only=True)
    places = serializers.StringRelatedField(many=True, read_only=True)
    organizations = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = PlotPoint
        fields = [
            'order', 'title', 'narrative_function', 'chapter_title', 'key_events',
            'information_revealed_to_reader', 'character_development_achieved',
            'conflict_introduced_or_escalated', 'characters', 'places', 'organizations'
        ]
    
    def get_narrative_function(self, obj): return get_semicolon_list(obj, 'narrative_function')
    def get_key_events(self, obj): return get_semicolon_list(obj, 'key_events')
    def get_information_revealed_to_reader(self, obj): return get_semicolon_list(obj, 'information_revealed_to_reader')
    def get_character_development_achieved(self, obj): return get_semicolon_list(obj, 'character_development_achieved')
    def get_conflict_introduced_or_escalated(self, obj): return get_semicolon_list(obj, 'conflict_introduced_or_escalated')


class ResearchNoteSerializer(CustomAttributeModelSerializer): # ResearchNotes don't have custom attributes
    file_name = serializers.CharField(source='file.name', read_only=True, allow_null=True)
    # Assuming 'tags' is a CharField and should be presented as is. If it needs splitting:
    # tags = serializers.SerializerMethodField() 
    # def get_tags(self, obj): return [t.strip() for t in obj.tags.split(',') if t.strip()] if obj.tags else None


    class Meta:
        model = ResearchNote
        fields = ['title', 'content', 'tags', 'file_name']
        # If tags needs processing, add 'get_tags' and include 'tags' in fields.
        # If 'tags' is fine as a string, it's already included.


class ProjectSerializer(CustomAttributeModelSerializer):
    characters = CharacterSerializer(many=True, read_only=True)
    plot_points = PlotPointSerializer(many=True, read_only=True)
    places = PlaceSerializer(many=True, read_only=True)
    organizations = OrganizationSerializer(many=True, read_only=True)
    chapters = ChapterSerializer(many=True, read_only=True)
    research_notes = ResearchNoteSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'name', 'description', 'characters', 'plot_points', 'places',
            'organizations', 'chapters', 'research_notes'
        ]

    def to_representation(self, instance):
        # Get the representation from the parent CustomAttributeModelSerializer.
        # This includes direct project fields and resolved nested serializers.
        # It has also been filtered for None values and empty lists by the parent.
        parent_representation = super().to_representation(instance)

        # Get custom project attributes
        custom_project_attributes = self.get_custom_attributes(instance, ProjectAttributeValue, 'project')

        # Initialize the dictionary that will hold data in the desired order
        ordered_data = {}

        # Define the names of fields that are nested serializers
        # These should match the field names of the nested serializers in this ProjectSerializer
        nested_serializer_field_names = [
            'characters', 'plot_points', 'places',
            'organizations', 'chapters', 'research_notes'
        ]

        # 1. Add direct project fields (fields from Project model itself)
        # Iterate over self.fields (which respects the order in Meta.fields)
        for field_name in self.fields:
            if field_name not in nested_serializer_field_names:
                if field_name in parent_representation: # Check if the field was serialized by the parent
                    ordered_data[field_name] = parent_representation[field_name]
        
        # 2. Add custom project attributes
        # These will be added after direct model fields and before nested serializers.
        ordered_data.update(custom_project_attributes)

        # 3. Add nested serializer data
        # Iterate in the predefined order of nested_serializer_field_names to maintain consistency
        for field_name in nested_serializer_field_names:
            if field_name in self.fields and field_name in parent_representation:
                ordered_data[field_name] = parent_representation[field_name]

        # Final filtering pass: remove any remaining None values, empty lists, 
        # or dictionaries that became empty after their own fields were filtered.
        # This loop operates on the 'ordered_data' we've constructed.
        final_filtered_data = {}
        for k, v in ordered_data.items():
            if v is not None and not (isinstance(v, list) and not v):
                # Skip dictionaries that are empty (e.g., a nested serializer with all None/empty fields)
                if isinstance(v, dict) and not v:
                    continue
                final_filtered_data[k] = v
        
        return {'project': final_filtered_data} # Match the original top-level 'project' key 