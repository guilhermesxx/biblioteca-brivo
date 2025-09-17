from django.urls import path
from .debug_views import simple_create_user, test_endpoint

urlpatterns = [
    path('create/', simple_create_user, name='simple-create-user'),
    path('test/', test_endpoint, name='test-endpoint'),
]