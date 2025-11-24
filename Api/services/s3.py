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

    # Get file content from S3
    def get_file_content(self, file_key: str) -> str:
        """Get content of a file from S3."""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            content = response['Body'].read().decode('utf-8')
            logger.info(f"Successfully fetched file: {file_key}")
            return content

        except Exception as e:
            logger.error(f"Error fetching file {file_key}: {e}")
            return None

    # Get solution file
    def get_solution_file(self, user_id: str, problem_name: str) -> str:
        """Get solution.py content from S3."""
        workspace = self.get_user_folder_prefix(user_id, problem_name)
        solution_key = f"{workspace}solution.py"
        return self.get_file_content(solution_key)

    # Get test cases file
    def get_test_cases(self, user_id: str, problem_name: str) -> str:
        """Get test_cases.json content from S3."""
        workspace = self.get_user_folder_prefix(user_id, problem_name)
        test_cases_key = f"{workspace}test_cases.json"
        return self.get_file_content(test_cases_key)

    # Get custom tests file
    def get_custom_tests(self, user_id: str, problem_name: str) -> str:
        """Get custom_tests.json content from S3."""
        workspace = self.get_user_folder_prefix(user_id, problem_name)
        custom_tests_key = f"{workspace}custom_tests.json"
        return self.get_file_content(custom_tests_key)
    