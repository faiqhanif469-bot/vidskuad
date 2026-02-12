"""
Storage Service - Supports both Local and DigitalOcean Spaces
"""

import boto3
from botocore.client import Config as BotoConfig
from app.config import settings
import os
from pathlib import Path
import zipfile
import shutil


class StorageService:
    """Handle file uploads to Local Storage or DigitalOcean Spaces"""
    
    def __init__(self):
        self.use_local = settings.USE_LOCAL_STORAGE
        
        if not self.use_local:
            self.client = boto3.client(
                's3',
                region_name=settings.DO_SPACES_REGION,
                endpoint_url=settings.DO_SPACES_ENDPOINT,
                aws_access_key_id=settings.DO_SPACES_KEY,
                aws_secret_access_key=settings.DO_SPACES_SECRET,
                config=BotoConfig(signature_version='s3v4')
            )
            self.bucket = settings.DO_SPACES_BUCKET
        else:
            # Create local storage directory
            self.local_path = Path(settings.LOCAL_STORAGE_PATH)
            self.local_path.mkdir(parents=True, exist_ok=True)
    
    def upload_file(self, file_path: str, object_name: str) -> str:
        """
        Upload a single file to Storage
        
        Args:
            file_path: Local file path
            object_name: Object name/path
        
        Returns:
            Public URL of uploaded file
        """
        try:
            if self.use_local:
                # Copy to local storage
                dest_path = self.local_path / object_name
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest_path)
                
                # Return local URL
                return f"/api/files/{object_name}"
            else:
                # Upload to Spaces
                self.client.upload_file(
                    file_path,
                    self.bucket,
                    object_name,
                    ExtraArgs={'ACL': 'public-read'}
                )
                
                url = f"{settings.DO_SPACES_ENDPOINT}/{self.bucket}/{object_name}"
                return url
        
        except Exception as e:
            print(f"Error uploading file: {e}")
            raise
    
    def upload_folder(self, folder_path: str, prefix: str) -> str:
        """
        Upload entire folder as ZIP to Storage
        
        Args:
            folder_path: Local folder path
            prefix: Prefix/path (user_id/job_id/type)
        
        Returns:
            Public URL of uploaded ZIP
        """
        try:
            # Create ZIP file
            zip_path = f"{folder_path}.zip"
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, folder_path)
                        zipf.write(file_path, arcname)
            
            # Upload ZIP
            object_name = f"{prefix}.zip"
            url = self.upload_file(zip_path, object_name)
            
            # Clean up local ZIP
            os.remove(zip_path)
            
            return url
        
        except Exception as e:
            print(f"Error uploading folder: {e}")
            raise
    
    def delete_file(self, object_name: str):
        """Delete file from Storage"""
        try:
            if self.use_local:
                file_path = self.local_path / object_name
                if file_path.exists():
                    file_path.unlink()
            else:
                self.client.delete_object(
                    Bucket=self.bucket,
                    Key=object_name
                )
        except Exception as e:
            print(f"Error deleting file: {e}")
    
    def delete_folder(self, prefix: str):
        """Delete all files with prefix"""
        try:
            if self.use_local:
                folder_path = self.local_path / prefix
                if folder_path.exists():
                    shutil.rmtree(folder_path)
            else:
                # List objects
                response = self.client.list_objects_v2(
                    Bucket=self.bucket,
                    Prefix=prefix
                )
                
                if 'Contents' not in response:
                    return
                
                # Delete objects
                objects = [{'Key': obj['Key']} for obj in response['Contents']]
                
                self.client.delete_objects(
                    Bucket=self.bucket,
                    Delete={'Objects': objects}
                )
        
        except Exception as e:
            print(f"Error deleting folder: {e}")
    
    def generate_presigned_url(self, object_name: str, expiration: int = 3600) -> str:
        """
        Generate presigned URL for private file
        
        Args:
            object_name: Object name in Spaces
            expiration: URL expiration in seconds
        
        Returns:
            Presigned URL
        """
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': object_name
                },
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            print(f"Error generating presigned URL: {e}")
            raise
