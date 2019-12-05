from flask_admin.contrib import sqla
from flask_security import current_user
from flask import url_for, redirect, request, abort
from flask_admin import menu
from flask_security.utils import hash_password
from flask_security.forms import EqualTo, unique_user_email
from wtforms import fields, validators
from wtforms.fields import html5


class FaLink(menu.MenuLink):

    def __init__(self, name, url = None, endpoint = None, category = None, class_name = None, icon_type = "fa",
                 icon_value = None, target = None):
        super(FaLink, self).__init__(name, url, endpoint, category, class_name, icon_type, icon_value, target)


class FaModelView(sqla.ModelView):

    def __init__(self, model, session, name = None, category = None, endpoint = None, url = None, static_folder = None,
                 menu_class_name = None, menu_icon_type = "fa", menu_icon_value = None):
        super(FaModelView, self).__init__(model, session, name, category, endpoint, url, static_folder, menu_class_name,
                                          menu_icon_type, menu_icon_value)


class BaseAdminView(FaModelView):
    required_role = 'admin'
    can_export = True
    can_view_details = True
    can_create = True
    can_edit = True
    can_delete = True
    edit_modal = True
    create_modal = True
    details_modal = True

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role(self.required_role):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
                return redirect(url_for('security.login', next = request.url))


class AdminsView(BaseAdminView):
    required_role = 'superadmin'

    column_display_all_relations = True
    column_editable_list = ['email', 'first_name', 'last_name']
    column_searchable_list = ['roles.name', 'email', 'first_name', 'last_name']
    column_exclude_list = ['password']
    column_details_exclude_list = ['password']
    form_excluded_columns = ['password']
    column_filters = ['email', 'first_name', 'last_name']
    can_export = True
    can_view_details = True
    can_create = True
    can_edit = True
    can_delete = True
    edit_modal = True
    create_modal = True
    details_modal = True

    def on_model_change(self, form, model, is_created):
        """
        :param form:
        :param hermes_ui.adminlte.models.User model:
        :param is_created:
        :return:
        """
        model.password = hash_password(form.password.data)

    def get_create_form(self):
        CreateForm = super().get_create_form()

        CreateForm.email = html5.EmailField(
            'Email',
            validators=[
                validators.DataRequired(),
                validators.Email(),
                unique_user_email,
            ],
        )
        CreateForm.password = fields.PasswordField(
            'Password',
            validators=[
                validators.DataRequired(),
            ],
        )

        CreateForm.confirm_password = fields.PasswordField(
            'Confirm Password',
            validators=[
                validators.DataRequired(),
                EqualTo('password', message='RETYPE_PASSWORD_MISMATCH'),
            ],
        )

        CreateForm.field_order = (
            'email', 'first_name', 'last_name',
            'password', 'confirm_password', 'roles', 'active')

        return CreateForm
