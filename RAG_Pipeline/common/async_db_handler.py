"""
Async database handler for RAG pipeline.

This module provides async Supabase operations for:
- Document deletion by file_id
- Batch chunk insertion
- Metadata management
- Full file processing workflow

All I/O operations are async following CLAUDE.md standards.
"""

import asyncio
import base64
import json
import traceback
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
from supabase import AClient, create_async_client

from .schemas import FileMetadata, IngestionResult, CaseStudyFrontmatter
from .text_processor import (
    chunk_text,
    create_embeddings,
    is_tabular_file,
    extract_schema_from_csv,
    extract_rows_from_csv
)

# Load environment variables from project root
project_root = Path(__file__).resolve().parent.parent.parent
dotenv_path = project_root / '.env'
load_dotenv(dotenv_path, override=True)

# Constants
BATCH_SIZE = 100
DEFAULT_CHUNK_SIZE = 400
DEFAULT_CHUNK_OVERLAP = 0


# ========== Retry Decorator ==========

def async_retry(max_attempts: int = 3, backoff_factor: int = 2):
    """
    Retry decorator for async functions with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        backoff_factor: Multiplier for wait time between retries
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    wait_time = backoff_factor ** attempt
                    print(f"Retry {attempt + 1}/{max_attempts} after {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
        return wrapper
    return decorator


# ========== Async Database Operations ==========

async def delete_document_by_file_id_async(supabase: AClient, file_id: str) -> None:
    """
    Delete all records related to a specific file ID (async).

    Removes from:
    - documents table (chunks)
    - document_rows table (tabular data)
    - document_metadata table (file info)

    Args:
        supabase: Async Supabase client
        file_id: File identifier (path or GDrive ID)
    """
    try:
        print(f"Starting deletion for file_id: {file_id}")

        # Delete all documents with the specified file_id in metadata
        response = await supabase.table("documents").delete().eq("metadata->>file_id", file_id).execute()
        print(f"Deleted {len(response.data)} document chunks for file ID: {file_id}")

        # Delete all document_rows with the specified dataset_id
        try:
            rows_response = await supabase.table("document_rows").delete().eq("dataset_id", file_id).execute()
            print(f"Deleted {len(rows_response.data)} document rows for file ID: {file_id}")
        except Exception as e:
            print(f"Error deleting document rows for file_id {file_id}: {e}")

        # Delete the document_metadata record
        try:
            metadata_response = await supabase.table("document_metadata").delete().eq("id", file_id).execute()
            print(f"Deleted metadata for file ID: {file_id}")
        except Exception as e:
            print(f"Error deleting document metadata for file_id {file_id}: {e}")

    except Exception as e:
        print(f"Error in delete_document_by_file_id_async for file_id {file_id}: {e}")


@async_retry(max_attempts=3)
async def insert_document_chunks_batch(
    supabase: AClient,
    chunks: List[str],
    embeddings: List[List[float]],
    file_meta: FileMetadata
) -> int:
    """
    Insert document chunks in batches for performance (async).

    Args:
        supabase: Async Supabase client
        chunks: List of text chunks
        embeddings: List of embedding vectors
        file_meta: File metadata including case study frontmatter

    Returns:
        Total number of chunks inserted
    """
    if len(chunks) != len(embeddings):
        raise ValueError("Number of chunks and embeddings must match")

    print(f"Starting batch insert for file_id: {file_meta.file_id} ({len(chunks)} chunks)")

    # Prepare base metadata
    base_metadata = {
        "file_id": file_meta.file_id,
        "file_url": file_meta.file_url,
        "file_title": file_meta.file_title,
        "mime_type": file_meta.mime_type,
    }

    # Merge case study frontmatter if available
    if file_meta.case_study_metadata:
        frontmatter_dict = file_meta.case_study_metadata.model_dump()
        base_metadata.update(frontmatter_dict)

    # Prepare all chunks
    data = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        data.append({
            "content": chunk,
            "metadata": {**base_metadata, "chunk_index": i},
            "embedding": embedding
        })

    # Insert in batches
    total_chunks = len(data)
    total_batches = (total_chunks + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, total_chunks, BATCH_SIZE):
        batch = data[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        print(f"Inserting batch {batch_num}/{total_batches} ({len(batch)} chunks)")

        await supabase.table("documents").insert(batch).execute()

    print(f"Successfully inserted {total_chunks} chunks for file_id: {file_meta.file_id}")
    return total_chunks


async def insert_or_update_document_metadata_async(
    supabase: AClient,
    file_meta: FileMetadata,
    schema: Optional[List[str]] = None
) -> None:
    """
    Insert or update document metadata record (async).

    Args:
        supabase: Async Supabase client
        file_meta: File metadata
        schema: Optional schema for tabular files (column names)
    """
    try:
        print(f"Upserting metadata for file_id: {file_meta.file_id}")

        # Check if record exists
        response = await supabase.table("document_metadata").select("*").eq("id", file_meta.file_id).execute()

        # Prepare data
        data = {
            "id": file_meta.file_id,
            "title": file_meta.file_title,
            "url": file_meta.file_url
        }

        # Add schema if provided
        if schema:
            data["schema"] = json.dumps(schema)

        if response.data and len(response.data) > 0:
            # Update existing record
            await supabase.table("document_metadata").update(data).eq("id", file_meta.file_id).execute()
            print(f"Updated metadata for file '{file_meta.file_title}' (ID: {file_meta.file_id})")
        else:
            # Insert new record
            await supabase.table("document_metadata").insert(data).execute()
            print(f"Inserted metadata for file '{file_meta.file_title}' (ID: {file_meta.file_id})")

    except Exception as e:
        print(f"Error in insert_or_update_document_metadata_async for file_id {file_meta.file_id}: {e}")


async def insert_document_rows_async(
    supabase: AClient,
    file_id: str,
    rows: List[Dict[str, Any]]
) -> int:
    """
    Insert tabular rows from CSV/Excel files (async).

    Args:
        supabase: Async Supabase client
        file_id: File identifier
        rows: List of row data as dictionaries

    Returns:
        Number of rows inserted
    """
    try:
        print(f"Inserting {len(rows)} rows for file_id: {file_id}")

        # First, delete any existing rows for this file (idempotent)
        await supabase.table("document_rows").delete().eq("dataset_id", file_id).execute()
        print(f"Deleted existing rows for file ID: {file_id}")

        # Insert new rows
        for row in rows:
            await supabase.table("document_rows").insert({
                "dataset_id": file_id,
                "row_data": row
            }).execute()

        print(f"Inserted {len(rows)} rows for file ID: {file_id}")
        return len(rows)

    except Exception as e:
        print(f"Error in insert_document_rows_async for file_id {file_id}: {e}")
        return 0


@async_retry(max_attempts=3)
async def process_file_for_rag_async(
    supabase: AClient,
    file_content: bytes,
    text: str,
    file_meta: FileMetadata,
    config: Dict[str, Any]
) -> IngestionResult:
    """
    Process a file for RAG pipeline - full async workflow.

    Workflow:
    1. Delete existing records for file_id (idempotent)
    2. Check if tabular file (CSV/Excel)
    3. Insert/update document metadata
    4. Insert tabular rows if applicable
    5. Chunk text and create embeddings
    6. Batch insert chunks

    Args:
        supabase: Async Supabase client
        file_content: Binary file content
        text: Extracted text content
        file_meta: File metadata with optional case study frontmatter
        config: Configuration dict (chunk_size, overlap, etc.)

    Returns:
        IngestionResult with success status and metrics
    """
    start_time = datetime.now()

    try:
        print(f"Starting process_file_for_rag_async for file_id: {file_meta.file_id}")

        # Delete existing records first (idempotent operation)
        await delete_document_by_file_id_async(supabase, file_meta.file_id)

        # Check if tabular file
        is_tabular = False
        schema = None

        if file_meta.mime_type:
            is_tabular = is_tabular_file(file_meta.mime_type, config)

        if is_tabular:
            schema = extract_schema_from_csv(file_content)

        # Insert or update document metadata (needed for foreign key)
        await insert_or_update_document_metadata_async(supabase, file_meta, schema)

        # Insert tabular rows if applicable
        rows_inserted = 0
        if is_tabular:
            rows = extract_rows_from_csv(file_content)
            if rows:
                rows_inserted = await insert_document_rows_async(supabase, file_meta.file_id, rows)

        # Get text processing settings from config
        text_processing = config.get('text_processing', {})
        chunk_size = text_processing.get('default_chunk_size', DEFAULT_CHUNK_SIZE)
        chunk_overlap = text_processing.get('default_chunk_overlap', DEFAULT_CHUNK_OVERLAP)

        # Chunk the text
        chunks = chunk_text(text, chunk_size=chunk_size, overlap=chunk_overlap)
        if not chunks:
            print(f"No chunks created for file '{file_meta.file_title}' (ID: {file_meta.file_id})")
            end_time = datetime.now()
            processing_time = int((end_time - start_time).total_seconds() * 1000)

            return IngestionResult(
                success=False,
                file_id=file_meta.file_id,
                chunks_inserted=0,
                rows_inserted=rows_inserted,
                error_message="No chunks created from text",
                processing_time_ms=processing_time,
                frontmatter_extracted=file_meta.case_study_metadata is not None
            )

        # Create embeddings for chunks
        embeddings = create_embeddings(chunks)

        # Batch insert chunks
        chunks_inserted = await insert_document_chunks_batch(supabase, chunks, embeddings, file_meta)

        # Calculate processing time
        end_time = datetime.now()
        processing_time = int((end_time - start_time).total_seconds() * 1000)

        print(f"Successfully processed file_id: {file_meta.file_id} in {processing_time}ms")

        return IngestionResult(
            success=True,
            file_id=file_meta.file_id,
            chunks_inserted=chunks_inserted,
            rows_inserted=rows_inserted,
            error_message=None,
            processing_time_ms=processing_time,
            frontmatter_extracted=file_meta.case_study_metadata is not None
        )

    except Exception as e:
        traceback.print_exc()
        print(f"Error in process_file_for_rag_async for file_id {file_meta.file_id}: {e}")

        end_time = datetime.now()
        processing_time = int((end_time - start_time).total_seconds() * 1000)

        return IngestionResult(
            success=False,
            file_id=file_meta.file_id,
            chunks_inserted=0,
            rows_inserted=0,
            error_message=str(e),
            processing_time_ms=processing_time,
            frontmatter_extracted=file_meta.case_study_metadata is not None
        )
