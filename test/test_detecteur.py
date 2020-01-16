import unittest
from hermes.detecteur import *
from hermes.source import Source

ma_source = Source(
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
        "Réf-"
    )
)

mon_detecteur.je_veux(
    DateRechercheInteret(
        "Recherche date de relève",
        "Relève des températures du mois d'Août le"
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
        "Nous avons mesurés à"
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


class TestDetecteur(unittest.TestCase):

    def test_detection(self):

        self.assertTrue(
            mon_detecteur.lance_toi(ma_source)
        )


if __name__ == '__main__':
    unittest.main()
