from django.apps import AppConfig

from . import __version__


class SquatBotConfig(AppConfig):
    name = 'squatbot'
    label = 'squatbot'

    verbose_name = f"SquatBot v{__version__}"
