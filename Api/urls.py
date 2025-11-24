from django.urls import path, include #type: ignore
from .views import *
urlpatterns = [
   path('', read_root, name='api-root'),
   path('health/', read_health, name='api-health'),
   path('s3/files', list_s3_user_files, name='s3-user-files'),
]
