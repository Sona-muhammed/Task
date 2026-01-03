import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student.settings')
django.setup()

from django.core.management import call_command

# Run makemigrations
print("Creating migrations...")
call_command('makemigrations')

# Run migrate
print("Applying migrations...")
call_command('migrate')

print("Migrations completed successfully!")