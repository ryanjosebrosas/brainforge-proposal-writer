"""
Template manager for proposal customization.

This module provides CRUD operations for templates, tones, and user preferences,
plus prompt building with template/tone customization.
"""

from typing import List, Optional

from supabase import Client

from template_schemas import (
    ContentRestriction,
    ProposalTemplate,
    TonePreset,
    UserPreferences
)


# ========== Template Loading ==========

def load_user_preferences(supabase: Client, user_id: str) -> UserPreferences:
    """
    Load user preferences from database with template and tone data.

    Args:
        supabase: Supabase client instance
        user_id: User identifier

    Returns:
        UserPreferences object (returns defaults if user has no saved preferences)

    Example:
        prefs = load_user_preferences(supabase, "user_123")
    """
    try:
        print(f"Loading preferences for user: {user_id}")

        # Query user_preferences table
        result = supabase.table("user_preferences").select("*").eq("user_id", user_id).execute()

        if not result.data or len(result.data) == 0:
            print(f"No preferences found for {user_id}, returning defaults")
            return UserPreferences(
                user_id=user_id,
                template_id="technical-001",
                tone_id="professional-001",
                restrictions=None
            )

        pref_data = result.data[0]

        # Load restrictions if they exist
        restrictions = None
        restriction_result = supabase.table("content_restrictions").select("*").eq("user_id", user_id).execute()

        if restriction_result.data and len(restriction_result.data) > 0:
            rest_data = restriction_result.data[0]
            restrictions = ContentRestriction(
                forbidden_phrases=rest_data.get('forbidden_phrases', []),
                required_elements=rest_data.get('required_elements', []),
                word_count_overrides=rest_data.get('word_count_overrides', {})
            )

        print(f"Loaded preferences: template={pref_data['template_id']}, tone={pref_data['tone_id']}")

        return UserPreferences(
            user_id=user_id,
            template_id=pref_data['template_id'],
            tone_id=pref_data['tone_id'],
            restrictions=restrictions
        )

    except Exception as e:
        print(f"Error loading user preferences: {e}")
        # Return defaults on error
        return UserPreferences(
            user_id=user_id,
            template_id="technical-001",
            tone_id="professional-001",
            restrictions=None
        )


# ========== Template Prompt Builder ==========

def build_customized_prompt(
    template: ProposalTemplate,
    tone: TonePreset,
    base_prompt: str
) -> str:
    """
    Inject template structure and tone modifications into base prompt.

    Args:
        template: Selected proposal template
        tone: Selected tone preset
        base_prompt: Original prompt to enhance

    Returns:
        Modified prompt with template/tone directives

    Example:
        prompt = build_customized_prompt(tech_template, professional_tone, base_prompt)
    """
    print(f"Building customized prompt: template={template.name}, tone={tone.name}")

    # Extract template config
    template_config = template.structure_config
    emphasis = template_config.get('emphasis', 'balanced')
    technical_detail = template_config.get('technical_detail', 'medium')
    section_weights = template_config.get('section_weights', {})
    opening_style = template_config.get('opening_style', 'standard')

    # Extract tone config
    tone_config = tone.language_patterns
    formality = tone_config.get('formality', 'medium')
    use_contractions = tone_config.get('contractions', False)
    vocabulary = tone_config.get('vocabulary', 'standard')

    # Build template directives
    template_directive = f"\n\n**TEMPLATE CUSTOMIZATION ({template.name})**:\n"
    template_directive += f"- Emphasis: {emphasis}\n"
    template_directive += f"- Technical detail level: {technical_detail}\n"
    template_directive += f"- Opening style: {opening_style}\n"

    if section_weights:
        template_directive += "- Section allocation:\n"
        for section, weight in section_weights.items():
            percentage = int(weight * 100)
            template_directive += f"  - {section.title()}: {percentage}% of content\n"

    # Build tone directives
    tone_directive = f"\n**TONE CUSTOMIZATION ({tone.name})**:\n"
    tone_directive += f"- Formality level: {formality}\n"
    tone_directive += f"- Use contractions: {'Yes' if use_contractions else 'No'}\n"
    tone_directive += f"- Vocabulary style: {vocabulary}\n"

    # Inject into base prompt
    customized_prompt = base_prompt + template_directive + tone_directive

    return customized_prompt


# ========== CRUD Operations ==========

def save_user_preferences(
    supabase: Client,
    user_id: str,
    preferences: UserPreferences
) -> bool:
    """
    Save user preferences to database (create or update).

    Args:
        supabase: Supabase client instance
        user_id: User identifier
        preferences: UserPreferences object to save

    Returns:
        True if save successful, False otherwise

    Example:
        success = save_user_preferences(supabase, "user_123", prefs)
    """
    try:
        print(f"Saving preferences for user: {user_id}")

        # Upsert user_preferences
        pref_data = {
            "user_id": user_id,
            "template_id": preferences.template_id,
            "tone_id": preferences.tone_id
        }

        result = supabase.table("user_preferences").upsert(
            pref_data,
            on_conflict="user_id"
        ).execute()

        if not result.data:
            print("Failed to save user preferences")
            return False

        # Save restrictions if provided
        if preferences.restrictions:
            rest_data = {
                "user_id": user_id,
                "forbidden_phrases": preferences.restrictions.forbidden_phrases,
                "required_elements": preferences.restrictions.required_elements,
                "word_count_overrides": preferences.restrictions.word_count_overrides
            }

            rest_result = supabase.table("content_restrictions").upsert(
                rest_data,
                on_conflict="user_id"
            ).execute()

            if not rest_result.data:
                print("Failed to save content restrictions")
                return False

        print(f"Successfully saved preferences for {user_id}")
        return True

    except Exception as e:
        print(f"Error saving user preferences: {e}")
        return False


def get_template_by_id(supabase: Client, template_id: str) -> Optional[ProposalTemplate]:
    """
    Retrieve template by ID from database.

    Args:
        supabase: Supabase client instance
        template_id: Template identifier

    Returns:
        ProposalTemplate object or None if not found

    Example:
        template = get_template_by_id(supabase, "technical-001")
    """
    try:
        result = supabase.table("proposal_templates").select("*").eq("id", template_id).execute()

        if not result.data or len(result.data) == 0:
            print(f"Template {template_id} not found")
            return None

        data = result.data[0]
        return ProposalTemplate(
            id=data['id'],
            name=data['name'],
            template_type=data['template_type'],
            structure_config=data['structure_config'],
            description=data.get('description')
        )

    except Exception as e:
        print(f"Error retrieving template {template_id}: {e}")
        return None


def get_tone_by_id(supabase: Client, tone_id: str) -> Optional[TonePreset]:
    """
    Retrieve tone preset by ID from database.

    Args:
        supabase: Supabase client instance
        tone_id: Tone identifier

    Returns:
        TonePreset object or None if not found

    Example:
        tone = get_tone_by_id(supabase, "professional-001")
    """
    try:
        result = supabase.table("tone_presets").select("*").eq("id", tone_id).execute()

        if not result.data or len(result.data) == 0:
            print(f"Tone {tone_id} not found")
            return None

        data = result.data[0]
        return TonePreset(
            id=data['id'],
            name=data['name'],
            tone_type=data['tone_type'],
            language_patterns=data['language_patterns'],
            description=data.get('description')
        )

    except Exception as e:
        print(f"Error retrieving tone {tone_id}: {e}")
        return None


def list_available_templates(supabase: Client) -> List[ProposalTemplate]:
    """
    List all available proposal templates.

    Args:
        supabase: Supabase client instance

    Returns:
        List of ProposalTemplate objects

    Example:
        templates = list_available_templates(supabase)
    """
    try:
        result = supabase.table("proposal_templates").select("*").execute()

        templates = []
        for data in result.data:
            templates.append(ProposalTemplate(
                id=data['id'],
                name=data['name'],
                template_type=data['template_type'],
                structure_config=data['structure_config'],
                description=data.get('description')
            ))

        print(f"Loaded {len(templates)} templates")
        return templates

    except Exception as e:
        print(f"Error listing templates: {e}")
        return []


def list_available_tones(supabase: Client) -> List[TonePreset]:
    """
    List all available tone presets.

    Args:
        supabase: Supabase client instance

    Returns:
        List of TonePreset objects

    Example:
        tones = list_available_tones(supabase)
    """
    try:
        result = supabase.table("tone_presets").select("*").execute()

        tones = []
        for data in result.data:
            tones.append(TonePreset(
                id=data['id'],
                name=data['name'],
                tone_type=data['tone_type'],
                language_patterns=data['language_patterns'],
                description=data.get('description')
            ))

        print(f"Loaded {len(tones)} tone presets")
        return tones

    except Exception as e:
        print(f"Error listing tones: {e}")
        return []
