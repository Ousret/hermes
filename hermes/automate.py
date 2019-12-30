import re
from copy import copy, deepcopy
from datetime import datetime
from email.mime.base import MIMEBase
from io import BytesIO
from os.path import exists
from smtplib import SMTPServerDisconnected
from ssl import SSLContext, OP_ALL, PROTOCOL_TLS

from emails.backend.smtp.exceptions import SMTPConnectNetworkError
from prettytable import PrettyTable
from requests import request, RequestException, Session, post
from slugify import slugify

from hermes.logger import logger, __path__
from zeep import Client, Transport
from zeep.exceptions import TransportError, Fault
from zeep.helpers import serialize_object
import emails
from requests.auth import HTTPBasicAuth
from json import loads, dumps
from json.decoder import JSONDecodeError
from dateutil.parser import parse
from jinja2 import Template, TemplateError
from ics import Calendar, Event, Attendee, Organizer
from uuid import uuid4
from hashlib import sha512
import ruamel.std.zipfile as zipfile
from logging.handlers import BufferingHandler

from hermes.i18n import _

import records

from hermes.source import ManipulationSourceException, Source


class Automate(object):

    def __init__(self, designation, detecteur):
        """
        :param str designation:
        :param hermes.Detecteur detecteur:
        """

        self._designation = designation
        self._detecteur = detecteur

        self._handler = BufferingHandler(capacity=2048)
        self._logger_handler_id = None

        self._action_racine = None  # type: ActionNoeud

        self._logs = ''

    @property
    def designation(self):
        return self._designation

    @property
    def action_racine(self):
        return self._action_racine

    @property
    def actions_lancees(self):
        """
        :return:
        :rtype: list[ActionNoeud]
        """
        return self._action_racine.actions_lancees if self._action_racine is not None else list()

    @property
    def derniere_action_lancee(self):
        """
        :rtype: ActionNoeud
        """
        return self._action_racine.derniere_action_lancee if self._action_racine is not None else None

    @action_racine.setter
    def action_racine(self, action_noeud):
        if isinstance(action_noeud, ActionNoeud):
            self._action_racine = action_noeud

    @property
    def detecteur(self):
        return self._detecteur

    def __del__(self):
        if self._logger_handler_id is not None:
            logger.remove(self._logger_handler_id)
            self._logger_handler_id = None

    @property
    def logs(self):
        """
        Récupère les logs d'après fonctionnement
        :rtype: str
        """
        return self._logs

    def explain(self):
        my_table = PrettyTable([_("Type"), _("Action"), _("Réussite"), _("Valeur")])

        for el in self.actions_lancees:
            my_table.add_row(
                [
                    str(type(el)).split('.')[-1][0:-1],
                    el.designation,
                    el.est_reussite,
                    str(el.payload) if el.payload is not None else _('Aucune')
                ]
            )

        return my_table.get_string()

    def raz(self):
        if self._detecteur:
            self._detecteur.raz()
        if self._action_racine is not None:
            self._action_racine.raz()

    def lance_toi(self, source, bypass_detecteur=False):
        """
        Exécution de la suite d'actions tel un arbre binaire
        :param bool bypass_detecteur:
        :param hermes.source.Source source:
        :return: Etat final sous la forme d'un boolean
        :rtype: bool
        """

        self._logger_handler_id = logger.add(self._handler, level='DEBUG', enqueue=True, colorize=False, catch=True)

        logger.debug(
            _("Initialisation de l'automate '{automate_nom}' avec la source '{source_nom}'."),
            automate_nom=self.designation, source_nom=source.titre
        )

        self.raz()

        if not bypass_detecteur:
            self._detecteur.lance_toi(source)

        if self._detecteur.est_accomplis or bypass_detecteur:

            logger.info(
                _("Démarrage de l'automate '{automate_nom}' avec la source '{source_nom}'."),
                automate_nom=self.designation, source_nom=source.titre
            )

            if not bypass_detecteur:
                exp_dict_detecteur = self._detecteur.to_dict()

                for k in exp_dict_detecteur.keys():
                    source.session.sauver(k, exp_dict_detecteur[k])

                for k in source.extraction_interet.interets.keys():
                    source.session.sauver(k, source.extraction_interet.interets[k])

            final_leaf_bool = self._action_racine.je_realise(source) if self._action_racine is not None else False

            self._logs = '\n'.join([str(el.msg) for el in self._handler.buffer])
            logger.remove(self._logger_handler_id)
            self._logger_handler_id = None

            return final_leaf_bool
        else:
            logger.debug(_("L'automate ne semble pas concerné par la source '{detecteur_nom}'"),
                         detecteur_nom=str(self._detecteur))

        self._logs = '\n'.join([str(el.msg) for el in self._handler.buffer])
        logger.remove(self._logger_handler_id)
        self._logger_handler_id = None

        return False


class ActionNoeud(object):

    def __init__(self, designation, friendly_name=None):
        self._designation = designation
        self._friendly_name = friendly_name  # type: str

        self._noeud_reussite = None  # type: ActionNoeud
        self._noeud_echec = None  # type: ActionNoeud

        self._payload = None
        self._success = None

        self._maximum_retries = 0
        self._n_retries = 0

        self._init_args = dict()

    @property
    def friendly_name(self):
        return self._friendly_name

    @property
    def designation(self):
        return self._designation

    @property
    def est_reussite(self):
        return self._success is True

    @property
    def actions_lancees(self):
        if self._success is None:
            return []
        return [self] + \
               (self._noeud_reussite.actions_lancees if self._noeud_reussite is not None else []) + \
               (self._noeud_echec.actions_lancees if self._noeud_echec is not None else [])

    @property
    def derniere_action_lancee(self):
        """
        Récupération de la dernière action lancée dans l'arbre binaire à partir du noeud self
        :rtype: ActionNoeud
        """
        if self._noeud_reussite is not None and self._noeud_reussite._success is not None:
            return self._noeud_reussite.derniere_action_lancee
        if self._noeud_echec is not None and self._noeud_echec._success is not None:
            return self._noeud_echec.derniere_action_lancee
        return self if self._success is not None else None

    def _jai_echouee(self, source, new_payload=None, force_success=False):
        """
        Prendre le chemin en cas d'échec
        :param hermes.source.Source source:
        :rtype: bool
        """
        logger.warning(_("Échec de l'action '{action_nom}' sur '{source_nom}'"), action_nom=self._designation,
                       source_nom=source.titre)
        self._payload = new_payload
        self._success = force_success
        if self._friendly_name is not None:
            source.session.sauver(self._friendly_name, self._payload)
        return self._noeud_echec.je_realise(source) if self._noeud_echec is not None else False

    def _jai_reussi(self, source, new_payload=None):
        """
        Prendre le chemin en cas de réussite
        :param hermes.source.Source source:
        :rtype: bool
        """
        logger.info(_("Fin de l'action '{action_nom}' sur '{source_nom}'"), action_nom=self._designation,
                    source_nom=source.titre)
        self._payload = new_payload
        self._success = True
        if self._friendly_name is not None:
            source.session.sauver(self._friendly_name, self._payload)
        return True and self._noeud_reussite.je_realise(source) if self._noeud_reussite is not None else True

    def raz(self):
        self._payload = None

        for key_attr in self._init_args.keys():
            try:
                setattr(
                    self,
                    str(self._init_args.keys()),
                    self._init_args[str(key_attr)]
                )
            except AttributeError:
                pass
            except ValueError:
                pass
            except KeyError:
                pass

        self._init_args = dict()

        if self._noeud_reussite is not None:
            self._noeud_reussite.raz()
        if self._noeud_echec is not None:
            self._noeud_echec.raz()

    @property
    def payload(self):
        return self._payload

    def je_realise_en_cas_reussite(self, action_noeud):
        if isinstance(action_noeud, ActionNoeud):
            self._noeud_reussite = action_noeud
        return self

    def je_realise_en_cas_echec(self, action_noeud):
        if isinstance(action_noeud, ActionNoeud):
            self._noeud_echec = action_noeud
        return self

    @property
    def snapshot(self):
        """
        prendre un snapshot de l'état des params de l'action
        :return: Un dict parametre -> valeur
        :rtype: dict
        """
        members = [attr for attr in dir(self) if not attr.startswith("_surcouche_session") and not attr.startswith(
            '_init_args') and not attr.startswith('snapshot') and not attr.startswith('_payload') and not callable(
            getattr(self, attr)) and not isinstance(getattr(self, attr), ActionNoeud) and not attr.startswith("__")]
        snap = dict()

        for member in members:
            mon_attr = getattr(self, member)
            if member.startswith('_') and isinstance(mon_attr, str) or isinstance(mon_attr, dict) or isinstance(
                    mon_attr, list) or isinstance(mon_attr, tuple):
                if member == 'actions_lancees':
                    snap[member] = _('{n_action} actions fils lancées').format(
                        n_action=str(len(self.actions_lancees) - 1))
                else:
                    snap[member] = str(mon_attr)

        return snap

    def _surcouche_session(self, source):
        """
        :param hermes.source.Source source:
        :return:
        """
        members = [attr for attr in dir(self) if
                   not callable(getattr(self, attr)) and not attr.startswith("__") and not attr.startswith(
                       '_init_args')]

        for member in members:
            mon_attr = getattr(self, member)
            if member.startswith('_') and isinstance(mon_attr, str) or isinstance(mon_attr, dict) or isinstance(
                    mon_attr, list) or isinstance(mon_attr, tuple):
                mon_attr_b = deepcopy(mon_attr)
                try:
                    retr = source.session.retranscrire(mon_attr)
                    setattr(
                        self,
                        member,
                        retr
                    )
                    if retr != mon_attr_b:
                        self._init_args[member] = mon_attr_b
                except AttributeError:
                    pass
                except TypeError:
                    pass

    def je_realise(self, source):
        """
        Réalisation de l'action
        :param gie_interoperabilite.source.Source source:
        :return:
        :rtype: bool
        """
        logger.info(_("Démarrage de l'action '{action_nom}' sur '{source_nom}'"), action_nom=self._designation,
                    source_nom=source.titre)
        self._surcouche_session(source)
        self._success = False


class RequeteSqlActionNoeud(ActionNoeud):

    def __init__(self, designation, hote_type_protocol, hote_ipv4, hote_port, hote_database, requete_sql,
                 nom_utilisateur, mot_de_passe, friendly_name=None):
        super().__init__(designation, friendly_name=friendly_name)

        self._hote_type_protocol = hote_type_protocol
        self._hote_ipv4 = hote_ipv4
        self._hote_port = hote_port
        self._hote_database = hote_database
        self._nom_utilisateur = nom_utilisateur
        self._mot_de_passe = mot_de_passe

        self._requete_sql = requete_sql

    def je_realise(self, source):

        requete_sql_originale = copy(self._requete_sql)  # type: str

        super().je_realise(source)

        if self._hote_type_protocol not in ['mysql', 'posgres', 'mariadb', 'mssql', 'oracle']:
            logger.error(_("L'action '{action_nom}' sur la source '{source_nom}' est en échec car '{msg_err}'"),
                         action_nom=self._designation, source_nom=source.titre,
                         msg_err=_('Le protocol SGDB {} n\'est pas encore supporté !').format(self._hote_type_protocol))
            return self._jai_echouee(source)

        try:
            db = records.Database(
                '{hote_type}://\'{nom_utilisateur}\':\'{mot_de_passe}\'@{hote_ipv4}:{hote_port}/{hote_database}'.format(
                    hote_type=self._hote_type_protocol,
                    hote_ipv4=self._hote_ipv4,
                    hote_port=self._hote_port,
                    hote_database=self._hote_database,
                    nom_utilisateur=self._nom_utilisateur,
                    mot_de_passe=self._mot_de_passe
                )
            )
        except Exception as e:
            logger.error(_("L'action '{action_nom}' sur la source '{source_nom}' est en échec car '{msg_err}'"),
                         action_nom=self._designation, source_nom=source.titre, msg_err=str(e))
            return self._jai_echouee(source)

        bind_param_secure = dict()

        for el in re.findall(r'{{[a-zA-Z0-9éàèç_|\-:. ]{2,}}}', requete_sql_originale):
            requete_sql_originale.replace(el, ':{var_name}'.format(var_name=slugify(el.strip('{}'))))
            bind_param_secure[el.strip('{}')] = source.session.retranscrire(el)

        try:
            rows = db.query(requete_sql_originale, fetchall=False, **bind_param_secure)
        except Exception as e:
            logger.error(_("L'action '{action_nom}' sur la source '{source_nom}' est en échec car '{msg_err}'"),
                         action_nom=self._designation, source_nom=source.titre, msg_err=str(e))
            return self._jai_echouee(source)

        return self._jai_reussi(source, rows.as_dict())


class RequeteSoapActionNoeud(ActionNoeud):

    def __init__(self, designation, url_service, methode_cible, form_data, basic_auth=None, proxies=None,
                 friendly_name=None):
        super().__init__(designation, friendly_name)

        self._url_service = url_service
        self._methode_cible = methode_cible
        self._form_data = form_data
        self._basic_auth = basic_auth
        self._proxies = proxies

    def je_realise(self, source):
        """

        :param gie_interoperabilite.source.Source source:
        :return:
        """
        super().je_realise(source)

        session = Session()
        session.proxies = self._proxies if self._proxies is not None else dict()

        if self._basic_auth is not None:
            nom_utilisateur, mot_de_passe = self._basic_auth
            session.auth = HTTPBasicAuth(nom_utilisateur, mot_de_passe)

        transport = Transport(session=session)

        client = Client(
            self._url_service,
            transport=transport)

        try:
            logger.debug(str(self._form_data))
            response = serialize_object(
                client.service[self._methode_cible](**self._form_data)
            )
            logger.debug(str(response))
        except TransportError as e:
            logger.error(_("L'action '{action_nom}' sur '{source_nom}' est en échec : {msg_err}"),
                         action_nom=self._designation,
                         source_nom=source.titre, msg_err=str(e))
            return self._jai_echouee(source)
        except Fault as e:
            logger.error(_("L'action '{action_nom}' sur '{source_nom}' est en échec : '{msg_err}' '{fault_msg}'"),
                         action_nom=self._designation,
                         source_nom=source.titre, msg_err=str(e), fault_msg=str(e.detail))
            return self._jai_echouee(source)
        except TypeError as e:
            logger.error(_("L'action '{action_nom}' sur '{source_nom}' est en échec : {msg_err}"),
                         action_nom=self._designation, source_nom=source.titre, msg_err=str(e))
            return self._jai_echouee(source)

        if isinstance(response, dict):
            if self._friendly_name is not None:
                source.session.sauver(self._designation if self._friendly_name is None else self._friendly_name,
                                      response)
            else:
                for key in response.keys():
                    source.session.sauver(key, response[key])
        elif isinstance(response, list) or isinstance(response, str):
            source.session.sauver(
                self._designation if self._friendly_name is None else self._friendly_name,
                response
            )

        return self._jai_reussi(source, response)


class RequeteHttpActionNoeud(ActionNoeud):
    def __init__(self, designation, url_dest, methode_http='GET', form_data=None, basic_auth=None, proxies=None,
                 resp_code_http=None, verify_peer=True, friendly_name=None):
        super().__init__(designation, friendly_name)

        self._url_dest = url_dest
        self._methode_http = methode_http
        self._form_data = form_data
        self._basic_auth = basic_auth
        self._resp_code_http = resp_code_http
        self._proxies = proxies
        self._verify_peer = verify_peer

    def je_realise(self, source):

        super().je_realise(source)

        try:
            response = request(self._methode_http, self._url_dest, data=self._form_data, proxies=self._proxies,
                               verify=self._verify_peer)
        except RequestException as e:
            logger.error(_("L'action '{action_nom}' est en échec pour la raison suivante : '{msg_err}'"),
                         action_nom=self._designation, msg_err=str(e))
            return self._jai_echouee(source)

        if response.status_code == self._resp_code_http or self._resp_code_http is None and response.ok:

            try:
                output = response.json()

                if isinstance(output, dict):
                    if self._friendly_name is not None:
                        source.session.sauver(self._friendly_name, output)
                    else:
                        for key in output.keys():
                            source.session.sauver(key, output[key])
                elif isinstance(output, list):
                    source.session.sauver(self._designation if self._friendly_name is None else self._friendly_name,
                                          output)
            except ValueError as e:
                output = response.content
                logger.warning(_("L'action '{action_nom}' n'a pas réussi à exploiter le résultat : '{msg_err}'"),
                               action_nom=self._designation, msg_err=str(e))

            return self._jai_reussi(source, output)

        logger.error(_("L'action '{action_nom}' est en échec pour la raison suivante : '{msg_err}'"),
                     action_nom=self._designation,
                     msg_err=_('La requête HTTP a retournée un code erreur ou différent de celui attendu'))

        return self._jai_echouee(source, response.content)


class ItopRequeteCoreGetActionNoeud(ActionNoeud):
    def __init__(self, designation, url_rest_itop, auth_user, auth_pwd, requete_dql, output_fields, basic_auth=None,
                 proxies=None, verify_peer=True, friendly_name=None):
        super().__init__(designation, friendly_name)
        self._url_rest_itop = url_rest_itop
        self._auth_user = auth_user
        self._auth_pwd = auth_pwd
        self._requete_dql = requete_dql  # type: str
        self._output_fields = output_fields
        self._basic_auth = basic_auth
        self._proxies = proxies
        self._verify_peer = verify_peer

    def je_realise(self, source):

        super().je_realise(source)

        ma_classe_itop_cible = self._requete_dql.split(' ')[1]

        try:
            response = post(
                self._url_rest_itop,
                {
                    'auth_user': self._auth_user,
                    'auth_pwd': self._auth_pwd,
                    'json_data': dumps(
                        {
                            'operation': 'core/get',
                            'class': ma_classe_itop_cible,
                            'key': self._requete_dql,
                            'output_fields': self._output_fields
                        }
                    )
                },
                proxies=self._proxies,
                verify=self._verify_peer
            )
        except RequestException as e:
            logger.error(_("L'action '{action_nom}' est en échec pour la raison suivante : '{msg_err}'"),
                         action_nom=self._designation, msg_err=str(e))
            return self._jai_echouee(source)

        if not response.ok:
            logger.error(_(
                "Le module REST JSON d'iTop ne semble pas fonctionner correctement. Une réponse a été capturée sous le code HTTP/{http_code}."),
                         http_code=response.status_code)
            return self._jai_echouee(source, response.content)

        my_payload = response.json()

        if 'code' not in my_payload or 'message' not in my_payload:
            return self._jai_echouee(source, response.content)

        if my_payload['code'] != 0:
            logger.error(_(
                "La requête core/get iTop REST '{req_dql}' n'a pas aboutie correctement. Une erreur a été soulevée (code {code_itop}) : {message_itop}"),
                         req_dql=self._requete_dql, code_itop=my_payload['code'], message_itop=my_payload['message'])
            return self._jai_echouee(source, response.content)

        return self._jai_reussi(source, my_payload)


class ItopRequeteCoreCreateActionNoeud(ActionNoeud):
    def __init__(self, designation, url_rest_itop, auth_user, auth_pwd, classe_itop_cible, fields, output_fields,
                 commentaire, basic_auth=None,
                 proxies=None, verify_peer=True, friendly_name=None):
        super().__init__(designation, friendly_name)
        self._url_rest_itop = url_rest_itop
        self._auth_user = auth_user
        self._auth_pwd = auth_pwd
        self._classe_itop_cible = classe_itop_cible
        self._fields = fields
        self._output_fields = output_fields
        self._commentaire = commentaire
        self._basic_auth = basic_auth
        self._proxies = proxies
        self._verify_peer = verify_peer

    def je_realise(self, source):

        super().je_realise(source)

        try:
            response = post(
                self._url_rest_itop,
                {
                    'auth_user': self._auth_user,
                    'auth_pwd': self._auth_pwd,
                    'json_data': dumps(
                        {
                            'operation': 'core/create',
                            'class': self._classe_itop_cible,
                            'fields': self._fields,
                            'output_fields': self._output_fields,
                            'comment': self._commentaire
                        }
                    )
                },
                proxies=self._proxies,
                verify=self._verify_peer
            )
        except RequestException as e:
            logger.error(_("L'action '{action_nom}' est en échec pour la raison suivante : '{msg_err}'"),
                         action_nom=self._designation, msg_err=str(e))
            return self._jai_echouee(source)

        if not response.ok:
            logger.error(_(
                "Le module REST JSON d'iTop ne semble pas fonctionner correctement. Une réponse a été capturée sous le code HTTP/{http_code}."),
                         http_code=response.status_code)
            return self._jai_echouee(source, response.content)

        my_payload = response.json()

        if 'code' not in my_payload or 'message' not in my_payload:
            return self._jai_echouee(source, response.content)

        if my_payload['code'] != 0:
            logger.error(_(
                "La requête core/create iTop REST '{classe_itop}' n'a pas aboutie correctement. Une erreur a été soulevée (code {code_itop}) : {message_itop}"),
                         classe_itop=self._classe_itop_cible, code_itop=my_payload['code'],
                         message_itop=my_payload['message'])
            return self._jai_echouee(source, response.content)

        return self._jai_reussi(source, my_payload)


class ItopRequeteCoreUpdateActionNoeud(ActionNoeud):
    def __init__(self, designation, url_rest_itop, auth_user, auth_pwd, requete_dql, fields, output_fields, commentaire,
                 basic_auth=None,
                 proxies=None, verify_peer=True, friendly_name=None):
        super().__init__(designation, friendly_name)
        self._url_rest_itop = url_rest_itop
        self._auth_user = auth_user
        self._auth_pwd = auth_pwd
        self._requete_dql = requete_dql
        self._fields = fields
        self._output_fields = output_fields
        self._commentaire = commentaire
        self._basic_auth = basic_auth
        self._proxies = proxies
        self._verify_peer = verify_peer

    def je_realise(self, source):

        super().je_realise(source)

        ma_classe_itop_cible = self._requete_dql.split(' ')[1]

        try:
            response = post(
                self._url_rest_itop,
                {
                    'auth_user': self._auth_user,
                    'auth_pwd': self._auth_pwd,
                    'json_data': dumps(
                        {
                            'operation': 'core/update',
                            'class': ma_classe_itop_cible,
                            'key': self._requete_dql,
                            'fields': self._fields,
                            'output_fields': self._output_fields,
                            'comment': self._commentaire
                        }
                    )
                },
                proxies=self._proxies,
                verify=self._verify_peer
            )
        except RequestException as e:
            logger.error(_("L'action '{action_nom}' est en échec pour la raison suivante : '{msg_err}'"),
                         action_nom=self._designation, msg_err=str(e))
            return self._jai_echouee(source)

        if not response.ok:
            logger.error(_(
                "Le module REST JSON d'iTop ne semble pas fonctionner correctement. Une réponse a été capturée sous le code HTTP/{http_code}."),
                         http_code=response.status_code)
            return self._jai_echouee(source, response.content)

        my_payload = response.json()

        if 'code' not in my_payload or 'message' not in my_payload:
            return self._jai_echouee(source, response.content)

        if my_payload['code'] != 0:
            logger.error(_(
                "La requête core/update iTop REST '{req_dql}' n'a pas aboutie correctement. Une erreur a été soulevée (code {code_itop}) : {message_itop}"),
                         req_dql=self._requete_dql, code_itop=my_payload['code'], message_itop=my_payload['message'])
            return self._jai_echouee(source, response.content)

        return self._jai_reussi(source, my_payload)


class ItopRequeteCoreApplyStimulusActionNoeud(ActionNoeud):
    def __init__(self, designation, url_rest_itop, auth_user, auth_pwd, requete_dql, stimulus, fields, output_fields,
                 commentaire, basic_auth=None,
                 proxies=None, verify_peer=True, friendly_name=None):
        super().__init__(designation, friendly_name)
        self._url_rest_itop = url_rest_itop
        self._auth_user = auth_user
        self._auth_pwd = auth_pwd
        self._requete_dql = requete_dql
        self._stimulus = stimulus
        self._fields = fields
        self._output_fields = output_fields
        self._commentaire = commentaire
        self._basic_auth = basic_auth
        self._proxies = proxies
        self._verify_peer = verify_peer

    def je_realise(self, source):

        super().je_realise(source)

        ma_classe_itop_cible = self._requete_dql.split(' ')[1]

        try:
            response = post(
                self._url_rest_itop,
                {
                    'auth_user': self._auth_user,
                    'auth_pwd': self._auth_pwd,
                    'json_data': dumps(
                        {
                            'operation': 'core/apply_stimulus',
                            'class': ma_classe_itop_cible,
                            'key': self._requete_dql,
                            'fields': self._fields,
                            'output_fields': self._output_fields,
                            'stimulus': self._stimulus,
                            'comment': self._commentaire
                        }
                    )
                },
                proxies=self._proxies,
                verify=self._verify_peer
            )
        except RequestException as e:
            logger.error(_("L'action '{action_nom}' est en échec pour la raison suivante : '{msg_err}'"),
                         action_nom=self._designation, msg_err=str(e))
            return self._jai_echouee(source, str(e))

        if not response.ok:
            logger.error(_(
                "Le module REST JSON d'iTop ne semble pas fonctionner correctement. Une réponse a été capturée sous le code HTTP/{http_code}."),
                         http_code=response.status_code)
            return self._jai_echouee(source, response.content)

        my_payload = response.json()

        if 'code' not in my_payload or 'message' not in my_payload:
            return self._jai_echouee(source, response.content)

        if my_payload['code'] != 0:
            logger.error(_(
                "La requête core/apply_stimulus iTop REST '{req_dql}' n'a pas aboutie correctement. Une erreur a été soulevée (code {code_itop}) : {message_itop}"),
                         req_dql=self._requete_dql, code_itop=my_payload['code'], message_itop=my_payload['message'])
            return self._jai_echouee(source, response.content)

        return self._jai_reussi(source, my_payload)


class ItopRequeteCoreDeleteActionNoeud(ActionNoeud):
    def __init__(self, designation, url_rest_itop, auth_user, auth_pwd, requete_dql, commentaire, basic_auth=None,
                 proxies=None, verify_peer=True, friendly_name=None):
        super().__init__(designation, friendly_name)
        self._url_rest_itop = url_rest_itop
        self._auth_user = auth_user
        self._auth_pwd = auth_pwd
        self._requete_dql = requete_dql
        self._commentaire = commentaire
        self._basic_auth = basic_auth
        self._proxies = proxies
        self._verify_peer = verify_peer

    def je_realise(self, source):

        super().je_realise(source)

        ma_classe_itop_cible = self._requete_dql.split(' ')[1]

        try:
            response = post(
                self._url_rest_itop,
                {
                    'auth_user': self._auth_user,
                    'auth_pwd': self._auth_pwd,
                    'json_data': dumps(
                        {
                            'operation': 'core/delete',
                            'class': ma_classe_itop_cible,
                            'key': self._requete_dql,
                            'comment': self._commentaire
                        }
                    )
                },
                proxies=self._proxies,
                verify=self._verify_peer
            )
        except RequestException as e:
            logger.error(_("L'action '{action_nom}' est en échec pour la raison suivante : '{msg_err}'"),
                         action_nom=self._designation, msg_err=str(e))
            return self._jai_echouee(source, str(e))

        if not response.ok:
            logger.error(_(
                "Le module REST JSON d'iTop ne semble pas fonctionner correctement. Une réponse a été capturée sous le code HTTP/{http_code}."),
                         http_code=response.status_code)
            return self._jai_echouee(source, response.content)

        my_payload = response.json()

        if 'code' not in my_payload or 'message' not in my_payload:
            return self._jai_echouee(source, response.content)

        if my_payload['code'] != 0:
            logger.error(_(
                "La requête core/delete iTop REST '{req_dql}' n'a pas aboutie correctement. Une erreur a été soulevée (code {code_itop}) : {message_itop}"),
                         req_dql=self._requete_dql, code_itop=my_payload['code'], message_itop=my_payload['message'])
            return self._jai_echouee(source, response.content)

        return self._jai_reussi(source, my_payload)


class VerifierSiVariableVraiActionNoeud(ActionNoeud):

    def __init__(self, designation, variable_cible, friendly_name):
        super().__init__(designation, friendly_name)

        self._variable_cible = variable_cible  # type: str

    def je_realise(self, source):
        super().je_realise(source)

        if self._variable_cible is False or self._variable_cible == 'False':
            self._payload = True
            return True and self._noeud_echec.je_realise(source) if self._noeud_echec is not None else True

        self._payload = True
        return self._jai_reussi(source)


class ComparaisonVariableActionNoeud(ActionNoeud):

    def __init__(self, designation, membre_gauche_variable, operande, membre_droite_variable, friendly_name):
        """
        :param str designation:
        :param str membre_gauche_variable:
        :param str operande:
        :param str membre_droite_variable:
        :param str friendly_name:
        """
        super().__init__(designation, friendly_name)

        self._membre_gauche = membre_gauche_variable
        self._operande = operande
        self._membre_droite = membre_droite_variable

    def je_realise(self, source):
        super().je_realise(source)

        if self._operande.upper() not in ['==', '>', '<', '>=', '<=', '!=', 'IN']:
            logger.warning(
                _("L'opérateur '{operateur}' n'est pas reconnu pour effectuer une comparaison entre deux membres"),
                operateur=self._operande)
            return self._jai_echouee(source, False, True)

        if self._membre_droite.isdigit() or self._membre_gauche.isdigit() and self._membre_droite.isdigit() != self._membre_gauche.isdigit():
            logger.warning(
                _(
                    "Impossible de comparer un nombre avec un autre type de donnée. ({membre_gauche} AVEC {membre_droite})"),
                membre_gauche=self._membre_gauche, membre_droite=self._membre_droite)
            return self._jai_echouee(source, False, True)
        elif self._membre_droite.isdigit() and self._membre_gauche.isdigit():
            self._membre_droite = int(self._membre_droite)
            self._membre_gauche = int(self._membre_gauche)

            if eval('{membre_gauche} {operande} {membre_droite}'.format(membre_gauche=self._membre_gauche,
                                                                        operande=self._operande,
                                                                        membre_droite=self._membre_droite)) is True:
                return self._jai_reussi(source, True)

            return self._jai_echouee(source, False, True)
        elif all([el.isdigit() for el in self._membre_droite.split('.') + self._membre_gauche.split('.')]) is True:
            self._membre_droite = float(self._membre_droite)
            self._membre_gauche = float(self._membre_gauche)

            if eval('{membre_gauche} {operande} {membre_droite}'.format(membre_gauche=self._membre_gauche,
                                                                        operande=self._operande,
                                                                        membre_droite=self._membre_droite)) is True:
                return self._jai_reussi(source, True)

            return self._jai_echouee(source, False, True)
        try:
            membre_date_droite = parse(self._membre_droite)
            membre_date_gauche = parse(self._membre_gauche)

            if eval('{membre_gauche} {operande} {membre_droite}'.format(membre_gauche=membre_date_gauche.timestamp(),
                                                                        operande=self._operande,
                                                                        membre_droite=membre_date_droite.timestamp())) is True:
                return self._jai_reussi(source, True)

            return self._jai_echouee(source, False, True)

        except ValueError as e:
            if self._operande == '==':
                expr_ret = self._membre_gauche == self._membre_droite
            elif self._operande == '>':
                expr_ret = self._membre_gauche > self._membre_droite
            elif self._operande == '<':
                expr_ret = self._membre_gauche < self._membre_droite
            elif self._operande == '>=':
                expr_ret = self._membre_gauche >= self._membre_droite
            elif self._operande == '<=':
                expr_ret = self._membre_gauche <= self._membre_droite
            elif self._operande == '!=':
                expr_ret = self._membre_gauche != self._membre_droite
            elif self._operande == 'IN':
                expr_ret = self._membre_gauche in self._membre_droite if isinstance(self._membre_gauche,
                                                                                    str) and isinstance(
                    self._membre_droite, str) else False
            else:
                expr_ret = False

            if expr_ret is True:
                return self._jai_reussi(source, True)

        return self._jai_echouee(source, False, True)


class InvitationEvenementActionNoeud(ActionNoeud):
    class EvenementICS(Source):

        def __init__(self, nom_fichier, raw_content):
            super().__init__('Evenement ICS', '')
            self._nom_fichier = nom_fichier
            self._raw_content = raw_content

        @property
        def raw(self):
            return self._raw_content

        @property
        def nom_fichier(self):
            return self._nom_fichier

    class AttendeePlus(Attendee):

        def __init__(self, email, common_name=None, rsvp=None):
            super().__init__(email, common_name, rsvp)

        def get_params(self):
            params = {}
            if self.common_name:
                params.update({'CN': ["'{}'".format(self.common_name)]})

            if self.rsvp:
                params.update({'RSVP': [self.rsvp]})

            params.update(
                {
                    'CUTYPE': ['INDIVIDUAL'],
                    'ROLE': ['REQ-PARTICIPANT'],
                    'PARTSTAT': ['NEEDS-ACTION'],
                    'X-NUM-GUESTS': ['0']
                }
            )

            return params

    def __init__(
            self,
            designation,
            organisateur,
            participants,
            sujet,
            description,
            lieu,
            date_heure_depart,
            date_heure_fin,
            est_maintenu,

            hote_smtp,
            port_smtp,
            nom_utilisateur,
            mot_de_passe,
            enable_tls=True,
            legacy_tls_support=False,
            friendly_name=None):
        super().__init__(designation, friendly_name)

        self._organisateur = organisateur
        self._participants = participants  # type: str
        self._sujet = sujet
        self._description = description
        self._lieu = lieu
        self._date_heure_depart = date_heure_depart
        self._date_heure_fin = date_heure_fin
        self._est_maintenu = est_maintenu

        self._hote_smtp = hote_smtp
        self._port_smtp = port_smtp
        self._nom_utilisateur_smtp = nom_utilisateur
        self._mot_de_passe_smtp = mot_de_passe
        self._enable_tls_smtp = enable_tls
        self._legacy_tls_support = legacy_tls_support

    def je_realise(self, source):
        super().je_realise(source)

        try:
            self._date_heure_depart = parse(self._date_heure_depart, dayfirst=True)
            self._date_heure_fin = parse(self._date_heure_fin, dayfirst=True)
        except ValueError:
            logger.error(
                _("L'action '{action_nom}' est en échec pour la raison suivante : '{msg_err}'"),
                action_nom=self._designation,
                msg_err=_('Les dates de départ et de fin, (' + str(self._date_heure_depart) + ', ' + str(
                    self._date_heure_fin) + '), '
                                            'ne sont pas dans un format facilement reconnaissable !')
            )
            return self._jai_echouee(source)

        if self._date_heure_depart.timestamp() >= self._date_heure_fin.timestamp():
            logger.error(
                _("L'action '{action_nom}' est en échec pour la raison suivante : '{msg_err}'"),
                action_nom=self._designation,
                msg_err=_('La date de départ est supérieure ou égale à la date de fin')
            )
            return self._jai_echouee(source)

        cached_ics_hash = sha512(
            dumps(
                {
                    'sujet': self._sujet,
                    'lieu': self._lieu,
                    'organisateur': self._organisateur
                }
            ).encode('utf-8')
        ).hexdigest()

        cached_ics_path = '{}/../invitations/{}.ics'.format(__path__, str(cached_ics_hash))
        my_cached_uid = None

        if exists(cached_ics_path) is True:

            logger.info(
                _("L'action '{action_nom}' se souvient d'avoir déjà émis un rendez-vous. "
                  "L'invitation '{invitation_sha512}' sera mise à jour automatiquement en conservant les références.").format(
                    action_nom=self._designation,
                    invitation_sha512=cached_ics_hash
                )
            )

            try:
                my_cached_calendar = Calendar(open(cached_ics_path, 'r', encoding='utf-8').read())
                my_cached_uid = my_cached_calendar.events.pop().uid
            except IOError as e:
                logger.error(
                    _("L'action '{action_nom}' est en échec pour la raison suivante : '{msg_err}'"),
                    action_nom=self._designation,
                    msg_err=_('Une erreur est survenue lors de la récupération du fichier ICS en cache. '
                              'Chemin: "{chemin}", Erreur: "{msg_err}"').format(chemin=cached_ics_path, msg_err=str(e))
                )
                return self._jai_echouee(source)

        if self._est_maintenu is False and my_cached_uid is None:
            logger.error(
                _("L'action '{action_nom}' est en échec pour la raison suivante : '{msg_err}'"),
                action_nom=self._designation,
                msg_err=_('Impossible d\'annuler un évènement sans l\'avoir créer au préalable')
            )
            return self._jai_echouee(source)

        message_from_field = source.destinataire if isinstance(source.destinataire, list) is False else source.destinataire[-1]

        if self._nom_utilisateur_smtp.split('@')[0] not in message_from_field:
            logger.warning(
                _("L'action '{action_nom}' ne reconnais pas l'adresse '{source_addr_to}' "
                  "pour être utilisée en tant qu'organisateur.").format(
                    action_nom=self._designation,
                    source_addr_to=message_from_field
                )
            )

            message_from_field = '{smtp_username}@{smtp_domain}'.format(
                smtp_username=self._nom_utilisateur_smtp.split('@')[0],
                smtp_domain=message_from_field.split('@')[-1]
            )

            logger.info(
                _("L'action '{action_nom}' va utiliser '{source_addr_to}' "
                  "pour être utilisée en tant qu'organisateur.").format(
                    action_nom=self._designation,
                    source_addr_to=message_from_field
                )
            )

        my_calendar = Calendar(creator='Microsoft Exchange Server 2010')
        my_calendar.scale = 'GREGORIAN'

        my_calendar.method = 'REQUEST' if self._est_maintenu is True else 'CANCEL'

        description_invitation_notification = self._description.format(
            organisateur=self._organisateur,
            sujet=self._sujet,
            lieu=self._lieu,
            date_depart=self._date_heure_depart.strftime('%d/%m/%Y à %H:%M')
        )

        my_event = Event(
            name=self._sujet,
            begin=self._date_heure_depart,
            end=self._date_heure_fin,
            uid=str(uuid4()).replace('-', '').upper() if my_cached_uid is None else my_cached_uid,
            description=description_invitation_notification,
            created=datetime.now(),
            location=self._lieu,
            status='CONFIRMED' if self._est_maintenu is True else 'CANCELLED',
            organizer=Organizer(
                email=message_from_field,
                sent_by=message_from_field,
            ),
            transparent=False,
            # alarms=[
            #     DisplayAlarm(
            #         trigger=timedelta(minutes=-30),
            #         display_text='REMINDER'
            #     )
            # ]
        )

        for attendee in [InvitationEvenementActionNoeud.AttendeePlus(el.strip(), rsvp="TRUE") for el in
                         self._participants.split(',') if ':' not in el]:
            my_event.add_attendee(attendee)

        my_calendar.events.add(my_event)

        vcalendar_output_raw = str(my_calendar)
        source.session.sauver(self._designation if self._friendly_name is None else self._friendly_name, self._payload)

        vcalendar_output = vcalendar_output_raw.encode('utf-8')

        with open(cached_ics_path, 'wb') as fp:
            fp.write(vcalendar_output)

        ma_source_ics_invitation = InvitationEvenementActionNoeud.EvenementICS(
            slugify(my_event.uid) + '.ics',
            vcalendar_output
        )

        mon_action_envoyer_notification_smtp = EnvoyerMessageSmtpActionNoeud(
            _("Envoyer invitation ICS depuis serveur SMTP"),
            self._participants,
            self._sujet,
            description_invitation_notification,
            self._hote_smtp,
            self._port_smtp,
            self._nom_utilisateur_smtp,
            self._mot_de_passe_smtp,
            self._enable_tls_smtp,
            pj_source=False,
            source_pj_complementaire=ma_source_ics_invitation,
            force_keep_template=True,
            legacy_tls_support=self._legacy_tls_support
        )

        if mon_action_envoyer_notification_smtp.je_realise(source) is False:
            logger.error(
                _("L'action '{action_nom}' est en échec pour la raison suivante : '{msg_err}'"),
                action_nom=self._designation,
                msg_err=_('Impossible d\'envoyer le fichier invitation ICS par le biais serveur SMTP')
            )
            return self._jai_echouee(source, str(my_calendar))

        return self._jai_reussi(source, str(my_calendar))


class ManipulationSmtpActionNoeud(ActionNoeud):

    def __init__(self, designation, hote_smtp, nom_utilisateur, mot_de_passe):
        super().__init__(designation)

        self._hote_smtp = hote_smtp
        self._nom_utilisateur = nom_utilisateur
        self._mot_de_passe = mot_de_passe


class EnvoyerMessageSmtpActionNoeud(ManipulationSmtpActionNoeud):
    ZIP_EXTENSION_SAFEMODE = [
        'eml',
        'txt'
    ]

    def __init__(self, designation, destinataire, sujet, corps, hote_smtp, port_smtp, nom_utilisateur, mot_de_passe,
                 enable_tls=False, pj_source=False, source_pj_complementaire=None, force_keep_template=False,
                 legacy_tls_support=False):
        super().__init__(designation, hote_smtp, nom_utilisateur, mot_de_passe)

        self._destinataire = destinataire
        self._sujet = sujet
        self._corps = corps.lstrip()  # type: str
        self._activation_tls = enable_tls
        self._port_smtp = port_smtp
        self._pj_source = pj_source

        self._source_pj_complementaire = source_pj_complementaire

        self._force_keep_template = force_keep_template
        self._legacy_tls_support = legacy_tls_support

    def je_realise(self, source):
        """
        :param gie_interoperabilite.mail.Mail source:
        :return:
        """
        super().je_realise(source)

        regex_html_tags = re.compile(
            r'<(br|basefont|hr|input|source|frame|param|area|meta|!--|col|link|option|base|img|wbr|!DOCTYPE|html|head).*?>|<(a|abbr|acronym|address|applet|article|aside|audio|b|bdi|bdo|big|blockquote|body|button|canvas|caption|center|cite|code|colgroup|command|datalist|dd|del|details|dfn|dialog|dir|div|dl|dt|em|embed|fieldset|figcaption|figure|font|footer|form|frameset|head|header|hgroup|h1|h2|h3|h4|h5|h6|html|i|iframe|ins|kbd|keygen|label|legend|li|map|mark|menu|meter|nav|noframes|noscript|object|ol|optgroup|output|p|pre|progress|q|rp|rt|ruby|s|samp|script|section|select|small|span|strike|strong|style|sub|summary|sup|table|tbody|td|textarea|tfoot|th|thead|time|title|tr|track|tt|u|ul|var|video).*?</\2>'
        )

        message_from_field = source.destinataire if isinstance(source.destinataire, list) is False else source.destinataire[-1]

        if self._nom_utilisateur.split('@')[0] not in message_from_field:

            logger.warning(
                _("L'action '{action_nom}' ne reconnais pas l'adresse '{source_addr_to}' "
                  "pour être utilisée en tant qu'expéditeur.").format(
                    action_nom=self._designation,
                    source_addr_to=message_from_field
                )
            )

            message_from_field = '{smtp_username}@{smtp_domain}'.format(
                smtp_username=self._nom_utilisateur.split('@')[0],
                smtp_domain=message_from_field.split('@')[-1]
            )

            logger.info(
                _("L'action '{action_nom}' va utiliser '{source_addr_to}' "
                  "pour être utilisée en tant qu'expéditeur.").format(
                    action_nom=self._designation,
                    source_addr_to=message_from_field
                )
            )

        if re.search(regex_html_tags, self._corps) is not None and self._force_keep_template is False:

            m = emails.Message(html=self._corps,
                               subject=self._sujet,
                               mail_from=message_from_field)

        else:

            rendered_template = None

            try:
                with open('{}/templates/mail/notification.html'.format(__path__), 'r', encoding='utf-8') as fp:
                    html_source = fp.read()

                template = Template(html_source)

                rendered_template = template.render(titre=self._sujet, description_courte=self._corps[0:60] + '..',
                                                    corps=self._corps, action=None)

            except FileNotFoundError as e:
                logger.warning(
                    _(
                        "Impossible de générer une notification HTML de votre message car la template n'existe pas, {msg_err}"),
                    msg_err=str(e)
                )
            except IOError as e:
                logger.warning(
                    _(
                        "Impossible de générer une notification HTML de votre message car la template est inaccesible, {msg_err}"),
                    msg_err=str(e)
                )
            except TemplateError as e:
                logger.warning(
                    _("Impossible de générer une notification HTML de votre message "
                      "car le moteur de template rend une erreur, {msg_err}"),
                    msg_err=str(e)
                )

            m = emails.Message(html=rendered_template,
                               text=self._corps,
                               subject=self._sujet,
                               date=datetime.now(),
                               mail_from=message_from_field)

        for pj_source in [source if self._pj_source is True else None,
                          self._source_pj_complementaire if self._source_pj_complementaire is not None else None]:

            if pj_source is None:
                continue

            try:

                if any([pj_source.nom_fichier.lower().endswith('.' + el) for el in
                        EnvoyerMessageSmtpActionNoeud.ZIP_EXTENSION_SAFEMODE]) is True:
                    my_zip_source = zipfile.InMemoryZipFile()
                    my_zip_source.append(pj_source.nom_fichier, pj_source.raw)

                    m.attach(data=BytesIO(my_zip_source.data), filename=pj_source.nom_fichier + '.zip')
                else:

                    m.attach(
                        data=BytesIO(pj_source.raw),
                        filename=pj_source.nom_fichier
                    )

                    # Hack python-emails, support invitation ICS en PJ
                    if pj_source.nom_fichier.endswith('.ics') is True:
                        p = m.attachments.by_filename(pj_source.nom_fichier).mime  # type: MIMEBase

                        p.set_type(
                            'text/calendar; charset=UTF-8; name="{}"; method={}; component=VEVENT'.format(
                                pj_source.nom_fichier,
                                'REQUEST' if 'METHOD:CANCEL' not in pj_source.raw.decode('utf-8') else 'CANCEL'
                            )
                        )
                        p.add_header('charset', 'UTF-8')
                        p.add_header('component', 'VEVENT')
                        p.add_header('method',
                                     'REQUEST' if 'METHOD:CANCEL' not in pj_source.raw.decode('utf-8') else 'CANCEL')
                        p.add_header('Content-Class', 'urn:content-classes:appointment')
                        p.add_header('Content-Description', pj_source.nom_fichier)

                        del p['Content-Disposition']

                        m.attachments.by_filename(pj_source.nom_fichier)._cached_part = p

            except NotImplemented:
                logger.warning(_("La source '{source_nom}' de type '{source_type}' "
                                 "ne supporte pas la transformation "
                                 "en PJ 'supplémentaire' pour un envoie via SMTP"), source_nom=pj_source.titre,
                               source_type=type(pj_source))

        destinaires_adresses_valides = list()
        destinataires_copies_cachees_valides = list()
        destinataire_copies_visibles_valides = list()

        for dest in [self._destinataire] if ',' not in self._destinataire else [destinataire.strip(' ') for destinataire
                                                                                in self._destinataire.split(',')]:

            type_copie = None

            if 'cc:' in dest.lower():
                type_copie, dest = dest.split(':')
            elif 'bcc:' in dest.lower():
                type_copie, dest = dest.split(':')

            if re.fullmatch(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', dest) is None:
                logger.warning(
                    _("Action '{action_nom}': Impossible d'émettre un message à cette adresse '{addr_cible}' "
                      "car elle ne respecte pas le RFC 5322"),
                    action_nom=self.designation,
                    addr_cible=dest
                )
                continue

            if type_copie is None:
                destinaires_adresses_valides.append(dest)
            elif type_copie.lower() == 'cc':
                destinataire_copies_visibles_valides.append(dest)
            elif type_copie.lower() == 'bcc':
                destinataires_copies_cachees_valides.append(dest)

        m.set_cc(destinataire_copies_visibles_valides)
        m.set_bcc(destinataires_copies_cachees_valides)
        m.set_mail_to(destinaires_adresses_valides)

        if len(destinaires_adresses_valides) == 0 and len(destinataire_copies_visibles_valides) == 0 and len(destinataires_copies_cachees_valides) == 0:
            logger.error(
                _("Action '{action_nom}': Impossible d'émettre un message car aucune adresse valide n'est disponible "
                  "au sens du RFC 5322"),
                action_nom=self.designation
            )
            return self._jai_echouee(source)

        try:

            smtp_kwargs = {
                "host": self._hote_smtp,
                "port": self._port_smtp,
                'tls': self._activation_tls
            }

            # if self._legacy_tls_support and self._activation_tls:
            #    smtp_kwargs["context"] = SSLContext(protocol=PROTOCOL_TLS)
            #    smtp_kwargs['context'].options = OP_ALL

            if self._nom_utilisateur is not None and self._mot_de_passe is not None:
                smtp_kwargs.update(
                    {
                        'user': self._nom_utilisateur,
                        'password': self._mot_de_passe
                    }
                )

            response = m.send(
                smtp=smtp_kwargs
            )

            logger.debug(response)

        except SMTPConnectNetworkError as e:
            logger.error(
                _(
                    "L'action '{action_nom}' est en échec car il est impossible de se connecter au serveur SMTP '{srv_smtp}' distant. "
                    "Veuillez vérifier votre configuration SMTP. {msg_err}."),
                action_nom=self.designation,
                srv_smtp=self._hote_smtp + ':' + str(self._port_smtp),
                msg_err=str(e)
            )
            return self._jai_echouee(source, str(e))
        except SMTPServerDisconnected as e:
            logger.error(
                _(
                    "L'action '{action_nom}' est en échec car le server '{srv_smtp}' distant n'a pas répondu correctement à un de nos échanges. {msg_err}."),
                action_nom=self.designation,
                srv_smtp=self._hote_smtp + ':' + str(self._port_smtp),
                msg_err=str(e)
            )
            return self._jai_echouee(source, str(e))
        except ValueError as e:
            logger.error(
                _("L'action '{action_nom}' est en échec car il est impossible de lire les adresses destinataires "
                  "Veuillez vérifier vos adresses. [{msg_err} :: {mail_to}]."),
                action_nom=self.designation,
                msg_err=str(e),
                mail_to=str(destinaires_adresses_valides[0] if len(
                    destinaires_adresses_valides) == 1 else destinaires_adresses_valides)
            )
            return self._jai_echouee(source, str(e))

        if response.status_code not in [250, ]:
            logger.warning(
                _(
                    "L'action '{action_nom}' est en échec car le serveur SMTP '{srv_smtp}' distant à refusé d'envoyer votre message. "
                    "Le serveur a répondu avec le code {smtp_code} ({smtp_err}). Veuillez vérifier votre configuration SMTP."),
                action_nom=self.designation,
                srv_smtp=self._hote_smtp + ':' + str(self._port_smtp),
                smtp_code=str(response.status_code),
                smtp_err=response.error
            )

            return self._jai_echouee(source, response)

        return self._jai_reussi(source, response)


class TransfertSmtpActionNoeud(ManipulationSmtpActionNoeud):

    def __init__(self, designation, destinataire, sujet, hote_smtp, port_smtp, nom_utilisateur, mot_de_passe,
                 enable_tls=True, legacy_tls_support=False):
        super().__init__(designation, hote_smtp, nom_utilisateur, mot_de_passe)

        self._destinataire = destinataire
        self._sujet = sujet
        self._activation_tls = enable_tls
        self._port_smtp = port_smtp
        self._legacy_tls_support = legacy_tls_support

    def je_realise(self, source):
        """

        :param gie_interoperabilite.mail.Mail source:
        :return:
        """
        super().je_realise(source)

        message_from_field = source.destinataire if isinstance(source.destinataire, list) is False else source.destinataire[-1]

        if self._nom_utilisateur.split('@')[0] not in message_from_field:

            logger.warning(
                _("L'action '{action_nom}' ne reconnais pas l'adresse '{source_addr_to}' "
                  "pour être utilisée en tant qu'expéditeur.").format(
                    action_nom=self._designation,
                    source_addr_to=message_from_field
                )
            )

            message_from_field = '{smtp_username}@{smtp_domain}'.format(
                smtp_username=self._nom_utilisateur.split('@')[0],
                smtp_domain=message_from_field.split('@')[-1]
            )

            logger.info(
                _("L'action '{action_nom}' va utiliser '{source_addr_to}' "
                  "pour être utilisée en tant qu'expéditeur.").format(
                    action_nom=self._designation,
                    source_addr_to=message_from_field
                )
            )

        m = emails.Message(html=source.extract_body('html', strict=True),
                           text=source.extract_body('plain', strict=True),
                           subject=self._sujet,
                           mail_from=message_from_field)

        for attachement in source.attachements:
            m.attach(filename=attachement.filename, data=BytesIO(attachement.content), content_disposition='attachment')

        destinaires_adresses_valides = list()
        destinataires_copies_cachees_valides = list()
        destinataire_copies_visibles_valides = list()

        for dest in [self._destinataire] if ',' not in self._destinataire else [destinataire.strip(' ') for destinataire
                                                                                in self._destinataire.split(',')]:

            type_copie = None

            if 'cc:' in dest.lower():
                type_copie, dest = dest.split(':')
            elif 'bcc:' in dest.lower():
                type_copie, dest = dest.split(':')

            if re.fullmatch(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', dest) is None:
                logger.warning(
                    _("Action '{action_nom}': Impossible d'émettre un message à cette adresse '{addr_cible}' "
                      "car elle ne respecte pas le RFC 5322"),
                    action_nom=self.designation,
                    addr_cible=dest
                )
                continue

            if type_copie is None:
                destinaires_adresses_valides.append(dest)
            elif type_copie.lower() == 'cc':
                destinataire_copies_visibles_valides.append(dest)
            elif type_copie.lower() == 'bcc':
                destinataires_copies_cachees_valides.append(dest)

        m.set_cc(destinataire_copies_visibles_valides)
        m.set_bcc(destinataires_copies_cachees_valides)
        m.set_mail_to(destinaires_adresses_valides)

        if len(destinaires_adresses_valides) == 0 and len(destinataire_copies_visibles_valides) == 0 and len(destinataires_copies_cachees_valides) == 0:
            logger.error(
                _("Action '{action_nom}': Impossible d'émettre un message car aucune adresse valide n'est disponible "
                  "au sens de la RFC 5322"),
                action_nom=self.designation
            )
            return self._jai_echouee(source)

        try:

            smtp_kwargs = {
                "host": self._hote_smtp,
                "port": self._port_smtp,
                'tls': self._activation_tls
            }

            # if self._legacy_tls_support and self._activation_tls:
            #     smtp_kwargs["context"] = SSLContext(protocol=PROTOCOL_TLS)
            #     smtp_kwargs['context'].options = OP_ALL

            if self._nom_utilisateur is not None and self._mot_de_passe is not None:
                smtp_kwargs.update(
                    {
                        'user': self._nom_utilisateur,
                        'password': self._mot_de_passe
                    }
                )

            logger.debug(
                _(
                    "Tentative de sollicitation du serveur SMTP pour expédier à '{mail_to}' le message '{mail_subject}'."),
                mail_to=destinaires_adresses_valides[0] if len(
                    destinaires_adresses_valides) == 1 else _(' ET ').join(destinaires_adresses_valides),
                mail_subject=self._sujet
            )

            response = m.send(
                smtp=smtp_kwargs
            )

            logger.debug(response)

        except SMTPConnectNetworkError as e:
            logger.error(
                _("L'action '{action_nom}' est en échec car il est impossible de se connecter au serveur SMTP distant. "
                  "Veuillez vérifier votre configuration SMTP. {smtp_err}."),
                action_nom=self.designation,
                smtp_err=str(e)
            )
            return self._jai_echouee(source, str(e))
        except SMTPServerDisconnected as e:
            logger.error(
                _(
                    "L'action '{action_nom}' est en échec car le server '{srv_smtp}' distant n'a pas répondu correctement à un de nos échanges. {msg_err}."),
                action_nom=self.designation,
                srv_smtp=self._hote_smtp + ':' + str(self._port_smtp),
                msg_err=str(e)
            )
            return self._jai_echouee(source, str(e))

        if response.status_code not in [250, ]:
            logger.warning(
                _("L'action '{action_nom}' est en échec car le serveur SMTP distant à refusé d'envoyer votre message. "
                  "Le serveur a répondu avec le code {smtp_err}. Veuillez vérifier votre configuration SMTP."),
                action_nom=self.designation,
                smtp_err=str(response.status_code)
            )
            return self._jai_echouee(source, response)

        return self._jai_reussi(source, response)


class ConstructionInteretActionNoeud(ActionNoeud):

    def __init__(self, designation, interet, friendly_name):
        super().__init__(designation, friendly_name=friendly_name)
        self._interet = interet

    def je_realise(self, source):

        try:
            super().je_realise(source)
        except KeyError as e:
            logger.warning(
                _("L'action '{action_nom}' est en échec car une variable n'a pas pu être résolue. "
                  "{msg_err}"),
                action_nom=self.designation,
                msg_err=str(e)
            )
            source.session.sauver(self._designation if self._friendly_name is None else self._friendly_name, None)
            return self._jai_echouee(source)

        source.session.sauver(self._designation if self._friendly_name is None else self._friendly_name, self._interet)

        return self._jai_reussi(source, str(self._interet))


class ConstructionChaineCaractereSurListeActionNoeud(ActionNoeud):

    def __init__(self, designation, variable_pattern, separateur, friendly_name):
        super().__init__(designation, friendly_name=friendly_name)
        self._variable_pattern = variable_pattern  # type: str
        self._separateur = separateur

    def je_realise(self, source):

        logger.info(_("Démarrage de l'action '{action_nom}' sur '{source_nom}'"), action_nom=self._designation,
                    source_nom=source.titre)

        self._success = False

        if self._variable_pattern.startswith('{{') is False or self._variable_pattern.endswith('}}') is False:
            logger.error(
                _("L'action '{action_nom}' sur la source '{source_nom}' est en échec : {msg_err}"),
                action_nom=self._designation, source_nom=source.titre,
                msg_err=_('Argument variable avec pattern liste identifiable non précisé, '
                          'une variable est forcement de la forme suivante : {{ ma_variable }}'))
            return self._jai_echouee(source)

        sous_niveau_index_regex = re.compile(r'.[\d]+')

        if len(re.findall(sous_niveau_index_regex, self._variable_pattern)) == 0:
            logger.error(
                _("L'action '{action_nom}' sur la source '{source_nom}' est en échec : {msg_err}"),
                action_nom=self._designation, source_nom=source.titre,
                msg_err=_('Argument variable avec pattern liste identifiable non identifiable, '
                          'aucun entier ne peut être découvert pour itérer '
                          'sur une liste tel que : {{ ma_variable.0.adresse_mail }}, '
                          'alors que vous donnez: {pattern_arg}').format(pattern_arg=self._variable_pattern))
            return self._jai_echouee(source)

        mes_decouvertes = list()

        logger.info(
            _("L'action '{action_nom}' débute une auto-découverte d'une liste à partir de '{pattern}'").format(
                action_nom=self._designation,
                pattern=self._variable_pattern
            )
        )

        try:
            mes_decouvertes.append(
                source.session.retranscrire(
                    self._variable_pattern
                )
            )
        except KeyError as e:
            logger.error(
                _("L'action '{action_nom}' sur la source '{source_nom}' est en échec : {msg_err}"),
                action_nom=self._designation, source_nom=source.titre,
                msg_err=_('Argument variable avec pattern liste identifiable mais non résolvable, '
                          'le premier niveau ne donne pas de résolution : {msg_err}').format(msg_err=str(e)))
            return self._jai_echouee(source)
        except TypeError as e:
            logger.error(
                _("L'action '{action_nom}' sur la source '{source_nom}' est en échec : {msg_err}"),
                action_nom=self._designation, source_nom=source.titre,
                msg_err=_('Argument variable avec pattern liste identifiable mais le type de sortie est inconnu, '
                          'le premier niveau ne donne pas de résolution avec type identifiable : {msg_err}').format(
                    msg_err=str(e)))
            return self._jai_echouee(source)
        except IndexError as e:
            logger.error(
                _("L'action '{action_nom}' sur la source '{source_nom}' est en échec : {msg_err}"),
                action_nom=self._designation, source_nom=source.titre,
                msg_err=_('Argument variable avec pattern liste identifiable mais non résolvable, '
                          'le premier niveau ne donne pas de résolution : {msg_err}').format(msg_err=str(e)))
            return self._jai_echouee(source)

        while True:
            correspondance = re.findall(sous_niveau_index_regex, self._variable_pattern)[-1]
            nouvel_index_list = int(correspondance[1:]) + 1

            if self._variable_pattern.count(correspondance) > 1:
                pass

            self._variable_pattern = self._variable_pattern.replace(correspondance, '.' + str(nouvel_index_list))

            try:
                mes_decouvertes.append(
                    source.session.retranscrire(
                        self._variable_pattern
                    )
                )
            except KeyError:
                break
            except IndexError:
                break

        source.session.sauver(self._designation if self._friendly_name is None else self._friendly_name,
                              self._separateur.join(mes_decouvertes))

        return self._jai_reussi(source, self._separateur.join(mes_decouvertes))


class ExecutionAutomateActionNoeud(ActionNoeud):

    def __init__(self, designation, mon_automate, friendly_name=None):
        """
        :param str designation:
        :param Automate mon_automate:
        :param str friendly_name:
        """
        super().__init__(designation, friendly_name)
        self._automate = mon_automate

    def je_realise(self, source):
        super().je_realise(source)

        try:
            r = self._automate.lance_toi(source, bypass_detecteur=True)
        except KeyError as e:
            return self._jai_echouee(source, str(e))
        except ValueError as e:
            return self._jai_echouee(source, str(e))
        except Exception as e:
            return self._jai_echouee(source, str(e))

        if r:
            return self._jai_reussi(source, self._automate.derniere_action_lancee.payload)

        return self._jai_echouee(source, self._automate.derniere_action_lancee.payload)


class ManipulationRudimentaireSourceActionNoeud(ActionNoeud):

    def __init__(self, designation, friendly_name=None):
        super().__init__(designation, friendly_name)
        self._maximum_retries = 1


class DeplacerMailSourceActionNoeud(ManipulationRudimentaireSourceActionNoeud):

    def __init__(self, designation, dossier_destination):

        super().__init__(designation)
        self._dossier_destination = dossier_destination

    def je_realise(self, source):

        super().je_realise(source)

        if source.factory is None:
            logger.error(
                _("L'action '{action_nom}' sur la source '{source_nom}' est en échec : {msg_err}"),
                action_nom=self._designation, source_nom=source.titre,
                msg_err=_('Aucune usine à production n\'est associée à la source'))
            return self._jai_echouee(source)

        try:
            source.factory.deplacer(
                source,
                self._dossier_destination
            )
        except FileNotFoundError as e:
            logger.error(
                _("L'action '{action_nom}' sur la source '{source_nom}' est en échec : {msg_err}"), self._designation,
                source.titre, str(e))
            return self._jai_echouee(source)
        except ManipulationSourceException as e:

            if self._maximum_retries > 0 and self._n_retries < self._maximum_retries:
                logger.warning(
                    _("L'action '{action_nom}' sur la source '{source_nom}' est en échec, "
                      "l'usine ayant produit la source n'a pas pu effectuer "
                      "un changement sur la source : {msg_err}"), action_nom=self._designation, source_nom=source.titre,
                    msg_err=str(e))

                self._n_retries += 1
                return self.je_realise(source)

            logger.error(
                _("L'action '{action_nom}' sur la source '{source_nom}' est en échec, "
                  "l'usine ayant produit la source n'a pas pu effectuer "
                  "un changement sur la source : {msg_err}"), action_nom=self._designation, source_nom=source.titre,
                msg_err=str(e))
            return self._jai_echouee(source)

        return self._jai_reussi(source)


class CopierMailSourceActionNoeud(ManipulationRudimentaireSourceActionNoeud):

    def __init__(self, designation, dossier_destination):
        super().__init__(designation)
        self._dossier_destination = dossier_destination

    def je_realise(self, source):

        super().je_realise(source)

        if source.factory is None:
            logger.error(
                _("L'action '{action_nom}' sur la source '{source_nom}' est en échec : {msg_err}"),
                action_nom=self._designation, source_nom=source.titre,
                msg_err=_('Aucune usine à production n\'est associée à la source'))
            return self._jai_echouee(source)

        try:
            source.factory.copier(
                source,
                self._dossier_destination
            )
        except FileNotFoundError as e:
            logger.error(
                _("L'action '{action_nom}' sur la source '{source_nom}' est en échec : {msg_err}"),
                action_nom=self._designation, source_nom=source.titre, msg_err=str(e))
            return self._jai_echouee(source)
        except ManipulationSourceException as e:

            if self._maximum_retries > 0 and self._n_retries < self._maximum_retries:
                logger.warning(
                    _("L'action '{action_nom}' sur la source '{source_nom}' est en échec, "
                      "l'usine ayant produit la source n'a pas pu effectuer "
                      "un changement sur la source : {msg_err}"), action_nom=self._designation, source_nom=source.titre,
                    msg_err=str(e))

                self._n_retries += 1
                return self.je_realise(source)

            logger.error(
                _("L'action '{action_nom}' sur la source '{source_nom}' est en échec, "
                  "l'usine ayant produit la source n'a pas pu effectuer "
                  "un changement sur la source : {msg_err}"), action_nom=self._designation, source_nom=source.titre,
                msg_err=str(e))
            return self._jai_echouee(source)

        return self._jai_reussi(source)


class SupprimerMailSourceActionNoeud(ManipulationRudimentaireSourceActionNoeud):

    def __init__(self, designation):
        super().__init__(designation)

    def je_realise(self, source):

        super().je_realise(source)

        if source.factory is None:
            logger.error(
                _("L'action '{action_nom}' sur la source '{source_nom}' est en échec : {msg_err}"),
                action_nom=self._designation, source_nom=source.titre,
                msg_err='Aucune usine à production n\'est associée à la source')
            return self._jai_echouee(source)

        try:
            source.factory.supprimer(
                source
            )
        except ManipulationSourceException as e:

            if self._maximum_retries > 0 and self._n_retries < self._maximum_retries:
                logger.warning(
                    _("L'action '{action_nom}' sur la source '{source_nom}' est en échec, "
                      "l'usine ayant produit la source n'a pas pu effectuer "
                      "un changement sur la source : {msg_err}"), action_nom=self._designation, source_nom=source.titre,
                    msg_err=str(e))

                self._n_retries += 1
                return self.je_realise(source)

            logger.error(
                _("L'action '{action_nom}' sur la source '{source_nom}' est en échec, "
                  "l'usine ayant produit la source n'a pas pu effectuer "
                  "un changement sur la source : {msg_err}"), action_nom=self._designation, source_nom=source.titre,
                msg_err=str(e))
            return self._jai_echouee(source)

        return self._jai_reussi(source)


class TransformationListeVersDictionnaireActionNoeud(ActionNoeud):

    def __init__(self, designation, resultat_concerne, champ_cle, champ_valeur, friendly_name):
        super().__init__(designation, friendly_name=friendly_name)

        self._resultat_concerne = resultat_concerne
        self._champ_cle = champ_cle
        self._champ_valeur = champ_valeur

    def je_realise(self, source):

        super().je_realise(source)

        if self._resultat_concerne not in source.session.elements:
            logger.error(
                _(
                    "L'action '{action_nom}' sur '{source_nom}' est en échec car votre cible '{resultat}' n'existe pas (1)"),
                action_nom=self._designation,
                source_nom=source.titre, resultat=self._resultat_concerne)
            return self._jai_echouee(source)

        try:
            ma_retranscription = source.session.retranscrire('{{ ' + self._resultat_concerne + ' }}')
        except KeyError as e:
            logger.error(
                _(
                    "L'action '{action_nom}' sur '{source_nom}' est en échec car votre cible '{resultat}' n'existe pas : {msg_err}"),
                action_nom=self._designation,
                source_nom=source.titre, resultat=self._resultat_concerne, msg_err=str(e))
            return self._jai_echouee(source)

        resultat_transformation = dict()

        try:
            ma_retranscription = loads(ma_retranscription)
        except JSONDecodeError as e:
            logger.error(
                _(
                    "L'action '{action_nom}' sur '{source_nom}' est en échec car votre cible n'est pas un objet serializable : {msg_err}"),
                action_nom=self._designation, source_nom=source.titre, msg_err=str(e))
            return self._jai_echouee(source)

        if isinstance(ma_retranscription, list) is False:
            logger.error(
                _("L'action '{action_nom}' sur '{source_nom}' est en échec car votre cible n'est pas une liste"),
                action_nom=self._designation,
                source_nom=source.titre)
            return self._jai_echouee(source)

        for mon_element in ma_retranscription:

            if isinstance(mon_element, dict) is False:
                return self._jai_echouee(source)

            if self._champ_cle not in mon_element.keys() or self._champ_valeur not in mon_element.keys():
                return self._jai_echouee(source)

            resultat_transformation[mon_element[self._champ_cle]] = mon_element[self._champ_valeur]

        source.session.sauver(self._designation if self._friendly_name is None else self._friendly_name,
                              resultat_transformation)

        return self._jai_reussi(source, resultat_transformation)
