import unittest
from hermes.source import Source
from hermes.detecteur import *


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


class TestCriteres(unittest.TestCase):

    def test_identifiant(self):

        critere = IdentificateurRechercheInteret(
            "Recherche de la référence",
            "Réf-"
        )

        self.assertTrue(
            critere.tester_sur(ma_source.extraction_interet)
        )

        self.assertEqual(
            critere.value,
            "Réf-091"
        )

    def test_date(self):

        critere = DateRechercheInteret(
            "Recherche date de relève",
            "Relève des températures du mois d'Août le"
        )

        self.assertTrue(
            critere.tester_sur(ma_source.extraction_interet)
        )

        self.assertEqual(
            critere.value,
            ' 12/12/2020'
        )

    def test_expression_exacte(self):

        critere = ExpressionCleRechercheInteret(
            "Recherche d'une phrase à l'identique",
            "Nous avons mesurés à"
        )

        self.assertTrue(
            critere.tester_sur(ma_source.extraction_interet)
        )

        self.assertEqual(
            critere.value,
            True
        )

    def test_localisation_expression(self):

        critere = LocalisationExpressionRechercheInteret(
            "Recherche du nombre de relève température",
            "reprises",
            "Nous avons mesurés à"
        )

        self.assertTrue(
            critere.tester_sur(ma_source.extraction_interet)
        )

        self.assertEqual(
            critere.value,
            '38'
        )

    def test_information(self):

        critere = InformationRechercheInteret(
            "Recherche de hashtag",
            "Mesures"
        )

        self.assertTrue(
            critere.tester_sur(ma_source.extraction_interet)
        )

        self.assertEqual(
            critere.value,
            "Mesures"
        )

    def test_cle_recherche(self):

        critere = CleRechercheInteret(
            "Présence de Auteur",
            "Auteur"
        )

        self.assertTrue(
            critere.tester_sur(ma_source.extraction_interet)
        )

        self.assertEqual(
            critere.value,
            "Ahmed TAHRI"
        )

    def test_expression_exacte_dans_cle(self):

        critere = ExpressionDansCleRechercheInteret(
            "Vérifier que Ahmed est auteur",
            "Auteur",
            "Ahmed"
        )

        self.assertTrue(
            critere.tester_sur(ma_source.extraction_interet)
        )

        self.assertEqual(
            critere.value,
            "Ahmed"
        )


if __name__ == '__main__':
    unittest.main()
