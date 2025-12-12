"""
ASGI config for monglo_admin project.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monglo_admin.settings')

# Get Django ASGI application
django_asgi_app = get_asgi_application()

# Initialize Monglo
from monglo_admin.urls import initialize
import asyncio
asyncio.create_task(initialize())

application = django_asgi_app
