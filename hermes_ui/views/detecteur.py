from hermes_ui.adminlte.views import BaseAdminView
from flask_login import current_user
from datetime import datetime


class DectecteurView(BaseAdminView):
    column_editable_list = []
    column_searchable_list = ['designation', 'regles.designation']
    column_exclude_list = ['date_creation']
    column_details_exclude_list = None
    column_filters = ['designation', 'regles.designation']
    form_excluded_columns = ['createur', 'date_creation', 'date_modification', 'responsable_derniere_modification']
    can_export = True
    can_view_details = False
    can_create = True
    can_edit = True
    can_delete = True
    edit_modal = True
    create_modal = True
    details_modal = True
    column_display_pk = False

    def on_model_change(self, form, model, is_created):
        """

        :param form:
        :param gie_interoperabilite_ui.models.configuration.Configuration model:
        :param bool is_created:
        :return:
        """
        if is_created is True:
            model.createur = current_user
            model.date_creation = datetime.now()

        model.date_modification = datetime.now()
        model.responsable_derniere_modification = current_user


class RechercheInteretView(BaseAdminView):
    column_editable_list = ['est_obligatoire']
    column_filters = ['est_obligatoire']
    column_exclude_list = ['detecteurs', 'createur', 'responsable_derniere_modification']
    can_export = True
    can_view_details = False
    can_create = False
    can_edit = False
    can_delete = True
    edit_modal = False
    create_modal = False
    details_modal = True
    column_labels = dict(mapped_class_child='Type', friendly_name='Résultat dans variable', focus_cle='Recherche ciblée')
    column_formatters = dict(mapped_class_child=lambda a, b, c, d: str(c))
    column_display_pk = False

    column_descriptions = {
        'friendly_name': 'Si vous souhaitez conserver et exploiter le résultat de la règle dans votre automate, '
                         'spécifiez un nom simple ici',
        'mapped_class_child': 'Nom du type de la règle',
        'focus_cle': 'Force le moteur à effectuer la recherche sur une partie restreinte de la source, laissez vide '
                     'pour laisser le moteur rechercher PARTOUT.'
    }


class DateRechercheInteretView(BaseAdminView):
    column_editable_list = ['est_obligatoire']
    column_searchable_list = ['designation', 'prefixe', 'est_obligatoire']
    column_exclude_list = ['mapped_class_child']
    column_details_exclude_list = None
    column_filters = ['designation', 'prefixe', 'est_obligatoire']
    form_excluded_columns = ['createur', 'date_creation', 'date_modification', 'responsable_derniere_modification', 'mapped_class_child']
    can_export = True
    can_view_details = False
    can_create = True
    can_edit = True
    can_delete = True
    edit_modal = True
    create_modal = True
    details_modal = True
    column_labels = dict(friendly_name='Résultat dans variable', focus_cle='Recherche ciblée')

    form_choices = {
        'focus_cle':
            [
                ('titre', 'Uniquement dans le TITRE'),
                ('corpus', 'Uniquement dans le CORPS'),
                ('expediteur', 'Dans le champ expéditeur du message'),
                ('destinataire', 'Dans le champ destinataire du message'),
                ('hyperliens', 'Dans la liste des URLs découvertes'),
                ('pieces-jointes', 'Dans la liste des noms des pièces jointes'),
                ('pieces-jointes-types', 'Dans la liste des formats MIME des pièces jointes')
            ],
    }

    column_descriptions = {
        'prefixe': 'Le préfixe qui précède votre date, par ex. "Suivi à la date du"',
        'friendly_name': 'Si vous souhaitez conserver et exploiter le résultat de la règle dans votre automate, '
                         'spécifiez un nom simple ici',
        'focus_cle': 'Force le moteur à effectuer la recherche sur une partie restreinte de la source, laissez vide '
                     'pour laisser le moteur rechercher PARTOUT.'
    }

    def on_model_change(self, form, model, is_created):
        """

        :param form:
        :param gie_interoperabilite_ui.models.configuration.Configuration model:
        :param bool is_created:
        :return:
        """
        if is_created is True:
            model.createur = current_user
            model.date_creation = datetime.now()
            model.mapped_class_child = str(model.__class__)

        model.date_modification = datetime.now()
        model.responsable_derniere_modification = current_user


class IdentificateurRechercheInteretView(BaseAdminView):
    column_editable_list = ['est_obligatoire']
    column_searchable_list = ['designation', 'prefixe', 'est_obligatoire']
    column_exclude_list = ['mapped_class_child']
    column_details_exclude_list = None
    column_filters = ['designation', 'prefixe', 'est_obligatoire']
    form_excluded_columns = ['createur', 'date_creation', 'date_modification', 'responsable_derniere_modification', 'mapped_class_child']
    can_export = True
    can_view_details = False
    can_create = True
    can_edit = True
    can_delete = True
    edit_modal = True
    create_modal = True
    details_modal = True
    column_labels = dict(friendly_name='Résultat dans variable', focus_cle='Recherche ciblée')

    column_descriptions = {
        'prefixe': 'Indiquez ici le préfixe de votre identifiant',
        'friendly_name': 'Si vous souhaitez conserver et exploiter le résultat de la règle dans votre automate, spécifiez un nom simple ici',
        'focus_cle': 'Force le moteur à effectuer la recherche sur une partie restreinte de la source, laissez vide '
                     'pour laisser le moteur rechercher PARTOUT.'
    }

    form_choices = {
        'focus_cle':
            [
                ('titre', 'Uniquement dans le TITRE'),
                ('corpus', 'Uniquement dans le CORPS'),
                ('expediteur', 'Dans le champ expéditeur du message'),
                ('destinataire', 'Dans le champ destinataire du message'),
                ('hyperliens', 'Dans la liste des URLs découvertes'),
                ('pieces-jointes', 'Dans la liste des noms des pièces jointes'),
                ('pieces-jointes-types', 'Dans la liste des formats MIME des pièces jointes')
            ],
    }

    def on_model_change(self, form, model, is_created):
        """

        :param form:
        :param gie_interoperabilite_ui.models.configuration.Configuration model:
        :param bool is_created:
        :return:
        """
        if is_created is True:
            model.createur = current_user
            model.date_creation = datetime.now()
            model.mapped_class_child = str(model.__class__)

        model.date_modification = datetime.now()
        model.responsable_derniere_modification = current_user


class LocalisationExpressionRechercheInteretView(BaseAdminView):
    column_editable_list = ['est_obligatoire']
    column_searchable_list = ['designation', 'expression_gauche', 'expression_droite', 'est_obligatoire']
    column_exclude_list = ['mapped_class_child']
    column_details_exclude_list = None
    column_filters = ['designation', 'expression_gauche', 'expression_droite', 'est_obligatoire']
    form_excluded_columns = ['createur', 'date_creation', 'date_modification', 'responsable_derniere_modification', 'mapped_class_child']
    can_export = True
    can_view_details = False
    can_create = True
    can_edit = True
    can_delete = True
    edit_modal = True
    create_modal = True
    details_modal = True
    column_labels = dict(friendly_name='Résultat dans variable', focus_cle='Recherche ciblée')

    column_descriptions = {
        'expression_gauche': 'Expression immédiatement à gauche de ce que vous souhaitez extraire, '
                             'laissez vide si votre cible est au début',
        'expression_droite': 'Expression immédiatement à droite de ce que vous souhaitez extraire, '
                             'laissez vide si votre cible est déjà en fin',
        'friendly_name': 'Si vous souhaitez conserver et exploiter le résultat de la règle dans votre automate, '
                         'spécifiez un nom simple ici',
        'focus_cle': 'Force le moteur à effectuer la recherche sur une partie restreinte de la source, laissez vide '
                     'pour laisser le moteur rechercher PARTOUT.'
    }

    form_choices = {
        'focus_cle':
            [
                ('titre', 'Uniquement dans le TITRE'),
                ('corpus', 'Uniquement dans le CORPS'),
                ('expediteur', 'Dans le champ expéditeur du message'),
                ('destinataire', 'Dans le champ destinataire du message'),
                ('hyperliens', 'Dans la liste des URLs découvertes'),
                ('pieces-jointes', 'Dans la liste des noms des pièces jointes'),
                ('pieces-jointes-types', 'Dans la liste des formats MIME des pièces jointes')
            ],
    }

    def on_model_change(self, form, model, is_created):
        """

        :param form:
        :param gie_interoperabilite_ui.models.detecteur.LocalisationExpressionRechercheInteret model:
        :param bool is_created:
        :return:
        """
        if is_created is True:
            model.createur = current_user
            model.date_creation = datetime.now()
            model.mapped_class_child = str(model.__class__)

        model.date_modification = datetime.now()
        model.responsable_derniere_modification = current_user
        if model.expression_droite is None:
            model.expression_droite = ''
        if model.expression_gauche is None:
            model.expression_gauche = ''


class ExpressionCleRechercheInteretView(BaseAdminView):

    column_editable_list = ['est_obligatoire']
    column_searchable_list = ['designation', 'expression_cle', 'est_obligatoire']
    column_exclude_list = ['mapped_class_child']
    column_details_exclude_list = None
    column_filters = ['designation', 'expression_cle', 'est_obligatoire']
    form_excluded_columns = ['createur', 'date_creation', 'date_modification', 'responsable_derniere_modification', 'mapped_class_child']
    can_export = True
    can_view_details = False
    can_create = True
    can_edit = True
    can_delete = True
    edit_modal = True
    create_modal = True
    details_modal = True
    column_labels = dict(friendly_name='Résultat dans variable', focus_cle='Recherche ciblée')

    column_descriptions = {
        'friendly_name': 'Si vous souhaitez conserver et exploiter le résultat de la règle dans votre automate, '
                         'spécifiez un nom simple ici',
        'focus_cle': 'Force le moteur à effectuer la recherche sur une partie restreinte de la source, laissez vide '
                     'pour laisser le moteur rechercher PARTOUT.'
    }

    form_choices = {
        'focus_cle':
            [
                ('titre', 'Uniquement dans le TITRE'),
                ('corpus', 'Uniquement dans le CORPS'),
                ('expediteur', 'Dans le champ expéditeur du message'),
                ('destinataire', 'Dans le champ destinataire du message'),
                ('hyperliens', 'Dans la liste des URLs découvertes'),
                ('pieces-jointes', 'Dans la liste des noms des pièces jointes'),
                ('pieces-jointes-types', 'Dans la liste des formats MIME des pièces jointes')
            ],
    }

    def on_model_change(self, form, model, is_created):
        """

        :param form:
        :param gie_interoperabilite_ui.models.configuration.Configuration model:
        :param bool is_created:
        :return:
        """
        if is_created is True:
            model.createur = current_user
            model.date_creation = datetime.now()
            model.mapped_class_child = str(model.__class__)

        model.date_modification = datetime.now()
        model.responsable_derniere_modification = current_user


class ExpressionReguliereRechercheInteretView(BaseAdminView):

    column_editable_list = ['est_obligatoire']
    column_searchable_list = ['designation', 'expression_reguliere', 'est_obligatoire']
    column_exclude_list = ['mapped_class_child']
    column_details_exclude_list = None
    column_filters = ['designation', 'est_obligatoire']
    form_excluded_columns = ['createur', 'date_creation', 'date_modification', 'responsable_derniere_modification', 'mapped_class_child']
    can_export = True
    can_view_details = False
    can_create = True
    can_edit = True
    can_delete = True
    edit_modal = True
    create_modal = True
    details_modal = True
    column_labels = dict(friendly_name='Résultat dans variable', focus_cle='Recherche ciblée')

    column_descriptions = {
        'friendly_name': 'Si vous souhaitez conserver et exploiter le résultat de la règle dans votre automate, '
                         'spécifiez un nom simple ici',
        'focus_cle': 'Force le moteur à effectuer la recherche sur une partie restreinte de la source, laissez vide '
                     'pour laisser le moteur rechercher PARTOUT.',
        'expression_reguliere': 'Expression régulière à utiliser pour la recherche d\'information. '
                                'Les groupes de capture sont supporté pour scinder le résultat.'
    }

    form_choices = {
        'focus_cle':
            [
                ('titre', 'Uniquement dans le TITRE'),
                ('corpus', 'Uniquement dans le CORPS'),
                ('expediteur', 'Dans le champ expéditeur du message'),
                ('destinataire', 'Dans le champ destinataire du message'),
                ('hyperliens', 'Dans la liste des URLs découvertes'),
                ('pieces-jointes', 'Dans la liste des noms des pièces jointes'),
                ('pieces-jointes-types', 'Dans la liste des formats MIME des pièces jointes')
            ],
    }

    def on_model_change(self, form, model, is_created):
        """

        :param form:
        :param gie_interoperabilite_ui.models.configuration.Configuration model:
        :param bool is_created:
        :return:
        """
        if is_created is True:
            model.createur = current_user
            model.date_creation = datetime.now()
            model.mapped_class_child = str(model.__class__)

        model.date_modification = datetime.now()
        model.responsable_derniere_modification = current_user


class CleRechercheInteretView(BaseAdminView):
    column_editable_list = ['est_obligatoire']
    column_searchable_list = ['designation', 'cle_recherchee', 'est_obligatoire']
    column_exclude_list = ['mapped_class_child', 'focus_cle']
    column_details_exclude_list = None
    column_filters = ['designation', 'cle_recherchee', 'est_obligatoire']
    form_excluded_columns = ['createur', 'date_creation', 'focus_cle', 'date_modification', 'responsable_derniere_modification', 'mapped_class_child']
    can_export = True
    can_view_details = False
    can_create = True
    can_edit = True
    can_delete = True
    edit_modal = True
    create_modal = True
    details_modal = True
    column_labels = dict(friendly_name='Résultat dans variable')

    column_descriptions = {
        'friendly_name': 'Si vous souhaitez conserver et exploiter le résultat de la règle dans votre automate, '
                         'spécifiez un nom simple ici'
    }

    def on_model_change(self, form, model, is_created):
        """

        :param form:
        :param gie_interoperabilite_ui.models.configuration.Configuration model:
        :param bool is_created:
        :return:
        """
        if is_created is True:
            model.createur = current_user
            model.date_creation = datetime.now()
            model.mapped_class_child = str(model.__class__)

        model.date_modification = datetime.now()
        model.responsable_derniere_modification = current_user


class ExpressionDansCleRechercheInteretView(BaseAdminView):
    column_editable_list = ['est_obligatoire']
    column_searchable_list = ['designation', 'expression_recherchee', 'est_obligatoire']
    column_exclude_list = ['mapped_class_child', 'focus_cle']
    column_details_exclude_list = None
    column_filters = ['designation', 'expression_recherchee', 'est_obligatoire']
    form_excluded_columns = ['createur', 'date_creation', 'focus_cle', 'date_modification', 'responsable_derniere_modification', 'mapped_class_child']
    can_export = True
    can_view_details = False
    can_create = True
    can_edit = True
    can_delete = True
    edit_modal = True
    create_modal = True
    details_modal = True
    column_labels = dict(friendly_name='Résultat dans variable')

    column_descriptions = {
        'friendly_name': 'Si vous souhaitez conserver et exploiter le résultat de la règle dans votre automate, '
                         'spécifiez un nom simple ici'
    }

    def on_model_change(self, form, model, is_created):
        """

        :param form:
        :param gie_interoperabilite_ui.models.configuration.Configuration model:
        :param bool is_created:
        :return:
        """
        if is_created is True:
            model.createur = current_user
            model.date_creation = datetime.now()
            model.mapped_class_child = str(model.__class__)

        model.date_modification = datetime.now()
        model.responsable_derniere_modification = current_user


class InformationRechercheInteretView(BaseAdminView):
    column_editable_list = ['est_obligatoire']
    column_searchable_list = ['designation', 'information_cible', 'est_obligatoire']
    column_exclude_list = ['mapped_class_child']
    column_details_exclude_list = None
    column_filters = ['designation', 'information_cible', 'est_obligatoire']
    form_excluded_columns = ['createur', 'date_creation', 'date_modification', 'responsable_derniere_modification', 'mapped_class_child']
    can_export = True
    can_view_details = False
    can_create = True
    can_edit = True
    can_delete = True
    edit_modal = True
    create_modal = True
    details_modal = True
    column_labels = dict(friendly_name='Résultat dans variable', focus_cle='Recherche ciblée')

    column_descriptions = {
        'friendly_name': 'Si vous souhaitez conserver et exploiter le résultat de la règle dans votre automate, '
                         'spécifiez un nom simple ici',
        'focus_cle': 'Force le moteur à effectuer la recherche sur une partie restreinte de la source, laissez vide '
                     'pour laisser le moteur rechercher PARTOUT.'
    }

    form_choices = {
        'focus_cle':
            [
                ('titre', 'Uniquement dans le TITRE'),
                ('corpus', 'Uniquement dans le CORPS'),
                ('expediteur', 'Dans le champ expéditeur du message'),
                ('destinataire', 'Dans le champ destinataire du message'),
                ('hyperliens', 'Dans la liste des URLs découvertes'),
                ('pieces-jointes', 'Dans la liste des noms des pièces jointes'),
                ('pieces-jointes-types', 'Dans la liste des formats MIME des pièces jointes')
            ],
    }

    def on_model_change(self, form, model, is_created):
        """

        :param form:
        :param gie_interoperabilite_ui.models.configuration.Configuration model:
        :param bool is_created:
        :return:
        """
        if is_created is True:
            model.createur = current_user
            model.date_creation = datetime.now()
            model.mapped_class_child = str(model.__class__)

        model.date_modification = datetime.now()
        model.responsable_derniere_modification = current_user


class OperationLogiqueRechercheInteretView(BaseAdminView):
    column_editable_list = ['est_obligatoire']
    column_searchable_list = ['designation', 'operande', 'est_obligatoire']
    column_exclude_list = ['mapped_class_child', 'focus_cle']
    column_details_exclude_list = None
    column_filters = ['designation', 'operande', 'sous_regles', 'est_obligatoire']
    form_excluded_columns = ['createur', 'date_creation', 'focus_cle', 'date_modification', 'responsable_derniere_modification', 'mapped_class_child']
    can_export = True
    can_view_details = False
    can_create = True
    can_edit = True
    can_delete = True
    edit_modal = True
    create_modal = True
    details_modal = True
    column_labels = dict(friendly_name='Résultat dans variable')
    column_descriptions = {
        'friendly_name': 'Si vous souhaitez conserver et exploiter le résultat de la règle dans votre automate, '
                         'spécifiez un nom simple ici'
    }

    def on_model_change(self, form, model, is_created):
        """

        :param form:
        :param gie_interoperabilite_ui.models.configuration.Configuration model:
        :param bool is_created:
        :return:
        """
        if is_created is True:
            model.createur = current_user
            model.date_creation = datetime.now()
            model.mapped_class_child = str(model.__class__)

        model.date_modification = datetime.now()
        model.responsable_derniere_modification = current_user


