from django.apps import AppConfig


class StratejilerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stratejiler'

    def ready(self):
        # Import the signals module to ensure the signals are registered
        import stratejiler.signals
