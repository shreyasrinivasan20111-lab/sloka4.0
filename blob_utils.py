"""
Vercel Blob Storage utilities for file uploads
"""
import httpx
import os
from typing import Optional

VERCEL_BLOB_TOKEN = os.getenv("BLOB_READ_WRITE_TOKEN")
VERCEL_BLOB_BASE_URL = "https://blob.vercel-storage.com"

async def upload_file_to_blob(file_content: bytes, filename: str, content_type: str) -> Optional[str]:
    """
    Upload a file to Vercel Blob Storage
    Returns the URL of the uploaded file or None if failed
    """
    if not VERCEL_BLOB_TOKEN:
        print("Error: BLOB_READ_WRITE_TOKEN not configured")
        return None
    
    try:
        headers = {
            "Authorization": f"Bearer {VERCEL_BLOB_TOKEN}",
        }
        
        # Use the put endpoint for Vercel Blob
        url = f"{VERCEL_BLOB_BASE_URL}/{filename}"
        
        async with httpx.AsyncClient() as client:
            response = await client.put(
                url,
                content=file_content,
                headers={
                    **headers,
                    "Content-Type": content_type,
                    "x-content-type": content_type,
                }
            )
            
            if response.status_code in [200, 201]:
                # Vercel Blob returns the URL in the response
                return response.json().get("url") or url
            else:
                print(f"Blob upload failed: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        print(f"Error uploading to blob: {e}")
        return None

def is_allowed_file_type(filename: str, allowed_extensions: set) -> bool:
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def is_allowed_audio_file(filename: str) -> bool:
    """Check if file is an allowed audio type"""
    allowed_audio = {'mp3', 'wav', 'ogg', 'm4a', 'aac', 'flac'}
    return is_allowed_file_type(filename, allowed_audio)

def is_allowed_document_file(filename: str) -> bool:
    """Check if file is an allowed document type"""
    allowed_docs = {'pdf', 'doc', 'docx', 'txt', 'md', 'ppt', 'pptx'}
    return is_allowed_file_type(filename, allowed_docs)

def get_content_type(filename: str) -> str:
    """Get content type based on file extension"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    content_types = {
        # Audio files
        'mp3': 'audio/mpeg',
        'wav': 'audio/wav',
        'ogg': 'audio/ogg',
        'm4a': 'audio/mp4',
        'aac': 'audio/aac',
        'flac': 'audio/flac',
        
        # Document files
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'txt': 'text/plain',
        'md': 'text/markdown',
        'ppt': 'application/vnd.ms-powerpoint',
        'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    }
    
    return content_types.get(ext, 'application/octet-stream')
