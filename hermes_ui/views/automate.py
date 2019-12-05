from hermes_ui.adminlte.views import BaseAdminView
from flask_login import current_user
from datetime import datetime

from hermes.i18n import _


class AutomateView(BaseAdminView):
    column_editable_list = ['production', 'notifiable']
    column_searchable_list = ['designation', 'production']
    column_exclude_list = ['action_racine', 'date_creation', 'createur', 'responsable_derniere_modification']
    column_details_exclude_list = None
    column_filters = ['designation']
    form_excluded_columns = ['actions', 'action_racine', 'createur', 'date_creation', 'date_modification', 'responsable_derniere_modification']
    can_export = True
    can_view_details = False
    can_create = True
    can_edit = True
    can_delete = True
    edit_modal = True
    create_modal = True
    details_modal = True

    column_descriptions = {
        'detecteur': _('Associe un détecteur, qui si résolu avec une source permet de lancer votre suite d\'action'),
        'designation': _('Description courte de ce que réalise votre automate, un objectif'),
        'production': _('Si cette case est cochée, votre automate sera executé en production'),
        'priorite': _('Un entier à partir de 0 (Zéro) permettant de priviligier une execution '
                    'd\'automate par rapport à un autre sur une source. De plus la priorité est proche de 0 (Zéro), '
                    'de plus il est prioritaire'),
        'notifiable': _('Active les notifications en cas d\'échec d\'au moins une des actions de votre automate')
    }

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
