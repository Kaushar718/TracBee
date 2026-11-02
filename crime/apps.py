from django.apps import AppConfig

class CrimeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crime'

    def ready(self):
        from . import signals
