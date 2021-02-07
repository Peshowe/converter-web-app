from django.apps import AppConfig


class ConverterConfig(AppConfig):
    name = "converter"

    def ready(self):
        # prompt the app to load the module before the first request
        from .views import converter