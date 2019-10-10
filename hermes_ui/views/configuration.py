from hermes_ui.adminlte.views import BaseAdminView
from flask_login import current_user
from datetime import datetime


class ConfigurationView(BaseAdminView):
    column_editable_list = ['designation']
    column_searchable_list = ['designation']
    column_exclude_list = ['valeur']
    form_excluded_columns = ['createur', 'date_creation', 'date_modification', 'responsable_derniere_modification']
    column_details_exclude_list = None
    column_filters = ['designation', 'createur', 'date_creation', 'date_modification']
    can_export = True
    can_view_details = True
    can_create = True
    can_edit = True
    can_delete = True
    edit_modal = True
    create_modal = True
    details_modal = False

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

