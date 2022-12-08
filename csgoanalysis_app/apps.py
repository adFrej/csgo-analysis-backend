from django.apps import AppConfig
import os
import logging

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"),
                    format='%(asctime)s - %(name)s - [%(levelname)s]: %(message)s')


class CsgoanalysisAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'csgoanalysis_app'
