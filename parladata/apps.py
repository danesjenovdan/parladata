from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class ParladataConfig(AppConfig):
    name = "parladata"

    def ready(self):
        import parladata.signals
