# tiny_erp/apps.py

from django.apps import AppConfig
from .tiny_api import import_products

class TinyErpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tiny_erp'

    def ready(self):
        import_products()