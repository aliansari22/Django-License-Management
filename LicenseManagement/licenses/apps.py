from django.apps import AppConfig

class LicensesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "licenses"

    def ready(self):
        from .scheduler import start_scheduler
        start_scheduler()
