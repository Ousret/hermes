from json import dumps, loads
from re import findall, sub
from glob import glob

from slugify import slugify
from yaml import load, FullLoader
from json import loads as json_loads
from dateutil.parser import parse
from dateutil import relativedelta
from copy import deepcopy
from datetime import timedelta


class SessionFiltre:
    FILTRES = list()  # type: list[SessionFiltre]

    def __init__(self, methode, fonction, types=None):
        """
        :param str methode:
        :param type fonction:
        :param list[type] types:
        """
        self._methode = methode
        self._fonction = fonction
        self._types = types

    @property
    def methode(self):
        return self._methode

    def filtrer(self, ma_variable):
        if self._types is not None:
            if any([isinstance(ma_variable, supported_type) for supported_type in self._types]) is False:
                raise TypeError(
                    "Impossible d'appliquer le filtre '{filtre_nom}' sur une variable de type '{variable_type}'.".format(
                        filtre_nom=self.methode,
                        variable_type=type(ma_variable)
                    )
                )

        return self._fonction(ma_variable)

    def __repr__(self):
        return self._methode


class Session:

    UNIVERSELLE = None  # type: Session

    def __init__(self):
        self._elements = dict()

    @staticmethod
    def variables(dict_, prefix=''):
        """

        :param dict dict_:
        :param str prefix:
        :return:
        """
        current_level_keys = [prefix+ma_cle for ma_cle in dict_.keys()]
        next_level_keys = list()

        for current_level_key in dict_.keys():
            if isinstance(dict_[current_level_key], dict) is True:
                next_level_keys += Session.variables(dict_[str(current_level_key)], prefix+str(current_level_key)+'.')
        return list(current_level_keys)+next_level_keys

    @property
    def variables_disponibles(self):
        return Session.variables(self._elements)

    @staticmethod
    def charger(dossier_src='./configurations'):
        fichiers_eligibles = glob("{dossier_dest}{slash}*.yml".format(dossier_dest=dossier_src, slash='/' if not dossier_src.endswith('/') else ''))
        for fichier_configuration in fichiers_eligibles:
            with open(fichier_configuration, 'r') as fp:
                output = load(fp, Loader=FullLoader)
                if not isinstance(output, dict):
                    raise TypeError('')
                for key in output.keys():
                    Session.UNIVERSELLE.sauver(key, output[key])
        return fichiers_eligibles

    @staticmethod
    def charger_input(designation, input_configuration, format_str='yaml'):

        if format_str.lower() == 'json' or format_str.lower() == 'yaml':
            try:
                output = load(input_configuration, Loader=FullLoader) if format_str == 'yaml' else json_loads(input_configuration)
            except Exception as e:
                raise TypeError(str(e))

            if not isinstance(output, dict):
                raise TypeError('')
            for key in output.keys():
                Session.UNIVERSELLE.sauver(key, output[key])

            return

        Session.UNIVERSELLE.sauver(designation, input_configuration)

    @property
    def nb_element(self):
        return len(self._elements)

    @property
    def elements(self):
        return self._elements.keys()

    def sauver(self, cle, element):
        """

        :param str cle:
        :param element:
        :return:
        """
        self._elements[cle.lower()] = element

    def __eq__(self, other):
        """
        :param Session other:
        :return:
        """
        return self.nb_element == other.nb_element and self.elements == other.elements

    def retranscrire(self, donnees):
        """
        :param donnees:
        :return:
        """

        if isinstance(donnees, str):
            return Session.UNIVERSELLE.retranscrire(
                self._remplacer(donnees, strict_mode=False)
            ) if self != Session.UNIVERSELLE else self._remplacer(donnees)
        if isinstance(donnees, dict) or isinstance(donnees, list) or isinstance(donnees, tuple):
            return Session.UNIVERSELLE.retranscrire(
                loads(
                    self._remplacer(
                        dumps(donnees),
                        strict_mode=False,
                        escape_child=True
                    ), strict=False
                )
            ) if self != Session.UNIVERSELLE else loads(
                    self._remplacer(
                        dumps(donnees),
                        escape_child=True,
                    ), strict=False
                )
        raise TypeError("Impossible d'effectuer une retranscription de l'information sur un type '{}' !".format(type(donnees)))

    @staticmethod
    def _should_replace(ma_str):
        return len(findall(r'{{[a-zA-Z0-9éàèç_|\-:. ]{2,}}}', ma_str))

    def _remplacer(self, ma_str, strict_mode=True, escape_child=False):
        """

        :param str ma_str:
        :return:
        """

        nb_key_mismatch = 0

        while Session._should_replace(ma_str)-nb_key_mismatch > 0:
            correspondances = findall(r'{{[a-zA-Z0-9éàèç_|\-:. ]{2,}}}', ma_str)
            for correspondance in correspondances:
                cle_recherchee_filtres = correspondance.replace('{', '').replace('}', '').replace(' ', '').lower().split('|')

                cle_recherchee = cle_recherchee_filtres[0]
                filtres = cle_recherchee_filtres[1:]

                sous_niveaux = cle_recherchee.split('.')
                valeur_dernier_niveau = self._elements
                etage = 0

                try:
                    for el, etage in zip(sous_niveaux, range(0, len(sous_niveaux))):
                        if isinstance(valeur_dernier_niveau, dict):
                            dict_case_insensible = {k.lower(): v for k, v in valeur_dernier_niveau.items()}
                            dict_case_insensible_keys = dict_case_insensible.keys()
                            if el.isdigit() is True and el not in dict_case_insensible_keys and int(el)+1 <= len(dict_case_insensible_keys):
                                el = list(dict_case_insensible_keys)[int(el)]
                            if el.lower() not in dict_case_insensible.keys():
                                raise KeyError(
                                    "Transcription du champs '{}' impossible car inexistant{}.".format(
                                        cle_recherchee,
                                        ", sous-niveau '{}'".format(el) if etage > 0 else ''
                                    )
                                )
                            valeur_dernier_niveau = dict_case_insensible[el.lower()]
                        elif isinstance(valeur_dernier_niveau, list):
                            if el.isdigit() is False or int(el) > len(valeur_dernier_niveau) - 1:
                                raise KeyError(
                                    "Transcription du champs '{}' impossible car index {} de liste hors limite".format(
                                        cle_recherchee,
                                        el
                                    )
                                )
                            valeur_dernier_niveau = valeur_dernier_niveau[int(el)]
                        else:
                            raise KeyError(
                                "Transcription du champs '{}' impossible car il n'y a "
                                "pas de sous niveaux pour le type {}.".format(
                                    cle_recherchee,
                                    type(valeur_dernier_niveau)
                                )
                            )
                except KeyError as e:
                    if strict_mode is True or etage > 0:
                        raise KeyError(e)
                    nb_key_mismatch += 1
                    continue

                try:
                    for filtre in filtres:
                        for filtre_existant in SessionFiltre.FILTRES:
                            if filtre_existant.methode.lower() == filtre.lower():
                                valeur_dernier_niveau = filtre_existant.filtrer(valeur_dernier_niveau)
                except TypeError as e:
                    raise TypeError("{msg_error_filtre} :: Variable '{variable_nom}'".format(msg_error_filtre=str(e), variable_nom=correspondance))

                if isinstance(valeur_dernier_niveau, str) or isinstance(valeur_dernier_niveau, float) or isinstance(valeur_dernier_niveau, int):
                    ma_str = ma_str.replace(correspondance, str(valeur_dernier_niveau))
                elif isinstance(valeur_dernier_niveau, dict) or isinstance(valeur_dernier_niveau, list):
                    dumps_v = dumps(valeur_dernier_niveau)
                    ma_str = ma_str.replace(correspondance, dumps_v.replace('"', '\\"') if escape_child is True else dumps_v)
                else:
                    raise TypeError("Transcription du champs '{}' sur le niveau '{}' impossible car format invalide: '{}'".format(cle_recherchee, el if len(sous_niveaux) > 1 else cle_recherchee, type(valeur_dernier_niveau)))

        return ma_str


Session.UNIVERSELLE = Session()

SessionFiltre.FILTRES.append(
    SessionFiltre(
        'escapeQuote',
        lambda ma_variable: dumps(str(ma_variable))[1:-1]
    )
)

SessionFiltre.FILTRES.append(
    SessionFiltre(
        'keys',
        lambda ma_variable: list(ma_variable.keys()) if isinstance(ma_variable, dict) else ma_variable,
        [
            dict
        ]
    )
)

SessionFiltre.FILTRES.append(
    SessionFiltre(
        'int',
        lambda ma_variable: int(sub(r'\D', '', ma_variable)) if isinstance(ma_variable, str) else ma_variable
    )
)

SessionFiltre.FILTRES.append(
    SessionFiltre(
        'float',
        lambda ma_variable: float(sub(r'[^\d.]', '', ma_variable.replace(',', '.'))) if isinstance(ma_variable, str) else ma_variable
    )
)

SessionFiltre.FILTRES.append(
    SessionFiltre(
        'lower',
        lambda ma_variable: ma_variable.lower() if isinstance(ma_variable, str) else ma_variable
    )
)

SessionFiltre.FILTRES.append(
    SessionFiltre(
        'upper',
        lambda ma_variable: ma_variable.upper() if isinstance(ma_variable, str) else ma_variable
    )
)

SessionFiltre.FILTRES.append(
    SessionFiltre(
        'strip',
        lambda ma_variable: ma_variable.strip() if isinstance(ma_variable, str) else ma_variable,
    )
)

SessionFiltre.FILTRES.append(
    SessionFiltre(
        'capitalize',
        lambda ma_variable: ma_variable.capitalize() if isinstance(ma_variable, str) else ma_variable
    )
)

SessionFiltre.FILTRES.append(
    SessionFiltre(
        'dateAjouterUnJour',
        lambda ma_variable: (parse(ma_variable) + timedelta(days=1)).strftime('%Y-%m-%d') if isinstance(ma_variable, str) else ma_variable
    )
)

SessionFiltre.FILTRES.append(
    SessionFiltre(
        'dateAjouterUnMois',
        lambda ma_variable: (parse(ma_variable) + relativedelta(month=1)).strftime('%Y-%m-%d') if isinstance(ma_variable, str) else ma_variable
    )
)

SessionFiltre.FILTRES.append(
    SessionFiltre(
        'dateAjouterUneAnnee',
        lambda ma_variable: (parse(ma_variable) + relativedelta(year=1)).strftime('%Y-%m-%d') if isinstance(ma_variable, str) else ma_variable
    )
)

SessionFiltre.FILTRES.append(
    SessionFiltre(
        'dateRetirerUnJour',
        lambda ma_variable: (parse(ma_variable) + timedelta(days=-1)).strftime('%Y-%m-%d') if isinstance(ma_variable, str) else ma_variable
    )
)

SessionFiltre.FILTRES.append(
    SessionFiltre(
        'dateRetirerUnMois',
        lambda ma_variable: (parse(ma_variable) + relativedelta(month=-1)).strftime('%Y-%m-%d') if isinstance(ma_variable, str) else ma_variable
    )
)

SessionFiltre.FILTRES.append(
    SessionFiltre(
        'dateRetirerUneAnnee',
        lambda ma_variable: (parse(ma_variable) + relativedelta(year=-1)).strftime('%Y-%m-%d') if isinstance(ma_variable, str) else ma_variable
    )
)

SessionFiltre.FILTRES.append(
    SessionFiltre(
        'dateFormatFrance',
        lambda ma_variable: parse(ma_variable).strftime('%d/%m/%Y') if isinstance(ma_variable, str) else ma_variable
    )
)

SessionFiltre.FILTRES.append(
    SessionFiltre(
        'dateFormatUS',
        lambda ma_variable: parse(ma_variable, dayfirst=True).strftime('%Y-%m-%d') if isinstance(ma_variable, str) else ma_variable
    )
)


def prochaine_journee_depuis(date_courante, journee_cible):
    """
    :param datetime.datetime date_courante:
    :param str journee_cible:
    """
    n_iter = 0
    while date_courante.strftime('%A').lower() != journee_cible.lower() or n_iter >= 7:
        date_courante += timedelta(days=+1)
        n_iter+=1
    return date_courante


SessionFiltre.FILTRES.append(
    SessionFiltre(
        'dateProchainLundi',
        lambda ma_variable: prochaine_journee_depuis(parse(ma_variable, dayfirst=True), 'Monday').strftime('%Y-%m-%d'),
        [
            str
        ]
    )
)

SessionFiltre.FILTRES.append(
    SessionFiltre(
        'dateProchainMardi',
        lambda ma_variable: prochaine_journee_depuis(parse(ma_variable, dayfirst=True), 'Thuesday').strftime('%Y-%m-%d'),
        [
            str
        ]
    )
)

SessionFiltre.FILTRES.append(
    SessionFiltre(
        'dateProchainMercredi',
        lambda ma_variable: prochaine_journee_depuis(parse(ma_variable, dayfirst=True), 'Wednesday').strftime('%Y-%m-%d'),
        [
            str
        ]
    )
)

SessionFiltre.FILTRES.append(
    SessionFiltre(
        'dateProchainJeudi',
        lambda ma_variable: prochaine_journee_depuis(parse(ma_variable, dayfirst=True), 'Thursday').strftime('%Y-%m-%d'),
        [
            str
        ]
    )
)

SessionFiltre.FILTRES.append(
    SessionFiltre(
        'dateProchainVendredi',
        lambda ma_variable: prochaine_journee_depuis(parse(ma_variable, dayfirst=True), 'Friday').strftime('%Y-%m-%d'),
        [
            str
        ]
    )
)

SessionFiltre.FILTRES.append(
    SessionFiltre(
        'dateProchainSamedi',
        lambda ma_variable: prochaine_journee_depuis(parse(ma_variable, dayfirst=True), 'Saturday').strftime('%Y-%m-%d'),
        [
            str
        ]
    )
)

SessionFiltre.FILTRES.append(
    SessionFiltre(
        'dateProchainDimanche',
        lambda ma_variable: prochaine_journee_depuis(parse(ma_variable, dayfirst=True), 'Sunday').strftime('%Y-%m-%d'),
        [
            str
        ]
    )
)

SessionFiltre.FILTRES.append(
    SessionFiltre(
        'slug',
        lambda ma_variable: slugify(ma_variable) if isinstance(ma_variable, str) else ma_variable
    )
)

SessionFiltre.FILTRES.append(
    SessionFiltre(
        'alNum',
        lambda ma_variable: ''.join([el for el in ma_variable if el.isalnum() is True]) if isinstance(ma_variable, str) else ma_variable
    )
)

SessionFiltre.FILTRES.append(
    SessionFiltre(
        'alpha',
        lambda ma_variable: ''.join([el for el in ma_variable if el.isalpha() is True]) if isinstance(ma_variable, str) else ma_variable
    )
)

for i, chiffre_lettre in zip(range(1, 10), ['Un', 'Deux', 'Trois', 'Quatre', 'Cinq', 'Six', 'Sept', 'Huit', 'Neuf', 'Dix']):

    SessionFiltre.FILTRES.append(
        SessionFiltre(
            'remplissage{}Zero'.format(chiffre_lettre),
            lambda ma_variable, nb_zero=deepcopy(i): str(ma_variable).zfill(nb_zero) if isinstance(ma_variable, str) or isinstance(ma_variable, int) else ma_variable
        )
    )
