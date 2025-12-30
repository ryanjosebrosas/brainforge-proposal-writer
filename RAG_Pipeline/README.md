# RAG Pipeline (Google Drive & Local Files)

This RAG (Retrieval Augmented Generation) pipeline processes files from either Google Drive or a local directory. It automatically extracts text content, generates embeddings, and stores this information in a Supabase database with PGVector support, enabling semantic search and retrieval for your applications.

## Features

- **Dual Data Source Support:**
    - Monitors Google Drive for file changes (creation, updates, deletion) in a specified folder or entire drive.
    - Monitors a local directory for file changes (creation, updates, deletion).
- **Versatile File Processing:** Processes various document types including PDFs, text documents, HTML, CSVs, and more (see Supported File Types).
- **Automated Text Extraction & Chunking:** Extracts text content and intelligently splits it into manageable chunks (default: 400 characters, configurable).
- **Embedding Generation:** Creates embeddings using OpenAI's embedding model (configurable via `LLM_API_KEY`).
- **Vector Storage:** Stores content chunks and their embeddings in a Supabase database with PGVector for efficient similarity search.
- **Automatic Sync:** Ensures the database reflects file deletions from the source.

## Requirements

- Python 3.11+
- Supabase account with a PGVector-enabled database.
- Tables created from the `sql/` files (alongside the `RAG_Pipeline` folder)
- OpenAI API key.
- **For Google Drive Pipeline:** Google Drive API credentials.

## Installation

1.  **Clone the repository** (if not already done).

2.  **Navigate to the RAG Pipeline directory:**
    ```bash
    cd RAG_Pipeline
    ```

3.  **Create and activate a virtual environment:**
    It's highly recommended to use a virtual environment to manage dependencies.
    ```bash
    # Create the virtual environment (e.g., named 'venv')
    python -m venv venv

    # Activate the virtual environment
    # On Windows (PowerShell/CMD):
    # venv\Scripts\activate
    # On macOS/Linux (bash/zsh):
    # source venv/bin/activate
    ```

4.  **Install dependencies:**
    With the virtual environment activated, install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Set up environment variables:**
    Create a `.env` file in the **project root directory** (i.e., one level above the `RAG_Pipeline` directory, so `../.env` from your current location if you are inside `RAG_Pipeline`). The scripts are configured to look for it there.
    ```env
    # ../.env
    EMBEDDING_MODEL_NAME=your_embedding_model_choice
    EMBEDDING_BASE_URL=your_provider_base_url
    EMBEDDING_API_KEY=your_provider_api_key
    SUPABASE_URL=your_supabase_url
    SUPABASE_SERVICE_KEY=your_supabase_service_key
    ```

6.  **For Google Drive Pipeline - Google Drive API Setup:**
    - Go to the [Google Cloud Console](https://console.cloud.google.com/).
    - Create a new project or select an existing one.
    - Enable the Google Drive API.
    - Create OAuth 2.0 credentials (Desktop application).
    - Download the credentials JSON file. By default, the pipeline expects this file to be named `credentials.json` and located in the `Google_Drive/` directory (relative to `RAG_Pipeline`, i.e., `RAG_Pipeline/Google_Drive/credentials.json`). You can specify a different path using the `--credentials` argument.
    - The first time you run the Google Drive pipeline, it will prompt you to authorize access via a web browser. A `token.json` file will be created in the `Google_Drive/` directory (or the path specified by `--token`) to store your authorization.

## Usage

Ensure your virtual environment is activated and you are in the `RAG_Pipeline` directory.

The pipeline can be run in two modes: for Google Drive or for Local Files.

### 1. Google Drive Pipeline

This mode watches a Google Drive folder (or your entire Drive) for changes.

**Command (run from the `RAG_Pipeline` directory):**
```bash
python Google_Drive/main.py [OPTIONS]
```

**Arguments:**
-   `--credentials FILE_PATH`: Path to Google Drive API credentials file.
    (Default: `Google_Drive/credentials.json`)
-   `--token FILE_PATH`: Path to Google Drive API token file.
    (Default: `Google_Drive/token.json`)
-   `--config FILE_PATH`: Path to the configuration JSON file for the Google Drive pipeline.
    (Default: `Google_Drive/config.json`)
-   `--interval SECONDS`: Interval in seconds between checks for changes.
    (Default: 60)
-   `--folder-id FOLDER_ID`: ID of the specific Google Drive folder to watch (and its subfolders). If not provided, it watches the entire Drive.
    (Default: None)

**Examples (run from the `RAG_Pipeline` directory):**
```bash
# Watch all of Google Drive with 30-second intervals, using default paths
python Google_Drive/main.py --interval 30

# Watch a specific Google Drive folder
python Google_Drive/main.py --folder-id "your_google_drive_folder_id"

# Use custom paths for credentials and config (paths relative to RAG_Pipeline)
python Google_Drive/main.py --credentials "./custom_creds/gdrive_creds.json" --config "./configs/drive_settings.json"
```

### 2. Local Files Pipeline

This mode watches a specified local directory for changes.

**Command (run from the `RAG_Pipeline` directory):**
```bash
python Local_Files/main.py [OPTIONS]
```

**Arguments:**
-   `--config FILE_PATH`: Path to the configuration JSON file for the Local Files pipeline.
    (Default: `Local_Files/config.json`)
-   `--directory DIR_PATH`: Path to the local directory to watch for files. This path can be absolute or relative to the `RAG_Pipeline` directory.
    (Default: None - **This argument is required**)
-   `--interval SECONDS`: Interval in seconds between checks for changes.
    (Default: 60)

**Examples (run from the `RAG_Pipeline` directory):**
```bash
# Watch the 'data/my_documents' directory (relative to RAG_Pipeline, e.g., RAG_Pipeline/data/my_documents)
python Local_Files/main.py --directory "data/my_documents"

# Watch a specific absolute local directory with a 120-second interval
python Local_Files/main.py --directory "/mnt/shared_data/project_files" --interval 120

# Use a custom config file (path relative to RAG_Pipeline)
python Local_Files/main.py --directory "./docs_to_process" --config "./configs/local_settings.json"
```

## Configuration Files (`config.json`)

Each pipeline (`Google_Drive` and `Local_Files`) has its own `config.json` file located within its respective subdirectory inside `RAG_Pipeline` (e.g., `RAG_Pipeline/Google_Drive/config.json`, `RAG_Pipeline/Local_Files/config.json`). When running scripts from within `RAG_Pipeline`, these paths become `Google_Drive/config.json` and `Local_Files/config.json` respectively. These files allow you to customize:
-   `supported_mime_types`: A list of MIME types the pipeline will attempt to process.
-   `text_processing`:
    -   `default_chunk_size`: The target size for text chunks.
    -   `default_chunk_overlap`: The overlap between text chunks.
-   Module-specific settings:
    -   For Google Drive: `export_mime_types` (how Google Workspace files are converted), `watch_folder_id` (can be overridden by CLI, default in `Google_Drive/config.json`), `last_check_time` (managed by the script).
    -   For Local Files: `watch_directory` (can be overridden by CLI, default in `Local_Files/config.json`), `last_check_time` (managed by the script).

## Architecture

### Async-First Design

The RAG pipeline uses **asynchronous operations** for all database and I/O tasks, providing significant performance improvements:

- **Non-blocking I/O**: Database operations, file downloads, and embedding generation run concurrently
- **Batch Processing**: Inserts up to 100 document chunks per database operation (vs. 1 at a time)
- **5-10x Faster**: Large document sets process dramatically faster than synchronous alternatives
- **Resilient**: Automatic retry logic with exponential backoff for transient failures

**Key Components:**
- `async_db_handler.py`: Async Supabase operations with batch inserts
- `metadata_parser.py`: YAML frontmatter extraction for case studies
- `schemas.py`: Pydantic models for type-safe data validation

### Performance Expectations

| Operation | Sync (Old) | Async (New) | Improvement |
|-----------|------------|-------------|-------------|
| 1 case study (5 pages) | ~60 seconds | ~10-15 seconds | **4-6x faster** |
| 50 case studies | ~50 minutes | ~8-12 minutes | **5x faster** |
| Batch insert | 1 chunk/operation | 100 chunks/operation | **100x fewer DB calls** |

## Database Schema

The pipeline uses a `documents` table in your Supabase database with the following columns:

-   `id` (UUID PRIMARY KEY or SERIAL PRIMARY KEY): Unique identifier for the chunk.
-   `content` (TEXT): The text content of the processed chunk.
-   `metadata` (JSONB): Contains comprehensive information about the source file:
    - **Standard fields**: `file_id`, `file_url`, `file_title`, `mime_type`, `chunk_index`
    - **Case study fields** (from YAML frontmatter): `title`, `client`, `industry`, `project_type`, `technologies_used`, `key_metrics`, `function`, `project_status`
-   `embedding` (VECTOR): The OpenAI embedding vector for the content chunk (typically 1536 dimensions).

### Metadata Fields for Filtering

The `metadata` JSONB column enables powerful filtering in RAG queries. For case studies with YAML frontmatter, the following fields are automatically extracted and stored:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `industry` | String | Business sector | "E-commerce", "Healthcare", "Home Services" |
| `project_type` | String | Project category | "AI_ML", "BI_Analytics", "Workflow_Automation" |
| `technologies_used` | Array | Tech stack | `["Python", "FastAPI", "OpenAI"]` |
| `client` | String | Client organization | "ABC Home & Commercial" |
| `function` | String | Business function | "Customer Support", "Analytics" |
| `key_metrics` | Object | Quantifiable outcomes | `{"error_reduction": 90, "time_saved": 50}` |

**Query Example:**
```sql
-- Find all AI/ML projects in Healthcare
SELECT * FROM documents
WHERE metadata->>'industry' = 'Healthcare'
  AND metadata->>'project_type' = 'AI_ML';

-- Find projects using specific technology
SELECT * FROM documents
WHERE metadata->'technologies_used' ? 'Python';
```

## How It Works

1.  **Initialization & Authentication:**
    -   **Google Drive:** Authenticates with the Google Drive API using provided/stored credentials and token.
    -   **Local Files:** Sets up a watcher for the specified local directory.
    -   Both connect to the Supabase database using environment variables (`SUPABASE_URL`, `SUPABASE_SERVICE_KEY`).
2.  **Periodic Monitoring:** The pipeline periodically checks the source (Google Drive or local directory) for new, updated, or deleted files based on the `interval` setting.
3.  **File Processing (for new/updated files):**
    -   The file is downloaded (from Google Drive) or read (from the local disk).
    -   Text content is extracted. For Google Workspace files, they are typically exported to a plain text or CSV format first, as defined in `Google_Drive/config.json`.
    -   The extracted text is split into smaller, manageable chunks based on the `text_processing` settings in the respective `config.json` file.
    -   OpenAI embeddings are generated for each text chunk using the model specified by `LLM_API_KEY` (and optionally `EMBEDDING_MODEL_NAME`).
    -   Any existing records for the file (if it was updated) are removed from the Supabase `documents` table to prevent duplicates.
    -   The new text chunks, their metadata, and embeddings are inserted into the `documents` table.
4.  **Deletion Handling (for deleted files):**
    -   When a file is detected as deleted from the source, all corresponding records (chunks and embeddings) for that file are removed from the Supabase `documents` table.

## Supported File Types

The pipeline supports a variety of file types. The exact list can be found and configured in the `supported_mime_types` section of the respective `config.json` files (e.g., `Google_Drive/config.json`, `Local_Files/config.json` when viewed from within the `RAG_Pipeline` directory).

Commonly supported types include:
-   **Markdown** (`text/markdown`, `.md`) - **Supports YAML frontmatter extraction** (see below)
-   PDF (`application/pdf`)
-   Plain Text (`text/plain`)
-   HTML (`text/html`)
-   CSV (`text/csv`)
-   Microsoft Excel (`application/vnd.ms-excel`, `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`)
-   Microsoft Word (`application/msword`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`) (More relevant for Local Files pipeline)
-   Google Docs, Sheets, Presentations (for Google Drive, converted as per `export_mime_types`)
-   Images (`image/png`, `image/jpg`, `image/jpeg`, `image/svg`)
    *Note: Text extraction from images (OCR) depends on the capabilities of the underlying `common/text_processor.py`. Review its implementation for details on image handling.*

## Case Study Metadata (YAML Frontmatter)

For **markdown files** (`.md`), the pipeline automatically extracts metadata from YAML frontmatter at the beginning of the file. This enables rich filtering and search capabilities in your RAG queries.

### Frontmatter Format

Add YAML frontmatter at the **very start** of your markdown case study files:

```markdown
---
title: "Project Name: Brief Description"
client: Client Organization Name
industry: Industry Sector
project_type: Project Category
technologies_used:
  - Python
  - FastAPI
  - PostgreSQL
key_metrics:
  error_reduction: 90
  time_saved: 50
function: Business Function
project_status: Ongoing
---

# Main Content Starts Here

Your case study content follows the frontmatter...
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | String | Case study title (required) |
| `client` | String | Client organization name (required) |
| `industry` | String | Industry or sector (required) |
| `project_type` | String | Category: "AI_ML", "BI_Analytics", "Workflow_Automation", etc. (required) |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `technologies_used` | Array | List of technologies/tools used |
| `key_metrics` | Object | Quantifiable outcomes (e.g., `{error_reduction: 90, cost_savings: 30000}`) |
| `function` | String | Business function (e.g., "Customer Support", "Analytics") |
| `project_status` | String | Current status (e.g., "Ongoing", "Completed") |

### Example: Real Case Study

```markdown
---
title: "Andi: The AI Agent Revolutionizing ABC Home's Call Center"
client: ABC Home & Commercial
industry: Home Services
project_type: Workflow_Automation
technologies_used:
  - Python
  - FastAPI
  - OpenAI
  - Twilio
function: Customer Support
project_status: Ongoing
key_metrics:
  call_handling_automation: 85
  customer_satisfaction: 92
---

# Andi: The AI Agent Revolutionizing ABC Home's Call Center

ABC Home & Commercial Services implemented an AI-powered call center agent...
```

### Benefits

- **Automatic Extraction**: Pipeline parses frontmatter during ingestion
- **Metadata Enrichment**: Fields stored in `metadata` JSONB column
- **Advanced Filtering**: Query by industry, technology, project type
- **Graceful Fallback**: Files without frontmatter still process normally

## Error Handling & Reliability

### Automatic Retry Logic

The pipeline includes **automatic retry with exponential backoff** for resilience against transient failures:

- **3 retry attempts** for database operations
- **Exponential backoff**: 2 seconds → 4 seconds → 8 seconds
- **Applies to**: Batch inserts, file processing, metadata updates

**Example:**
```
Attempt 1: Network timeout → Retry in 2 seconds
Attempt 2: Connection refused → Retry in 4 seconds
Attempt 3: Success! ✓
```

### Error Scenarios Handled

| Error Type | Behavior | User Action |
|------------|----------|-------------|
| Transient network failure | Auto-retry 3 times | None - handles automatically |
| Invalid YAML frontmatter | Log warning, process without metadata | Check frontmatter syntax |
| Missing required fields | Validation error, skip metadata | Add required fields to frontmatter |
| Empty file | Skip processing, log warning | Remove or fix empty file |
| Malformed PDF | Text extraction fails, log error | Check PDF file integrity |

### Logging

The pipeline logs all operations for debugging:

- **Start of operations**: "Starting process_file_for_rag_async for file_id: X"
- **Batch operations**: "Inserting batch 1/5 (100 chunks)"
- **Completions**: "Successfully processed file_id: X in 1500ms"
- **Errors**: "Error in delete_document_by_file_id_async for file_id X: timeout"

Check console output or logs for detailed operation traces.
