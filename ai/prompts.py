CHARACTER_BIO_PROMPT = '''Please improve and expand the bio for the character "{name}" in this writing project. 
Consider their role, traits, relationships, and involvement in plot points to create a more detailed and engaging character bio.
The bio should be consistent with the existing project context and maintain the character's established personality and relationships. 
It should be plain text and have a literary quality. Don't add any comments or explanation.

Current character description:
{description}

Here is the full project context:
{llm_context}

Please provide an improved version of the character's bio that:
1. Expands on their background and motivations
2. Incorporates their relationships with other characters
3. References their involvement in key plot points
4. Maintains consistency with their established traits
5. Adds depth while staying true to their role in the story'''

PLACE_DESCRIPTION_PROMPT = '''Please improve and expand the description for the place "{name}" in this writing project. 
Consider its type, role in the story, and connections to characters and plot points to create a more detailed and engaging place description.
The description should be consistent with the existing project context and maintain the place's established characteristics and significance.
It should be plain text, not json and it should have a literary quality. Very aestetic language. Don't add any comments or explanation.

Current place description:
{description}

Here is the full project context:
{llm_context}

Please provide an improved version of the place's description that:
1. Expands on its physical characteristics and atmosphere
2. Incorporates its significance to the story and characters
3. References its involvement in key plot points
4. Maintains consistency with its established type and role
5. Adds depth while staying true to its purpose in the story
6. Has a literary quality and vivid imagery'''

ORG_DESCRIPTION_PROMPT = '''Please improve and expand the description for the organization "{name}" in this writing project. 
Consider its type, members, and role in the story to create a more detailed and engaging organization description.
The description should be consistent with the existing project context and maintain the organization's established characteristics and significance.
It should be plain text, not json and it should have a literary quality. Very aestetic language. Don't add any comments or explanation.

Current organization type:
{org_type}

Current organization description:
{description}

Here is the full project context:
{llm_context}

Please provide an improved version of the organization's description that:
1. Expands on its type and goals
2. Incorporates its relationships with characters and other organizations
3. References its involvement in key plot points
4. Maintains consistency with its established role and influence
5. Adds depth while staying true to its purpose in the story
6. Has a literary quality and vivid description of its operations and culture'''

PROJECT_SUMMARY_PROMPT = '''Please provide a comprehensive summary of this writing project. Include:
1. A brief overview of the project
2. Key characters and their roles
3. Main plot points in order
4. Important locations and organizations
5. Any notable relationships or dynamics between characters

Here is the project data:
{llm_context}''' 