# DRF NumPy Runtime Service

A Django REST Framework service that executes user-submitted Python code with NumPy support against test cases stored in AWS S3. This service is designed for coding challenge platforms and educational systems that need secure code execution with scientific computing capabilities.

## Features

- **Secure Code Execution**: Execute user Python code in isolated environments
- **NumPy Integration**: Full support for NumPy scientific computing operations
- **AWS S3 Integration**: Store and retrieve user solutions and test cases from S3
- **Test Case Management**: Support for both submission tests and custom tests
- **REST API**: Clean and simple RESTful endpoints
- **Health Monitoring**: Built-in health check endpoints
- **Comprehensive Logging**: Detailed logging for monitoring and debugging

## Architecture

```
users/{user_id}/problems/{problem_name}/
├── solution.py          # User's solution code
├── test_cases.json      # Official test cases for submissions
└── custom_tests.json    # Custom test cases for practice
```

## API Endpoints

### Health Check
```http
GET /health/
```
Returns service health status and version information.

### Execute Code
```http
POST /execute
Content-Type: application/json

{
  "user_id": "user123",
  "problem_name": "array_sum",
  "is_submission": false
}
```

Executes the user's solution against test cases and returns detailed results.

## Installation

### Prerequisites
- Python 3.8+
- AWS Account with S3 access
- Virtual environment (recommended)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd drf-numpy-runtime-svc
   ```

2. **Create virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   
   Copy `.env.example` to `.env` and configure:
   ```bash
   cp .env.example .env
   ```
   
   Update the following variables in `.env`:
   ```env
   # AWS Configuration
   S3_BUCKET_NAME=your-s3-bucket-name
   S3_REGION=your-aws-region
   AWS_ACCESS_KEY_ID=your-aws-access-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret-key
   
   # Application Configuration
   DEBUG=True
   APP_NAME=DRF NumPy Runtime Service
   APP_VERSION=1.0.0
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

The service will be available at `http://localhost:8000`

## Usage Examples

### Health Check
```bash
curl http://localhost:8000/health/
```

Response:
```json
{
  "status": "OK",
  "platform": "DRF NumPy Runtime Service",
  "version": "1.0.0"
}
```

### Execute Code
```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "problem_name": "array_sum",
    "is_submission": false
  }'
```

Response:
```json
{
  "user_id": "user123",
  "problem_name": "array_sum",
  "is_submission": false,
  "total_tests": 3,
  "passed": 2,
  "failed": 1,
  "results": [
    {
      "test_number": 1,
      "status": "passed",
      "test": "print(sum_array([1, 2, 3]))",
      "expected": "6",
      "actual": "6"
    },
    {
      "test_number": 2,
      "status": "failed",
      "test": "print(sum_array([]))",
      "expected": "0",
      "actual": "None"
    }
  ]
}
```

## File Structure

```
drf-numpy-runtime-svc/
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── .env.example                # Environment variables template
├── core/                       # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── Api/                        # Main API application
│   ├── views.py                # API endpoints
│   ├── urls.py                 # URL routing
│   ├── config.py               # Configuration settings
│   └── services/
│       └── s3.py               # AWS S3 service integration
└── env/                        # Virtual environment (auto-generated)
```

## Test File Formats

### solution.py
```python
import numpy as np

def sum_array(arr):
    """Calculate sum of array elements"""
    if not arr:
        return 0
    return np.sum(arr)
```

### test_cases.json (for submissions)
```json
[
  {
    "test": "print(sum_array([1, 2, 3, 4]))",
    "expected_output": "10"
  },
  {
    "test": "print(sum_array([]))",
    "expected_output": "0"
  }
]
```

### custom_tests.json (for practice)
```json
{
  "customTests": [
    {
      "test": "print(sum_array([5, 5]))",
      "expected_output": "10"
    }
  ]
}
```

## Production Deployment

### Using Gunicorn
```bash
gunicorn core.wsgi:application --bind 0.0.0.0:8000
```

### Environment Variables
Set `DEBUG=False` and configure proper logging for production use.

### AWS S3 Permissions
Ensure your AWS credentials have the following S3 permissions:
- `s3:GetObject`
- `s3:ListBucket`

## Security Considerations

- **Code Isolation**: User code runs in isolated Python namespaces
- **Resource Limits**: Consider implementing execution timeouts
- **Input Validation**: All inputs are validated before processing
- **Error Handling**: Comprehensive error handling prevents information leakage

## Dependencies

- **Django 4.2.23**: Web framework
- **Django REST Framework 3.14.0**: REST API functionality
- **NumPy 2.0.0+**: Scientific computing support
- **Boto3**: AWS SDK for S3 operations
- **python-decouple**: Environment configuration management
- **Gunicorn**: Production WSGI server