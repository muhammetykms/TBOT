import os
import glob
import django
from django.conf import settings

# Django ortamını ayarla
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tbotmumarayuz.settings')  # Proje adını doğru gir!
django.setup()

# INSTALLED_APPS içindeki tüm özel uygulamaları bul
APPS = [app for app in settings.INSTALLED_APPS if not app.startswith("django.")]

def delete_migrations():
    for app in APPS:
        migration_path = os.path.join(app, "migrations")

        if os.path.exists(migration_path):
            print(f"🧹 {app} uygulamasının migration dosyaları temizleniyor...")

            # `__init__.py` hariç tüm `.py` dosyalarını sil
            for file in glob.glob(os.path.join(migration_path, "*.py")):
                if file.endswith("__init__.py"):
                    continue
                os.remove(file)
                print(f"   ❌ Silindi: {file}")

            # `__pycache__` klasörünü de temizle
            pycache_path = os.path.join(migration_path, "__pycache__")
            if os.path.exists(pycache_path):
                for file in glob.glob(os.path.join(pycache_path, "*.pyc")):
                    os.remove(file)
                    print(f"   ❌ Silindi: {file}")

    print("✅ Tüm migration dosyaları temizlendi!")

if __name__ == "__main__":
    delete_migrations()
