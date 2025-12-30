"""
One-time batch ingestion script for case studies.

This script processes all files in a directory once and exits.
Use this for initial data loading instead of the continuous file watcher.
"""
import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path to import common modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.text_processor import extract_text_from_file
from common.db_handler import process_file_for_rag

def get_mime_type(file_path: str) -> str:
    """Get MIME type from file extension."""
    extension_mappings = {
        '.md': 'text/markdown',
        '.txt': 'text/plain',
        '.pdf': 'application/pdf',
        '.csv': 'text/csv',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }

    _, ext = os.path.splitext(file_path.lower())
    return extension_mappings.get(ext, 'text/plain')


def ingest_directory(directory_path: str, config: dict) -> None:
    """
    Process all files in a directory for RAG ingestion.

    Args:
        directory_path: Path to directory containing files to ingest
        config: Configuration dictionary with processing settings
    """
    directory = Path(directory_path).resolve()

    if not directory.exists():
        print(f"Error: Directory does not exist: {directory}")
        return

    print(f"\n>> Starting batch ingestion from: {directory}\n")

    # Get all files (recursively)
    files = list(directory.rglob('*'))
    files = [f for f in files if f.is_file() and not f.name.startswith('.')]

    print(f"Found {len(files)} files to process\n")

    processed = 0
    skipped = 0
    failed = 0

    for file_path in files:
        try:
            file_name = file_path.stem
            mime_type = get_mime_type(str(file_path))

            # Check if supported
            supported_types = config.get('supported_mime_types', [])
            if not any(mime_type.startswith(t) for t in supported_types):
                print(f"[SKIP] Unsupported type: {file_path.name} ({mime_type})")
                skipped += 1
                continue

            print(f"[PROC] Processing: {file_path.name}")

            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()

            # Extract text
            text = extract_text_from_file(file_content, mime_type, file_path.name, config)

            if not text:
                print(f"  [FAIL] No text extracted from {file_path.name}")
                failed += 1
                continue

            # Process for RAG
            file_id = str(file_path)
            web_view_link = f"file://{file_path}"

            success = process_file_for_rag(
                file_content=file_content,
                text=text,
                file_id=file_id,
                file_url=web_view_link,
                file_title=file_name,
                mime_type=mime_type,
                config=config
            )

            if success:
                print(f"  [OK] Successfully ingested: {file_path.name}")
                processed += 1
            else:
                print(f"  [FAIL] Failed to ingest: {file_path.name}")
                failed += 1

        except Exception as e:
            print(f"  [ERROR] Error processing {file_path.name}: {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Ingestion Summary:")
    print(f"  Processed: {processed}")
    print(f"  Skipped:   {skipped}")
    print(f"  Failed:    {failed}")
    print(f"  Total:     {len(files)}")
    print(f"{'='*60}\n")


def main():
    """Main entry point for batch ingestion."""
    parser = argparse.ArgumentParser(
        description='Batch ingest files for RAG pipeline (one-time operation)'
    )
    parser.add_argument(
        'directory',
        type=str,
        help='Directory containing files to ingest (can be relative or absolute)'
    )

    args = parser.parse_args()

    # Load config
    script_dir = Path(__file__).resolve().parent
    config_path = script_dir / 'config.json'

    try:
        import json
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"[OK] Loaded configuration from {config_path}")
    except Exception as e:
        print(f"Warning: Could not load config, using defaults: {e}")
        config = {
            "supported_mime_types": [
                "text/markdown",
                "text/plain",
                "application/pdf",
                "text/csv"
            ],
            "text_processing": {
                "default_chunk_size": 400,
                "default_chunk_overlap": 0
            }
        }

    # Ingest directory
    ingest_directory(args.directory, config)


if __name__ == "__main__":
    main()
