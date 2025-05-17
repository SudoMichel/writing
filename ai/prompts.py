BASE_PROMPT = '''Improve the following {entity_type} for this writing project.
Be consistent with existing information and maintain a literary quality.
Write plain text with no comments, explanations, or JSON formatting.

Current {entity_type}:
{description}

{additional_context}

Project context will follow. Focus only on information relevant to this {entity_type}:
{llm_context}'''

# Character-specific prompt
CHARACTER_BIO_PROMPT = BASE_PROMPT.format(
    entity_type="character bio",
    description="{description}",
    additional_context='''Character name: {name}

Please provide an improved character bio that:
1. Expands background and motivations
2. Incorporates relationships with other characters
3. References involvement in key plot points
4. Maintains consistency with established traits
5. Adds depth while staying true to their role''',
    llm_context="{llm_context}"
)

# Place-specific prompt
PLACE_DESCRIPTION_PROMPT = BASE_PROMPT.format(
    entity_type="place description",
    description="{description}",
    additional_context='''Place name: {name}

Please provide an improved place description that:
1. Expands physical characteristics and atmosphere
2. Incorporates significance to story and characters
3. References involvement in key plot points
4. Maintains consistency with established role
5. Adds depth with vivid imagery and literary quality''',
    llm_context="{llm_context}"
)

# Organization-specific prompt
ORG_DESCRIPTION_PROMPT = BASE_PROMPT.format(
    entity_type="organization description",
    description="{description}",
    additional_context='''Organization name: {name}
Organization type: {org_type}

Please provide an improved organization description that:
1. Expands goals and structure
2. Incorporates relationships with characters and other organizations
3. References involvement in key plot points
4. Maintains consistency with established role
5. Adds depth with vivid description of operations and culture''',
    llm_context="{llm_context}"
)

# Project summary prompt
PROJECT_SUMMARY_PROMPT = '''Create a comprehensive summary of this writing project that includes:
1. Brief project overview
2. Key characters and roles
3. Main plot points in sequence
4. Important locations and organizations
5. Notable character relationships

Project data:
{llm_context}'''

# Chapter content prompt
CHAPTER_CONTENT_PROMPT = '''Write the content for Chapter {chapter_number}: {chapter_title}

POV Character: {point_of_view_character}
Chapter Notes: {chapter_notes}

Write narrative fiction with dialogue and description appropriate to the story.
Be consistent with existing characters, plot progression, and tone.
Provide only the chapter content without comments or explanations.

Relevant project context:
{llm_context}''' 