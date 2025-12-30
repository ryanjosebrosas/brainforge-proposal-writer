"""
YAML frontmatter extraction for markdown case studies.

This module provides functions to:
- Extract YAML frontmatter from markdown files
- Validate frontmatter against CaseStudyFrontmatter schema
- Parse case studies with full error handling
"""

import re
import yaml
from typing import Tuple, Dict, Any, Optional
from pydantic import ValidationError

from .schemas import CaseStudyFrontmatter


def extract_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """
    Extract YAML frontmatter from markdown content.

    Frontmatter must be at the START of the file, delimited by --- markers:
    ---
    title: Example
    client: Acme Corp
    ---

    Main content here...

    Args:
        content: Full markdown file content as string

    Returns:
        Tuple of (frontmatter_dict, content_without_frontmatter)
        If no frontmatter found, returns ({}, original_content)
    """
    # Match YAML frontmatter: ---\n...\n---
    # Pattern: start of string, ---, yaml content, ---, rest of content
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return {}, content

    frontmatter_text = match.group(1)
    body = match.group(2)

    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        return frontmatter or {}, body
    except yaml.YAMLError as e:
        print(f"Error parsing YAML frontmatter: {e}")
        return {}, content


def validate_frontmatter(frontmatter: Dict[str, Any]) -> Optional[CaseStudyFrontmatter]:
    """
    Validate frontmatter dict against CaseStudyFrontmatter schema.

    Args:
        frontmatter: Dictionary from extract_frontmatter

    Returns:
        CaseStudyFrontmatter instance if valid, None if validation fails
    """
    if not frontmatter:
        return None

    try:
        # Use Pydantic to validate and convert
        validated = CaseStudyFrontmatter(**frontmatter)
        return validated
    except ValidationError as e:
        print(f"Frontmatter validation error: {e}")
        return None


def parse_case_study(file_content: bytes, file_name: str) -> Tuple[Optional[CaseStudyFrontmatter], str]:
    """
    Parse case study markdown file with YAML frontmatter extraction.

    Main entry point for processing case study files. Handles:
    - Decoding bytes to string
    - Extracting YAML frontmatter
    - Validating frontmatter schema
    - Returning clean content body

    Args:
        file_content: Binary content of markdown file
        file_name: Name of file (for logging purposes)

    Returns:
        Tuple of (CaseStudyFrontmatter or None, body_text)
        - If frontmatter found and valid: (CaseStudyFrontmatter, body_text)
        - If no frontmatter or invalid: (None, full_text)
    """
    try:
        # Decode bytes to string
        text_content = file_content.decode('utf-8', errors='replace')
    except Exception as e:
        print(f"Error decoding file {file_name}: {e}")
        return None, ""

    # Extract frontmatter
    frontmatter_dict, body = extract_frontmatter(text_content)

    if not frontmatter_dict:
        print(f"No frontmatter found in {file_name}")
        return None, text_content

    # Validate frontmatter
    validated_frontmatter = validate_frontmatter(frontmatter_dict)

    if not validated_frontmatter:
        print(f"Invalid frontmatter in {file_name}, proceeding without metadata")
        return None, text_content

    print(f"Extracted frontmatter from {file_name}: {validated_frontmatter.title} ({validated_frontmatter.industry})")
    return validated_frontmatter, body
