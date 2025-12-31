"""
Pydantic schemas for template customization and output restrictions.

This module defines 5 core data models for the template system:
- ProposalTemplate: Pre-defined proposal structures (Technical, Consultative, Quick Win)
- TonePreset: Style configurations (professional, conversational, technical, friendly)
- ContentRestriction: Forbidden phrases, required elements, word count overrides
- UserPreferences: Container for user's selected template + tone + restrictions
- TemplatePromptConfig: Combined config for prompt generation
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Literal, Optional


class ProposalTemplate(BaseModel):
    """Pre-defined proposal structure variant."""

    id: str = Field(..., description="Unique template identifier")
    name: str = Field(..., description="Human-readable template name")
    template_type: Literal["technical", "consultative", "quick_win"] = Field(
        ..., description="Template category"
    )
    structure_config: Dict[str, any] = Field(
        default_factory=dict,
        description="Template configuration (section weights, emphasis areas)"
    )
    description: Optional[str] = Field(
        None, description="Template description for UI"
    )


class TonePreset(BaseModel):
    """Writing style and tone configuration."""

    id: str = Field(..., description="Unique tone identifier")
    name: str = Field(..., description="Human-readable tone name")
    tone_type: Literal["professional", "conversational", "technical", "friendly"] = Field(
        ..., description="Tone category"
    )
    language_patterns: Dict[str, any] = Field(
        default_factory=dict,
        description="Language modifications (formality level, vocabulary choices)"
    )
    description: Optional[str] = Field(
        None, description="Tone description for UI"
    )


class ContentRestriction(BaseModel):
    """Content filtering rules and validation constraints."""

    forbidden_phrases: List[str] = Field(
        default_factory=list,
        description="Phrases that must NOT appear in generated content"
    )
    required_elements: List[str] = Field(
        default_factory=list,
        description="Elements that MUST appear (supports regex patterns)"
    )
    word_count_overrides: Dict[str, Dict[str, int]] = Field(
        default_factory=dict,
        description="Custom word count ranges per content type"
    )

    @field_validator('word_count_overrides')
    @classmethod
    def validate_word_counts(cls, v):
        """Ensure min < max for all word count overrides."""
        for content_type, range_dict in v.items():
            if 'min' in range_dict and 'max' in range_dict:
                if range_dict['min'] >= range_dict['max']:
                    raise ValueError(
                        f"Invalid word count for {content_type}: "
                        f"min ({range_dict['min']}) must be < max ({range_dict['max']})"
                    )
        return v


class UserPreferences(BaseModel):
    """User's selected template, tone, and content restrictions."""

    user_id: str = Field(..., description="User identifier")
    template_id: str = Field(
        default="technical-001",
        description="Selected proposal template ID"
    )
    tone_id: str = Field(
        default="professional-001",
        description="Selected tone preset ID"
    )
    restrictions: Optional[ContentRestriction] = Field(
        None, description="Optional content restrictions"
    )


class TemplatePromptConfig(BaseModel):
    """Combined configuration for prompt generation."""

    template: ProposalTemplate = Field(..., description="Selected template structure")
    tone: TonePreset = Field(..., description="Selected tone preset")
    restrictions: Optional[ContentRestriction] = Field(
        None, description="Optional content restrictions"
    )
    base_requirements: List[str] = Field(
        default_factory=lambda: [
            "Include 2+ specific quantifiable metrics",
            "Reference company-specific context when available",
            "Professional tone",
            "Clear call-to-action"
        ],
        description="Non-negotiable requirements that must be preserved"
    )
