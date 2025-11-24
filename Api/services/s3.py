from decouple import config #type: ignore
import boto3 #type: ignore
from botocore.exceptions import NoCredentialsError, PartialCredentialsError #type: ignore
import logging #type: ignore

# Set up logging
logger = logging.getLogger(__name__)

# Load AWS configurations from environment variables
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", default="")
AWS_S3_BUCKET_NAME = config("AWS_S3_BUCKET_NAME", default="my-bucket-cloud-test")


class S3NumpyService:
    
    # Constructor
    def __init__(self, bucket_name: str = AWS_S3_BUCKET_NAME):
        if not bucket_name:
            raise ValueError("Bucket name must be provided.")
        self.bucket_name = bucket_name
        self.s3_client = self.init_s3_client()
        
    
    # Initialize S3 Client
    def init_s3_client(self):
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )
            logger.info("S3 client initialized successfully.")
            return s3_client
        
        except (NoCredentialsError, PartialCredentialsError) as e:
            logger.error(f"AWS credentials are not properly configured: {e}")
            self.s3_client = None
            return None
    
    # Get user folder prefix
    def get_user_folder_prefix(self, user_id: str, problemName: str) -> str:
        """Get S3 prefix for user's workspace folder."""
        workspace = f"users/{user_id}/problems/{problemName}/"
        return workspace
    
    # List user files
    def list_user_files(self, user_id: str, workspace: str):
        """List files in the user's workspace folder."""
        prefix = workspace
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            files = [obj['Key'] for obj in response.get('Contents', [])]
            return files
        
        except Exception as e:
            logger.error(f"Error listing files for user {user_id}: {e}")
            return []
    