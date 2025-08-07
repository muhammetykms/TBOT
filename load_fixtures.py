import os
import django
from django.core.management import call_command
from django.core.management.base import CommandError

"""
Bu dosya çalıştırıldığında sırayla bütün fixtures dosyalarını yükler !!!
"""

# Django projesinin ayarlarını yükleyin
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tbotmumarayuz.settings')
django.setup()

def load_fixtures_from_directory(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            try:
                print(f"Loading {filepath}")
                call_command('loaddata', filepath)
            except CommandError as e:
                print(f"Error loading {filepath}: {e}")

if __name__ == "__main__":
    fixtures_directory = os.path.join(os.path.dirname(__file__), 'fixtures')
    load_fixtures_from_directory(fixtures_directory)
