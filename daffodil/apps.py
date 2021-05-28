from django.apps import AppConfig

class DaffodilAppConfig(AppConfig):
    name = 'daffodil'

    def ready(self):
        # from . import monkey_patches
        pass