"""
Unit tests for metadata_parser.py - YAML frontmatter extraction.
"""

import pytest
from RAG_Pipeline.common.metadata_parser import (
    extract_frontmatter,
    validate_frontmatter,
    parse_case_study
)
from RAG_Pipeline.common.schemas import CaseStudyFrontmatter


def test_extract_frontmatter_valid():
    """Test extraction of valid YAML frontmatter."""
    content = """---
title: Test Case Study
client: Acme Corp
industry: E-commerce
project_type: AI_ML
---

# Main Content Here

This is the body of the case study.
"""
    frontmatter, body = extract_frontmatter(content)

    assert frontmatter['title'] == "Test Case Study"
    assert frontmatter['client'] == "Acme Corp"
    assert frontmatter['industry'] == "E-commerce"
    assert frontmatter['project_type'] == "AI_ML"
    assert "Main Content Here" in body
    assert "---" not in body


def test_extract_frontmatter_missing():
    """Test handling of content without frontmatter."""
    content = """# Just a Regular Markdown File

No frontmatter here.
"""
    frontmatter, body = extract_frontmatter(content)

    assert frontmatter == {}
    assert body == content


def test_extract_frontmatter_invalid_yaml():
    """Test handling of malformed YAML frontmatter."""
    content = """---
title: Test
: invalid yaml
  - broken
---

Content
"""
    frontmatter, body = extract_frontmatter(content)

    # Should return empty dict and original content on YAML error
    assert frontmatter == {}
    assert body == content


def test_validate_frontmatter_required_fields():
    """Test Pydantic validation with missing required fields."""
    # Missing 'client' field
    incomplete_frontmatter = {
        "title": "Test",
        "industry": "Tech",
        "project_type": "AI_ML"
    }

    result = validate_frontmatter(incomplete_frontmatter)
    assert result is None  # Should return None on validation error


def test_validate_frontmatter_valid():
    """Test Pydantic validation with all required fields."""
    valid_frontmatter = {
        "title": "Test Case Study",
        "client": "Acme Corp",
        "industry": "E-commerce",
        "project_type": "Workflow_Automation"
    }

    result = validate_frontmatter(valid_frontmatter)
    assert isinstance(result, CaseStudyFrontmatter)
    assert result.title == "Test Case Study"
    assert result.client == "Acme Corp"


def test_parse_case_study_full_workflow():
    """Test end-to-end case study parsing with real frontmatter."""
    file_content = b"""---
title: "Andi: AI Agent for ABC Home"
client: ABC Home & Commercial
industry: Home Services
project_type: Workflow_Automation
technologies_used:
  - Python
  - FastAPI
  - OpenAI
---

# Project Overview

ABC Home implemented an AI agent to handle customer calls.
"""

    frontmatter, body = parse_case_study(file_content, "test.md")

    assert frontmatter is not None
    assert isinstance(frontmatter, CaseStudyFrontmatter)
    assert frontmatter.title == "Andi: AI Agent for ABC Home"
    assert frontmatter.client == "ABC Home & Commercial"
    assert frontmatter.industry == "Home Services"
    assert frontmatter.project_type == "Workflow_Automation"
    assert "Python" in frontmatter.technologies_used
    assert "Project Overview" in body


def test_parse_case_study_empty_frontmatter():
    """Test parsing with empty frontmatter section."""
    file_content = b"""---
---

Just content, no metadata.
"""

    frontmatter, body = parse_case_study(file_content, "test.md")

    # Empty frontmatter should be treated as missing
    assert frontmatter is None


def test_parse_case_study_no_frontmatter():
    """Test parsing markdown without any frontmatter."""
    file_content = b"""# Regular Markdown

No frontmatter at all.
"""

    frontmatter, body = parse_case_study(file_content, "test.md")

    assert frontmatter is None
    assert "Regular Markdown" in body
