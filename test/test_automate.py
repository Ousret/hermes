import unittest
from hermes.automate import *
from hermes.detecteur import *


class FakeSource(Source):

    def __init__(self, titre, corps):
        super().__init__(titre, corps)
        self._titre = titre
        self._corps = corps

    def titre(self):
        return self._titre

    def corps(self):
        return self._corps


ma_source = FakeSource(
    "#Mesures Relève des températures du mois d'Août le 12/12/2020",
    """Réf-091

    Bonjour JOHN DOE !

    Date de mesure : 12/12/2020
    Auteur : Ahmed TAHRI

    Nous avons mesurés à 38 reprises la température de votre ville natale.

    Merci de votre attention.
    """
)

mon_detecteur = Detecteur(
    "Relève de température"
)

mon_detecteur.je_veux(
    IdentificateurRechercheInteret(
        "Recherche de la référence",
        "Réf-",
        friendly_name='reference_releve'
    )
)

mon_detecteur.je_veux(
    DateRechercheInteret(
        "Recherche date de relève",
        "Relève des températures du mois d'Août le",
        friendly_name='date_releve'
    )
)

mon_detecteur.je_veux(
    ExpressionCleRechercheInteret(
        "Recherche d'une phrase à l'identique",
        "Nous avons mesurés à"
    )
)

mon_detecteur.je_veux(
    LocalisationExpressionRechercheInteret(
        "Recherche du nombre de relève température",
        "reprises",
        "Nous avons mesurés à",
        friendly_name='nombre_releve'
    )
)

mon_detecteur.je_veux(
    InformationRechercheInteret(
        "Recherche de hashtag",
        "Mesures"
    )
)

mon_detecteur.je_veux(
    CleRechercheInteret(
        "Présence de Auteur",
        "Auteur"
    )
)

mon_detecteur.je_veux(
    ExpressionDansCleRechercheInteret(
        "Vérifier que Ahmed est auteur",
        "Auteur",
        "Ahmed"
    )
)

action_a = RequeteHttpActionNoeud(
    "Requête sur httpbin",
    "https://httpbin.org/post",
    "POST",
    {
        'nombre_releve': '{{ nombre_releve }}',
        'date_releve': '{{ date_releve }}',
        'id': '{{ reference_releve }}'
    },
    None,
    None,
    200,
    friendly_name='reponse_webservice_httpbin'
)

action_b = ComparaisonVariableActionNoeud(
    "Vérifier la cohérence réponse du website",
    "{{ reponse_webservice_httpbin.form.id }}",
    '==',
    '{{ reference_releve }}',
    None
)


class TestAutomate(unittest.TestCase):
    def test_automate_basic(self):
        mon_automate = Automate(
            "Réaction à la reception des mesures de température",
            mon_detecteur
        )

        mon_automate.action_racine = action_a
        action_a.je_realise_en_cas_reussite(action_b)

        self.assertTrue(
            mon_automate.lance_toi(
                ma_source
            )
        )

        self.assertEqual(
            2,
            len(mon_automate.actions_lancees)
        )


if __name__ == '__main__':
    unittest.main()
