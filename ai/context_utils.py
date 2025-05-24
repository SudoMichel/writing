import json
from core.serializers import ProjectSerializer
from core.models import Project # Import Project model for type hinting and potential prefetching examples

def get_project_context(project: Project, exclude_fields: list[str] | None = None):
    """Get the full context of a project using DRF serializers, with dynamic field exclusion."""
    
    # For optimal performance, ensure related data is pre-fetched before passing the project instance here.
    # Example of how you might fetch the project object with prefetching in your view/caller:
    # project_instance = Project.objects.prefetch_related(
    #     'characters__relationships_from__to_character', # For Character.relationships
    #     'characters__attribute_values__attribute',      # For Character custom attributes
    #     'plot_points__chapter',
    #     'plot_points__characters',
    #     'plot_points__places',
    #     'plot_points__organizations',
    #     'places__characters',
    #     'places__attribute_values__attribute',          # For Place custom attributes
    #     'organizations__characters',
    #     'organizations__places',
    #     'organizations__attribute_values__attribute',   # For Organization custom attributes
    #     'chapters__point_of_view',
    #     'chapters__characters',
    #     'chapters__places',
    #     'chapters__organizations',
    #     'research_notes',
    #     'attribute_values__attribute'                   # For Project custom attributes
    # ).get(pk=project.pk) # or however you get your project instance

    serializer = ProjectSerializer(project, exclude_fields=exclude_fields)
    context_data = serializer.data # This is already a dictionary
    
    # The ProjectSerializer now wraps its output in a {'project': ...} structure.
    # So, context_data is {'project': {... actual project data ...}}
    # The llm_context should be the JSON dump of the inner {... actual project data ...} part.
    # If ProjectSerializer.data directly gives {'project': data}, then use context_data['project']
    
    # Ensure context_data is not empty and contains the 'project' key
    if not context_data or 'project' not in context_data:
        # Handle the case where serialization might have failed or returned an unexpected structure
        # This could be logging an error or returning a default structure
        llm_context = json.dumps({}, indent=2, ensure_ascii=False)
        return {}, llm_context # Return empty dict for context_data if project key is missing

    project_data_for_llm = context_data['project']
    llm_context = json.dumps(project_data_for_llm, indent=2, ensure_ascii=False)
            
    return context_data, llm_context 

# Example Usage (can be called from other parts of your AI logic):
# def generate_prompt_variant_a(project_instance):
#     # Excludes research notes for this prompt
#     context_data, llm_context = get_project_context(project_instance, exclude_fields=['research_notes'])
#     # ... use llm_context to build prompt ...
#     return llm_context

# def generate_prompt_variant_b(project_instance):
#     # Excludes chapters and research notes for this prompt
#     context_data, llm_context = get_project_context(project_instance, exclude_fields=['chapters', 'research_notes'])
#     # ... use llm_context to build prompt ...
#     return llm_context

# def get_full_project_llm_context(project_instance):
#     # Gets all data
#     _, llm_context = get_project_context(project_instance) # exclude_fields is None by default
#     return llm_context 