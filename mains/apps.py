from django.apps import AppConfig


class MainsConfig(AppConfig):
    name = 'mains'

    def ready(self):
        import mains.signals