from django.urls import path, include #type: ignore

urlpatterns = [
    path('', include('Api.urls'))
]
