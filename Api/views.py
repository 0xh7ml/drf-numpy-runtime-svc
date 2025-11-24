from django.shortcuts import render #type: ignore
from rest_framework.decorators import api_view #type: ignore
from rest_framework.response import Response #type: ignore
from rest_framework import status #type: ignore
import logging #type: ignore

from .config import APP_NAME, APP_VERSION
from .services.s3 import S3NumpyService


# Initialize S3 Numpy Service
s3_service = S3NumpyService()

# set up logging
logger = logging.getLogger(__name__)


# Create your views here.

# Root Endpoint
@api_view(['GET'])
def read_root(request):
    return Response({"message": "Welcome to the API root."})

# Health Check Endpoint
@api_view(['GET'])
def read_health(request):
    return Response(
        {
            "status": "OK",
            "platform": APP_NAME,
            "version": APP_VERSION,
        }
    )

# List S3 User Problems Folder Endpoint
@api_view(['POST'])
def list_s3_user_files(request):
    user_id = request.data.get("user_id")
    problem_name = request.data.get("problem_name")
    
    if not user_id:
        return Response(
            {"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    
    if not problem_name:
        return Response(
            {"error": "problem_name is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get workspace prefix
    workspace = s3_service.get_user_folder_prefix(user_id, problem_name)
    
    if not workspace:
        return Response({"error": "workspace is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    files = s3_service.list_user_files(user_id, workspace)
    return Response(
        {
        "user_id": user_id, 
        "files": files
        },
    status=status.HTTP_200_OK)