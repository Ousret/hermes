from .app import app
from hermes.session import Session
from hermes.logger import logger, __path__

logger.info('Chargement du dossiers contenant les configurations YAML')
configurations_chargees = Session.charger(__path__+'/../configurations')
logger.info('Les fichiers de configuration suivant ont été chargées: "{}"', str(configurations_chargees))
