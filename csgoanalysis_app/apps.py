from django.apps import AppConfig
import os
import logging
# import warnings
# warnings.filterwarnings("ignore")

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"),
                    format='%(asctime)s - %(name)s - [%(levelname)s]: %(message)s')
logging.captureWarnings(True)


class CsgoanalysisAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'csgoanalysis_app'
