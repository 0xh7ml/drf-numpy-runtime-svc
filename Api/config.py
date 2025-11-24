"""Configuration settings for the API service."""

from decouple import config #type: ignore


S3_BUCKET_NAME = config('S3_BUCKET_NAME')
S3_REGION = config('S3_REGION')
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')


APP_NAME = config('APP_NAME', default='My DRF App')
APP_VERSION = config('APP_VERSION', default='v1.0.0')

