from hermes.automate import EnvoyerMessageSmtpActionNoeud
from hermes.source import Source
from hermes.logger import logger

from .models import Automate


class SourceLogger(Source):

    def __init__(self):
        super().__init__('', '')

        self._destinataire = 'admin@localhost'
        self._raw_content = '\n'.join([InteroperabiliteLogger.formatter.format(el) for el in InteroperabiliteLogger.handler_debug.buffer]).encode('utf-8')

    @property
    def raw(self):
        return self._raw_content

    @property
    def nom_fichier(self):
        return 'interoperabilite.log'

    @property
    def destinataire(self):
        return self._destinataire

    @destinataire.setter
    def destinataire(self, nouveau_destinataire):
        self._destinataire = nouveau_destinataire

    @property
    def titre(self):
        return 'Traces de votre interopérabilité'


class NotificationIncident:

    EMAIL_HOST = None
    EMAIL_PORT = None
    EMAIL_TIMEOUT = None
    EMAIL_USE_TLS = None
    EMAIL_HOST_USER = None
    EMAIL_HOST_PASSWORD = None
    EMAIL_FROM = None

    EMAIL_TO_DEFAULT = None

    @staticmethod
    def init_app(app):
        """
        :param flask.Flask app:
        """
        NotificationIncident.EMAIL_HOST = app.config.get('EMAIL_HOST', 'localhost')
        NotificationIncident.EMAIL_PORT = app.config.get('EMAIL_PORT', 25)
        NotificationIncident.EMAIL_TIMEOUT = app.config.get('EMAIL_TIMEOUT', 10)
        NotificationIncident.EMAIL_USE_TLS = app.config.get('EMAIL_USE_TLS', False)
        NotificationIncident.EMAIL_HOST_USER = app.config.get('EMAIL_HOST_USER', None)
        NotificationIncident.EMAIL_HOST_PASSWORD = app.config.get('EMAIL_HOST_PASSWORD', None)
        NotificationIncident.EMAIL_FROM = app.config.get('EMAIL_FROM', None)

        NotificationIncident.EMAIL_TO_DEFAULT = app.config.get('INCIDENT_NOTIFIABLE', None)

    @staticmethod
    def prevenir(automate, source, titre, description):
        """
        :param Automate automate:
        :param Source source:
        :param str titre:
        :param str description:
        :return:
        """

        if NotificationIncident.EMAIL_HOST is None or NotificationIncident.EMAIL_PORT is None or NotificationIncident.EMAIL_USE_TLS is None:
            return False

        ma_fausse_source = SourceLogger()
        ma_fausse_source.destinataire = NotificationIncident.EMAIL_FROM

        if automate is None:
            return False

        mon_action = EnvoyerMessageSmtpActionNoeud(
            "Envoyer une notification d'erreur au(x) responsable(s) de l'automate",
            str(NotificationIncident.EMAIL_TO_DEFAULT) + ((',' + automate.responsable_derniere_modification.email) if automate.responsable_derniere_modification is not None else ''),
            titre,
            description,
            hote_smtp=NotificationIncident.EMAIL_HOST,
            port_smtp=NotificationIncident.EMAIL_PORT,
            nom_utilisateur=NotificationIncident.EMAIL_HOST_USER,
            mot_de_passe=NotificationIncident.EMAIL_HOST_PASSWORD,
            enable_tls=NotificationIncident.EMAIL_USE_TLS,
            pj_source=True,
            source_pj_complementaire=source,
            force_keep_template=True
        )

        return mon_action.je_realise(ma_fausse_source)
