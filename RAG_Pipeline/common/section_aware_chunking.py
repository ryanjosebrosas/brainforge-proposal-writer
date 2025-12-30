"""
Section-aware intelligent chunking for case studies.

This module provides advanced chunking that:
- Respects [START/END OF SECTION] markers
- Preserves section headers within chunks
- Splits large sections at paragraph boundaries
- Enriches metadata with section context
- Maintains semantic coherence

Usage:
    from section_aware_chunking import create_section_aware_chunks

    chunks = create_section_aware_chunks(
        text="# Title\n\n## Context\n[START OF SECTION]...",
        frontmatter=case_study_frontmatter
    )
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from schemas import CaseStudyFrontmatter


@dataclass
class Section:
    """Represents a logical section of a document."""
    header: str  # e.g., "## Context", "## Challenge"
    content: str  # Full content of the section
    start_marker: bool  # Whether section had [START OF SECTION]
    end_marker: bool  # Whether section had [END OF SECTION]


@dataclass
class EnrichedChunk:
    """A chunk with enhanced metadata."""
    content: str  # Text content with header preserved
    metadata: Dict[str, Any]  # Enriched metadata
    chunk_index: int  # Global chunk index
    section_name: str  # e.g., "Context", "Challenge"
    section_chunk_index: int  # Index within this section (0, 1, 2...)
    total_section_chunks: int  # Total chunks in this section


def extract_sections(text: str) -> List[Section]:
    """
    Extract sections from markdown text using [START/END OF SECTION] markers.

    Args:
        text: Full markdown body (after frontmatter removal)

    Returns:
        List of Section objects
    """
    sections = []

    # Pattern: Section header (## Title) followed by optional markers and content
    # We'll split by section headers first
    header_pattern = r'^(#{1,3}\s+.+)$'

    # Split text by headers while keeping them
    parts = re.split(header_pattern, text, flags=re.MULTILINE)

    current_header = None
    current_content = []

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Check if this is a header
        if re.match(header_pattern, part, flags=re.MULTILINE):
            # Save previous section if exists
            if current_header and current_content:
                full_content = '\n\n'.join(current_content)
                has_start = '[START OF SECTION]' in full_content
                has_end = '[END OF SECTION]' in full_content

                # Clean markers from content
                clean_content = full_content.replace('[START OF SECTION]', '').replace('[END OF SECTION]', '').strip()

                sections.append(Section(
                    header=current_header,
                    content=clean_content,
                    start_marker=has_start,
                    end_marker=has_end
                ))

            # Start new section
            current_header = part
            current_content = []
        else:
            current_content.append(part)

    # Don't forget the last section
    if current_header and current_content:
        full_content = '\n\n'.join(current_content)
        has_start = '[START OF SECTION]' in full_content
        has_end = '[END OF SECTION]' in full_content
        clean_content = full_content.replace('[START OF SECTION]', '').replace('[END OF SECTION]', '').strip()

        sections.append(Section(
            header=current_header,
            content=clean_content,
            start_marker=has_start,
            end_marker=has_end
        ))

    return sections


def split_section_at_paragraphs(
    section: Section,
    max_chunk_size: int = 1500,
    min_chunk_size: int = 300
) -> List[str]:
    """
    Split a large section into chunks at paragraph boundaries.

    Args:
        section: Section object to split
        max_chunk_size: Maximum characters per chunk
        min_chunk_size: Minimum characters per chunk (avoid tiny fragments)

    Returns:
        List of chunk strings, each starting with the section header
    """
    full_text = f"{section.header}\n\n{section.content}"

    # If section fits in one chunk, return as-is
    if len(full_text) <= max_chunk_size:
        return [full_text]

    # Split by paragraphs (double newline)
    paragraphs = section.content.split('\n\n')

    chunks = []
    current_chunk = section.header + '\n\n'

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If adding this paragraph would exceed max_chunk_size
        if len(current_chunk) + len(para) + 2 > max_chunk_size:
            # Save current chunk if it's not just the header
            if len(current_chunk) > len(section.header) + 10:
                chunks.append(current_chunk.strip())
                # Start new chunk with header
                current_chunk = section.header + '\n\n' + para + '\n\n'
            else:
                # First paragraph itself is huge, include it anyway
                current_chunk += para + '\n\n'
                chunks.append(current_chunk.strip())
                current_chunk = section.header + '\n\n'
        else:
            current_chunk += para + '\n\n'

    # Add the last chunk
    if len(current_chunk) > len(section.header) + 10:
        chunks.append(current_chunk.strip())

    return chunks


def extract_section_name(header: str) -> str:
    """
    Extract clean section name from header.

    Examples:
        "## Context" -> "Context"
        "### Solution: Technical Architecture" -> "Solution"
        "# Title" -> "Title"
    """
    # Remove markdown header markers
    clean = re.sub(r'^#{1,6}\s+', '', header)
    # Take first part before colon if exists
    clean = clean.split(':')[0].strip()
    return clean


def create_section_aware_chunks(
    text: str,
    frontmatter: Optional[CaseStudyFrontmatter] = None,
    max_chunk_size: int = 1500,
    file_id: str = "",
    file_url: str = "",
    file_title: str = ""
) -> List[EnrichedChunk]:
    """
    Create section-aware chunks from markdown text.

    Main entry point for intelligent chunking. This function:
    1. Extracts sections using [START/END OF SECTION] markers
    2. Keeps small sections intact
    3. Splits large sections at paragraph boundaries
    4. Preserves section headers in every chunk
    5. Enriches metadata with frontmatter + section context

    Args:
        text: Markdown body text (frontmatter already removed)
        frontmatter: Validated CaseStudyFrontmatter object or None
        max_chunk_size: Maximum characters per chunk (default 1500)
        file_id: File identifier for metadata
        file_url: File URL for metadata
        file_title: File title for metadata

    Returns:
        List of EnrichedChunk objects ready for database insertion
    """
    # Extract sections
    sections = extract_sections(text)

    if not sections:
        # Fallback: No sections found, treat entire text as one section
        sections = [Section(
            header="# Document",
            content=text,
            start_marker=False,
            end_marker=False
        )]

    enriched_chunks = []
    global_chunk_index = 0

    for section in sections:
        section_name = extract_section_name(section.header)

        # Split section into chunks (might be just 1 chunk if small)
        section_chunks = split_section_at_paragraphs(section, max_chunk_size)
        total_section_chunks = len(section_chunks)

        for section_chunk_idx, chunk_text in enumerate(section_chunks):
            # Build base metadata
            metadata = {
                "file_id": file_id,
                "file_url": file_url,
                "file_title": file_title,
                "chunk_index": global_chunk_index,
                "section": section_name,
                "section_chunk_index": section_chunk_idx,
                "total_section_chunks": total_section_chunks,
            }

            # Add frontmatter fields to metadata if available
            if frontmatter:
                metadata.update({
                    "title": frontmatter.title,
                    "client": frontmatter.client,
                    "industry": frontmatter.industry,
                    "project_type": frontmatter.project_type,
                    "tech_stack": frontmatter.tech_stack,
                    "function": frontmatter.function,
                    "project_status": frontmatter.project_status,
                })

                # Add key metrics if present
                if frontmatter.key_metrics:
                    metadata["key_metrics"] = frontmatter.key_metrics

            # Determine chunk role
            if total_section_chunks == 1:
                metadata["chunk_role"] = "section_complete"
            else:
                metadata["chunk_role"] = f"section_part_{section_chunk_idx + 1}_of_{total_section_chunks}"

            # Create enriched chunk
            enriched_chunks.append(EnrichedChunk(
                content=chunk_text,
                metadata=metadata,
                chunk_index=global_chunk_index,
                section_name=section_name,
                section_chunk_index=section_chunk_idx,
                total_section_chunks=total_section_chunks
            ))

            global_chunk_index += 1

    return enriched_chunks


def chunks_to_db_format(
    enriched_chunks: List[EnrichedChunk],
    embeddings: List[List[float]]
) -> List[Dict[str, Any]]:
    """
    Convert EnrichedChunk objects to database insertion format.

    Args:
        enriched_chunks: List of EnrichedChunk objects
        embeddings: List of embedding vectors (same length as chunks)

    Returns:
        List of dicts ready for Supabase insertion
    """
    if len(enriched_chunks) != len(embeddings):
        raise ValueError(f"Chunk count ({len(enriched_chunks)}) doesn't match embedding count ({len(embeddings)})")

    db_records = []
    for chunk, embedding in zip(enriched_chunks, embeddings):
        db_records.append({
            "content": chunk.content,
            "metadata": chunk.metadata,
            "embedding": embedding
        })

    return db_records


# ========== Example Usage ==========

if __name__ == "__main__":
    # Example markdown content
    example_text = """# ABC Home AI Dashboard

## Context

[START OF SECTION]

ABC Home & Commercial is one of Texas's largest home service providers.
They needed a dashboard to track their AI agent performance.

This project addressed the critical need to measure AI value.

[END OF SECTION]

## Challenge

[START OF SECTION]

CSRs wanted AI support they could count on, but there was no measurement system.

The organization faced several obstacles:
- No way to track quality
- Fragmented feedback
- Recurring issues unresolved
- Leadership had no visibility

[END OF SECTION]

## Solution

[START OF SECTION]

Brainforge built a comprehensive dashboard with four components:

**1. Response Logging**
Logged all AI responses in Snowflake for audit trail.

**2. Real-Time Feedback**
Added Google Chat integration for thumbs up/down ratings.

**3. Automated Triage**
Routed negative feedback into Linear automatically.

**4. Collaborative Model**
Split responsibilities between teams for faster fixes.

Dashboard features included total exchange tracking, quality scores,
error rates, execution time, escalation tracking, and drill-down capability.

Technologies used: n8n, Snowflake, Rill, Braintrust, Google Chat, Linear.

[END OF SECTION]
"""

    # Mock frontmatter
    from schemas import CaseStudyFrontmatter

    mock_frontmatter = CaseStudyFrontmatter(
        title="AI Agent Performance Dashboard",
        client="ABC Home & Commercial",
        industry="Home Services",
        project_type="BI_Analytics",
        technologies_used=["n8n", "Snowflake", "Rill"],
        function="Customer Support"
    )

    # Create chunks
    chunks = create_section_aware_chunks(
        text=example_text,
        frontmatter=mock_frontmatter,
        file_id="abc_home_dashboard",
        file_url="file://abc_home_dashboard.md",
        file_title="ABC Home AI Dashboard"
    )

    # Print results
    print(f"\n{'='*80}")
    print(f"Created {len(chunks)} section-aware chunks:")
    print(f"{'='*80}\n")

    for chunk in chunks:
        print(f"Chunk {chunk.chunk_index}: {chunk.section_name} (part {chunk.section_chunk_index + 1}/{chunk.total_section_chunks})")
        print(f"Role: {chunk.metadata['chunk_role']}")
        print(f"Length: {len(chunk.content)} chars")
        print(f"Metadata keys: {list(chunk.metadata.keys())}")
        print(f"Content preview: {chunk.content[:150]}...")
        print(f"{'-'*80}\n")
