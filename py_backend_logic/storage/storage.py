import os
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# S3 Configuration
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://minio:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "cv-documents")
USE_MOCK_S3 = os.getenv("USE_MOCK_S3", "true").lower() == "true"

class S3Storage:
    """
    A class to handle S3 storage operations with support for toggling between
    mock S3 (MinIO) and real AWS S3.
    """
    
    def __init__(self):
        """
        Initialize the S3 client based on configuration.
        """
        self.endpoint_url = S3_ENDPOINT if USE_MOCK_S3 else None
        self.bucket_name = S3_BUCKET_NAME
        
        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            config=Config(signature_version='s3v4'),
            region_name='us-east-1'  # Default region, can be changed
        )
        
        # Create bucket if it doesn't exist (for MinIO)
        if USE_MOCK_S3:
            self._ensure_bucket_exists()
            logger.info(f"Using mock S3 storage at {self.endpoint_url}")
        else:
            logger.info("Using AWS S3 storage")
    
    def _ensure_bucket_exists(self):
        """
        Ensure the configured bucket exists, creating it if necessary.
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket {self.bucket_name} already exists")
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code')
            if error_code == '404':
                # Bucket doesn't exist, create it
                self.s3_client.create_bucket(Bucket=self.bucket_name)
                logger.info(f"Created bucket {self.bucket_name}")
            else:
                logger.error(f"Error checking bucket: {str(e)}")
                raise
    
    def upload_file(self, file_path, object_name=None):
        """
        Upload a file to S3 bucket.
        
        Args:
            file_path (str): Path to the file to upload
            object_name (str, optional): S3 object name. If not specified, file_path's basename is used
            
        Returns:
            bool: True if file was uploaded, else False
        """
        if object_name is None:
            object_name = os.path.basename(file_path)
            
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, object_name)
            logger.info(f"Uploaded {file_path} to {self.bucket_name}/{object_name}")
            return True
        except ClientError as e:
            logger.error(f"Error uploading file: {str(e)}")
            return False
    
    def upload_fileobj(self, file_obj, object_name):
        """
        Upload a file-like object to S3 bucket.
        
        Args:
            file_obj: File-like object to upload
            object_name (str): S3 object name
            
        Returns:
            bool: True if file was uploaded, else False
        """
        try:
            self.s3_client.upload_fileobj(file_obj, self.bucket_name, object_name)
            logger.info(f"Uploaded file object to {self.bucket_name}/{object_name}")
            return True
        except ClientError as e:
            logger.error(f"Error uploading file object: {str(e)}")
            return False
    
    def download_file(self, object_name, file_path):
        """
        Download a file from S3 bucket.
        
        Args:
            object_name (str): S3 object name
            file_path (str): Path where the file will be downloaded
            
        Returns:
            bool: True if file was downloaded, else False
        """
        try:
            self.s3_client.download_file(self.bucket_name, object_name, file_path)
            logger.info(f"Downloaded {self.bucket_name}/{object_name} to {file_path}")
            return True
        except ClientError as e:
            logger.error(f"Error downloading file: {str(e)}")
            return False
    
    def get_object(self, object_name):
        """
        Get an object from S3 bucket.
        
        Args:
            object_name (str): S3 object name
            
        Returns:
            dict: Object data and metadata
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=object_name)
            return response
        except ClientError as e:
            logger.error(f"Error getting object: {str(e)}")
            return None
    
    def list_objects(self, prefix=""):
        """
        List objects in the S3 bucket.
        
        Args:
            prefix (str, optional): Filter objects by prefix
            
        Returns:
            list: List of object information dictionaries
        """
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            return response.get('Contents', [])
        except ClientError as e:
            logger.error(f"Error listing objects: {str(e)}")
            return []
    
    def delete_object(self, object_name):
        """
        Delete an object from S3 bucket.
        
        Args:
            object_name (str): S3 object name
            
        Returns:
            bool: True if object was deleted, else False
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_name)
            logger.info(f"Deleted {self.bucket_name}/{object_name}")
            return True
        except ClientError as e:
            logger.error(f"Error deleting object: {str(e)}")
            return False
    
    def generate_presigned_url(self, object_name, expiration=3600):
        """
        Generate a presigned URL for an object.
        
        Args:
            object_name (str): S3 object name
            expiration (int, optional): Time in seconds for the URL to remain valid
            
        Returns:
            str: Presigned URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            return None

# Create a singleton instance
s3_storage = S3Storage()