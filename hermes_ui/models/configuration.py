from hermes_ui.adminlte.models import User
from hermes_ui.db import db
from flask_login import current_user
from datetime import datetime

from hermes.session import Session


class Configuration(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    designation = db.Column(db.String(255), nullable=False, unique=True)
    valeur = db.Column(db.Text(), nullable=False)

    createur_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    createur = db.relationship(User, primaryjoin="User.id==Configuration.createur_id")

    date_creation = db.Column(db.DateTime(timezone=True), nullable=False)
    date_modification = db.Column(db.DateTime(timezone=True), nullable=False)

    responsable_derniere_modification_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    responsable_derniere_modification = db.relationship(User, primaryjoin="User.id==Configuration.responsable_derniere_modification_id")

    format = db.Column(db.Enum("JSON", 'YAML', 'AUTRE'), nullable=False)

    def __repr__(self):
        return '<Configuration \'{}\'>'.format(self.designation)

    def on_model_change(self, form, model, is_created):
        """

        :param form:
        :param Configuration model:
        :param bool is_created:
        :return:
        """
        if is_created is True:
            model.createur = current_user
            model.date_creation = datetime.now()

        model.date_modification = datetime.now()
        model.responsable_derniere_modification = current_user

        Session.charger_input(model.designation, model.valeur, model.format)
