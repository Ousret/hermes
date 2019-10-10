from hermes_ui.models.automate import Automate, ActionNoeud
from hermes_ui.models.detecteur import Detecteur, RechercheInteret
from hermes_ui.db import db


class AutomateExecution(db.Model):

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)

    automate_id = db.Column(db.Integer(), db.ForeignKey(Automate.id), nullable=False)
    automate = db.relationship(Automate)

    sujet = db.Column(db.String(255), nullable=False)
    corps = db.Column(db.Text(), nullable=False)

    date_creation = db.Column(db.DateTime(timezone=True), nullable=False)

    detecteur_id = db.Column(db.Integer(), db.ForeignKey(Detecteur.id), nullable=False)
    detecteur = db.relationship(Detecteur)

    validation_detecteur = db.Column(db.Boolean(), default=False, nullable=False)
    validation_automate = db.Column(db.Boolean(), default=False, nullable=False)

    explications_detecteur = db.Column(db.Text(), nullable=True)

    date_finalisation = db.Column(db.DateTime(timezone=True), nullable=False)

    actions_noeuds_executions = db.relationship('ActionNoeudExecution')
    recherches_interets_executions = db.relationship('RechercheInteretExecution')


class ActionNoeudExecution(db.Model):

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)

    automate_execution_id = db.Column(db.BigInteger(), db.ForeignKey(AutomateExecution.id), nullable=False)
    automate_execution = db.relationship(AutomateExecution)

    action_noeud_id = db.Column(db.Integer(), db.ForeignKey(ActionNoeud.id))
    action_noeud = db.relationship(ActionNoeud)

    validation_action_noeud = db.Column(db.Boolean(), default=False, nullable=False)

    args_payload = db.Column(db.Text(), nullable=True)
    payload = db.Column(db.Text(), nullable=True)


class RechercheInteretExecution(db.Model):

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)

    automate_execution_id = db.Column(db.BigInteger(), db.ForeignKey(AutomateExecution.id), nullable=False)
    automate_execution = db.relationship(AutomateExecution)

    recherche_interet_id = db.Column(db.Integer(), db.ForeignKey(RechercheInteret.id))
    recherche_interet = db.relationship(RechercheInteret)

    validation_recherche_interet = db.Column(db.Boolean(), default=False, nullable=False)

    payload = db.Column(db.Text(), nullable=True)


class AutomateExecutionDataTable:

    def __init__(self, executions):
        self.data = executions
