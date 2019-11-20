import datetime

from hermes_ui.adminlte.models import User
from hermes_ui.db import db


class Detecteur(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    designation = db.Column(db.String(255), nullable=False)

    regles = db.relationship("RechercheInteret", secondary='lien_detecteur_recherche_interet', lazy='joined', enable_typechecks=False, cascade="save-update, delete")  # type: list[RechercheInteret]

    createur_id = db.Column(db.ForeignKey('user.id'), nullable=True)
    createur = db.relationship(User, primaryjoin="User.id==Detecteur.createur_id")

    date_creation = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow())
    date_modification = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow())

    responsable_derniere_modification_id = db.Column(db.ForeignKey('user.id'), nullable=True)
    responsable_derniere_modification = db.relationship(User,
                                                        primaryjoin="User.id==Detecteur.responsable_derniere_modification_id")

    def __repr__(self):
        return '<Détecteur \'{}\'>'.format(self.designation)


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
        return '<Recherche Intêret \'{}\'>'.format(self.designation)


class LienDetecteurRechercheInteret(db.Model):

    __tablename__ = 'lien_detecteur_recherche_interet'

    detecteur_id = db.Column(db.Integer(), db.ForeignKey('detecteur.id'), primary_key=True)
    recherche_interet_id = db.Column(db.Integer(), db.ForeignKey('recherche_interet.id'), primary_key=True)


class IdentificateurRechercheInteret(RechercheInteret):
    __tablename__ = 'identificateur_recherche_interet'

    id = db.Column(db.Integer, db.ForeignKey('recherche_interet.id'), primary_key=True)

    prefixe = db.Column(db.String(255), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': str(RechercheInteret).replace('RechercheInteret', 'IdentificateurRechercheInteret'),
    }

    def __repr__(self):
        return '<Recherche Identifiant \'{}\'>'.format(self.prefixe)


class LocalisationExpressionRechercheInteret(RechercheInteret):

    __tablename__ = 'localisation_expression_recherche_interet'

    id = db.Column(db.Integer, db.ForeignKey('recherche_interet.id'), primary_key=True)

    expression_gauche = db.Column(db.String(255), nullable=True)
    expression_droite = db.Column(db.String(255), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': str(RechercheInteret).replace('RechercheInteret', 'LocalisationExpressionRechercheInteret'),
    }

    def __repr__(self):
        return '<Recherche Expression ENTRE \'{}\' ET \'{}\'>'.format(self.expression_gauche, self.expression_droite)


class ExpressionCleRechercheInteret(RechercheInteret):
    __tablename__ = 'expression_cle_recherche_interet'
    id = db.Column(db.Integer, db.ForeignKey('recherche_interet.id'), primary_key=True)

    expression_cle = db.Column(db.String(255), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': str(RechercheInteret).replace('RechercheInteret', 'ExpressionCleRechercheInteret'),
    }

    def __repr__(self):
        return '<Recherche Exactement \'{}\'>'.format(self.expression_cle)


class ExpressionReguliereRechercheInteret(RechercheInteret):
    __tablename__ = 'expression_reguliere_recherche_interet'

    id = db.Column(db.Integer, db.ForeignKey('recherche_interet.id'), primary_key=True)

    expression_reguliere = db.Column(db.String(255), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': str(RechercheInteret).replace('RechercheInteret', 'ExpressionReguliereRechercheInteret'),
    }

    def __repr__(self):
        return '<Recherche REGEX \'{}\'>'.format(self.expression_reguliere)


class CleRechercheInteret(RechercheInteret):
    __tablename__ = 'cle_recherche_interet'
    id = db.Column(db.Integer, db.ForeignKey('recherche_interet.id'), primary_key=True)

    cle_recherchee = db.Column(db.String(255), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': str(RechercheInteret).replace('RechercheInteret', 'CleRechercheInteret'),
    }

    def __repr__(self):
        return '<Recherche Clé \'{}\'>'.format(self.cle_recherchee)


class DateRechercheInteret(RechercheInteret):
    __tablename__ = 'date_recherche_interet'
    id = db.Column(db.Integer, db.ForeignKey('recherche_interet.id'), primary_key=True)

    prefixe = db.Column(db.String(255), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': str(RechercheInteret).replace('RechercheInteret', 'DateRechercheInteret'),
    }

    def __repr__(self):
        return '<Recherche Date \'{}\'>'.format(self.prefixe)


class ExpressionDansCleRechercheInteret(RechercheInteret):
    __tablename__ = 'expression_dans_cle_recherche_interet'

    id = db.Column(db.Integer(), db.ForeignKey('recherche_interet.id'), primary_key=True)

    cle_recherchee = db.Column(db.String(255), nullable=False)
    expression_recherchee = db.Column(db.String(255), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': str(RechercheInteret).replace('RechercheInteret', 'ExpressionDansCleRechercheInteret'),
    }

    def __repr__(self):
        return '<Recherche Exactement \'{} IN "{}"\'>'.format(self.expression_recherchee, self.cle_recherchee)


class InformationRechercheInteret(RechercheInteret):
    __tablename__ = 'information_recherche_interet'
    id = db.Column(db.Integer, db.ForeignKey('recherche_interet.id'), primary_key=True)

    information_cible = db.Column(db.String(255), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': str(RechercheInteret).replace('RechercheInteret', 'InformationRechercheInteret'),
    }


class LienSousRegleOperationLogique(db.Model):

    __tablename__ = 'lien_sous_regle_operation_logique'

    operation_logique_recherche_interet_id = db.Column(
        db.Integer(),
        db.ForeignKey('operation_logique_recherche_interet.id'),
        primary_key=True
    )

    recherche_interet_id = db.Column(
        db.Integer(),
        db.ForeignKey('recherche_interet.id'),
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
