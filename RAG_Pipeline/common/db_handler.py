from typing import List, Dict, Any, Optional
import os
import io
import json
import traceback
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
import base64
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from text_processor import chunk_text, create_embeddings, is_tabular_file, extract_schema_from_csv, extract_rows_from_csv, extract_text_and_metadata
from section_aware_chunking import create_section_aware_chunks, chunks_to_db_format

# Load environment variables from the project root .env file
# Get the path to the project root (4_Pydantic_AI_Agent directory)
project_root = Path(__file__).resolve().parent.parent.parent
dotenv_path = project_root / '.env'

# Force override of existing environment variables
load_dotenv(dotenv_path, override=True)

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def delete_document_by_file_id(file_id: str) -> None:
    """
    Delete all records related to a specific file ID (documents, document_rows, and document_metadata).
    
    Args:
        file_id: The Google Drive file ID
    """
    try:
        # Delete all documents with the specified file_id in metadata
        response = supabase.table("documents").delete().eq("metadata->>file_id", file_id).execute()
        print(f"Deleted {len(response.data)} document chunks for file ID: {file_id}")
        
        # Delete all document_rows with the specified dataset_id
        try:
            rows_response = supabase.table("document_rows").delete().eq("dataset_id", file_id).execute()
            print(f"Deleted {len(rows_response.data)} document rows for file ID: {file_id}")
        except Exception as e:
            print(f"Error deleting document rows: {e}")
            
        # Delete the document_metadata record
        try:
            metadata_response = supabase.table("document_metadata").delete().eq("file_id", file_id).execute()
            print(f"Deleted metadata for file ID: {file_id}")
        except Exception as e:
            print(f"Error deleting document metadata: {e}")
            
    except Exception as e:
        print(f"Error deleting documents: {e}")

def insert_document_chunks(chunks: List[str], embeddings: List[List[float]], file_id: str,
                        file_url: str, file_title: str, mime_type: str, file_contents: bytes | None = None,
                        enriched_metadata: List[Dict[str, Any]] = None) -> None:
    """
    Insert document chunks with their embeddings into the Supabase database.

    Args:
        chunks: List of text chunks
        embeddings: List of embedding vectors for each chunk
        file_id: The Google Drive file ID
        file_url: The URL to access the file
        file_title: The title of the file
        mime_type: The mime type of the file
        file_contents: Optional binary of the file to store as metadata
        enriched_metadata: Optional list of metadata dicts (from section-aware chunking)
    """
    try:
        # Ensure we have the same number of chunks and embeddings
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks and embeddings must match")

        # Prepare the data for insertion
        data = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            file_bytes_str = base64.b64encode(file_contents).decode('utf-8') if file_contents else None

            # Use enriched metadata if provided, otherwise create basic metadata
            if enriched_metadata and i < len(enriched_metadata):
                metadata = enriched_metadata[i].copy()
                # Add file_contents if present
                if file_bytes_str:
                    metadata["file_contents"] = file_bytes_str
            else:
                metadata = {
                    "file_id": file_id,
                    "file_url": file_url,
                    "file_title": file_title,
                    "mime_type": mime_type,
                    "chunk_index": i,
                    **({"file_contents": file_bytes_str} if file_bytes_str else {})
                }

            data.append({
                "content": chunk,
                "metadata": metadata,
                "embedding": embedding
            })

        # Batch insert for performance (100 chunks at a time)
        BATCH_SIZE = 100
        total_batches = (len(data) - 1) // BATCH_SIZE + 1

        for i in range(0, len(data), BATCH_SIZE):
            batch = data[i:i + BATCH_SIZE]
            supabase.table("documents").insert(batch).execute()
            if total_batches > 1:
                print(f"  Inserted batch {i//BATCH_SIZE + 1}/{total_batches} ({len(batch)} chunks)")
    except Exception as e:
        print(f"Error inserting/updating document chunks: {e}")

def insert_or_update_document_metadata(file_id: str, file_name: str, schema: Dict[str, Any]) -> None:
    """
    Insert or update a record in the document_metadata table.

    Args:
        file_id: The file ID (path or GDrive ID)
        file_name: The name of the file
        schema: Schema data - for CSV: column names, for Markdown: frontmatter dict
    """
    try:
        # Check if the record already exists
        response = supabase.table("document_metadata").select("*").eq("file_id", file_id).execute()

        # Prepare the data
        data = {
            "file_id": file_id,
            "file_name": file_name,
            "schema": schema  # JSONB - stores frontmatter for markdown or columns for CSV
        }

        if response.data and len(response.data) > 0:
            # Update existing record
            supabase.table("document_metadata").update(data).eq("file_id", file_id).execute()
            print(f"Updated metadata for file '{file_name}' (ID: {file_id})")
        else:
            # Insert new record
            supabase.table("document_metadata").insert(data).execute()
            print(f"Inserted metadata for file '{file_name}' (ID: {file_id})")
    except Exception as e:
        print(f"Error inserting/updating document metadata: {e}")

def insert_document_rows(file_id: str, rows: List[Dict[str, Any]]) -> None:
    """
    Insert rows into the document_rows table.

    Used for:
    - CSV/Excel: Each row of tabular data
    - Markdown: Each metric from key_metrics (optional)

    Args:
        file_id: The file ID (references document_metadata.file_id)
        rows: List of row data as dictionaries
    """
    try:
        # First, delete any existing rows for this file
        supabase.table("document_rows").delete().eq("dataset_id", file_id).execute()
        print(f"Deleted existing rows for file ID: {file_id}")

        # Insert new rows
        for row in rows:
            supabase.table("document_rows").insert({
                "dataset_id": file_id,
                "row_data": row
            }).execute()
        print(f"Inserted {len(rows)} rows for file ID: {file_id}")
    except Exception as e:
        print(f"Error inserting document rows: {e}")

def process_file_for_rag(file_content: bytes, text: str, file_id: str, file_url: str,
                        file_title: str, mime_type: str = None, config: Dict[str, Any] = None) -> None:
    """
    Process a file for the RAG pipeline - delete existing records and insert new ones.

    Uses section-aware chunking for markdown files with frontmatter,
    falls back to regular chunking for other file types.

    Args:
        file_content: The binary content of the file
        text: The text content extracted from the file (may be unused if frontmatter extraction happens)
        file_id: The Google Drive file ID
        file_url: The URL to access the file
        file_title: The title of the file
        mime_type: Mime type of the file
        config: Configuration for things like the chunk size and overlap
    """
    try:
        # First, delete any existing records for this file
        delete_document_by_file_id(file_id)

        # Prepare schema data for document_metadata table
        schema_data = {}
        metrics_rows = []

        # Get text processing settings from config
        text_processing = config.get('text_processing', {})
        chunk_size = text_processing.get('default_chunk_size', 1500)  # Updated default
        chunk_overlap = text_processing.get('default_chunk_overlap', 200)  # Updated default

        # Check if this is a markdown file that might have frontmatter
        is_markdown = (
            mime_type and
            ('text/markdown' in mime_type or
             (mime_type.startswith('text/') and file_title.endswith('.md')))
        )

        chunks_list = []
        embeddings = []
        enriched_metadata_list = None

        if is_markdown:
            print(f"Detected markdown file, using section-aware chunking for: {file_title}")

            # Extract text and metadata (frontmatter)
            body_text, frontmatter = extract_text_and_metadata(
                file_content, mime_type, file_title, config
            )

            # Create section-aware chunks ONCE
            enriched_chunks = create_section_aware_chunks(
                text=body_text,
                frontmatter=frontmatter,
                max_chunk_size=chunk_size,
                file_id=file_id,
                file_url=file_url,
                file_title=file_title
            )

            # Extract section names (unique, ordered)
            section_names = list(dict.fromkeys([chunk.section_name for chunk in enriched_chunks]))

            # Store frontmatter + sections in document_metadata.schema
            if frontmatter:
                schema_data = {
                    "type": "markdown",
                    "frontmatter": frontmatter.model_dump(),
                    "sections": section_names,
                    "total_sections": len(section_names)
                }

                # Extract metrics as rows for document_rows
                if frontmatter.key_metrics:
                    if isinstance(frontmatter.key_metrics, dict):
                        # Store each metric as a row
                        for key, value in frontmatter.key_metrics.items():
                            if isinstance(value, dict):
                                # Nested metric (type/value/unit structure)
                                metrics_rows.append({
                                    "metric_name": key,
                                    **value
                                })
                            else:
                                # Simple key-value metric
                                metrics_rows.append({
                                    "metric_name": key,
                                    "value": value
                                })
                    elif isinstance(frontmatter.key_metrics, list):
                        # Already a list of metric objects
                        metrics_rows = frontmatter.key_metrics
            else:
                schema_data = {
                    "type": "markdown",
                    "frontmatter": None,
                    "sections": section_names,
                    "total_sections": len(section_names)
                }

            # Extract text chunks and MINIMAL metadata (no frontmatter duplication)
            chunks_list = [chunk.content for chunk in enriched_chunks]
            enriched_metadata_list = [
                {
                    "file_id": chunk.metadata["file_id"],
                    "file_title": chunk.metadata["file_title"],
                    "chunk_index": chunk.metadata["chunk_index"],
                    "section": chunk.metadata["section"],
                    "section_chunk_index": chunk.metadata["section_chunk_index"],
                    "chunk_role": chunk.metadata["chunk_role"]
                }
                for chunk in enriched_chunks
            ]

            print(f"Created {len(chunks_list)} section-aware chunks (frontmatter: {'Yes' if frontmatter else 'No'})")

        else:
            # Use regular chunking for non-markdown files
            print(f"Using regular chunking for: {file_title}")
            chunks_list = chunk_text(text, chunk_size=chunk_size, overlap=chunk_overlap)

            # Set basic schema for non-markdown files
            if not schema_data:
                schema_data = {"type": "text", "mime_type": mime_type}

        # Insert document metadata (YAML frontmatter or CSV schema)
        if schema_data:
            insert_or_update_document_metadata(file_id, file_title, schema_data)

        # Insert metrics/rows if present
        if metrics_rows:
            insert_document_rows(file_id, metrics_rows)

        if not chunks_list:
            print(f"No chunks were created for file '{file_title}' (ID: {file_id})")
            return False

        # Create embeddings for the chunks
        print(f"Generating embeddings for {len(chunks_list)} chunks...")
        embeddings = create_embeddings(chunks_list)

        # For images, don't chunk the image, just store the title for RAG and include the binary in the metadata
        if mime_type and mime_type.startswith("image"):
            insert_document_chunks(chunks_list, embeddings, file_id, file_url, file_title, mime_type, file_content)
            return True

        # Insert the chunks with their embeddings (with enriched metadata if available)
        print(f"Inserting {len(chunks_list)} chunks into database...")
        insert_document_chunks(
            chunks_list,
            embeddings,
            file_id,
            file_url,
            file_title,
            mime_type,
            enriched_metadata=enriched_metadata_list
        )

        print(f"SUCCESS: Processed {file_title}: {len(chunks_list)} chunks inserted")
        return True
    except Exception as e:
        traceback.print_exc()
        print(f"Error processing file for RAG: {e}")
        return False
