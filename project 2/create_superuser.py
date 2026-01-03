import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student.settings')
django.setup()

from auth_module.models import CustomUser

# Create superuser
try:
    user = CustomUser.objects.create_superuser(
        email='admin@example.com',
        username='admin',
        password='admin123'
    )
    print('Superuser created successfully')
except Exception as e:
    print(f'Error creating superuser: {e}')