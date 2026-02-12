"""
DigitalOcean Spaces Storage Service
"""

import boto3
from botocore.client import Config as BotoConfig
from app.config import settings
import os
from pathlib import Path
import zipfile


class StorageService:
    """Handle file uploads to DigitalOcean Spaces"""
    
    def __init__(self):
        self.client = boto3.client(
            's3',
            region_name=settings.DO_SPACES_REGION,
            endpoint_url=settings.DO_SPACES_ENDPOINT,
            aws_access_key_id=settings.DO_SPACES_KEY,
            aws_secret_access_key=settings.DO_SPACES_SECRET,
            config=BotoConfig(signature_version='s3v4')
        )
        self.bucket = settings.DO_SPACES_BUCKET
    
    def upload_file(self, file_path: str, object_name: str) -> str:
        """
        Upload a single file to Spaces
        
        Args:
            file_path: Local file path
            object_name: Object name in Spaces
        
        Returns:
            Public URL of uploaded file
        """
        try:
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
        Upload entire folder as ZIP to Spaces
        
        Args:
            folder_path: Local folder path
            prefix: Prefix in Spaces (user_id/job_id/type)
        
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
        """Delete file from Spaces"""
        try:
            self.client.delete_object(
                Bucket=self.bucket,
                Key=object_name
            )
        except Exception as e:
            print(f"Error deleting file: {e}")
    
    def delete_folder(self, prefix: str):
        """Delete all files with prefix"""
        try:
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
