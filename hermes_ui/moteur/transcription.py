from hermes.detecteur import *
from hermes.automate import *

from hermes_ui.db import db

import hermes_ui.models


class ServiceTranspositionModels:

    @staticmethod
    def get_model_class(mapped_class_child):
        """
        Charger la classe correspondant à un chemin complet (dot package) str
        Orienté pour le champs mapped class child SQLAlchemy
        :param str mapped_class_child:
        :rtype: type
        :raise AttributeError:
        """
        decompose_type_action = mapped_class_child.split("'")  # type: list[str]

        if len(decompose_type_action) != 3 or not decompose_type_action[-2].startswith('hermes_ui.models.'):
            return None

        from sys import modules

        target_module = modules['.'.join(decompose_type_action[-2].split('.')[0:-1])]

        return getattr(target_module, decompose_type_action[-2].split('.')[-1])

    @staticmethod
    def generer_detecteur(detecteur):
        """
        :param hermes_ui.models.detecteur.Detecteur detecteur:
        :return:
        :rtype: Detecteur
        """

        mon_detecteur = Detecteur(
            titre=detecteur.designation
        )

        for regle in detecteur.regles:
            mon_detecteur.je_veux(
                ServiceTranspositionModels.generer_recherche_interet(
                    regle
                )
            )

        return mon_detecteur

    @staticmethod
    def generer_recherche_interet(regle):
        """
        Transformation générique d'un critère db.Model vers un objet moteur Hermes
        :param hermes_ui.models.detecteur.RechercheInteret regle:
        :return:
        """
        try:
            target_model_class = ServiceTranspositionModels.get_model_class(regle.mapped_class_child)
        except AttributeError as e:
            return None

        mon_critere = db.session.query(target_model_class).get(regle.id)  # type: hermes_ui.models.RechercheInteret

        if mon_critere is None:
            return None

        ma_recherche_interet = mon_critere.transcription()

        return ma_recherche_interet

    @staticmethod
    def generer_arbre_action_noeud(action):
        """

        :param hermes_ui.models.automate.ActionNoeud action:
        :return:
        """
        if action is None:
            return None

        try:
            target_model_class = ServiceTranspositionModels.get_model_class(action.mapped_class_child)
        except AttributeError as e:
            return None

        action = db.session.query(target_model_class).get(
            action.id)  # type: hermes_ui.models.ActionNoeud
        mon_action_noeud = action.transcription()

        if action.action_reussite is not None:
            mon_action_noeud.je_realise_en_cas_reussite(
                ServiceTranspositionModels.generer_arbre_action_noeud(
                    action.action_reussite
                )
            )

        if action.action_echec is not None:
            mon_action_noeud.je_realise_en_cas_echec(
                ServiceTranspositionModels.generer_arbre_action_noeud(
                    action.action_echec
                )
            )

        return mon_action_noeud

    @staticmethod
    def generer(automates):
        """

        :param list[hermes_ui.models.Automate] automates:
        :return:
        """

        mes_creations = list()  # type: list[Automate]

        for el in automates:

            mon_detecteur = Detecteur(
                el.detecteur.designation
            )

            for regle in el.detecteur.regles:
                mon_detecteur.je_veux(
                    ServiceTranspositionModels.generer_recherche_interet(regle)
                )

            mon_automate = Automate(
                el.designation,
                mon_detecteur
            )

            mon_automate.action_racine = ServiceTranspositionModels.generer_arbre_action_noeud(
                el.action_racine
            )

            mes_creations.append(mon_automate)

        return mes_creations

