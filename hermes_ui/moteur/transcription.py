from hermes.detecteur import *
from hermes.automate import *

from hermes_ui.db import db

import hermes_ui.models

from json import loads


class ServiceTranspositionModels:

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

        :param hermes_ui.models.detecteur.RechercheInteret regle:
        :return:
        """

        ma_recherche_interet = None

        if '.IdentificateurRechercheInteret' in regle.mapped_class_child:
            regle = db.session.query(hermes_ui.models.IdentificateurRechercheInteret).get(regle.id)

            ma_recherche_interet = IdentificateurRechercheInteret(
                regle.designation,
                regle.prefixe,
                est_obligatoire=regle.est_obligatoire,
                friendly_name=regle.friendly_name,
                focus_cle=regle.focus_cle
            )

        elif '.DateRechercheInteret' in regle.mapped_class_child:

            regle = db.session.query(hermes_ui.models.DateRechercheInteret).get(regle.id)

            ma_recherche_interet = DateRechercheInteret(
                regle.designation,
                regle.prefixe,
                est_obligatoire=regle.est_obligatoire,
                friendly_name=regle.friendly_name,
                focus_cle=regle.focus_cle
            )

        elif '.LocalisationExpressionRechercheInteret' in regle.mapped_class_child:

            regle = db.session.query(hermes_ui.models.LocalisationExpressionRechercheInteret).get(regle.id)

            ma_recherche_interet = LocalisationExpressionRechercheInteret(
                regle.designation,
                regle.expression_droite,
                regle.expression_gauche,
                est_obligatoire=regle.est_obligatoire,
                friendly_name=regle.friendly_name,
                focus_cle=regle.focus_cle
            )

        elif '.ExpressionCleRechercheInteret' in regle.mapped_class_child:

            regle = db.session.query(hermes_ui.models.ExpressionCleRechercheInteret).get(regle.id)

            ma_recherche_interet = ExpressionCleRechercheInteret(
                regle.designation,
                regle.expression_cle,
                est_obligatoire=regle.est_obligatoire,
                friendly_name=regle.friendly_name,
                focus_cle=regle.focus_cle
            )

        elif '.CleRechercheInteret' in regle.mapped_class_child:

            regle = db.session.query(hermes_ui.models.CleRechercheInteret).get(regle.id)

            ma_recherche_interet = CleRechercheInteret(
                regle.designation,
                regle.cle_recherchee,
                est_obligatoire=regle.est_obligatoire,
                friendly_name=regle.friendly_name
            )

        elif '.ExpressionDansCleRechercheInteret' in regle.mapped_class_child:

            regle = db.session.query(hermes_ui.models.ExpressionDansCleRechercheInteret).get(regle.id)

            ma_recherche_interet = ExpressionDansCleRechercheInteret(
                regle.designation,
                regle.cle_recherchee,
                regle.expression_recherchee,
                est_obligatoire=regle.est_obligatoire,
                friendly_name=regle.friendly_name
            )

        elif '.InformationRechercheInteret' in regle.mapped_class_child:

            regle = db.session.query(hermes_ui.models.InformationRechercheInteret).get(regle.id)

            ma_recherche_interet = InformationRechercheInteret(
                regle.designation,
                regle.information_cible,
                est_obligatoire=regle.est_obligatoire,
                friendly_name=regle.friendly_name,
                focus_cle=regle.focus_cle
            )

        elif '.ExpressionReguliereRechercheInteret' in regle.mapped_class_child:

            regle = db.session.query(hermes_ui.models.ExpressionReguliereRechercheInteret).get(regle.id)

            ma_recherche_interet = ExpressionReguliereRechercheInteret(
                regle.designation,
                regle.expression_reguliere,
                regle.focus_cle,
                regle.est_obligatoire,
                regle.friendly_name
            )

        elif '.OperationLogiqueRechercheInteret' in regle.mapped_class_child:

            regle = db.session.query(hermes_ui.models.OperationLogiqueRechercheInteret).get(regle.id)

            kwargs = dict()

            for sous_regle in regle.sous_regles:
                kwargs['ma_cond_{}'.format(sous_regle.id)] = ServiceTranspositionModels.generer_recherche_interet(
                    sous_regle
                )

            kwargs['friendly_name'] = regle.friendly_name

            ma_recherche_interet = OperationLogiqueRechercheInteret(
                regle.designation,
                regle.operande,
                **kwargs
            )

        return ma_recherche_interet

    @staticmethod
    def generer_arbre_action_noeud(action):
        """

        :param hermes_ui.models.automate.ActionNoeud action:
        :return:
        """
        if action is None:
            return None

        action = db.session.query(action.mapped_class_child).get(
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

