"""
Supabase Storage Integration

This module provides file storage functionality using Supabase Storage.
"""

import mimetypes
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Union
from uuid import uuid4

from supabase import Client
from storage3.utils import StorageException

from app.infrastructure.external.supabase.client import get_supabase_client
from app.utils.logging import get_logger

logger = get_logger(__name__)


class SupabaseStorageManager:
    """Supabase Storage manager for file operations."""
    
    def __init__(
        self,
        client: Optional[Client] = None,
        default_bucket: str = "connet-files"
    ):
        self.client = client or get_supabase_client()
        self.default_bucket = default_bucket
    
    async def create_bucket(
        self,
        bucket_name: str,
        public: bool = False,
        file_size_limit: Optional[int] = None,
        allowed_mime_types: Optional[List[str]] = None
    ) -> bool:
        """Create a new storage bucket."""
        try:
            options = {
                "public": public,
            }
            
            if file_size_limit:
                options["fileSizeLimit"] = file_size_limit
            
            if allowed_mime_types:
                options["allowedMimeTypes"] = allowed_mime_types
            
            self.client.storage.create_bucket(bucket_name, options)
            logger.info(f"Created storage bucket: {bucket_name}")
            return True
            
        except StorageException as e:
            logger.error(f"Failed to create bucket {bucket_name}: {e}")
            return False
    
    async def upload_file(
        self,
        file_content: Union[bytes, BytesIO],
        file_path: str,
        bucket: Optional[str] = None,
        content_type: Optional[str] = None,
        upsert: bool = False
    ) -> Optional[str]:
        """Upload file to Supabase Storage."""
        try:
            bucket_name = bucket or self.default_bucket
            
            # Auto-detect content type if not provided
            if not content_type:
                content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
            
            # Upload file
            response = self.client.storage.from_(bucket_name).upload(
                path=file_path,
                file=file_content,
                file_options={
                    "content-type": content_type,
                    "upsert": upsert
                }
            )
            
            if response:
                logger.info(f"File uploaded successfully: {file_path}")
                return self.get_public_url(file_path, bucket_name)
            
            return None
            
        except StorageException as e:
            logger.error(f"Failed to upload file {file_path}: {e}")
            return None
    
    async def download_file(
        self,
        file_path: str,
        bucket: Optional[str] = None
    ) -> Optional[bytes]:
        """Download file from Supabase Storage."""
        try:
            bucket_name = bucket or self.default_bucket
            
            response = self.client.storage.from_(bucket_name).download(file_path)
            
            if response:
                logger.info(f"File downloaded successfully: {file_path}")
                return response
            
            return None
            
        except StorageException as e:
            logger.error(f"Failed to download file {file_path}: {e}")
            return None
    
    async def delete_file(
        self,
        file_path: str,
        bucket: Optional[str] = None
    ) -> bool:
        """Delete file from Supabase Storage."""
        try:
            bucket_name = bucket or self.default_bucket
            
            response = self.client.storage.from_(bucket_name).remove([file_path])
            
            if response:
                logger.info(f"File deleted successfully: {file_path}")
                return True
            
            return False
            
        except StorageException as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False
    
    async def list_files(
        self,
        folder_path: str = "",
        bucket: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """List files in a bucket folder."""
        try:
            bucket_name = bucket or self.default_bucket
            
            response = self.client.storage.from_(bucket_name).list(
                path=folder_path,
                options={
                    "limit": limit,
                    "offset": offset
                }
            )
            
            return response or []
            
        except StorageException as e:
            logger.error(f"Failed to list files in {folder_path}: {e}")
            return []
    
    def get_public_url(
        self,
        file_path: str,
        bucket: Optional[str] = None,
        expires_in: Optional[int] = None
    ) -> str:
        """Get public URL for a file."""
        bucket_name = bucket or self.default_bucket
        
        if expires_in:
            # Create signed URL with expiration
            response = self.client.storage.from_(bucket_name).create_signed_url(
                file_path,
                expires_in
            )
            return response.get("signedURL", "")
        else:
            # Get public URL
            response = self.client.storage.from_(bucket_name).get_public_url(file_path)
            return response
    
    async def create_signed_upload_url(
        self,
        file_path: str,
        bucket: Optional[str] = None,
        expires_in: int = 3600
    ) -> Optional[Dict]:
        """Create signed URL for file upload."""
        try:
            bucket_name = bucket or self.default_bucket
            
            response = self.client.storage.from_(bucket_name).create_signed_upload_url(
                file_path
            )
            
            return response
            
        except StorageException as e:
            logger.error(f"Failed to create signed upload URL: {e}")
            return None
    
    async def move_file(
        self,
        from_path: str,
        to_path: str,
        bucket: Optional[str] = None
    ) -> bool:
        """Move/rename file in storage."""
        try:
            bucket_name = bucket or self.default_bucket
            
            response = self.client.storage.from_(bucket_name).move(from_path, to_path)
            
            if response:
                logger.info(f"File moved from {from_path} to {to_path}")
                return True
            
            return False
            
        except StorageException as e:
            logger.error(f"Failed to move file from {from_path} to {to_path}: {e}")
            return False
    
    async def get_file_info(
        self,
        file_path: str,
        bucket: Optional[str] = None
    ) -> Optional[Dict]:
        """Get file metadata."""
        try:
            bucket_name = bucket or self.default_bucket
            
            # List the specific file to get its info
            files = await self.list_files(
                folder_path=str(Path(file_path).parent),
                bucket=bucket_name,
                limit=1000
            )
            
            # Find the specific file
            file_name = Path(file_path).name
            for file_info in files:
                if file_info.get("name") == file_name:
                    return file_info
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {e}")
            return None
    
    def generate_unique_file_path(
        self,
        original_filename: str,
        folder: str = "uploads"
    ) -> str:
        """Generate unique file path to avoid conflicts."""
        file_extension = Path(original_filename).suffix
        unique_id = str(uuid4())
        filename = f"{unique_id}{file_extension}"
        
        return f"{folder}/{filename}" if folder else filename


# Global instance
_storage_manager: Optional[SupabaseStorageManager] = None


def get_supabase_storage_manager() -> SupabaseStorageManager:
    """Get global Supabase storage manager instance."""
    global _storage_manager
    
    if _storage_manager is None:
        _storage_manager = SupabaseStorageManager()
    
    return _storage_manager