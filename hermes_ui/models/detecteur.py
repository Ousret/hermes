import datetime

from hermes_ui.adminlte.models import User
from hermes_ui.db import db
from hermes_ui.db.polymorphic import get_child_polymorphic

from hermes.i18n import _


class Detecteur(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    designation = db.Column(db.String(255), nullable=False)

    regles = db.relationship("RechercheInteret", secondary='lien_detecteur_recherche_interet', lazy='joined', enable_typechecks=False, cascade="save-update, merge")  # type: list[RechercheInteret]

    createur_id = db.Column(db.ForeignKey('user.id'), nullable=True)
    createur = db.relationship(User, primaryjoin="User.id==Detecteur.createur_id")

    date_creation = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow())
    date_modification = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow())

    responsable_derniere_modification_id = db.Column(db.ForeignKey('user.id'), nullable=True)
    responsable_derniere_modification = db.relationship(User,
                                                        primaryjoin="User.id==Detecteur.responsable_derniere_modification_id")

    def __repr__(self):
        return _('<Détection DE \'{detecteur_nom}\'>').format(detecteur_nom=self.designation)

    def transcription(self):
        """
        :rtype: hermes.detecteur.Detecteur
        """
        from hermes.detecteur import Detecteur as HermesDetecteur

        mon_detecteur = HermesDetecteur(
            self.designation
        )

        for regle in self.regles:
            mon_detecteur.je_veux(
                get_child_polymorphic(regle).transcription()
            )

        return mon_detecteur


class RechercheInteret(db.Model):
    __tablename__ = 'recherche_interet'

    id = db.Column(db.Integer(), primary_key=True)
    designation = db.Column(db.String(255), nullable=False)

    detecteurs = db.relationship(Detecteur, secondary='lien_detecteur_recherche_interet')

    est_obligatoire = db.Column(db.Boolean(), nullable=False)

    focus_cle = db.Column(db.String(255), nullable=True)

    createur_id = db.Column(db.ForeignKey('user.id'), nullable=True)
    createur = db.relationship(User, primaryjoin="User.id==RechercheInteret.createur_id")

    date_creation = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow())
    date_modification = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow())

    responsable_derniere_modification_id = db.Column(db.ForeignKey('user.id'), nullable=True)
    responsable_derniere_modification = db.relationship(User,
                                                        primaryjoin="User.id==RechercheInteret.responsable_derniere_modification_id")

    mapped_class_child = db.Column(db.String(128), nullable=True)

    friendly_name = db.Column(db.String(255), nullable=True)

    __mapper_args__ = {
        'polymorphic_on': mapped_class_child,
        'polymorphic_identity': str(Detecteur).replace('.Detecteur', '.RechercheInteret'),
    }

    def __repr__(self):
        return _('<Recherche DE \'{nom}\'>').format(nom=self.designation)

    def transcription(self):
        """
        Transforme un critère "RechercheInteret < db.Model" en objet "RechercheInteret < hermes"
        :rtype: hermes.detecteur.RechercheInteret
        """
        raise NotImplemented


class LienDetecteurRechercheInteret(db.Model):

    __tablename__ = 'lien_detecteur_recherche_interet'

    detecteur_id = db.Column(db.Integer(), db.ForeignKey('detecteur.id', ondelete='CASCADE'), primary_key=True)
    recherche_interet_id = db.Column(db.Integer(), db.ForeignKey('recherche_interet.id', ondelete='CASCADE'), primary_key=True)


class IdentificateurRechercheInteret(RechercheInteret):
    __tablename__ = 'identificateur_recherche_interet'

    id = db.Column(db.Integer, db.ForeignKey('recherche_interet.id'), primary_key=True)

    prefixe = db.Column(db.String(255), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': str(RechercheInteret).replace('RechercheInteret', 'IdentificateurRechercheInteret'),
    }

    def __repr__(self):
        if self.focus_cle and self.focus_cle != '':
            return _('<Recherche Identifiant Préfixé \'{identifiant_prefixe}\' DANS \'{focus_cle}\'>').format(identifiant_prefixe=self.prefixe, focus_cle=self.focus_cle)
        return _('<Recherche Identifiant Préfixé \'{identifiant_prefixe}\' PARTOUT>').format(identifiant_prefixe=self.prefixe)

    def transcription(self):
        """
        :rtype: hermes.detecteur.IdentificateurRechercheInteret
        """
        from hermes.detecteur import IdentificateurRechercheInteret as Critere
        return Critere(
            self.designation,
            self.prefixe,
            taille_stricte=None,
            focus_cle=self.focus_cle,
            est_obligatoire=self.est_obligatoire,
            friendly_name=self.friendly_name
        )


class ExpressionXPathRechercheInteret(RechercheInteret):

    __tablename__ = 'expression_xpath_recherche_interet'

    id = db.Column(db.Integer, db.ForeignKey('recherche_interet.id'), primary_key=True)

    expression_xpath = db.Column(db.String(255), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': str(RechercheInteret).replace('RechercheInteret',
                                                              'ExpressionXPathRechercheInteret'),
    }

    def __repr__(self):
        return _('<Recherche XPath \'{expr_xpath}\' DANS CORPS HTML>').format(expr_xpath=self.expression_xpath)

    def transcription(self):
        """
        :rtype: hermes.detecteur.ExpressionXPathRechercheInteret
        """
        from hermes.detecteur import ExpressionXPathRechercheInteret as Critere
        return Critere(
            self.designation,
            self.expression_xpath,
            self.est_obligatoire,
            self.friendly_name
        )


class LocalisationExpressionRechercheInteret(RechercheInteret):

    __tablename__ = 'localisation_expression_recherche_interet'

    id = db.Column(db.Integer, db.ForeignKey('recherche_interet.id'), primary_key=True)

    expression_gauche = db.Column(db.String(255), nullable=True)
    expression_droite = db.Column(db.String(255), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': str(RechercheInteret).replace('RechercheInteret', 'LocalisationExpressionRechercheInteret'),
    }

    def __repr__(self):
        if self.expression_gauche and self.expression_droite and self.expression_gauche != '' and self.expression_droite != '':
            return _('<Recherche Expression ENTRE \'{expr_gauche}\' ET \'{expr_droite}\' {loc}>').format(expr_gauche=self.expression_gauche, expr_droite=self.expression_droite, loc=_('PARTOUT') if self.focus_cle and self.focus_cle != '' else _('DANS \'{}\'').format(self.focus_cle))
        if self.expression_gauche and self.expression_gauche != '':
            return _('<Recherche Expression À DROITE DE \'{expr_gauche}\' {loc}>').format(expr_gauche=self.expression_gauche, loc=_('PARTOUT') if self.focus_cle and self.focus_cle != '' else _('DANS \'{}\'').format(self.focus_cle))
        if self.expression_droite and self.expression_droite != '':
            return _('<Recherche Expression À GAUCHE DE \'{expr_droite}\' {loc}>').format(expr_droite=self.expression_droite, loc=_('PARTOUT') if self.focus_cle and self.focus_cle != '' else _('DANS \'{}\'').format(self.focus_cle))

        return _('<Recherche Expression ENTRE \'{expr_gauche}\' ET \'{expr_droite}\' {loc}>').format(expr_gauche=self.expression_gauche, expr_droite=self.expression_droite, loc=_('PARTOUT') if self.focus_cle and self.focus_cle != '' else _('DANS \'{}\'').format(self.focus_cle))

    def transcription(self):
        """
        :rtype: hermes.detecteur.LocalisationExpressionRechercheInteret
        """
        from hermes.detecteur import LocalisationExpressionRechercheInteret as Critere
        return Critere(
            self.designation,
            self.expression_droite,
            self.expression_gauche,
            self.focus_cle,
            self.est_obligatoire,
            self.friendly_name
        )


class ExpressionCleRechercheInteret(RechercheInteret):
    __tablename__ = 'expression_cle_recherche_interet'
    id = db.Column(db.Integer, db.ForeignKey('recherche_interet.id'), primary_key=True)

    expression_cle = db.Column(db.String(255), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': str(RechercheInteret).replace('RechercheInteret', 'ExpressionCleRechercheInteret'),
    }

    def __repr__(self):
        if self.focus_cle and self.focus_cle != '':
            return _('<Recherche Exactement \'{expr}\' DANS \'{loc}\'>').format(expr=self.expression_cle, loc=self.focus_cle)
        return _('<Recherche Exactement \'{expr}\' PARTOUT>').format(expr=self.expression_cle)

    def transcription(self):
        """
        :rtype: hermes.detecteur.ExpressionCleRechercheInteret
        """
        from hermes.detecteur import ExpressionCleRechercheInteret as Critere
        return Critere(
            self.designation,
            self.expression_cle,
            self.focus_cle,
            self.est_obligatoire,
            self.friendly_name
        )


class ExpressionReguliereRechercheInteret(RechercheInteret):
    __tablename__ = 'expression_reguliere_recherche_interet'

    id = db.Column(db.Integer, db.ForeignKey('recherche_interet.id'), primary_key=True)

    expression_reguliere = db.Column(db.String(255), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': str(RechercheInteret).replace('RechercheInteret', 'ExpressionReguliereRechercheInteret'),
    }

    def __repr__(self):
        if self.focus_cle and self.focus_cle != '':
            return _('<Recherche REGEX \'{expr}\' DANS \'{loc}\'>').format(expr=self.expression_reguliere, loc=self.focus_cle)
        return _('<Recherche REGEX \'{expr}\' PARTOUT>').format(expr=self.expression_reguliere)

    def transcription(self):
        """
        :rtype: hermes.detecteur.ExpressionReguliereRechercheInteret
        """
        from hermes.detecteur import ExpressionReguliereRechercheInteret as Critere
        return Critere(
            self.designation,
            self.expression_reguliere,
            self.focus_cle,
            self.est_obligatoire,
            self.friendly_name
        )


class CleRechercheInteret(RechercheInteret):
    __tablename__ = 'cle_recherche_interet'
    id = db.Column(db.Integer, db.ForeignKey('recherche_interet.id'), primary_key=True)

    cle_recherchee = db.Column(db.String(255), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': str(RechercheInteret).replace('RechercheInteret', 'CleRechercheInteret'),
    }

    def __repr__(self):
        return _('<Recherche Clé Auto-Découverte \'{loc}\'>').format(loc=self.cle_recherchee)

    def transcription(self):
        """
        :rtype: hermes.detecteur.CleRechercheInteret
        """
        from hermes.detecteur import CleRechercheInteret as Critere
        return Critere(
            self.designation,
            self.cle_recherchee,
            self.est_obligatoire,
            self.friendly_name
        )


class DateRechercheInteret(RechercheInteret):
    __tablename__ = 'date_recherche_interet'
    id = db.Column(db.Integer, db.ForeignKey('recherche_interet.id'), primary_key=True)

    prefixe = db.Column(db.String(255), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': str(RechercheInteret).replace('RechercheInteret', 'DateRechercheInteret'),
    }

    def __repr__(self):
        if self.focus_cle and self.focus_cle != '':
            return _('<Recherche Date \'{prefixe}\' DANS \'{loc}\'>').format(prefixe=self.prefixe, loc=self.focus_cle)
        return _('<Recherche Date \'{prefixe}\' PARTOUT>').format(prefixe=self.prefixe)

    def transcription(self):
        """
        :rtype: hermes.detecteur.DateRechercheInteret
        """
        from hermes.detecteur import DateRechercheInteret as Critere
        return Critere(
            self.designation,
            self.prefixe,
            self.focus_cle,
            self.est_obligatoire,
            self.friendly_name
        )


class ExpressionDansCleRechercheInteret(RechercheInteret):
    __tablename__ = 'expression_dans_cle_recherche_interet'

    id = db.Column(db.Integer(), db.ForeignKey('recherche_interet.id'), primary_key=True)

    cle_recherchee = db.Column(db.String(255), nullable=False)
    expression_recherchee = db.Column(db.String(255), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': str(RechercheInteret).replace('RechercheInteret', 'ExpressionDansCleRechercheInteret'),
    }

    def __repr__(self):
        return _('<Recherche Exactement \'{expr}\' DANS Clé Auto-Découverte "{loc}">').format(expr=self.expression_recherchee, loc=self.cle_recherchee)

    def transcription(self):
        """
        :rtype: hermes.detecteur.ExpressionDansCleRechercheInteret
        """
        from hermes.detecteur import ExpressionDansCleRechercheInteret as Critere
        return Critere(
            self.designation,
            self.cle_recherchee,
            self.expression_recherchee,
            self.est_obligatoire,
            self.friendly_name
        )


class InformationRechercheInteret(RechercheInteret):
    __tablename__ = 'information_recherche_interet'
    id = db.Column(db.Integer, db.ForeignKey('recherche_interet.id'), primary_key=True)

    information_cible = db.Column(db.String(255), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': str(RechercheInteret).replace('RechercheInteret', 'InformationRechercheInteret'),
    }

    def __repr__(self):
        if self.focus_cle and self.focus_cle != '':
            return _('<Recherche Information Balisée \'{expr}\' DANS "{loc}">').format(expr=self.expression_recherchee, loc=self.focus_cle)
        return _('<Recherche Information Balisée \'{expr}\' PARTOUT>').format(expr=self.expression_recherchee)

    def transcription(self):
        """
        :rtype: hermes.detecteur.InformationRechercheInteret
        """
        from hermes.detecteur import InformationRechercheInteret as Critere
        return Critere(
            self.designation,
            self.information_cible,
            self.focus_cle,
            self.est_obligatoire,
            self.friendly_name
        )


class LienSousRegleOperationLogique(db.Model):

    __tablename__ = 'lien_sous_regle_operation_logique'

    operation_logique_recherche_interet_id = db.Column(
        db.Integer(),
        db.ForeignKey('operation_logique_recherche_interet.id', ondelete='CASCADE'),
        primary_key=True
    )

    recherche_interet_id = db.Column(
        db.Integer(),
        db.ForeignKey('recherche_interet.id', ondelete='CASCADE'),
        primary_key=True
    )


class OperationLogiqueRechercheInteret(RechercheInteret):
    __tablename__ = 'operation_logique_recherche_interet'
    id = db.Column(db.Integer, db.ForeignKey('recherche_interet.id'), primary_key=True)

    operande = db.Column(db.Enum("AND", "NOT", 'XOR', 'OR'), nullable=False)
    sous_regles = db.relationship(RechercheInteret, secondary='lien_sous_regle_operation_logique', enable_typechecks=False, cascade="save-update, delete")

    __mapper_args__ = {
        'polymorphic_identity': str(RechercheInteret).replace('RechercheInteret', 'OperationLogiqueRechercheInteret'),
    }

    def __repr__(self):
        return _('<Opération sur Critère(s) {operande} "{nom}">').format(operande=self.operande, nom=self.designation)

    def transcription(self):
        """
        :rtype: hermes.detecteur.OperationLogiqueRechercheInteret
        """
        from hermes.detecteur import OperationLogiqueRechercheInteret as Critere

        kwargs = dict()

        for sous_regle in self.sous_regles:
            kwargs['ma_cond_{}'.format(sous_regle.id)] = sous_regle.transcription()

        kwargs['friendly_name'] = self.friendly_name

        return Critere(
            self.designation,
            self.operande,
            **kwargs
        )
