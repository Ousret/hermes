from hermes_ui.adminlte.views import BaseAdminView
from flask_login import current_user
from datetime import datetime


class BoiteAuxLettresImapView(BaseAdminView):
    column_editable_list = ['designation', 'activation']
    column_searchable_list = ['designation']
    column_exclude_list = ['mot_de_passe']
    column_details_exclude_list = None
    column_filters = ['designation']
    form_excluded_columns = ['actions', 'createur', 'date_creation', 'date_modification', 'responsable_derniere_modification']
    can_export = True
    can_view_details = False
    can_create = True
    can_edit = True
    can_delete = True
    edit_modal = True
    create_modal = True
    details_modal = False

    def on_model_change(self, form, model, is_created):
        """

        :param form:
        :param hermes_ui.models.automate.Automate model:
        :param bool is_created:
        :return:
        """
        if is_created is True:
            model.createur = current_user
            model.date_creation = datetime.now()

        model.date_modification = datetime.now()
        model.responsable_derniere_modification = current_user
