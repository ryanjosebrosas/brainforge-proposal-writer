"""
Content restriction validation engine.

This module implements validation logic for:
- Forbidden phrase detection
- Required element checking
- Custom word count range enforcement
"""

import re
from typing import List, Tuple

from template_schemas import ContentRestriction


# ========== Forbidden Phrase Detection ==========

def check_forbidden_phrases(content: str, restrictions: ContentRestriction) -> List[str]:
    """
    Check if content contains any forbidden phrases.

    Args:
        content: Generated proposal/email text
        restrictions: ContentRestriction object with forbidden_phrases list

    Returns:
        List of found forbidden phrases (empty if clean)

    Example:
        found = check_forbidden_phrases("Use Snowflake", ContentRestriction(forbidden_phrases=["snowflake"]))
        # Returns: ["snowflake"]
    """
    if not restrictions.forbidden_phrases:
        return []

    found_phrases = []
    content_lower = content.lower()

    for phrase in restrictions.forbidden_phrases:
        # Escape special regex characters
        escaped_phrase = re.escape(phrase.lower())

        # Support wildcards: "very *" matches "very good", "very bad"
        pattern = escaped_phrase.replace(r'\*', r'.*?')

        if re.search(pattern, content_lower):
            found_phrases.append(phrase)
            print(f"Found forbidden phrase: {phrase}")

    return found_phrases


# ========== Required Element Checking ==========

def check_required_elements(content: str, restrictions: ContentRestriction) -> List[str]:
    """
    Check if content contains all required elements.

    Args:
        content: Generated proposal/email text
        restrictions: ContentRestriction object with required_elements list

    Returns:
        List of MISSING required elements (empty if all present)

    Example:
        missing = check_required_elements("I use Java", ContentRestriction(required_elements=["Python"]))
        # Returns: ["Python"]
    """
    if not restrictions.required_elements:
        return []

    missing_elements = []

    for element in restrictions.required_elements:
        try:
            # Support regex patterns (e.g., "Python|JavaScript" = at least one)
            if not re.search(element, content, re.IGNORECASE):
                missing_elements.append(element)
                print(f"Missing required element: {element}")
        except re.error as e:
            print(f"Invalid regex pattern '{element}': {e}")
            # Treat as literal string if regex fails
            if element.lower() not in content.lower():
                missing_elements.append(element)

    return missing_elements


# ========== Word Count Range Enforcement ==========

def get_word_count_range(
    content_type: str,
    restrictions: ContentRestriction
) -> Tuple[int, int]:
    """
    Get word count range for content type (custom or default).

    Args:
        content_type: Type of content (upwork_proposal, outreach_email, etc.)
        restrictions: ContentRestriction object with word_count_overrides

    Returns:
        Tuple of (min_words, max_words)

    Raises:
        ValueError: If custom min >= max

    Example:
        min_w, max_w = get_word_count_range("upwork_proposal", restrictions)
        # Returns: (150, 300) or custom range if set
    """
    # Check for custom override
    if restrictions.word_count_overrides and content_type in restrictions.word_count_overrides:
        custom_range = restrictions.word_count_overrides[content_type]

        min_words = custom_range.get('min', 0)
        max_words = custom_range.get('max', 9999)

        if min_words >= max_words:
            raise ValueError(
                f"Invalid word count for {content_type}: "
                f"min ({min_words}) must be < max ({max_words})"
            )

        print(f"Using custom word count for {content_type}: {min_words}-{max_words}")
        return (min_words, max_words)

    # Return defaults based on content type
    defaults = {
        "upwork_proposal": (150, 300),
        "outreach_email": (100, 200),
        "rfp_response": (300, 1000)
    }

    return defaults.get(content_type, (100, 500))


# ========== Combined Validation ==========

def validate_content_restrictions(
    content: str,
    content_type: str,
    restrictions: ContentRestriction
) -> dict:
    """
    Run all restriction validations on content.

    Args:
        content: Generated proposal/email text
        content_type: Type of content (upwork_proposal, outreach_email, etc.)
        restrictions: ContentRestriction object

    Returns:
        Dict with validation results:
        {
            "passes_restrictions": bool,
            "forbidden_phrases_found": List[str],
            "required_elements_missing": List[str],
            "word_count_valid": bool,
            "word_count": int,
            "word_count_range": Tuple[int, int]
        }

    Example:
        results = validate_content_restrictions(content, "upwork_proposal", restrictions)
    """
    word_count = len(content.split())

    # Check forbidden phrases
    forbidden_found = check_forbidden_phrases(content, restrictions)

    # Check required elements
    required_missing = check_required_elements(content, restrictions)

    # Check word count
    min_words, max_words = get_word_count_range(content_type, restrictions)
    word_count_valid = min_words <= word_count <= max_words

    passes_restrictions = (
        len(forbidden_found) == 0
        and len(required_missing) == 0
        and word_count_valid
    )

    return {
        "passes_restrictions": passes_restrictions,
        "forbidden_phrases_found": forbidden_found,
        "required_elements_missing": required_missing,
        "word_count_valid": word_count_valid,
        "word_count": word_count,
        "word_count_range": (min_words, max_words)
    }
