from datetime import datetime

import flask_login
from flask import redirect, url_for, flash, request, Markup
from flask_admin import Admin, expose, helpers, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from webapp.data_access.sqlalchemy_models import User, EventGroup, Event, Country, Company, Market, \
    Sector, Commodity
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import form, fields, validators
from . import theapp, db
from flask_admin.model import typefmt
from webapp.data_access.sqlalchemy_models import User

###############################
### Initialize flask-login  ###
###############################
login_manager = flask_login.LoginManager()
login_manager.init_app(theapp)

# Create user loader function
@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)

# Define login form (for flask-login)
class LoginForm(form.Form):
    email = fields.StringField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_email(self, field):
        user = self.get_user()

        if user is None:
            # flash('Invalid user')
            raise validators.ValidationError('Invalid user')

        # we're comparing the plaintext pw with the the hash from the db
        # if not check_password_hash(user.password, self.password.data):
        # to compare plain text passwords use
        if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(User).filter_by(email=self.email.data).first()


# Create customized model view class
class AdminModelView(ModelView):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated

    form_excluded_columns = ['created_by_id', 'created_on', 'modified_by_id', 'modified_on']

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.created_by_id = flask_login.current_user.id
            model.created_on = datetime.now()

        model.modified_by_id = flask_login.current_user.id
        model.modified_on = datetime.now()


# Create customized index view class that handles login & registration
class FintechAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not flask_login.current_user.is_authenticated:
            url = url_for('.login_view')
            return redirect(url)
        return super(FintechAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            flask_login.login_user(user)
        # flash('You were successfully logged in')
        if flask_login.current_user.is_authenticated:
            return redirect(url_for('.index'))
        # link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
        self._template_args['form'] = form
        # self._template_args['link'] = link
        # return super(FintechAdminIndexView, self).index()
        return self.render("admin/login.html")

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = User()

            form.populate_obj(user)
            # we hash the users password to avoid saving it as plaintext in the db,
            # remove to use plain text:
            user.password = generate_password_hash(form.password.data)

            db.session.add(user)
            db.session.commit()

            login.login_user(user)
            return redirect(url_for('.index'))
        link = '<p>Already have an account? <a href="' + url_for('.login_view') + '">Click here to log in.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(FintechAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        flask_login.logout_user()
        return redirect(url_for('.index'))


class UserModelView(AdminModelView):
    can_view_details = True
    column_searchable_list = ['email']
    column_filters = ['email']
    column_list = ['email', 'type', 'created_on']

    types = [
        ('1', 'Public Portal'),
        ('2', 'Control Panel'),
        ('3', 'Control Panel Admin'),
        ('4', 'Developer')
    ]

    form_extra_fields = {
        'password': fields.PasswordField('Password')
    }

    def formatUserType(view, context, model, name):
        typesDict = {1: 'Public Portal', 2: 'Control Pannel', 3: 'Control Pannel Admin', 4: 'Developer'}
        return Markup('{}'.format(typesDict[model.type]))

    column_formatters = {
        'type': formatUserType
    }

    form_overrides = dict(type=fields.SelectField)
    form_args = dict(type=dict(choices=types))

    def on_model_change(self, form, model, is_created):
        super(UserModelView, self).on_model_change(form, model, is_created)
        model.password = generate_password_hash(form.password.data)


class EventGroupModelView(AdminModelView):
    form_columns = ['event_type','name_en', 'name_ar']
    column_list = ['name_en','name_ar','event_type']


    list_template = 'admin/custom_listview_eventgroup.html'

    def formatEventType(view, context, model, name):
        typesDict = {1: 'Single day event', 2: 'Range date event'}
        return Markup('{}'.format(typesDict[model.event_type]))

    column_formatters = {
        'event_type': formatEventType
    }

    # For Edit Event_Group ajax call to check whether the EventGoup Contain Events or Not.
    @expose('/chkcontainevents', methods=["GET"])
    def chkcontainevents(self):
        ev_id = request.args.get('event_group_id')
        data = db.session.query(Event).filter_by(event_group_id=ev_id).count()
        return str(data)


    form_overrides = dict(
        event_type=fields.SelectField
    )

    form_args = dict(
        event_type=dict(
            choices=[
                ('1', 'Single day event'),
                ('2', 'Range date event')
            ]
        ),
    )

############################################
### NOT NEEDED ANYMORE BUT DO NOT DELETE ###
############################################
# class EventCategoryModelView(AdminModelView):
#     can_view_details = True
#     form_excluded_columns = ['children', ]
#     form_columns = column_list = ['name_en', 'name_ar', 'is_subcategory', 'parent', 'created_on']
#     form_edit_rules = form_create_rules = ('parent', 'name_en', 'name_ar', 'is_subcategory')
#
#     def create_form(self):
#         return self._use_filtered_parent(
#             super(EventCategoryModelView, self).create_form()
#         )
#
#     def edit_form(self, obj):
#         return self._use_filtered_parent(
#             super(EventCategoryModelView, self).edit_form(obj)
#         )
#
#     def _use_filtered_parent(self, form):
#         form.parent.query_factory = self._get_parent_list
#         return form
#
#     def _get_parent_list(self):
#         return self.session.query(EventCategory).filter_by(is_subcategory=False).all()

class EventModelView(AdminModelView):
    form_columns = column_list = ['name_en', 'name_ar', 'type', 'starts_on', 'ends_on', 'event_group', 'company']
    form_edit_rules = form_create_rules = ('event_group', 'name_en', 'name_ar','starts_on', 'ends_on', 'company')

    column_filters = ('event_group.name_en', 'company.short_name_en', 'starts_on', 'ends_on', 'type', 'name_en', 'name_ar')

    form_overrides = dict(
        starts_on=fields.DateField,
        ends_on=fields.DateField

    )

    def formatEventType(view, context, model, name):
        typesDict = {1: 'Single day event', 2: 'Range date event'}
        return Markup('{}'.format(typesDict[model.type]))

    column_formatters = {
        'type': formatEventType
    }

    # For ajax call located in admin_master.html purpose to Enable or Disable Ends_On Field.
    @expose('/getType', methods=["GET", "POST"])
    def getType(self):
        ev_id =request.args.get('event_group')
        data = db.session.query(EventGroup.event_type).filter_by(id=ev_id).first()
        value = data.event_type
        return str(value)

    # Will Override Default Behavior and Print Null Over Empty.
    MY_DEFAULT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
    MY_DEFAULT_FORMATTERS.update({
        type(None): typefmt.null_formatter
    })
    column_type_formatters = MY_DEFAULT_FORMATTERS

    # Call When Model Change.
    def on_model_change(self, form, model, is_created):
        super(EventModelView, self).on_model_change(form, model, is_created)
        if model.company_id == '':
            model.company_id = None
        model.type = model.event_group.event_type  # Set Type value from selected dropdown of EventGroup type.



class MetaDataAdminModelView(AdminModelView):
    column_list = ['argaam_id', 'name_en', 'name_ar', 'short_name_en', 'short_name_ar']


##################################
### Create the Admin Interface ###
##################################
admin = Admin(theapp, name='Fintech CP', index_view=FintechAdminIndexView(), base_template='admin/admin_master.html',
              template_mode='bootstrap3')

###############################
### Add the ModelViews      ###
###############################Country, Markets, Sectors, Companies, Commodities
admin.add_view(UserModelView(User, db.session))
# admin.add_view(EventCategoryModelView(EventCategory, db.session))
admin.add_view(EventGroupModelView(EventGroup, db.session))
admin.add_view(EventModelView(Event, db.session))
admin.add_view(MetaDataAdminModelView(Country, db.session, category="Meta Data"))
admin.add_view(MetaDataAdminModelView(Market, db.session, category="Meta Data"))
admin.add_view(MetaDataAdminModelView(Sector, db.session, category="Meta Data"))
admin.add_view(MetaDataAdminModelView(Company, db.session, category="Meta Data"))
admin.add_view(MetaDataAdminModelView(Commodity, db.session, category="Meta Data"))