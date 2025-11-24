from django.urls import path, include #type: ignore
from .views import *
urlpatterns = [
   path('', read_root, name='api-root'),
   path('health/', read_health, name='api-health'),
   path('execute', execute_code, name='execute-code'),
]
