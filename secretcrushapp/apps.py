from django.apps import AppConfig


class SecretcrushappConfig(AppConfig):
    name = 'secretcrushapp'

    def ready(self):
        from secretcrushapp import stablizer
        stablizer.startStablizerThread()
