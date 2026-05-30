import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'twt_project.settings')
django.setup()

print(f"DEBUG: {settings.DEBUG}")
print(f"STATIC_URL: {settings.STATIC_URL}")
print(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
print(f"STATIC_ROOT: {settings.STATIC_ROOT}")

# Check if the static directory exists
for directory in settings.STATICFILES_DIRS:
    print(f"Directory {directory} exists: {os.path.exists(directory)}")
    if os.path.exists(directory):
        print(f"Contents of {directory}: {os.listdir(directory)}")
