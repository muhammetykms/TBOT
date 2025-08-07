from django.apps import AppConfig


class MumlarConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mumlar'

    def ready(self):
        import mumlar.signals  # Signal dosyasını burada içe aktarın
