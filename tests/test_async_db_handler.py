"""
Unit tests for async_db_handler.py - Async database operations.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from RAG_Pipeline.common.async_db_handler import (
    delete_document_by_file_id_async,
    insert_document_chunks_batch,
    insert_or_update_document_metadata_async,
    insert_document_rows_async,
    process_file_for_rag_async
)
from RAG_Pipeline.common.schemas import FileMetadata, IngestionResult, CaseStudyFrontmatter


@pytest.fixture
def mock_supabase():
    """Mock async Supabase client."""
    supabase = MagicMock()

    # Mock table().delete().eq().execute() chain
    delete_mock = AsyncMock()
    delete_mock.return_value.data = []
    supabase.table.return_value.delete.return_value.eq.return_value.execute = delete_mock

    # Mock table().select().eq().execute() chain
    select_mock = AsyncMock()
    select_mock.return_value.data = []
    supabase.table.return_value.select.return_value.eq.return_value.execute = select_mock

    # Mock table().insert().execute() chain
    insert_mock = AsyncMock()
    insert_mock.return_value.data = []
    supabase.table.return_value.insert.return_value.execute = insert_mock

    # Mock table().update().eq().execute() chain
    update_mock = AsyncMock()
    update_mock.return_value.data = []
    supabase.table.return_value.update.return_value.eq.return_value.execute = update_mock

    return supabase


@pytest.fixture
def sample_file_metadata():
    """Sample FileMetadata for testing."""
    return FileMetadata(
        file_id="test_file_001",
        file_url="/path/to/test.md",
        file_title="Test Case Study",
        mime_type="text/markdown",
        source_type="local_file",
        case_study_metadata=CaseStudyFrontmatter(
            title="Test Project",
            client="Test Client",
            industry="Technology",
            project_type="AI_ML",
            technologies_used=["Python", "TensorFlow"]
        )
    )


@pytest.fixture
def sample_chunks():
    """Sample text chunks for testing."""
    return [
        "This is the first chunk of text.",
        "This is the second chunk of text.",
        "This is the third chunk of text."
    ]


@pytest.fixture
def sample_embeddings():
    """Sample embedding vectors for testing."""
    return [
        [0.1] * 1536,  # OpenAI text-embedding-3-small dimension
        [0.2] * 1536,
        [0.3] * 1536
    ]


@pytest.mark.asyncio
async def test_delete_document_by_file_id_async(mock_supabase):
    """Test async deletion of document by file_id."""
    await delete_document_by_file_id_async(mock_supabase, "test_file_001")

    # Verify delete was called for documents table
    assert mock_supabase.table.called
    assert "documents" in str(mock_supabase.table.call_args_list)


@pytest.mark.asyncio
async def test_insert_document_chunks_batch(mock_supabase, sample_file_metadata, sample_chunks, sample_embeddings):
    """Test batch insertion of document chunks."""
    chunks_inserted = await insert_document_chunks_batch(
        mock_supabase,
        sample_chunks,
        sample_embeddings,
        sample_file_metadata
    )

    assert chunks_inserted == 3
    # Verify insert was called
    assert mock_supabase.table.called


@pytest.mark.asyncio
async def test_insert_or_update_document_metadata_async(mock_supabase, sample_file_metadata):
    """Test upsert of document metadata."""
    await insert_or_update_document_metadata_async(mock_supabase, sample_file_metadata)

    # Verify select was called to check existence
    assert mock_supabase.table.called


@pytest.mark.asyncio
async def test_insert_document_rows_async(mock_supabase):
    """Test insertion of tabular rows."""
    rows = [
        {"col1": "val1", "col2": "val2"},
        {"col1": "val3", "col2": "val4"}
    ]

    rows_inserted = await insert_document_rows_async(mock_supabase, "test_file_001", rows)

    assert rows_inserted == 2


@pytest.mark.asyncio
async def test_process_file_for_rag_async_success(mock_supabase, sample_file_metadata):
    """Test full file processing workflow."""
    file_content = b"Test content for processing"
    text = "Test content for processing"
    config = {
        "text_processing": {
            "default_chunk_size": 100,
            "default_chunk_overlap": 0
        }
    }

    # Mock chunk_text and create_embeddings
    with patch('RAG_Pipeline.common.async_db_handler.chunk_text') as mock_chunk:
        with patch('RAG_Pipeline.common.async_db_handler.create_embeddings') as mock_embed:
            mock_chunk.return_value = ["chunk1", "chunk2"]
            mock_embed.return_value = [[0.1] * 1536, [0.2] * 1536]

            result = await process_file_for_rag_async(
                mock_supabase,
                file_content,
                text,
                sample_file_metadata,
                config
            )

    assert isinstance(result, IngestionResult)
    assert result.success is True
    assert result.file_id == "test_file_001"
    assert result.chunks_inserted == 2
    assert result.frontmatter_extracted is True


@pytest.mark.asyncio
async def test_process_file_for_rag_async_no_chunks(mock_supabase, sample_file_metadata):
    """Test processing when no chunks are created."""
    file_content = b""
    text = ""
    config = {"text_processing": {}}

    # Mock chunk_text to return empty list
    with patch('RAG_Pipeline.common.async_db_handler.chunk_text') as mock_chunk:
        mock_chunk.return_value = []

        result = await process_file_for_rag_async(
            mock_supabase,
            file_content,
            text,
            sample_file_metadata,
            config
        )

    assert result.success is False
    assert "No chunks created" in result.error_message
