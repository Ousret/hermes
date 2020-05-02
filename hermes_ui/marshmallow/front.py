from flask_marshmallow import Marshmallow
import flask_marshmallow.fields
from marshmallow_oneofschema import OneOfSchema
from hermes_ui.models import *


ma = Marshmallow()


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ('password',)


class ActionNoeudSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ActionNoeud
        exclude = ('createur', 'responsable_derniere_modification', 'date_creation', 'date_modification')

    action_reussite = flask_marshmallow.fields.fields.Nested('ActionNoeudPolySchema')
    action_echec = flask_marshmallow.fields.fields.Nested('ActionNoeudPolySchema')


for my_class in ActionNoeud.__subclasses__():
    exec(
        """class {class_name}Schema(ActionNoeudSchema):
    class Meta:
        model = {class_name}
        exclude = ('createur', 'responsable_derniere_modification', 'date_creation', 'date_modification')""".format(class_name=str(my_class).split("'")[-2].split('.')[-1])
    )


class ActionNoeudPolySchema(OneOfSchema):

    type_field = "type"
    type_schemas = dict([(str(cl_type).split("'")[-2].split('.')[-1].replace('Schema', ''), cl_type) for cl_type in ActionNoeudSchema.__subclasses__()])


class RechercheInteretSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RechercheInteret
        exclude = ('createur', 'responsable_derniere_modification', 'date_creation', 'date_modification')

    createur = flask_marshmallow.fields.fields.Nested(UserSchema)
    responsable_derniere_modification = flask_marshmallow.fields.fields.Nested(UserSchema)


for my_class in RechercheInteret.__subclasses__():
    exec(
        """class {class_name}Schema(RechercheInteretSchema):
    class Meta:
        model = {class_name}
        exclude = ('createur', 'responsable_derniere_modification', 'date_creation', 'date_modification')""".format(class_name=str(my_class).split("'")[-2].split('.')[-1])
    )


class RechercheInteretPolySchema(OneOfSchema):

    type_field = "type"
    type_schemas = dict([(str(cl_type).split("'")[-2].split('.')[-1].replace('Schema', ''), cl_type) for cl_type in RechercheInteretSchema.__subclasses__()])


class DetecteurSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = Detecteur
        exclude = ('createur', 'responsable_derniere_modification', 'date_creation', 'date_modification')

    createur = flask_marshmallow.fields.fields.Nested(UserSchema)
    responsable_derniere_modification = flask_marshmallow.fields.fields.Nested(UserSchema)

    regles = flask_marshmallow.fields.fields.Nested(
        RechercheInteretPolySchema, many=True
    )


class AutomateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Automate
        exclude = ('createur', 'responsable_derniere_modification', 'date_creation', 'date_modification')

    detecteur = flask_marshmallow.fields.fields.Nested(DetecteurSchema)
    action_racine = flask_marshmallow.fields.fields.Nested(ActionNoeudPolySchema)
    actions = flask_marshmallow.fields.fields.List(flask_marshmallow.fields.fields.Nested(ActionNoeudPolySchema))

    createur = flask_marshmallow.fields.fields.Nested(UserSchema)
    responsable_derniere_modification = flask_marshmallow.fields.fields.Nested(UserSchema)


class ActionNoeudExecutionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ActionNoeudExecution

    action_noeud = flask_marshmallow.fields.fields.Nested(ActionNoeudPolySchema)


class RechercheInteretExecutionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RechercheInteretExecution

    recherche_interet = flask_marshmallow.fields.fields.Nested(RechercheInteretSchema)


class AutomateExecutionSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = AutomateExecution

    automate = flask_marshmallow.fields.fields.Nested(AutomateSchema)
    detecteur = flask_marshmallow.fields.fields.Nested(DetecteurSchema)

    actions_noeuds_executions = flask_marshmallow.fields.fields.List(
        flask_marshmallow.fields.fields.Nested(ActionNoeudExecutionSchema)
    )

    recherches_interets_executions = flask_marshmallow.fields.fields.List(
        flask_marshmallow.fields.fields.Nested(RechercheInteretExecutionSchema)
    )


class AutomateExecutionDataTableSchema(ma.SQLAlchemyAutoSchema):

    data = flask_marshmallow.fields.fields.List(
        flask_marshmallow.fields.fields.Nested(AutomateExecutionSchema)
    )
