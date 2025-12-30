import os
import io
import csv
import tempfile
from typing import List, Dict, Any, Tuple, Optional
import pypdf
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

from .metadata_parser import parse_case_study
from .schemas import CaseStudyFrontmatter

# Load environment variables from the project root .env file
# Get the path to the project root (4_Pydantic_AI_Agent directory)
project_root = Path(__file__).resolve().parent.parent.parent
dotenv_path = project_root / '.env'

# Force override of existing environment variables
load_dotenv(dotenv_path, override=True)

# Initialize OpenAI client
api_key = os.getenv("EMBEDDING_API_KEY", "") or "ollama"
openai_client = OpenAI(api_key=api_key, base_url=os.getenv("EMBEDDING_BASE_URL"))

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 0) -> List[str]:
    """
    Split text into chunks of specified size with optional overlap.
    
    Args:
        text: The text to chunk
        chunk_size: Size of each chunk in characters
        overlap: Number of overlapping characters between chunks
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    # Clean the text
    text = text.replace('\r', '')
    
    # Split text into chunks
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        if chunk:  # Only add non-empty chunks
            chunks.append(chunk)
    
    return chunks

def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        file_content: Binary content of the PDF file
        
    Returns:
        Extracted text from the PDF
    """
    # Create a temporary file to store the PDF content
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        temp_file.write(file_content)
        temp_file_path = temp_file.name
    
    try:
        # Open the PDF file
        with open(temp_file_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            text = ""
            
            # Extract text from each page
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        
        return text
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def extract_text_from_file(file_content: bytes, mime_type: str, file_name: str, config: Dict[str, Any] = None) -> str:
    """
    Extract text from a file based on its MIME type.
    
    Args:
        file_content: Binary content of the file
        mime_type: MIME type of the file
        config: Configuration dictionary with supported_mime_types
        
    Returns:
        Extracted text from the file
    """
    supported_mime_types = []
    if config and 'supported_mime_types' in config:
        supported_mime_types = config['supported_mime_types']
    
    if 'application/pdf' in mime_type:
        return extract_text_from_pdf(file_content)
    elif mime_type.startswith('image'):
        return file_name
    elif config and any(mime_type.startswith(t) for t in supported_mime_types):
        return file_content.decode('utf-8', errors='replace')
    else:
        # For unsupported file types, just try to extract the text
        return file_content.decode('utf-8', errors='replace')

def create_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Create embeddings for a list of text chunks using OpenAI.
    
    Args:
        texts: List of text chunks to embed
        
    Returns:
        List of embedding vectors
    """
    if not texts:
        return []
    
    response = openai_client.embeddings.create(
        model=os.getenv("EMBEDDING_MODEL_CHOICE"),
        input=texts
    )
    
    # Extract the embedding vectors from the response
    embeddings = [item.embedding for item in response.data]
    
    return embeddings

def is_tabular_file(mime_type: str, config: Dict[str, Any] = None) -> bool:
    """
    Check if a file is tabular based on its MIME type.
    
    Args:
        mime_type: The MIME type of the file
        config: Optional configuration dictionary
        
    Returns:
        bool: True if the file is tabular (CSV or Excel), False otherwise
    """
    # Default tabular MIME types if config is not provided
    tabular_mime_types = [
        'csv',
        'xlsx',
        'text/csv',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.google-apps.spreadsheet'
    ]
    
    # Use tabular_mime_types from config if available
    if config and 'tabular_mime_types' in config:
        tabular_mime_types = config['tabular_mime_types']
    
    return any(mime_type.startswith(t) for t in tabular_mime_types)

def extract_schema_from_csv(file_content: bytes) -> List[str]:
    """
    Extract column names from a CSV file.
    
    Args:
        file_content: The binary content of the CSV file
        
    Returns:
        List[str]: List of column names
    """
    try:
        # Decode the CSV content
        text_content = file_content.decode('utf-8', errors='replace')
        csv_reader = csv.reader(io.StringIO(text_content))
        # Get the header row (first row)
        header = next(csv_reader)
        return header
    except Exception as e:
        print(f"Error extracting schema from CSV: {e}")
        return []

def extract_rows_from_csv(file_content: bytes) -> List[Dict[str, Any]]:
    """
    Extract rows from a CSV file as a list of dictionaries.

    Args:
        file_content: The binary content of the CSV file

    Returns:
        List[Dict[str, Any]]: List of row data as dictionaries
    """
    try:
        # Decode the CSV content
        text_content = file_content.decode('utf-8', errors='replace')
        csv_reader = csv.DictReader(io.StringIO(text_content))
        return list(csv_reader)
    except Exception as e:
        print(f"Error extracting rows from CSV: {e}")
        return []


def extract_text_and_metadata(
    file_content: bytes,
    mime_type: str,
    file_name: str,
    config: Dict[str, Any] = None
) -> Tuple[str, Optional[CaseStudyFrontmatter]]:
    """
    Extract text content and metadata from a file.

    For markdown files, extracts YAML frontmatter. For other file types,
    just extracts text without metadata.

    Args:
        file_content: Binary content of the file
        mime_type: MIME type of the file
        file_name: Name of file for logging
        config: Configuration dictionary

    Returns:
        Tuple of (extracted_text, case_study_metadata)
        - For markdown with frontmatter: (body_text, CaseStudyFrontmatter)
        - For other files: (full_text, None)
    """
    # Check if this is a markdown file
    is_markdown = (
        'text/markdown' in mime_type or
        mime_type.startswith('text/') and file_name.endswith('.md')
    )

    if is_markdown:
        # Parse case study with frontmatter extraction
        frontmatter, body_text = parse_case_study(file_content, file_name)
        return body_text, frontmatter
    else:
        # For non-markdown, use existing text extraction
        text = extract_text_from_file(file_content, mime_type, file_name, config)
        return text, None
