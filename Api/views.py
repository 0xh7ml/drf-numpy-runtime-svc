from django.shortcuts import render #type: ignore
from rest_framework.decorators import api_view #type: ignore
from rest_framework.response import Response #type: ignore
from rest_framework import status #type: ignore
import logging #type: ignore
import json
import sys
from io import StringIO
import traceback

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

# Execute Code Endpoint
@api_view(['POST'])
def execute_code(request):
    """
    Execute user's solution.py against test cases.
    Request body: { user_id, problem_name, is_submission }
    """
    user_id = request.data.get("user_id")
    problem_name = request.data.get("problem_name")
    is_submission = request.data.get("is_submission", False)

    # Validate required fields
    if not user_id:
        return Response(
            {"error": "user_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not problem_name:
        return Response(
            {"error": "problem_name is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Fetch solution.py from S3
        solution_code = s3_service.get_solution_file(user_id, problem_name)
        if not solution_code:
            return Response(
                {"error": "solution.py not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Fetch appropriate test file based on is_submission
        if is_submission:
            test_content = s3_service.get_test_cases(user_id, problem_name)
            if not test_content:
                return Response(
                    {"error": "test_cases.json not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            test_content = s3_service.get_custom_tests(user_id, problem_name)
            if not test_content:
                return Response(
                    {"error": "custom_tests.json not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

        # Parse test content
        try:
            test_data = json.loads(test_content)
            # Handle custom tests format with "customTests" key
            if not is_submission and isinstance(test_data, dict) and "customTests" in test_data:
                tests = test_data["customTests"]
            else:
                tests = test_data
        except json.JSONDecodeError as e:
            return Response(
                {"error": f"Invalid JSON in test file: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Execute tests
        results = []
        passed_count = 0
        failed_count = 0

        for idx, test_case in enumerate(tests):
            test_code = test_case.get("test")
            expected_output = test_case.get("expected_output", "").strip()

            if not test_code:
                results.append({
                    "test_number": idx + 1,
                    "status": "error",
                    "error": "Test code is missing"
                })
                failed_count += 1
                continue

            # Execute the test
            try:
                # Create isolated namespace for execution
                # Import numpy to make it available for user code
                import numpy as np
                namespace = {'np': np, 'numpy': np}

                # Capture stdout
                old_stdout = sys.stdout
                sys.stdout = StringIO()

                try:
                    # Execute solution code first to define functions
                    exec(solution_code, namespace)

                    # Execute test code
                    exec(test_code, namespace)

                    # Get captured output
                    actual_output = sys.stdout.getvalue().strip()

                finally:
                    # Restore stdout
                    sys.stdout = old_stdout

                # Compare outputs
                if actual_output == expected_output:
                    results.append({
                        "test_number": idx + 1,
                        "status": "passed",
                        "test": test_code,
                        "expected": expected_output,
                        "actual": actual_output
                    })
                    passed_count += 1
                else:
                    results.append({
                        "test_number": idx + 1,
                        "status": "failed",
                        "test": test_code,
                        "expected": expected_output,
                        "actual": actual_output
                    })
                    failed_count += 1

            except Exception as e:
                # Restore stdout in case of error
                sys.stdout = old_stdout

                results.append({
                    "test_number": idx + 1,
                    "status": "error",
                    "test": test_code,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })
                failed_count += 1

        # Prepare response
        response_data = {
            "user_id": user_id,
            "problem_name": problem_name,
            "is_submission": is_submission,
            "total_tests": len(tests),
            "passed": passed_count,
            "failed": failed_count,
            "results": results
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error executing code for user {user_id}, problem {problem_name}: {e}")
        return Response(
            {
                "error": "Internal server error during code execution",
                "details": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )