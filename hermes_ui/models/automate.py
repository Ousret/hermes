import datetime

from hermes_ui.adminlte.models import User
from hermes_ui.models.detecteur import Detecteur
from hermes_ui.db import db
from hermes_ui.db.polymorphic import get_child_polymorphic
from copy import deepcopy
from collections import OrderedDict


from hermes.i18n import _


class Automate(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    designation = db.Column(db.String(255), nullable=False, unique=True)

    production = db.Column(db.Boolean(), nullable=False, default=False)
    notifiable = db.Column(db.Boolean(), nullable=False, default=True)

    priorite = db.Column(db.Integer(), nullable=False, default=0)

    createur_id = db.Column(db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    createur = db.relationship(User, primaryjoin="User.id==Automate.createur_id")

    date_creation = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow())
    date_modification = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow())

    responsable_derniere_modification_id = db.Column(db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    responsable_derniere_modification = db.relationship(User,
                                                        primaryjoin="User.id==Automate.responsable_derniere_modification_id")

    limite_echec_par_heure = db.Column(db.Integer(), nullable=True, default=10)
    limite_par_heure = db.Column(db.Integer(), nullable=True, default=100)

    detecteur_id = db.Column(db.Integer(), db.ForeignKey(Detecteur.id, ondelete='SET NULL'), nullable=True)
    detecteur = db.relationship(Detecteur, foreign_keys="Automate.detecteur_id", lazy='joined', backref='automates', cascade="all, save-update, delete, merge")

    actions = db.relationship('ActionNoeud', primaryjoin='ActionNoeud.automate_id==Automate.id', lazy='joined', enable_typechecks=False, cascade="all, save-update, merge, delete, delete-orphan")

    action_racine_id = db.Column(db.Integer(), db.ForeignKey('action_noeud.id', ondelete='SET NULL'), nullable=True)
    action_racine = db.relation('ActionNoeud', foreign_keys='Automate.action_racine_id', lazy='joined', enable_typechecks=False, cascade="all, save-update, merge, delete")

    def __repr__(self):
        return _('<Automate \'{automate_nom}\'>').format(automate_nom=self.designation)

    def transcription(self):
        from hermes.automate import Automate as NoModelAutomate

        automate = NoModelAutomate(
            self.designation,
            self.detecteur.transcription() if self.detecteur is not None else None
        )

        automate.action_racine = self.action_racine.transcription()

        return automate


class ActionNoeud(db.Model):
    DESCRIPTION = None
    PARAMETRES = OrderedDict({
        'designation': {
            'format': 'TEXT',
            'required': True,
            'help': _('Une courte explication de ce que votre action va réaliser')
        },
        'friendly_name': {
            'format': 'TEXT',
            'required': False,
            'help': _('Un nom simple (de variable) sans espace pour réutiliser le résultat de votre action si il y a lieu')
        }
    })

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)

    automate_id = db.Column(db.Integer(), db.ForeignKey('automate.id', ondelete='SET NULL'), nullable=True)

    designation = db.Column(db.String(255), nullable=False)

    createur_id = db.Column(db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    createur = db.relationship(User, primaryjoin="User.id==ActionNoeud.createur_id")

    date_creation = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow())
    date_modification = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow())

    responsable_derniere_modification_id = db.Column(db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    responsable_derniere_modification = db.relationship(User,
                                                        primaryjoin="User.id==ActionNoeud.responsable_derniere_modification_id")

    action_reussite_id = db.Column(db.Integer(), db.ForeignKey('action_noeud.id', ondelete='CASCADE'), nullable=True)
    action_reussite = db.relationship('ActionNoeud', foreign_keys='ActionNoeud.action_reussite_id', lazy='joined', uselist=False, enable_typechecks=False, cascade="all, save-update, merge, delete")

    action_echec_id = db.Column(db.Integer(), db.ForeignKey('action_noeud.id', ondelete='CASCADE'), nullable=True)
    action_echec = db.relation('ActionNoeud', foreign_keys='ActionNoeud.action_echec_id', lazy='joined', uselist=False, enable_typechecks=False, cascade="all, save-update, merge, delete")

    mapped_class_child = db.Column(db.String(128), nullable=True)

    friendly_name = db.Column(db.String(255), nullable=True)

    __mapper_args__ = {'polymorphic_on': mapped_class_child}

    def transcription(self):
        """
        Création d'une instance hermes.ActionNoeud depuis un db.Model hermes_ui.models.ActionNoeud
        :rtype: hermes.automate.ActionNoeud
        """
        raise NotImplemented

    def transcription_fils(self, action_noeud):
        """
        :param hermes.automate.ActionNoeud action_noeud:
        :return:
        """
        if self.action_reussite is not None:
            action_noeud.je_realise_en_cas_reussite(
                get_child_polymorphic(self.action_reussite).transcription()
            )
        if self.action_echec is not None:
            action_noeud.je_realise_en_cas_echec(
                get_child_polymorphic(self.action_echec).transcription()
            )
        return action_noeud

    @staticmethod
    def descriptifs(ma_classe=None, ancetres_parametres=None):
        """

        :param type ma_classe:
        :param dict ancetres_parametres:
        :return:
        """
        ma_liste_descriptif = list()

        if ma_classe is not None and isinstance(ma_classe, type) is False:
            return ma_liste_descriptif
        if ma_classe is None and ancetres_parametres is None:
            ancetres_parametres = deepcopy(getattr(ActionNoeud, 'PARAMETRES'))

        for my_class in ma_classe.__subclasses__() if ma_classe is not None else ActionNoeud.__subclasses__():

            parametres = deepcopy(getattr(my_class, 'PARAMETRES'))  # type: dict
            parametres.update(ancetres_parametres)

            if len(my_class.__subclasses__()) == 0:

                ma_liste_descriptif.append(
                    {
                        'type': str(my_class),
                        'description': getattr(my_class, 'DESCRIPTION'),
                        'formulaire': parametres
                    }
                )

            else:
                ma_liste_descriptif += ActionNoeud.descriptifs(my_class, ancetres_parametres=ancetres_parametres)

        return ma_liste_descriptif


class RequeteSqlActionNoeud(ActionNoeud):
    DESCRIPTION = _('Effectuer une requête de type SQL sur un serveur SGDB tel que '
                    'Oracle, MySQL, PosgreSQL, Microsoft SQL Serveur et MariaDB')
    PARAMETRES = OrderedDict({
        'hote_type_protocol': {
            'format': 'SELECT',
            'required': True,
            'help': _('Type de serveur SGDB distant'),
            'choix': ['mysql', 'mariadb', 'posgres', 'mssql', 'oracle']
        },
        'hote_ipv4': {
            'format': 'TEXT',
            'required': True,
            'help': _('Adresse IPv4 xxx.xxx.xxx.xxx de votre serveur SGDB'),
        },
        'hote_port': {
            'format': 'NUMBER',
            'required': True,
            'help': _('Port TCP à utiliser pour se connecter à votre serveur, '
                    'eg. 3306 pour MySQL, MariaDB; 5432 pour PosgreSQL; 1521 pour Oracle; etc..'),
        },
        'hote_database': {
            'format': 'TEXT',
            'required': True,
            'help': _('Nom de votre base de données sur laquelle sera executée la requête SQL'),
        },
        'requete_sql': {
            'format': 'TEXTAREA',
            'required': True,
            'help': _('Requête SQL à lancer sur votre serveur, l\'usage des variables {{ ma_variable }} '
                    'est autorisée dans la clause WHERE. Elles seront insérées de manière sécurisée. '
                    'eg. "SELECT * FROM Product WHERE name = {{ nom_produit }} LIMIT 5"'),
        },
        'nom_utilisateur': {
            'format': 'TEXT',
            'required': False,
            'help': _('Saisir le nom d\'utilisateur pour la connexion si nécessaire'),
        },
        'mot_de_passe': {
            'format': 'TEXT',
            'required': False,
            'help': _('Saisir le mot de passe associé à l\'utilisateur pour la connexion si nécessaire'),
        },
    })

    __tablename__ = 'requete_sql_action_noeud'

    id = db.Column(db.Integer, db.ForeignKey('action_noeud.id'), primary_key=True)

    hote_type_protocol = db.Column(db.Enum('mysql', 'posgres', 'mariadb', 'mssql', 'oracle'), nullable=False)
    hote_ipv4 = db.Column(db.String(255), nullable=False)
    hote_port = db.Column(db.String(255), nullable=False)
    hote_database = db.Column(db.String(255), nullable=False)

    requete_sql = db.Column(db.Text(), nullable=False)

    nom_utilisateur = db.Column(db.String(255), nullable=True)
    mot_de_passe = db.Column(db.String(255), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': str(ActionNoeud).replace('ActionNoeud', 'RequeteSqlActionNoeud'),
    }

    def transcription(self):
        """
        :rtype: gie_interoperabilite.automate.RequeteSqlActionNoeud
        """
        from hermes.automate import RequeteSqlActionNoeud as Action
        return self.transcription_fils(
            Action(
                self.designation,
                self.hote_type_protocol,
                self.hote_ipv4,
                self.hote_port,
                self.hote_database,
                self.requete_sql,
                self.nom_utilisateur,
                self.mot_de_passe,
                self.friendly_name
            )
        )


class RequeteSoapActionNoeud(ActionNoeud):
    DESCRIPTION = _('Effectuer une requête de type SOAP Webservice')
    PARAMETRES = OrderedDict({
        'url_service': {
            'format': 'TEXT',
            'required': True,
            'help': _('URL du service WDSL cible sur lequel le webservice SOAP est actif')
        },
        'methode_cible': {
            'format': 'TEXT',
            'required': True,
            'help': _('Choix de la méthode (fonction) à utiliser, la documentation du webservice doit vous le fournir'),
        },
        'form_data': {
            'format': 'JSON',
            'required': False,
            'help': _('La structure de données à fournir au webservice, il est possible que celle-ci soit vide'),
        },
        'authentification_basique_utilisateur': {
            'format': 'TEXT',
            'required': False,
            'help': _('Nom utilisateur à utiliser pour une éventuelle authentification'),
        },
        'authentification_basique_mot_de_passe': {
            'format': 'TEXT',
            'required': False,
            'help': _('Mot de passe associé à utiliser pour une éventuelle authentification'),
        },
        'proxy_http': {
            'format': 'TEXT',
            'required': False,
            'help': _('Adresse de votre proxy pour les requêtes HTTP non sécurisée'),
        },
        'proxy_https': {
            'format': 'TEXT',
            'required': False,
            'help': _('Adresse de votre proxy pour les requêtes HTTPS sécurisée'),
        },
    })

    __tablename__ = 'requete_soap_action_noeud'

    id = db.Column(db.Integer, db.ForeignKey('action_noeud.id'), primary_key=True)

    url_service = db.Column(db.String(255), nullable=False)
    methode_cible = db.Column(db.String(255), nullable=False)
    form_data = db.Column(db.Text(), nullable=False)

    authentification_basique_utilisateur = db.Column(db.String(255), nullable=True)
    authentification_basique_mot_de_passe = db.Column(db.String(255), nullable=True)

    proxy_http = db.Column(db.String(255), nullable=True)
    proxy_https = db.Column(db.String(255), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': str(ActionNoeud).replace('ActionNoeud', 'RequeteSoapActionNoeud'),
    }

    def transcription(self):
        """
        :rtype: gie_interoperabilite.automate.RequeteSoapActionNoeud
        """
        from hermes.automate import RequeteSoapActionNoeud as Action
        from json import loads
        return self.transcription_fils(
            Action(
                self.designation,
                self.url_service,
                self.methode_cible,
                loads(self.form_data) if self.form_data is not None and len(self.form_data) >= 1 else {},
                (
                    self.authentification_basique_utilisateur,
                    self.authentification_basique_mot_de_passe
                ) if self.authentification_basique_utilisateur is not None else None,
                {
                    'http': self.proxy_http,
                    'https': self.proxy_https
                } if self.proxy_http is not None else None,
                self.friendly_name
            )
        )


class RequeteHttpActionNoeud(ActionNoeud):
    DESCRIPTION = _('Effectuer une requête de type HTTP sur un serveur distant')
    PARAMETRES = OrderedDict({
        'url_dest': {
            'format': 'TEXT',
            'required': True,
            'help': _('Adresse URL du serveur HTTP distant sur laquelle la requête sera lancée')
        },
        'methode_http': {
            'format': 'SELECT',
            'required': True,
            'help': _('La méthode (ou verbe) HTTP à utiliser avec la requête, cette information peut être disponible dans votre documentation du service distant'),
            'choix': ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        },
        'form_data': {
            'format': 'JSON',
            'required': False,
            'help': _('Les données à transmettre dans votre requête HTTP'),
        },
        'authentification_basique_utilisateur': {
            'format': 'TEXT',
            'required': False,
            'help': _('Si une authentification est nécessaire par le billet d\'une authentification basique, précisez le nom utilisateur'),
        },
        'authentification_basique_mot_de_passe': {
            'format': 'TEXT',
            'required': False,
            'help': _('Si une authentification est nécessaire par le billet d\'une authentification basique, précisez le mot de passe'),
        },
        'proxy_http': {
            'format': 'TEXT',
            'required': False,
            'help': _('Si votre requête doit utiliser un proxy pour les requêtes non sécurisées, précisez l\'adresse de votre serveur mandataire HTTP'),
        },
        'proxy_https': {
            'format': 'TEXT',
            'required': False,
            'help': _('Si votre requête doit utiliser un proxy pour les requêtes sécurisées, précisez l\'adresse de votre serveur mandataire HTTP'),
        },
        'resp_code_http': {
            'format': 'NUMBER',
            'required': False,
            'help': _('Si vous attendez un code de retour HTTP spécifique pour vérifier que la requête à réussi, précisez-le'),
        },
        'verify_peer': {
            'format': 'CHECKBOX',
            'required': False,
            'help': _('Cochez cette case pour activer la vérification TLS distante, dans le doute laissez cette case cochée'),
        }
    })

    __tablename__ = 'requete_http_action_noeud'

    id = db.Column(db.Integer, db.ForeignKey('action_noeud.id'), primary_key=True)

    url_dest = db.Column(db.String(255), nullable=False)
    methode_http = db.Column(db.Enum('GET', 'POST', 'DELETE', 'PATCH', 'PUT', 'HEAD'), nullable=False)
    form_data = db.Column(db.Text(), nullable=False)

    authentification_basique_utilisateur = db.Column(db.String(255), nullable=True)
    authentification_basique_mot_de_passe = db.Column(db.String(255), nullable=True)

    proxy_http = db.Column(db.String(255), nullable=True)
    proxy_https = db.Column(db.String(255), nullable=True)

    resp_code_http = db.Column(db.Integer(), nullable=True)
    verify_peer = db.Column(db.Boolean, nullable=False, default=True)

    __mapper_args__ = {
        'polymorphic_identity': str(ActionNoeud).replace('ActionNoeud', 'RequeteHttpActionNoeud'),
    }

    def transcription(self):
        """
        :rtype: hermes.automate.RequeteHttpActionNoeud
        """
        from hermes.automate import RequeteHttpActionNoeud as ACTION
        from json import loads
        return self.transcription_fils(
            ACTION(
                self.designation,
                self.url_dest,
                self.methode_http,
                loads(self.form_data) if self.form_data is not None and len(self.form_data) >= 1 else {},
                (
                    self.authentification_basique_utilisateur,
                    self.authentification_basique_mot_de_passe
                ) if self.authentification_basique_utilisateur is not None else None,
                {
                    'http': self.proxy_http,
                    'https': self.proxy_https
                } if self.proxy_http is not None else None,
                self.resp_code_http,
                self.verify_peer,
                self.friendly_name
            )
        )


class EnvoyerMessageSmtpActionNoeud(ActionNoeud):
    DESCRIPTION = _('Ecrire un message électronique vers n-tiers via un serveur SMTP')
    PARAMETRES = OrderedDict({
        'destinataire': {
            'format': 'TEXT',
            'required': True,
            'help': _("L'adresse email du destinataire, en cas de multiple destinataire, "
                    "veuillez les séparer par une virgule.")
        },
        'sujet': {
            'format': 'TEXT',
            'required': True,
            'help': _('Le sujet de votre email transféré')
        },
        'corps': {
            'format': 'TEXTAREA',
            'required': True,
            'help': _('Le corps de votre message électronique, format HTML supporté')
        },
        'hote_smtp': {
            'format': 'TEXT',
            'required': True,
            'help': _('Votre serveur SMTP par lequel votre message transitera')
        },
        'port_smtp': {
            'format': 'NUMBER',
            'required': True,
            'help': _('Le port de votre serveur SMTP à utiliser, '
                    'soit 587 (le plus courant) ou le port 25 à titre d\'exemple')
        },
        'nom_utilisateur': {
            'format': 'TEXT',
            'required': False,
            'help': _('Le nom d\'utilisateur à utiliser avec le serveur SMTP si il y a lieu'),
        },
        'mot_de_passe': {
            'format': 'TEXT',
            'required': False,
            'help': _('Le mot de passe à utiliser avec le serveur SMTP si il y a lieu'),
        },
        'enable_tls': {
            'format': 'CHECKBOX',
            'required': False,
            'help': _('Cochez cette case pour utiliser la connexion via un port sécurisé, '
                    'dans le doute laissez cette case cochée'),
        },
        'pj_source': {
            'format': 'CHECKBOX',
            'required': False,
            'help': _('Cochez cette case pour transférer le message source en pièce jointe si la source le permet'),
        },
        'legacy_tls_support': {
            'format': 'CHECKBOX',
            'required': False,
            'help': _("Cochez cette case si votre serveur SMTP utilise des protocols obsolètes. eg. TLS inférieur à 1.2.")
        }
    })

    __tablename__ = 'envoyer_message_smtp_action_noeud'

    id = db.Column(db.Integer, db.ForeignKey('action_noeud.id'), primary_key=True)

    destinataire = db.Column(db.String(255), nullable=False)
    sujet = db.Column(db.String(255), nullable=False)
    corps = db.Column(db.Text(), nullable=False)
    hote_smtp = db.Column(db.String(255), nullable=False)
    port_smtp = db.Column(db.Integer(), nullable=False)
    nom_utilisateur = db.Column(db.String(255), nullable=True)
    mot_de_passe = db.Column(db.String(255), nullable=True)
    enable_tls = db.Column(db.Boolean(), nullable=False, default=True)
    pj_source = db.Column(db.Boolean(), nullable=False, default=True)
    legacy_tls_support = db.Column(db.Boolean(), nullable=False, default=False)

    __mapper_args__ = {
        'polymorphic_identity': str(ActionNoeud).replace('ActionNoeud', 'EnvoyerMessageSmtpActionNoeud'),
    }

    def transcription(self):
        """
        :rtype: gie_interoperabilite.automate.EnvoyerMessageSmtpActionNoeud
        """
        from hermes.automate import EnvoyerMessageSmtpActionNoeud as ACTION
        return self.transcription_fils(
            ACTION(
                self.designation,
                self.destinataire,
                self.sujet,
                self.corps,
                self.hote_smtp,
                self.port_smtp,
                self.nom_utilisateur,
                self.mot_de_passe,
                self.enable_tls,
                self.pj_source,
                self.legacy_tls_support
            )
        )


class TransfertSmtpActionNoeud(ActionNoeud):
    DESCRIPTION = _('Transferer un message électronique vers n-tiers via un serveur SMTP')
    PARAMETRES = OrderedDict({
        'destinataire': {
            'format': 'TEXT',
            'required': True,
            'help': _("L'adresse email du destinaire, en cas de multiple destinataire, "
                    "veuillez les séparer par une virgule")
        },
        'sujet': {
            'format': 'TEXT',
            'required': True,
            'help': _('Le sujet de votre email transféré')
        },
        'hote_smtp': {
            'format': 'TEXT',
            'required': True,
            'help': _('Votre serveur SMTP par lequel votre message transitera')
        },
        'port_smtp': {
            'format': 'NUMBER',
            'required': True,
            'help': _('Le port de votre serveur SMTP à utiliser, le plus fréquent 587 ou 25')
        },
        'nom_utilisateur': {
            'format': 'TEXT',
            'required': False,
            'help': _('Le nom d\'utilisateur à utiliser avec le serveur SMTP si il y a lieu'),
        },
        'mot_de_passe': {
            'format': 'TEXT',
            'required': False,
            'help': _('Le mot de passe à utiliser avec le serveur SMTP si il y a lieu'),
        },
        'enable_tls': {
            'format': 'CHECKBOX',
            'required': False,
            'help': _('Cochez cette case pour utiliser la connexion SMTP via un port sécurisé, '
                    'dans le doute laissez cette case cochée'),
        },
        'legacy_tls_support': {
            'format': 'CHECKBOX',
            'required': False,
            'help': _("Cochez cette case si votre serveur SMTP utilise des protocols obsolètes. eg. TLS inférieur à 1.2.")
        }
    })

    __tablename__ = 'transfert_smtp_action_noeud'

    id = db.Column(db.Integer, db.ForeignKey('action_noeud.id'), primary_key=True)

    destinataire = db.Column(db.String(255), nullable=False)
    sujet = db.Column(db.String(255), nullable=False)
    hote_smtp = db.Column(db.String(255), nullable=False)
    port_smtp = db.Column(db.Integer(), nullable=False)
    nom_utilisateur = db.Column(db.String(255), nullable=True)
    mot_de_passe = db.Column(db.String(255), nullable=True)
    enable_tls = db.Column(db.Boolean(), nullable=False, default=True)
    legacy_tls_support = db.Column(db.Boolean(), nullable=False, default=False)

    __mapper_args__ = {
        'polymorphic_identity': str(ActionNoeud).replace('ActionNoeud', 'TransfertSmtpActionNoeud'),
    }

    def transcription(self):
        """
        :rtype: gie_interoperabilite.automate.EnvoyerMessageSmtpActionNoeud
        """
        from hermes.automate import TransfertSmtpActionNoeud as ACTION
        return self.transcription_fils(
            ACTION(
                self.designation,
                self.destinataire,
                self.sujet,
                self.hote_smtp,
                self.port_smtp,
                self.nom_utilisateur,
                self.mot_de_passe,
                self.enable_tls
            )
        )


class ConstructionInteretActionNoeud(ActionNoeud):
    DESCRIPTION = _("Construire une variable intermédiaire")
    PARAMETRES = OrderedDict({
        'interet': {
            'format': 'JSON',
            'required': True,
            'help': _('Contruire votre objet variable intermédiaire')
        },
    })

    __tablename__ = 'construction_interet_action_noeud'

    id = db.Column(db.Integer, db.ForeignKey('action_noeud.id'), primary_key=True)

    interet = db.Column(db.Text(), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': str(ActionNoeud).replace('ActionNoeud', 'ConstructionInteretActionNoeud'),
    }

    def transcription(self):
        """
        :rtype: hermes.automate.ConstructionInteretActionNoeud
        """
        from hermes.automate import ConstructionInteretActionNoeud as ACTION
        from json import loads
        return self.transcription_fils(
            ACTION(
                self.designation,
                loads(self.interet),
                self.friendly_name
            )
        )


class ConstructionChaineCaractereSurListeActionNoeud(ActionNoeud):
    DESCRIPTION = _("Fabriquer une chaîne de caractère à partir d'une liste identifiable")
    PARAMETRES = OrderedDict({
        'variable_pattern': {
            'format': 'TEXT',
            'required': True,
            'help': _('Votre variable contenant au moins une liste identifiable tel que {{ ma_variable.0.adresse }}')
        },
        'separateur': {
            'format': 'TEXT',
            'required': True,
            'help': _('Le séparateur à mettre pendant la phase de collage')
        },
    })

    __tablename__ = 'construction_chaine_caractere_sur_liste_action_noeud'

    id = db.Column(db.Integer, db.ForeignKey('action_noeud.id'), primary_key=True)

    variable_pattern = db.Column(db.String(255), nullable=False)
    separateur = db.Column(db.String(255), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': str(ActionNoeud).replace('ActionNoeud', 'ConstructionChaineCaractereSurListeActionNoeud'),
    }

    def transcription(self):
        """
        :rtype: hermes.automate.ConstructionChaineCaractereSurListeActionNoeud
        """
        from hermes.automate import ConstructionChaineCaractereSurListeActionNoeud as ACTION
        return self.transcription_fils(
            ACTION(
                self.designation,
                self.variable_pattern,
                self.separateur,
                self.friendly_name
            )
        )


class InvitationEvenementActionNoeud(ActionNoeud):
    DESCRIPTION = _("Emettre ou mettre à jour une invitation à un évenement par message electronique")
    PARAMETRES = OrderedDict({
        'organisateur': {
            'format': 'TEXT',
            'required': True,
            'help': _('Précisez-nous qui est à l\'origine de cette invitation, nom ou adresse de messagerie')
        },
        'participants': {
            'format': 'TEXT',
            'required': True,
            'help': _("Une liste d'adresse de messagerie séparées par une virgule, "
                    "peut être précédemment construit par une autre action")
        },
        'sujet': {
            'format': 'TEXT',
            'required': True,
            'help': _("En bref, le sujet au coeur de votre invitation")
        },
        'description': {
            'format': 'TEXTAREA',
            'required': True,
            'help': _('Décrivez-nous en détails votre invitation, les enjeux, les prérequis, etc.. '
                      'Vous pouvez intégrer les mots dynamiques suivants: {organisateur}, {sujet}, {lieu} et {date_depart}.')
        },
        'lieu': {
            'format': 'TEXT',
            'required': True,
            'help': _('Le lieu où l\'invitation aura lieu')
        },
        'date_heure_depart': {
            'format': 'TEXT',
            'required': True,
            'help': _("La date et heure de début de l'évenement, "
                    "doit être facilement lisible pour un robot, format français ou anglais. "
                    "eg. '15/01/2019 15:22 GMT+02'")
        },
        'date_heure_fin': {
            'format': 'TEXT',
            'required': True,
            'help': _("La date et heure de fin de l'évenement, "
                    "doit être facilement lisible pour un robot, format français ou anglais. "
                    "eg. '20/01/2019 15:22 GMT+02'")
        },
        'est_maintenu': {
            'format': 'CHECKBOX',
            'required': False,
            'help': _("Cochez-le si l'évenement doit être maintenu")
        },

        'hote_smtp': {
            'format': 'TEXT',
            'required': True,
            'help': _('Votre serveur SMTP par lequel votre message transitera')
        },
        'port_smtp': {
            'format': 'NUMBER',
            'required': True,
            'help': _('Le port de votre serveur SMTP à utiliser, le plus fréquent 587 ou 25')
        },
        'nom_utilisateur': {
            'format': 'TEXT',
            'required': False,
            'help': _('Le nom d\'utilisateur à utiliser avec le serveur SMTP si il y a lieu'),
        },
        'mot_de_passe': {
            'format': 'TEXT',
            'required': False,
            'help': _('Le mot de passe à utiliser avec le serveur SMTP si il y a lieu'),
        },
        'enable_tls': {
            'format': 'CHECKBOX',
            'required': False,
            'help': _('Cochez cette case pour utiliser la connexion SMTP via un port sécurisé, '
                    'dans le doute laissez cette case cochée'),
        },
        'legacy_tls_support': {
            'format': 'CHECKBOX',
            'required': False,
            'help': _("Cochez cette case si votre serveur SMTP utilise des protocols obsolètes. eg. TLS inférieur à 1.2.")
        }
    })

    __tablename__ = 'invitation_evenement_action_noeud'

    id = db.Column(db.Integer, db.ForeignKey('action_noeud.id'), primary_key=True)

    organisateur = db.Column(db.String(255), nullable=False)
    participants = db.Column(db.String(255), nullable=False)
    sujet = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    lieu = db.Column(db.String(255), nullable=False)
    date_heure_depart = db.Column(db.Text(), nullable=False)
    date_heure_fin = db.Column(db.Text(), nullable=False)
    est_maintenu = db.Column(db.Boolean(), nullable=False, default=True)

    hote_smtp = db.Column(db.String(255), nullable=False)
    port_smtp = db.Column(db.String(255), nullable=False)
    nom_utilisateur = db.Column(db.String(255), nullable=False)
    mot_de_passe = db.Column(db.String(255), nullable=False)
    enable_tls = db.Column(db.Boolean(), nullable=False, default=True)
    legacy_tls_support = db.Column(db.Boolean(), nullable=False, default=False)

    __mapper_args__ = {
        'polymorphic_identity': str(ActionNoeud).replace('ActionNoeud', 'InvitationEvenementActionNoeud'),
    }

    def transcription(self):
        """
        :rtype: hermes.automate.InvitationEvenementActionNoeud
        """
        from hermes.automate import InvitationEvenementActionNoeud as Action
        return self.transcription_fils(
            Action(
                self.designation,
                self.organisateur,
                self.participants,
                self.sujet,
                self.description,
                self.lieu,
                self.date_heure_depart,
                self.date_heure_fin,
                self.est_maintenu,
                self.hote_smtp,
                self.port_smtp,
                self.nom_utilisateur,
                self.mot_de_passe,
                self.enable_tls,
                self.legacy_tls_support,
                self.friendly_name
            )
        )


class VerifierSiVariableVraiActionNoeud(ActionNoeud):
    DESCRIPTION = _("Vérifie si une variable est Vrai")
    PARAMETRES = OrderedDict({
        'variable_cible': {
            'format': 'TEXT',
            'required': True,
            'help': _('Nom de votre variable à tester à Vrai, vous pouvez utiliser le format {{ ma_varible }}')
        },
    })

    __tablename__ = 'verifier_si_variable_vrai_action_noeud'

    id = db.Column(db.Integer, db.ForeignKey('action_noeud.id'), primary_key=True)

    variable_cible = db.Column(db.String(255), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': str(ActionNoeud).replace('ActionNoeud', 'VerifierSiVariableVraiActionNoeud'),
    }

    def transcription(self):
        """
        :rtype: hermes.automate.VerifierSiVariableVraiActionNoeud
        """
        from hermes.automate import VerifierSiVariableVraiActionNoeud as Action
        return self.transcription_fils(
            Action(
                self.designation,
                self.variable_cible,
                self.friendly_name
            )
        )


class ExecutionAutomateActionNoeud(ActionNoeud):
    DESCRIPTION = _("Execution d'une routine en ce basant sur un automate existant")
    PARAMETRES = OrderedDict({
        'sous_automate_id': {
            'format': 'AUTOMATE',
            'required': True,
            'help': _("Nom de l'automate à executer sur la source. "
                    "Le résultat final est celui donnée par la dernière action. "
                    "Priere de ne pas jouer à Inception. À vos risques et périls")
        }
    })

    __tablename__ = 'execution_automate_action_noeud'

    id = db.Column(db.Integer, db.ForeignKey('action_noeud.id'), primary_key=True)

    sous_automate_id = db.Column(db.Integer(), db.ForeignKey('automate.id', ondelete='CASCADE'), nullable=False)
    sous_automate = db.relation(Automate, foreign_keys="ExecutionAutomateActionNoeud.sous_automate_id")

    __mapper_args__ = {
        'polymorphic_identity': str(ActionNoeud).replace('ActionNoeud', 'ExecutionAutomateActionNoeud'),
    }

    def transcription(self):
        """
        :rtype: hermes.automate.ExecutionAutomateActionNoeud
        """
        from hermes.automate import ExecutionAutomateActionNoeud as Action
        return self.transcription_fils(
            Action(
                self.designation,
                self.sous_automate.transcription(),
                self.friendly_name
            )
        )


class ComparaisonVariableActionNoeud(ActionNoeud):
    DESCRIPTION = _("Effectue une comparaison entre deux variables de votre choix, nombres, dates, etc..")
    PARAMETRES = OrderedDict({
        'membre_gauche_variable': {
            'format': 'TEXT',
            'required': True,
            'help': _('Membre de gauche de notre comparaison, vous pouvez utiliser le format {{ ma_varible }}')
        },
        'operande': {
            'format': 'SELECT',
            'required': True,
            'help': _("Type d'opérateur à utiliser dans le cadre de notre comparaison. "
                      "L'opérateur IN signifie SI membre_gauche_variable INCLUS DANS membre_droite_variable."),
            'choix': ['==', '>', '<', '>=', '<=', '!=', 'IN']
        },
        'membre_droite_variable': {
            'format': 'TEXT',
            'required': True,
            'help': _('Membre de gauche de notre comparaison, vous pouvez utiliser le format {{ ma_varible }}')
        },
    })

    __tablename__ = 'comparaison_variable_action_noeud'

    id = db.Column(db.Integer, db.ForeignKey('action_noeud.id'), primary_key=True)

    membre_gauche_variable = db.Column(db.String(255), nullable=False)
    operande = db.Column(db.Enum('==', '>', '<', '>=', '<=', '!='), nullable=False)
    membre_droite_variable = db.Column(db.String(255), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': str(ActionNoeud).replace('ActionNoeud', 'ComparaisonVariableActionNoeud'),
    }

    def transcription(self):
        """
        :rtype: hermes.automate.ComparaisonVariableActionNoeud
        """
        from hermes.automate import ComparaisonVariableActionNoeud as Action
        return self.transcription_fils(
            Action(
                self.designation,
                self.membre_gauche_variable,
                self.operande,
                self.membre_droite_variable,
                self.friendly_name
            )
        )


class DeplacerMailSourceActionNoeud(ActionNoeud):
    DESCRIPTION = _("Déplacer un message électronique sur un autre dossier")
    PARAMETRES = OrderedDict({
        'dossier_destination': {
            'format': 'TEXT',
            'required': True,
            'help': _('La destination dans lequel votre source sera déplacée')
        }
    })

    __tablename__ = 'deplacer_mail_source_action_noeud'

    id = db.Column(db.Integer, db.ForeignKey('action_noeud.id'), primary_key=True)

    dossier_destination = db.Column(db.String(255), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': str(ActionNoeud).replace('ActionNoeud', 'DeplacerMailSourceActionNoeud'),
    }

    def transcription(self):
        """
        :rtype: hermes.automate.DeplacerMailSourceActionNoeud
        """
        from hermes.automate import DeplacerMailSourceActionNoeud as Action
        return self.transcription_fils(
            Action(
                self.designation,
                self.dossier_destination
            )
        )


class CopierMailSourceActionNoeud(ActionNoeud):
    DESCRIPTION = _("Copier un message électronique dans un autre dossier")
    PARAMETRES = OrderedDict({
        'dossier_destination': {
            'format': 'TEXT',
            'required': True,
            'help': _('La destination dans lequel votre source sera copiée'),
        },
    })

    __tablename__ = 'copier_mail_source_action_noeud'

    id = db.Column(db.Integer, db.ForeignKey('action_noeud.id'), primary_key=True)

    dossier_destination = db.Column(db.String(255), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': str(ActionNoeud).replace('ActionNoeud', 'CopierMailSourceActionNoeud'),
    }

    def transcription(self):
        """
        :rtype: hermes.automate.CopierMailSourceActionNoeud
        """
        from hermes.automate import CopierMailSourceActionNoeud as Action
        return self.transcription_fils(
            Action(
                self.designation,
                self.dossier_destination
            )
        )


class SupprimerMailSourceActionNoeud(ActionNoeud):
    DESCRIPTION = _("Supprime un message électronique")
    PARAMETRES = OrderedDict()

    __tablename__ = 'supprimer_mail_source_action_noeud'

    id = db.Column(db.Integer, db.ForeignKey('action_noeud.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': str(ActionNoeud).replace('ActionNoeud', 'SupprimerMailSourceActionNoeud'),
    }

    def transcription(self):
        """
        :rtype: hermes.automate.SupprimerMailSourceActionNoeud
        """
        from hermes.automate import SupprimerMailSourceActionNoeud as Action
        return self.transcription_fils(
            Action(
                self.designation
            )
        )


class TransformationListeVersDictionnaireActionNoeud(ActionNoeud):
    DESCRIPTION = _("Création d'une variable intermédiaire "
                    "sachant une liste [{'cle_a': 'val_a', 'cle_b': 'val_b'}] vers {'val_a': 'val_b'}")

    PARAMETRES = OrderedDict({
        'resultat_concerne': {
            'format': 'TEXT',
            'required': True,
            'help': _('Le nom de la variable concernée par la transformation')
        },
        'champ_cle': {
            'format': 'TEXT',
            'required': True,
            'help': _('Le nom du champ clé')
        },
        'champ_valeur': {
            'format': 'TEXT',
            'required': True,
            'help': _('Le nom du champ valeur')
        },
    })

    __tablename__ = 'transformation_liste_vers_dictionnaire_action_noeud'

    id = db.Column(db.Integer, db.ForeignKey('action_noeud.id'), primary_key=True)

    resultat_concerne = db.Column(db.String(255), nullable=False)
    champ_cle = db.Column(db.String(255), nullable=False)
    champ_valeur = db.Column(db.String(255), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': str(ActionNoeud).replace('ActionNoeud', 'TransformationListeVersDictionnaireActionNoeud'),
    }

    def transcription(self):
        """
        :rtype: hermes.automate.TransformationListeVersDictionnaireActionNoeud
        """
        from hermes.automate import TransformationListeVersDictionnaireActionNoeud as Action
        return self.transcription_fils(
            Action(
                self.designation,
                self.resultat_concerne,
                self.champ_cle,
                self.champ_valeur,
                self.friendly_name
            )
        )


class ItopRequeteCoreGetActionNoeud(ActionNoeud):
    DESCRIPTION = _('Requête sur iTop opération core/get REST JSON')
    PARAMETRES = OrderedDict({
        'url_rest_itop': {
            'format': 'TEXT',
            'required': True,
            'help': _('Adresse URL du service iTop REST/JSON à utiliser pour la requête')
        },
        'auth_user': {
            'format': 'TEXT',
            'required': True,
            'help': _("Nom d'utilisateur iTop ayant la capacité d'émettre une requête rest de type core/get"),
        },
        'auth_pwd': {
            'format': 'TEXT',
            'required': True,
            'help': _("Mot de passe de votre utilisateur iTop ayant la capacité d'émettre une requête rest de type core/get"),
        },
        'requete_dql': {
            'format': 'TEXT',
            'required': True,
            'help': _('Votre requête DQL à utiliser dans le cadre de la requête'),
        },
        'output_fields': {
            'format': 'TEXT',
            'required': True,
            'help': _('Les champs à extraire des objets iTop, pour récupérer l\'ensemble des champs, mettre "*". Sinon la liste des champs séparés par une virgule.'),
        },
        'authentification_basique_utilisateur': {
            'format': 'TEXT',
            'required': False,
            'help': _('Si une authentification est nécessaire par le billet d\'une authentification basique, précisez le nom utilisateur'),
        },
        'authentification_basique_mot_de_passe': {
            'format': 'TEXT',
            'required': False,
            'help': _('Si une authentification est nécessaire par le billet d\'une authentification basique, précisez le mot de passe'),
        },
        'proxy_http': {
            'format': 'TEXT',
            'required': False,
            'help': _('Si votre requête doit utiliser un proxy pour les requêtes non sécurisées, précisez l\'adresse de votre serveur mandataire HTTP'),
        },
        'proxy_https': {
            'format': 'TEXT',
            'required': False,
            'help': _('Si votre requête doit utiliser un proxy pour les requêtes sécurisées, précisez l\'adresse de votre serveur mandataire HTTP'),
        },
        'verify_peer': {
            'format': 'CHECKBOX',
            'required': False,
            'help': _('Cochez cette case pour activer la vérification TLS distante, dans le doute laissez cette case cochée'),
        }
    })

    __tablename__ = 'itop_requete_core_get_action_noeud'

    id = db.Column(db.Integer, db.ForeignKey('action_noeud.id'), primary_key=True)

    url_rest_itop = db.Column(db.String(255), nullable=False)

    auth_user = db.Column(db.String(255), nullable=False)
    auth_pwd = db.Column(db.String(255), nullable=False)

    requete_dql = db.Column(db.Text(), nullable=False)

    output_fields = db.Column(db.Text(), nullable=False)

    authentification_basique_utilisateur = db.Column(db.String(255), nullable=True)
    authentification_basique_mot_de_passe = db.Column(db.String(255), nullable=True)

    proxy_http = db.Column(db.String(255), nullable=True)
    proxy_https = db.Column(db.String(255), nullable=True)

    verify_peer = db.Column(db.Boolean, nullable=False, default=True)

    __mapper_args__ = {
        'polymorphic_identity': str(ActionNoeud).replace('ActionNoeud', 'ItopRequeteCoreGetActionNoeud'),
    }

    def transcription(self):
        """
        :rtype: hermes.automate.RequeteHttpActionNoeud
        """
        from hermes.automate import ItopRequeteCoreGetActionNoeud as ACTION
        return self.transcription_fils(
            ACTION(
                self.designation,
                self.url_rest_itop,
                self.auth_user,
                self.auth_pwd,
                self.requete_dql,
                self.output_fields,
                (
                    self.authentification_basique_utilisateur,
                    self.authentification_basique_mot_de_passe
                ) if self.authentification_basique_utilisateur is not None else None,
                {
                    'http': self.proxy_http,
                    'https': self.proxy_https
                } if self.proxy_http is not None else None,
                self.verify_peer,
                self.friendly_name
            )
        )


class ItopRequeteCoreCreateActionNoeud(ActionNoeud):
    DESCRIPTION = _('Requête sur iTop opération core/create REST JSON')
    PARAMETRES = OrderedDict({
        'url_rest_itop': {
            'format': 'TEXT',
            'required': True,
            'help': _('Adresse URL du service iTop REST/JSON à utiliser pour la requête')
        },
        'auth_user': {
            'format': 'TEXT',
            'required': True,
            'help': _("Nom d'utilisateur iTop ayant la capacité d'émettre une requête rest de type core/create"),
        },
        'auth_pwd': {
            'format': 'TEXT',
            'required': True,
            'help': _("Mot de passe de votre utilisateur iTop ayant la capacité d'émettre une requête rest de type core/get"),
        },
        'classe_itop_cible': {
            'format': 'TEXT',
            'required': True,
            'help': _('Le nom de votre classe iTop dont la création sera nécessaire'),
        },
        'fields': {
            'format': 'JSON',
            'required': True,
            'help': _('Veuillez construire votre nouvel objet à l\'aide de cet utilitaire tel que votre schéma de données le permet'),
        },
        'output_fields': {
            'format': 'TEXT',
            'required': True,
            'help': _('Les champs à extraire des objets iTop, pour récupérer l\'ensemble des champs, mettre "*". Sinon la liste des champs séparés par une virgule.'),
        },
        'commentaire': {
            'format': 'TEXT',
            'required': True,
            'help': _('Explicitez brièvement la nature de votre création sous iTop (Journal iTop)'),
        },
        'authentification_basique_utilisateur': {
            'format': 'TEXT',
            'required': False,
            'help': _('Si une authentification est nécessaire par le billet d\'une authentification basique, précisez le nom utilisateur'),
        },
        'authentification_basique_mot_de_passe': {
            'format': 'TEXT',
            'required': False,
            'help': _('Si une authentification est nécessaire par le billet d\'une authentification basique, précisez le mot de passe'),
        },
        'proxy_http': {
            'format': 'TEXT',
            'required': False,
            'help': _('Si votre requête doit utiliser un proxy pour les requêtes non sécurisées, précisez l\'adresse de votre serveur mandataire HTTP'),
        },
        'proxy_https': {
            'format': 'TEXT',
            'required': False,
            'help': _('Si votre requête doit utiliser un proxy pour les requêtes sécurisées, précisez l\'adresse de votre serveur mandataire HTTP'),
        },
        'verify_peer': {
            'format': 'CHECKBOX',
            'required': False,
            'help': _('Cochez cette case pour activer la vérification TLS distante, dans le doute laissez cette case cochée'),
        }
    })

    __tablename__ = 'itop_requete_core_create_action_noeud'

    id = db.Column(db.Integer, db.ForeignKey('action_noeud.id'), primary_key=True)

    url_rest_itop = db.Column(db.String(255), nullable=False)

    auth_user = db.Column(db.String(255), nullable=False)
    auth_pwd = db.Column(db.String(255), nullable=False)

    classe_itop_cible = db.Column(db.String(255), nullable=False)

    fields = db.Column(db.Text(), nullable=False)

    output_fields = db.Column(db.Text(), nullable=False)
    commentaire = db.Column(db.Text(), nullable=False)

    authentification_basique_utilisateur = db.Column(db.String(255), nullable=True)
    authentification_basique_mot_de_passe = db.Column(db.String(255), nullable=True)

    proxy_http = db.Column(db.String(255), nullable=True)
    proxy_https = db.Column(db.String(255), nullable=True)

    verify_peer = db.Column(db.Boolean, nullable=False, default=True)

    __mapper_args__ = {
        'polymorphic_identity': str(ActionNoeud).replace('ActionNoeud', 'ItopRequeteCoreCreateActionNoeud'),
    }

    def transcription(self):
        """
        :rtype: hermes.automate.ItopRequeteCoreCreateActionNoeud
        """
        from hermes.automate import ItopRequeteCoreCreateActionNoeud as ACTION
        from json import loads
        return self.transcription_fils(
            ACTION(
                self.designation,
                self.url_rest_itop,
                self.auth_user,
                self.auth_pwd,
                self.classe_itop_cible,
                loads(self.fields),
                self.output_fields,
                self.commentaire,
                (
                    self.authentification_basique_utilisateur,
                    self.authentification_basique_mot_de_passe
                ) if self.authentification_basique_utilisateur is not None else None,
                {
                    'http': self.proxy_http,
                    'https': self.proxy_https
                } if self.proxy_http is not None else None,
                self.verify_peer,
                self.friendly_name
            )
        )


class ItopRequeteCoreUpdateActionNoeud(ActionNoeud):
    DESCRIPTION = _('Requête sur iTop opération core/update REST JSON')
    PARAMETRES = OrderedDict({
        'url_rest_itop': {
            'format': 'TEXT',
            'required': True,
            'help': _('Adresse URL du service iTop REST/JSON à utiliser pour la requête')
        },
        'auth_user': {
            'format': 'TEXT',
            'required': True,
            'help': _("Nom d'utilisateur iTop ayant la capacité d'émettre une requête rest de type core/get"),
        },
        'auth_pwd': {
            'format': 'TEXT',
            'required': True,
            'help': _("Mot de passe de votre utilisateur iTop ayant la capacité d'émettre une requête rest de type core/update"),
        },
        'requete_dql': {
            'format': 'TEXT',
            'required': True,
            'help': _('La requête DQL permettant d\'identifier l\'objet iTop visé'),
        },
        'fields': {
            'format': 'JSON',
            'required': True,
            'help': _('Veuillez indiquez les champs à mettre à niveau à l\'aide de cet utilitaire'),
        },
        'output_fields': {
            'format': 'TEXT',
            'required': True,
            'help': _('Les champs à extraire des objets iTop ensuite, pour récupérer l\'ensemble des champs, mettre "*". Sinon la liste des champs séparés par une virgule.'),
        },
        'commentaire': {
            'format': 'TEXT',
            'required': True,
            'help': _('Explicitez brièvement la nature de votre mise à jour iTop (Journal iTop)'),
        },
        'authentification_basique_utilisateur': {
            'format': 'TEXT',
            'required': False,
            'help': _('Si une authentification est nécessaire par le billet d\'une authentification basique, précisez le nom utilisateur'),
        },
        'authentification_basique_mot_de_passe': {
            'format': 'TEXT',
            'required': False,
            'help': _('Si une authentification est nécessaire par le billet d\'une authentification basique, précisez le mot de passe'),
        },
        'proxy_http': {
            'format': 'TEXT',
            'required': False,
            'help': _('Si votre requête doit utiliser un proxy pour les requêtes non sécurisées, précisez l\'adresse de votre serveur mandataire HTTP'),
        },
        'proxy_https': {
            'format': 'TEXT',
            'required': False,
            'help': _('Si votre requête doit utiliser un proxy pour les requêtes sécurisées, précisez l\'adresse de votre serveur mandataire HTTP'),
        },
        'verify_peer': {
            'format': 'CHECKBOX',
            'required': False,
            'help': _('Cochez cette case pour activer la vérification TLS distante, dans le doute laissez cette case cochée'),
        }
    })

    __tablename__ = 'itop_requete_core_update_action_noeud'

    id = db.Column(db.Integer, db.ForeignKey('action_noeud.id'), primary_key=True)

    url_rest_itop = db.Column(db.String(255), nullable=False)

    auth_user = db.Column(db.String(255), nullable=False)
    auth_pwd = db.Column(db.String(255), nullable=False)

    requete_dql = db.Column(db.Text(), nullable=False)
    commentaire = db.Column(db.Text(), nullable=False)

    fields = db.Column(db.Text(), nullable=False)

    output_fields = db.Column(db.Text(), nullable=False)

    authentification_basique_utilisateur = db.Column(db.String(255), nullable=True)
    authentification_basique_mot_de_passe = db.Column(db.String(255), nullable=True)

    proxy_http = db.Column(db.String(255), nullable=True)
    proxy_https = db.Column(db.String(255), nullable=True)

    verify_peer = db.Column(db.Boolean(), nullable=False, default=True)

    __mapper_args__ = {
        'polymorphic_identity': str(ActionNoeud).replace('ActionNoeud', 'ItopRequeteCoreUpdateActionNoeud'),
    }

    def transcription(self):
        """
        :rtype: hermes.automate.ItopRequeteCoreUpdateActionNoeud
        """
        from hermes.automate import ItopRequeteCoreUpdateActionNoeud as ACTION
        from json import loads
        return self.transcription_fils(
            ACTION(
                self.designation,
                self.url_rest_itop,
                self.auth_user,
                self.auth_pwd,
                self.requete_dql,
                loads(self.fields) if self.fields is not None and len(self.fields) > 1 else {},
                self.output_fields,
                self.commentaire,
                (
                    self.authentification_basique_utilisateur,
                    self.authentification_basique_mot_de_passe
                ) if self.authentification_basique_utilisateur is not None else None,
                {
                    'http': self.proxy_http,
                    'https': self.proxy_https
                } if self.proxy_http is not None else None,
                self.verify_peer,
                self.friendly_name
            )
        )


class ItopRequeteCoreApplyStimulusActionNoeud(ActionNoeud):
    DESCRIPTION = _('Requête sur iTop opération core/apply_stimulus REST JSON')
    PARAMETRES = OrderedDict({
        'url_rest_itop': {
            'format': 'TEXT',
            'required': True,
            'help': _('Adresse URL du service iTop REST/JSON à utiliser pour la requête')
        },
        'auth_user': {
            'format': 'TEXT',
            'required': True,
            'help': _("Nom d'utilisateur iTop ayant la capacité d'émettre une requête rest de type core/apply_stimulus"),
        },
        'auth_pwd': {
            'format': 'TEXT',
            'required': True,
            'help': _("Mot de passe de votre utilisateur iTop ayant la capacité d'émettre une requête rest de type core/get"),
        },
        'requete_dql': {
            'format': 'TEXT',
            'required': True,
            'help': _('Le requête DQL à effectuer pour identifier l\'objet sur lequel appliquer un stimulis iTop'),
        },
        'stimulus': {
            'format': 'TEXT',
            'required': True,
            'help': _('Veuillez indiquez le nom de votre stimulus. eg. "ev_xxxxx".'),
        },
        'fields': {
            'format': 'JSON',
            'required': False,
            'help': _('Veuillez indiquez les arguments nécessaires à votre stimulus. Laissez vide si aucun.'),
        },
        'output_fields': {
            'format': 'TEXT',
            'required': True,
            'help': _('Les champs à extraire des objets iTop ensuite, pour récupérer l\'ensemble des champs, mettre "*". Sinon la liste des champs séparés par une virgule.'),
        },
        'commentaire': {
            'format': 'TEXT',
            'required': True,
            'help': _('Explicitez brièvement la nature de votre mise à jour iTop (Journal iTop)'),
        },
        'authentification_basique_utilisateur': {
            'format': 'TEXT',
            'required': False,
            'help': _('Si une authentification est nécessaire par le billet d\'une authentification basique, précisez le nom utilisateur'),
        },
        'authentification_basique_mot_de_passe': {
            'format': 'TEXT',
            'required': False,
            'help': _('Si une authentification est nécessaire par le billet d\'une authentification basique, précisez le mot de passe'),
        },
        'proxy_http': {
            'format': 'TEXT',
            'required': False,
            'help': _('Si votre requête doit utiliser un proxy pour les requêtes non sécurisées, précisez l\'adresse de votre serveur mandataire HTTP'),
        },
        'proxy_https': {
            'format': 'TEXT',
            'required': False,
            'help': _('Si votre requête doit utiliser un proxy pour les requêtes sécurisées, précisez l\'adresse de votre serveur mandataire HTTP'),
        },
        'verify_peer': {
            'format': 'CHECKBOX',
            'required': False,
            'help': _('Cochez cette case pour activer la vérification TLS distante, dans le doute laissez cette case cochée'),
        }
    })

    __tablename__ = 'itop_requete_core_apply_stimulus_action_noeud'

    id = db.Column(db.Integer, db.ForeignKey('action_noeud.id'), primary_key=True)

    url_rest_itop = db.Column(db.String(255), nullable=False)

    auth_user = db.Column(db.String(255), nullable=False)
    auth_pwd = db.Column(db.String(255), nullable=False)

    requete_dql = db.Column(db.Text(), nullable=False)
    stimulus = db.Column(db.String(255), nullable=False)
    commentaire = db.Column(db.Text(), nullable=False)

    fields = db.Column(db.Text(), nullable=False)

    output_fields = db.Column(db.Text(), nullable=False)

    authentification_basique_utilisateur = db.Column(db.String(255), nullable=True)
    authentification_basique_mot_de_passe = db.Column(db.String(255), nullable=True)

    proxy_http = db.Column(db.String(255), nullable=True)
    proxy_https = db.Column(db.String(255), nullable=True)

    verify_peer = db.Column(db.Boolean, nullable=False, default=True)

    __mapper_args__ = {
        'polymorphic_identity': str(ActionNoeud).replace('ActionNoeud', 'ItopRequeteCoreApplyStimulusActionNoeud'),
    }

    def transcription(self):
        """
        :rtype: hermes.automate.ItopRequeteCoreApplyStimulusActionNoeud
        """
        from hermes.automate import ItopRequeteCoreApplyStimulusActionNoeud as ACTION
        from json import loads
        return self.transcription_fils(
            ACTION(
                self.designation,
                self.url_rest_itop,
                self.auth_user,
                self.auth_pwd,
                self.requete_dql,
                self.stimulus,
                loads(self.fields) if self.fields is not None and len(self.fields) > 1 else {},
                self.output_fields,
                self.commentaire,
                (
                    self.authentification_basique_utilisateur,
                    self.authentification_basique_mot_de_passe
                ) if self.authentification_basique_utilisateur is not None else None,
                {
                    'http': self.proxy_http,
                    'https': self.proxy_https
                } if self.proxy_http is not None else None,
                self.verify_peer,
                self.friendly_name
            )
        )


class ItopRequeteCoreDeleteActionNoeud(ActionNoeud):
    DESCRIPTION = 'Requête sur iTop opération core/delete REST JSON'
    PARAMETRES = OrderedDict({
        'url_rest_itop': {
            'format': 'TEXT',
            'required': True,
            'help': 'Adresse URL du service iTop REST/JSON à utiliser pour la requête'
        },
        'auth_user': {
            'format': 'TEXT',
            'required': True,
            'help': "Nom d'utilisateur iTop ayant la capacité d'émettre une requête rest core/delete",
        },
        'auth_pwd': {
            'format': 'TEXT',
            'required': True,
            'help': "Mot de passe de votre utilisateur iTop ayant la capacité d'émettre une requête rest",
        },
        'requete_dql': {
            'format': 'TEXT',
            'required': True,
            'help': 'Votre requête DQL à utiliser dans le cadre de la requête',
        },
        'commentaire': {
            'format': 'TEXT',
            'required': True,
            'help': 'Explicitez brièvement la nature de votre mise à jour iTop (Journal iTop)',
        },
        'authentification_basique_utilisateur': {
            'format': 'TEXT',
            'required': False,
            'help': 'Si une authentification est nécessaire par le billet d\'une authentification basique, précisez le nom utilisateur',
        },
        'authentification_basique_mot_de_passe': {
            'format': 'TEXT',
            'required': False,
            'help': 'Si une authentification est nécessaire par le billet d\'une authentification basique, précisez le mot de passe',
        },
        'proxy_http': {
            'format': 'TEXT',
            'required': False,
            'help': 'Si votre requête doit utiliser un proxy pour les requêtes non sécurisées, précisez l\'adresse de votre serveur mandataire HTTP',
        },
        'proxy_https': {
            'format': 'TEXT',
            'required': False,
            'help': 'Si votre requête doit utiliser un proxy pour les requêtes sécurisées, précisez l\'adresse de votre serveur mandataire HTTP',
        },
        'verify_peer': {
            'format': 'CHECKBOX',
            'required': False,
            'help': 'Cochez cette case pour activer la vérification TLS distante, dans le doute laissez cette case cochée',
        }
    })

    __tablename__ = 'itop_requete_core_delete_action_noeud'

    id = db.Column(db.Integer, db.ForeignKey('action_noeud.id'), primary_key=True)

    url_rest_itop = db.Column(db.String(255), nullable=False)

    auth_user = db.Column(db.String(255), nullable=False)
    auth_pwd = db.Column(db.String(255), nullable=False)

    requete_dql = db.Column(db.Text(), nullable=False)

    commentaire = db.Column(db.Text(), nullable=False)

    authentification_basique_utilisateur = db.Column(db.String(255), nullable=True)
    authentification_basique_mot_de_passe = db.Column(db.String(255), nullable=True)

    proxy_http = db.Column(db.String(255), nullable=True)
    proxy_https = db.Column(db.String(255), nullable=True)

    verify_peer = db.Column(db.Boolean, nullable=False, default=True)

    __mapper_args__ = {
        'polymorphic_identity': str(ActionNoeud).replace('ActionNoeud', 'ItopRequeteCoreDeleteActionNoeud'),
    }

    def transcription(self):
        """
        :rtype: hermes.automate.ItopRequeteCoreDeleteActionNoeud
        """
        from hermes.automate import ItopRequeteCoreDeleteActionNoeud as ACTION
        return self.transcription_fils(
            ACTION(
                self.designation,
                self.url_rest_itop,
                self.auth_user,
                self.auth_pwd,
                self.requete_dql,
                self.commentaire,
                (
                    self.authentification_basique_utilisateur,
                    self.authentification_basique_mot_de_passe
                ) if self.authentification_basique_utilisateur is not None else None,
                {
                    'http': self.proxy_http,
                    'https': self.proxy_https
                } if self.proxy_http is not None else None,
                self.verify_peer,
                self.friendly_name
            )
        )
