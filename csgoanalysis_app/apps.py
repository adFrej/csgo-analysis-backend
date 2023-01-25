from django.apps import AppConfig
from django.conf import settings
import os
import logging
# import warnings
# warnings.filterwarnings("ignore")

logging.basicConfig(level=os.environ.get("LOGLEVEL", settings.LOG_LEVEL),
                    format='%(asctime)s - %(name)s - [%(levelname)s]: %(message)s')
logging.captureWarnings(True)


class CsgoanalysisAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'csgoanalysis_app'
