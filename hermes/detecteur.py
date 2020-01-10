from slugify import slugify
import copy
from prettytable import PrettyTable


class AucuneObligationInteretException(Exception):
    pass


class Detecteur(object):

    def __init__(self, titre):
        self._titre = titre
        self._elements = list()  # type: list[RechercheInteret]

    @property
    def elements(self):
        """
        Permet d'obtenir la liste des critères de recherche
        :return:
        """
        return copy.deepcopy(self._elements)

    @property
    def est_contraignant(self):
        for elem in self._elements:
            if elem.est_obligatoire is True:
                return True
        return False

    def raz(self):
        """
        Remet à zéro le détecteur
        :return:
        """
        for el in self._elements:
            el.value = None

    def __eq__(self, autre_detecteur):
        """
        :param Detecteur autre_detecteur:
        :return:
        """
        lst_elements_other = autre_detecteur.elements
        if len(lst_elements_other) != len(self._elements):
            return False
        for elem in lst_elements_other:
            if elem not in self._elements:
                return False
        return True

    @property
    def est_accomplis(self):

        for el in self._elements:
            if el.est_obligatoire is True and el.est_accomplis is False:
                return False

        return True

    def __str__(self):
        return "Je {negation} identifié comme '{ma_designation}'".format(negation="suis bien" if self.est_accomplis else "ne suis pas", ma_designation=self._titre)

    def explain(self):
        """
        :return:
        """
        my_table = PrettyTable()
        my_table.field_names = ["Règle", "Execution", "Obligatoire", "Réussite", "Valeur"]

        for el in self._elements:
            my_table.add_row(
                [
                    el.titre,
                    str(el.value is not None),
                    str(el.est_obligatoire),
                    str(el.est_accomplis),
                    "Aucune" if el.value is None else str(el.value)
                ]
            )

        return my_table.get_string()

    def to_dict(self):
        output_dict = dict()
        for el in self._elements:
            if el.est_accomplis is True and el.value is not None:
                output_dict[slugify(el.titre) if el.friendly_name is None else el.friendly_name] = el.value
        return output_dict

    def lance_toi(self, source):
        """
        :param hermes.source.Source source:
        :return:
        """
        if self.est_contraignant is False:
            raise AucuneObligationInteretException('Aucun des intêrets ne présentent un caractère obligatoire, '
                                                   'le détecteur ne peut pas aboutir')

        for el in self._elements:
            el.tester_sur(source.extraction_interet)

    def je_veux(self, recherche_interet):
        """

        :param RechercheInteret recherche_interet:
        :return:
        """
        if isinstance(recherche_interet, RechercheInteret):
            self._elements.append(recherche_interet)

    def je_veux_cet_identifiant(self, designation, prefixe, est_obligatoire=True):
        self._elements.append(
            IdentificateurRechercheInteret(
                designation,
                prefixe,
                est_obligatoire
            )
        )
        return self

    def je_veux_cette_expression_cle(self, designation, expression, est_obligatoire=True):
        self._elements.append(
            ExpressionCleRechercheInteret(
                designation,
                expression,
                est_obligatoire
            )
        )
        return self

    def je_veux_cette_information_balise(self, designation, information, est_obligatoire=True):
        self._elements.append(
            InformationRechercheInteret(
                designation,
                information,
                est_obligatoire
            )
        )
        return self

    def je_veux_cette_cle_dans_mes_interets(self, designation, ma_cle_recherchee, est_obligatoire=True):
        self._elements.append(
            CleRechercheInteret(
                designation,
                ma_cle_recherchee,
                est_obligatoire
            )
        )
        return self

    def je_veux_cette_expression_dans_ma_cle(self, designation, ma_cle_recherchee, expression_recherchee, est_obligatoire=True):
        self._elements.append(
            ExpressionDansCleRechercheInteret(
                designation,
                ma_cle_recherchee,
                expression_recherchee,
                est_obligatoire
            )
        )
        return self

    def je_souhaite_toute_ces_conditions(self, designation, **kwargs):
        self._elements.append(
            AndOperationLogiqueRechercheInteret(
                designation,
                **kwargs
            )
        )
        return self

    def je_ne_veux_rien_de_ces_conditions(self, designation, **kwargs):
        self._elements.append(
            NotOperationLogiqueRechercheInteret(
                designation,
                **kwargs
            )
        )
        return self

    def je_veux_une_seule_des_conditions(self, designation, **kwargs):
        raise NotImplemented

    def je_souhaite_au_moins_une_condition(self, designation, **kwargs):
        self._elements.append(
            OrOperationLogiqueRechercheInteret(
                designation,
                **kwargs
            )
        )
        return self


class RechercheInteret:

    def __init__(self, titre, est_obligatoire=False, friendly_name=None):

        self._titre = titre
        self._est_obligatoire = est_obligatoire
        self._friendly_name = friendly_name

        self._value = None

    def __eq__(self, other):
        raise NotImplemented

    def __str__(self):
        return "Je {negation} '{ma_designation}'".format(negation="contient bien" if self.est_accomplis else "ne contient pas", ma_designation=self._titre)

    @property
    def friendly_name(self):
        return self._friendly_name

    def tester_sur(self, extraction_interet):
        """
        :param hermes.ExtractionInteret extraction_interet:
        :return:
        """
        raise NotImplemented

    @property
    def est_obligatoire(self):
        return self._est_obligatoire

    @property
    def titre(self):
        return self._titre

    @property
    def value(self):
        return self._value

    @property
    def est_accomplis(self):
        """
        Détermine si une recherche d'intêret est réussite
        :return:
        """
        if self.est_obligatoire is False and self.value is None:
            return False
        if self.est_obligatoire is False and self.value is not None:
            return True
        return self.est_obligatoire is True and (self._value is not None and self._value is not False)

    @value.setter
    def value(self, new_value):
        self._value = new_value


class IdentificateurRechercheInteret(RechercheInteret):

    def __init__(self, titre, prefixe, taille_stricte=None, focus_cle=None, est_obligatoire=True, friendly_name=None):
        """
        :param titre:
        :param str prefixe:
        :param est_obligatoire:
        """
        super().__init__(titre, est_obligatoire, friendly_name)
        self._prefixe = prefixe
        self._focus_cle = focus_cle
        self._taille_stricte = taille_stricte

    def __eq__(self, other):
        """

        :param IdentificateurRechercheInteret other:
        :return:
        """
        return self.prefixe == other.prefixe and self.est_obligatoire == other.est_obligatoire and self.focus_cle == other.focus_cle and self.taille_stricte == other.taille_stricte

    @property
    def prefixe(self):
        return self._prefixe

    @property
    def focus_cle(self):
        return self._focus_cle

    @property
    def taille_stricte(self):
        return self._taille_stricte

    def tester_sur(self, extraction_interet):
        """
        :param hermes.ExtractionInteret extraction_interet:
        :return:
        """

        self.value = extraction_interet.retrieve_identifer(
            self.prefixe,
            focus=self._focus_cle
        )

        if self.value is None:
            self.value = False

        return self.est_accomplis


class ExpressionReguliereRechercheInteret(RechercheInteret):

    def __init__(self, titre, expression_reguliere, focus_cle=None, est_obligatoire=True, friendly_name=None):
        super().__init__(titre, est_obligatoire, friendly_name)
        self._expression_reguliere = expression_reguliere
        self._focus_cle = focus_cle

    @property
    def expression_reguliere(self):
        return self._expression_reguliere

    @property
    def focus_cle(self):
        return self._focus_cle

    def __eq__(self, other):
        """
        :param ExpressionReguliereRechercheInteret other:
        :return:
        """
        return self.expression_reguliere == other.expression_reguliere and self.est_obligatoire == other.est_obligatoire and self.focus_cle == other.focus_cle

    def tester_sur(self, extraction_interet):
        """
        :param hermes.ExtractionInteret extraction_interet:
        :return:
        """

        self.value = extraction_interet.retrieve_expression_reguliere(
            self.expression_reguliere,
            focus=self._focus_cle
        )

        return self.est_accomplis


class ExpressionCleRechercheInteret(RechercheInteret):

    def __init__(self, titre, expression_cle, focus_cle=None, est_obligatoire=True, friendly_name=None):

        super().__init__(titre, est_obligatoire, friendly_name)
        self._expression_cle = expression_cle
        self._focus_cle = focus_cle

    def __eq__(self, other):
        """
        :param ExpressionCleRechercheInteret other:
        :return:
        """
        return self.expression_cle == other.expression_cle and self.est_obligatoire == other.est_obligatoire and self.focus_cle == other.focus_cle

    @property
    def expression_cle(self):
        return self._expression_cle

    @property
    def focus_cle(self):
        return self._focus_cle

    def tester_sur(self, extraction_interet):
        """
        :param hermes.ExtractionInteret extraction_interet:
        :return:
        """

        self.value = extraction_interet.has_expression_cle(
            self.expression_cle,
            focus=self._focus_cle
        )

        return self.est_accomplis


class DateRechercheInteret(RechercheInteret):

    def __init__(self, titre, prefixe, focus_cle=None, est_obligatoire=True, friendly_name=None):
        super().__init__(titre, est_obligatoire, friendly_name)
        self._focus_cle = focus_cle
        self._prefixe = prefixe

    @property
    def prefixe(self):
        return self._prefixe

    @property
    def focus_cle(self):
        return self._focus_cle

    def __eq__(self, other):
        """

        :param DateRechercheInteret other:
        :return:
        """
        return self.prefixe == other.prefixe and self.est_obligatoire == other.est_obligatoire and self.focus_cle == other.focus_cle

    def tester_sur(self, extraction_interet):
        """
        :param hermes.ExtractionInteret extraction_interet:
        :return:
        """
        self.value = extraction_interet.retrieve_date(self._prefixe, focus=self._focus_cle)

        return self.est_accomplis


class CleRechercheInteret(RechercheInteret):

    def __init__(self, titre, cle_recherchee, est_obligatoire=True, friendly_name=None):
        super().__init__(titre, est_obligatoire, friendly_name)
        self._cle_recherchee = cle_recherchee

    @property
    def cle_recherchee(self):
        return self._cle_recherchee

    def __eq__(self, other):
        """

        :param CleRechercheInteret other:
        :return:
        """
        return self.cle_recherchee == other.cle_recherchee and self.est_obligatoire == other.est_obligatoire

    def tester_sur(self, extraction_interet):
        """
        :param hermes.ExtractionInteret extraction_interet:
        :return:
        """

        self.value = extraction_interet.get_interet(self._cle_recherchee) if extraction_interet.has_interet(self._cle_recherchee) else False

        return self.est_accomplis


class ExpressionDansCleRechercheInteret(CleRechercheInteret):

    def __init__(self, titre, cle_recherchee, expression_recherchee, est_obligatoire=True, friendly_name=None):
        super().__init__(titre, cle_recherchee, est_obligatoire, friendly_name)
        self._expression_recherchee = expression_recherchee

    @property
    def expression_recherchee(self):
        return self._expression_recherchee

    def __eq__(self, other):
        """
        :param ExpressionDansCleRechercheInteret other:
        :return:
        """
        return self.expression_recherchee == other.expression_recherchee and self.est_obligatoire == other.est_obligatoire

    def tester_sur(self, extraction_interet):
        if super().tester_sur(extraction_interet):
            self.value = self._expression_recherchee if extraction_interet.has_expression_dans_cle(self._cle_recherchee, self._expression_recherchee) is True else False

        return self.est_accomplis


class ExpressionXPathRechercheInteret(RechercheInteret):

    def __init__(self, titre, expression_xpath, est_obligatoire=True, friendly_name=None):
        super().__init__(titre, est_obligatoire, friendly_name)

        self._expression_xpath = expression_xpath

    @property
    def expression_xpath(self):
        return self._expression_xpath

    def tester_sur(self, extraction_interet):
        """
        :param hermes.analysis.ExtractionInteret extraction_interet:
        :return:
        """
        self.value = extraction_interet.retrieve_xpath(self.expression_xpath)

        return self.est_accomplis


class LocalisationExpressionRechercheInteret(RechercheInteret):

    def __init__(self, titre, expression_droite, expression_gauche, focus_cle=None, est_obligatoire=True, friendly_name=None):
        super().__init__(titre, est_obligatoire, friendly_name)
        self._expression_droite = expression_droite
        self._expression_gauche = expression_gauche
        self._focus_cle = focus_cle

    @property
    def expression_droite(self):
        return self._expression_droite

    @property
    def expression_gauche(self):
        return self._expression_gauche

    @property
    def focus_cle(self):
        return self._focus_cle

    def __eq__(self, other):
        """

        :param LocalisationExpressionRechercheInteret other:
        :return:
        """
        return self.expression_droite == other.expression_droite and self.expression_gauche == other.expression_gauche

    def tester_sur(self, extraction_interet):
        """
        :param hermes.analysis.ExtractionInteret extraction_interet:
        :return:
        """
        self.value = extraction_interet.retrieve_inner_expression(
            self._expression_gauche,
            self._expression_droite,
            focus=self._focus_cle
        )

        return self.est_accomplis


class InformationRechercheInteret(RechercheInteret):

    def __init__(self, titre, information_cible, focus_cle=None, est_obligatoire=True, friendly_name=None):
        super().__init__(titre, est_obligatoire, friendly_name)
        self._information_cible = information_cible
        self._focus_cle = focus_cle

    @property
    def information_cible(self):
        return self._information_cible

    @property
    def focus_cle(self):
        return self._focus_cle

    def __eq__(self, other):
        """

        :param InformationRechercheInteret other:
        :return:
        """
        return self.information_cible == other.information_cible and self.est_obligatoire == other.est_obligatoire

    def tester_sur(self, extraction_interet):
        """
        :param hermes.ExtractionInteret extraction_interet:
        :return:
        """

        self.value = self.information_cible if extraction_interet.has_information(
            self.information_cible,
            focus=self._focus_cle
        ) is True else False

        return self.est_accomplis


class OperationLogiqueRechercheInteret(RechercheInteret):

    def __init__(self, titre, operation, **kwargs):

        super().__init__(titre, est_obligatoire=True, friendly_name=None)

        self._operation = operation.lower()

        if self._operation not in ['and', 'or', 'not', 'xor']:
            raise KeyError('Opérande {} non supporté par OperationLogiqueRechercheInteret'.format(operation))

        self._recherches = list()  # type: list[RechercheInteret]

        for key, value in kwargs.items():

            if key == 'friendly_name' and isinstance(value, str):
                self._friendly_name = value
                continue

            if isinstance(value, RechercheInteret):

                self._recherches.append(
                    value
                )

    @property
    def operation(self):
        return self._operation

    @property
    def criteres(self):
        return copy.deepcopy(self._recherches)

    def __eq__(self, other):
        """

        :param OperationLogiqueRechercheInteret other:
        :return:
        """
        if self.operation != other.operation:
            return False
        lst_critere_other = other.criteres
        if len(lst_critere_other) != len(self._recherches):
            return False
        for critere in lst_critere_other:
            if critere not in self._recherches:
                return False
        return True

    def tester_sur(self, extraction_interet):

        resultats = list()
        resultats_accomplis = list()

        self.value = None

        for el in self._recherches:
            resultats.append(
                el.tester_sur(extraction_interet)
            )
            if resultats[-1]:
                resultats_accomplis.append(el.value)
            if self.operation == 'or' and resultats[-1]:
                self.value = True
                break
            if self.operation == 'not' and resultats[-1]:
                self.value = False
                break

        if self.operation == 'and':
            self.value = all(resultats)
        if self.operation == 'xor':
            self.value = resultats_accomplis.pop() if len(resultats_accomplis) == 1 else False
        if self.operation == 'not':
            self.value = True if self.value is None else False

        return self.est_accomplis


class OrOperationLogiqueRechercheInteret(OperationLogiqueRechercheInteret):

    def __init__(self, titre, **kwargs):
        super().__init__(titre, 'or', **kwargs)


class AndOperationLogiqueRechercheInteret(OperationLogiqueRechercheInteret):

    def __init__(self, titre, **kwargs):
        super().__init__(titre, 'and', **kwargs)


class NotOperationLogiqueRechercheInteret(OperationLogiqueRechercheInteret):

    def __init__(self, titre, **kwargs):
        super().__init__(titre, 'not', **kwargs)
