from flask_marshmallow import Marshmallow
import flask_marshmallow.fields
from marshmallow_oneofschema import OneOfSchema
from hermes_ui.models import *


ma = Marshmallow()


class ActionNoeudLegacySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ActionNoeud
        exclude = ('id', 'createur', 'responsable_derniere_modification', 'date_creation', 'date_modification', 'mapped_class_child', 'friendly_name')
        load_instance = True

    action_reussite = flask_marshmallow.fields.fields.Nested('ActionNoeudLegacyPolySchema', allow_none=True, required=False)
    action_echec = flask_marshmallow.fields.fields.Nested('ActionNoeudLegacyPolySchema', allow_none=True, required=False)

    variable = flask_marshmallow.fields.fields.String(attribute='friendly_name', allow_none=True, required=False)


for my_class in ActionNoeud.__subclasses__():
    t_ = str(my_class).split("'")[-2].split('.')[-1]
    if 'ExecutionAutomate' not in t_:
        exec(
            """class {class_name}LegacySchema(ActionNoeudLegacySchema):
        class Meta:
            model = {class_name}
            exclude = ('createur', 'responsable_derniere_modification', 'date_creation', 'date_modification', 'mapped_class_child', 'id', 'friendly_name')
            load_instance = True""".format(class_name=str(my_class).split("'")[-2].split('.')[-1])
        )
    else:
        exec(
            """class {class_name}LegacySchema(ActionNoeudLegacySchema):
        class Meta:
            model = {class_name}
            exclude = ('createur', 'responsable_derniere_modification', 'date_creation', 'date_modification', 'mapped_class_child', 'id', 'friendly_name', 'automate')
            load_instance = True
        automate = flask_marshmallow.fields.fields.Nested('AutomateLegacySchema', many=False)""".format(
                class_name=str(my_class).split("'")[-2].split('.')[-1])
        )


class ActionNoeudLegacyPolySchema(OneOfSchema):

    type_field = "type"
    type_schemas = dict([(str(cl_type).split("'")[-2].split('.')[-1].replace('LegacySchema', ''), cl_type) for cl_type in ActionNoeudLegacySchema.__subclasses__()])


class RechercheInteretLegacySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RechercheInteret
        exclude = ('createur', 'responsable_derniere_modification', 'date_creation', 'date_modification', 'friendly_name')
        load_instance = True

    variable = flask_marshmallow.fields.fields.String(attribute='friendly_name', allow_none=True, required=False)


for my_class in RechercheInteret.__subclasses__():
    t_ = str(my_class).split("'")[-2].split('.')[-1]
    if 'OperationLogique' not in t_:
        exec(
            """class {class_name}LegacySchema(RechercheInteretLegacySchema):
        class Meta:
            model = {class_name}
            exclude = ('createur', 'responsable_derniere_modification', 'date_creation', 'date_modification', 'id', 'detecteurs', 'mapped_class_child', 'friendly_name')
            load_instance = True""".format(class_name=str(my_class).split("'")[-2].split('.')[-1])
        )
    else:
        exec(
            """class {class_name}LegacySchema(RechercheInteretLegacySchema):
        class Meta:
            model = {class_name}
            exclude = ('createur', 'responsable_derniere_modification', 'date_creation', 'date_modification', 'id', 'detecteurs', 'mapped_class_child', 'sous_regles', 'friendly_name')
            load_instance = True
        sous_criteres = flask_marshmallow.fields.fields.Nested('RechercheInteretLegacyPolySchema', many=True, attribute="sous_regles")""".format(
                class_name=str(my_class).split("'")[-2].split('.')[-1])
        )


class RechercheInteretLegacyPolySchema(OneOfSchema):

    type_field = "type"
    type_schemas = dict([(str(cl_type).split("'")[-2].split('.')[-1].replace('LegacySchema', ''), cl_type) for cl_type in RechercheInteretLegacySchema.__subclasses__()])


class DetecteurLegacySchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = Detecteur
        exclude = ('id', 'createur', 'responsable_derniere_modification', 'date_creation', 'date_modification', 'automates', 'regles')
        load_instance = True

    criteres = flask_marshmallow.fields.fields.Nested(
        RechercheInteretLegacyPolySchema, many=True, attribute="regles"
    )


class AutomateLegacySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Automate
        exclude = ('createur', 'responsable_derniere_modification', 'date_creation', 'date_modification', 'actions', 'id', 'detecteur', 'priorite')
        load_instance = True

    regle = flask_marshmallow.fields.fields.Nested(DetecteurLegacySchema, attribute='detecteur')
    action_racine = flask_marshmallow.fields.fields.Nested(ActionNoeudLegacyPolySchema, allow_none=True, required=False)

    rang = flask_marshmallow.fields.fields.Integer(attribute='priorite')
