from io import StringIO, BytesIO

from flask import url_for, redirect, jsonify, request, Response, send_file
from flask_sqlalchemy import Pagination
from marshmallow.exceptions import MarshmallowError
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.datastructures import FileStorage

from flask_babelex import Babel

from hermes import Mail
from hermes.detecteur import AucuneObligationInteretException
from .flask_extended import Flask
from flask_migrate import Migrate
from flask_security import Security, login_required, current_user
from flask_security.utils import hash_password
from flask_admin import helpers as admin_helpers, AdminIndexView

from json import dumps
from os.path import realpath, dirname
from sys import modules
from os.path import join

from sqlalchemy.exc import NoReferencedTableError, NoSuchTableError, OperationalError, IntegrityError, SQLAlchemyError, \
    ProgrammingError

from hermes_ui.adminlte.admin import AdminLte, admins_store
from hermes_ui.adminlte.models import *
from hermes_ui.adminlte.views import FaLink

from hermes_ui.views import *

from hermes.session import SessionFiltre
from hermes.analysis import ExtractionInteret
from hermes.logger import logger, mem_handler
from hermes_ui.moteur.processus import InstanceInteroperabilite
from hermes_ui.incident import NotificationIncident

from hermes.i18n import _

from hermes_ui.marshmallow.legacy import *
from hermes_ui.marshmallow.front import *
from flask_webpackext.project import WebpackTemplateProject
from flask_webpackext import FlaskWebpackExt


app = Flask(__name__)
app.config.from_yaml(join(app.root_path, '../configuration.yml'))
app.config['JSON_SORT_KEYS'] = False

app.logger = logger

__path__ = dirname(realpath(__file__))

security = Security(app, admins_store)

babel = Babel(
    app
)

project = WebpackTemplateProject(
    __name__,
    project_folder='assets',
    config_path='assets/config.json',
)

app.config.update(dict(
    WEBPACKEXT_PROJECT=project,
))

# Initialize extension
FlaskWebpackExt(app)

admin = AdminLte(
    app,
    skin='green-light',
    name=_('Hermes - Automates à réaction aux échanges IMAP'),
    short_name="<b>H</b><sup>ermes</sup>",
    long_name="<b>Hermes</b>",
    index_view=AdminIndexView(name=_("Éditeur d'Automate"), menu_icon_value='fa-pencil', menu_icon_type='fa')
)

db.init_app(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)
NotificationIncident.init_app(app)

admin.add_view(
    BoiteAuxLettresImapView(
        BoiteAuxLettresImap,
        db.session,
        name=_("Boite aux lettres (IMAP)"),
        menu_icon_value="fa-envelope",
        category=_("Sources de données")
    )
)

admin.add_view(
    ConfigurationView(
        Configuration,
        db.session,
        name=_("Mes variables globales"),
        menu_icon_value="fa-cogs"
    )
)

admin.add_view(
    AutomateView(
        Automate,
        db.session,
        name=_("Description des Automates"),
        menu_icon_value="fa-android"
    )
)

admin.add_view(
    DectecteurView(
        Detecteur,
        db.session,
        name=_("Détecteur"),
        menu_icon_value="fa-flag"
    )
)

admin.add_view(
    IdentificateurRechercheInteretView(
        IdentificateurRechercheInteret,
        db.session,
        name=_("Identifiant"),
        menu_icon_value="fa-sort-numeric-desc",
        category=_("Critères de recherche")
    )
)

admin.add_view(
    LocalisationExpressionRechercheInteretView(
        LocalisationExpressionRechercheInteret,
        db.session,
        name=_("Recherche d'expression"),
        menu_icon_value="fa-search-plus",
        category=_("Critères de recherche")
    )
)

admin.add_view(
    DateRechercheInteretView(
        DateRechercheInteret,
        db.session,
        name=_("Date"),
        menu_icon_value="fa-calendar",
        category=_("Critères de recherche")
    )
)

admin.add_view(
    ExpressionXPathInteretView(
        ExpressionXPathRechercheInteret,
        db.session,
        name=_("XPath (HTML)"),
        menu_icon_value="fa-code",
        category=_("Critères de recherche")
    )
)

admin.add_view(
    ExpressionCleRechercheInteretView(
        ExpressionCleRechercheInteret,
        db.session,
        name=_("Expression exacte"),
        menu_icon_value="fa-commenting",
        category=_("Critères de recherche")
    )
)

admin.add_view(
    CleRechercheInteretView(
        CleRechercheInteret,
        db.session,
        name=_("Clé"),
        menu_icon_value="fa-key",
        category=_("Critères de recherche")
    )
)

admin.add_view(
    ExpressionDansCleRechercheInteretView(
        ExpressionDansCleRechercheInteret,
        db.session,
        name=_("Expression exacte dans la clé"),
        menu_icon_value="fa-cubes",
        category=_("Critères de recherche")
    )
)

admin.add_view(
    ExpressionReguliereRechercheInteretView(
        ExpressionReguliereRechercheInteret,
        db.session,
        name=_("Expression régulière"),
        menu_icon_value="fa-magic",
        category=_("Critères de recherche")
    )
)

admin.add_view(
    InformationRechercheInteretView(
        InformationRechercheInteret,
        db.session,
        name=_("Information balisée"),
        menu_icon_value="fa-hashtag",
        category=_("Critères de recherche")
    )
)

admin.add_view(
    OperationLogiqueRechercheInteretView(
        OperationLogiqueRechercheInteret,
        db.session,
        name=_("Opération sur critères"),
        menu_icon_value="fa-list-ol",
        category=_("Critères de recherche")
    )
)

admin.add_view(
    RechercheInteretView(
        RechercheInteret,
        db.session,
        name=_("Vue globales critères"),
        menu_icon_value="fa-list"
    )
)

admin.add_link(FaLink(name='GitHub', category=_('Liens'), url='https://github.com/Ousret/hermes',
                              icon_value='fa-github', target="_blank"))

admin.add_link(FaLink(name=_('Support'), category=_('Liens'), url='https://github.com/Ousret/hermes/issues',
                              icon_value='fa-ticket', target="_blank"))

admin.add_link(FaLink(name=_('Documentations'), category=_('Liens'), url='https://github.com/Ousret/hermes/blob/master/docs/CHAPITRE-1.md',
                              icon_value='fa-book', target="_blank"))

bookmarks = app.config.get('BOOKMARKS')

if bookmarks:

    for bookmark in bookmarks:
        admin.add_link(FaLink(name=bookmark['LABEL'], category=_('Liens'), url=bookmark['URL'],
                              icon_value=bookmark['ICON'], target="_blank"))


admin.set_category_icon(name='Liens', icon_value='fa-star')


@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )


@babel.localeselector
def get_locale():
    translations = [str(translation) for translation in babel.list_translations()]
    return request.accept_languages.best_match(translations)


@app.route("/", methods=['GET'])
def index():
    return redirect(app.config.get('SECURITY_URL_PREFIX'))


@app.route("/admin/import/automates", methods=['GET'])
@login_required
def import_automates():
    automates = db.session.query(Automate).all()

    r = AutomateLegacySchema(many=True).jsonify(automates)  # type: Response

    return send_file(
        BytesIO(r.get_data() if isinstance(r.get_data(), bytes) else r.get_data().encode('utf-8')),
        attachment_filename='automates-{}.json'.format(datetime.datetime.now().timestamp()),
        mimetype='text/json; charset=utf-8',
        as_attachment=True
    )


@app.route("/admin/export/automates", methods=['POST'])
@login_required
def export_automates():
    if 'file' not in request.files:
        return jsonify({'message': 'Aucun fichier envoyé'}), 400

    mon_fichier = request.files['file']  # type: FileStorage

    if mon_fichier.content_type != 'application/json' or mon_fichier.filename.endswith('.json') is False:
        return jsonify({'message': _('Fichier message invalide, fichier JSON requis !')}), 400

    def rec_(at, act):
        """
        :param Automate at:
        :param ActionNoeud act:
        :return:
        """
        act.automate_id = at.id
        if act.action_reussite is not None:
            rec_(at, act.action_reussite)
        if act.action_echec is not None:
            rec_(at, act.action_echec)

    db.session.query(ActionNoeudExecution).delete()
    db.session.query(RechercheInteretExecution).delete()
    db.session.query(AutomateExecution).delete()

    for sb in ActionNoeud.__subclasses__():
        db.session.query(sb).delete()

    db.session.query(ActionNoeud).delete()
    db.session.query(Automate).delete()

    db.session.query(LienDetecteurRechercheInteret).delete()

    db.session.query(LienSousRegleOperationLogique).delete()

    for sb in RechercheInteret.__subclasses__():
        db.session.query(sb).delete()

    db.session.query(RechercheInteret).delete()

    db.session.query(Detecteur).delete()

    db.session.commit()
    db.session.flush()

    try:
        from json import loads
        automates = AutomateLegacySchema(many=True).load(loads(mon_fichier.stream.read().decode('ascii')))  # type: list[Automate]
    except MarshmallowError as e:
        return jsonify({'message': _("Impossible d'importer votre fichier '{fname}' car votre fichier ne respecte pas la structure JSON obligatoire ! '{msg_err}'.").format(fname=mon_fichier.filename, msg_err=str(e))}), 409

    for automate in automates:

        try:
            act_r = deepcopy(automate.action_racine)
            automate.action_racine = None

            automate.createur = current_user
            automate.responsable_derniere_modification = current_user

            automate.detecteur.createur = current_user
            automate.detecteur.responsable_derniere_modification = current_user

            for rg in automate.detecteur.regles:

                ri_ex = db.session.query(RechercheInteret).filter_by(designation=rg.designation, mapped_class_child=rg.mapped_class_child).first()

                if ri_ex is not None:
                    automate.detecteur.regles[automate.detecteur.regles.index(rg)] = ri_ex

            db.session.add(automate)
            db.session.commit()

            if act_r is not None:
                rec_(automate, act_r)
                automate.action_racine = act_r
                db.session.commit()

        except SQLAlchemyError as e:
            logger.error(
                _("Impossible d'importer votre automate '{automate_nom}' car une erreur de transposition en base de données est survenue '{msg_err}'."),
                automate_nom=automate.designation,
                msg_err=str(e)
            )
            continue

    try:
        db.session.flush()
    except SQLAlchemyError as e:
        logger.warning(
            _("Erreur SQL '{err_msg}'."), err_msg=str(e)
        )
        return jsonify({'message': _('Erreur de transaction SQL : {err_msg}').format(err_msg=str(e))}), 409

    return jsonify({}), 204


@app.route("/admin/rest/statistique", methods=['GET'])
@login_required
def recuperation_statistique_generale():

    nb_automate = db.session.query(Automate).count()
    nb_execution = db.session.query(AutomateExecution).count()
    nb_critere = db.session.query(RechercheInteret).count()

    nb_execution_reussite = db.session.query(AutomateExecution).filter_by(validation_automate=True).count()
    nb_execution_echec = db.session.query(AutomateExecution).filter_by(validation_automate=False).count()

    return jsonify(
        {
            'automate': nb_automate,
            'executions': nb_execution,
            'reussites': nb_execution_reussite,
            'echecs': nb_execution_echec,
            'criteres': nb_critere
        }
    ), 200


@app.route("/admin/rest/statistique/automate/<int:automate_id>", methods=['GET'])
@login_required
def recuperation_statistique_automate(automate_id):
    nb_execution = db.session.query(AutomateExecution).filter_by(automate_id=automate_id).count()

    nb_execution_reussite = db.session.query(AutomateExecution).filter_by(validation_automate=True, automate_id=automate_id).count()
    nb_execution_echec = db.session.query(AutomateExecution).filter_by(validation_automate=False, automate_id=automate_id).count()

    return jsonify(
        {
            'executions': nb_execution,
            'reussites': nb_execution_reussite,
            'echecs': nb_execution_echec
        }
    ), 200


@app.route("/admin/rest/automate-execution", methods=['GET'])
@login_required
def lecture_automates_executions():
    page = request.args.get('page', default=1, type=int)
    executions = db.session.query(AutomateExecution).order_by(AutomateExecution.date_finalisation.desc()).paginate(page, 50)  # type: Pagination
    return AutomateExecutionDataTableSchema().jsonify(AutomateExecutionDataTable(executions.items)), 200


@app.route("/admin/rest/automate-execution/<int:automate_execution_id>", methods=['GET'])
@login_required
def lecture_automate_execution(automate_execution_id):
    execution = db.session.query(AutomateExecution).get(automate_execution_id)
    return AutomateExecutionSchema().jsonify(execution), 200 if execution is not None else 404


@app.route("/admin/rest/automate-execution/automate/<int:automate_id>", methods=['GET'])
@login_required
def lecture_automate_executions(automate_id):

    executions = db.session.query(AutomateExecution).filter_by(
        automate_id=automate_id
    ).order_by(
        AutomateExecution.date_finalisation.desc()
    ).paginate(
        1,
        50
    )  # type: Pagination

    return AutomateExecutionDataTableSchema().jsonify(AutomateExecutionDataTable(executions.items)), 200


@app.route("/admin/rest/assistance-saisie", methods=['GET'])
@login_required
def assistance_saisie():

    configurations = db.session.query(Configuration).all()  # type: list[Configuration]

    for conf_globale in configurations:
        Session.charger_input(
            conf_globale.designation,
            conf_globale.valeur,
            conf_globale.format
        )

    propositions = list()

    for el in Session.UNIVERSELLE.variables_disponibles:
        propositions.append('{{'+str(el)+'}}')

    for filtre in SessionFiltre.FILTRES:
        propositions.append('|'+filtre.methode)

    return jsonify(
        propositions
    ), 200


@app.route("/admin/rest/assistance-saisie/automate/<int:automate_id>", methods=['GET'])
@login_required
def assistance_saisie_automate(automate_id):
    automate = db.session.query(Automate).get(automate_id)

    if automate is None:
        return jsonify(
            {'message': _('Impossible de proposer la liste des variables disponibles pour un automate inexistant')})

    propositions = list()

    for el in automate.detecteur.regles:  # type: RechercheInteret
        if el.friendly_name is not None and el.friendly_name != '':
            propositions.append('{{' + el.friendly_name + '}}')

    for el in automate.actions:  # type: ActionNoeud
        if el.friendly_name is not None and el.friendly_name != '':
            propositions.append('{{' + el.friendly_name + '}}')

    return jsonify(
        propositions
    ), 200


@app.route("/admin/service", methods=['GET'])
@login_required
def etat_service():
    return jsonify({}), 204 if InstanceInteroperabilite.current_thread is None else 200


@app.route("/admin/service", methods=['POST'])
@login_required
def demarrer_service():
    return jsonify({}), 201 if InstanceInteroperabilite.demarrer() is True else 409


@app.route("/admin/service", methods=['DELETE'])
@login_required
def arreter_service():
    return jsonify({}), 204 if InstanceInteroperabilite.arreter() is True else 409


@app.route("/admin/service/test", methods=['POST'])
@login_required
def creation_test_service():
    automate_id = request.form.get('automate_id', type=int, default=None)

    if automate_id is None:
        return jsonify({}), 400

    if InstanceInteroperabilite.current_thread is not None:
        return jsonify({'message': _("L'environnement de test nécessite que le traitement des flux soit désactivé.")}), 409

    automate = db.session.query(Automate).get(automate_id)  # type: Automate

    if automate is None:
        return jsonify({'message': _('Aucun automate ne correspond à ID {id}').format(id=automate_id)}), 404

    if automate.production is True:
        return jsonify({'message': _('Votre automate ne doit pas être en mode production.')}), 409

    InstanceInteroperabilite.liste_attente_test_lock.acquire(blocking=True)

    if automate_id in InstanceInteroperabilite.liste_attente_test:
        InstanceInteroperabilite.liste_attente_test_lock.release()
        return jsonify({'message': _("Votre automate est toujours en attente d'être testé. Veuillez patienter.")}), 409

    InstanceInteroperabilite.liste_attente_test.append(automate_id)
    InstanceInteroperabilite.liste_attente_test_lock.release()

    demarrage = InstanceInteroperabilite.demarrer()

    return jsonify({}), 201 if demarrage is True else 409


@app.route("/admin/rest/simulation/detecteur/fichier", methods=['POST'])
@login_required
def simulation_detecteur_fichier():
    if 'file' not in request.files:
        return jsonify({'message': 'Aucun fichier envoyé'}), 400

    mon_fichier = request.files['file']  # type: FileStorage

    if (mon_fichier.content_type != 'application/octet-stream' and mon_fichier.content_type != 'message/rfc822') or (
            mon_fichier.filename.endswith('.eml') is False and mon_fichier.filename.endswith('.msg') is False):
        return jsonify({'message': _('Fichier message invalide, fichier binaire *.EML ou *.MSG requis !')}), 400

    if mon_fichier.filename.endswith('.eml') is True:
        mon_message = Mail.from_eml(mon_fichier.stream.read())
    else:
        mon_message = Mail.from_msg(mon_fichier.stream.read())

    detecteurs = db.session.query(Detecteur).all()

    ob_detecteurs = list()
    ma_reponse_html = str()

    ma_reponse_html += """
    <div class="panel box box-warning">
      <div class="box-header with-border">
        <h4 class="box-title">
          <a data-toggle="collapse" data-parent="#accordion" href="#collapse-x" aria-expanded="false" class="">
            Ce que le moteur perçoit
          </a>
        </h4>
      </div>
      <div id="collapse-x" class="panel-collapse collapse" aria-expanded="false" style="">
        <div class="box-body">
            <pre>
    <code class="json">
{perception_moteur}
    </code>
            </pre>
        </div>
      </div>
    </div>""".format(
        perception_moteur=dumps(mon_message.extraction_interet.interets, indent=4, ensure_ascii=False)
    )

    for detecteur, i in zip(detecteurs, range(0, len(detecteurs))):
        ob_detecteurs.append(
            detecteur.transcription()
        )
        try:
            ob_detecteurs[-1].lance_toi(mon_message)
        except AucuneObligationInteretException as e:
            continue

        ma_reponse_html += """
<div class="panel box {box_color}">
  <div class="box-header with-border">
    <h4 class="box-title">
      <a data-toggle="collapse" data-parent="#accordion" href="#collapse{i_row}" aria-expanded="false" class="">
        {detecteur_res}
      </a>
    </h4>
  </div>
  <div id="collapse{i_row}" class="panel-collapse collapse" aria-expanded="false" style="">
    <div class="box-body">
        <pre>
<code>
{detecteur_explications}
</code>
        </pre>
    </div>
  </div>
</div>""".format(
            detecteur_res=str(ob_detecteurs[-1]),
            detecteur_explications=ob_detecteurs[-1].explain(),
            box_color="box-success" if ob_detecteurs[-1].est_accomplis else 'box-danger',
            i_row=str(i),
        )

    return Response(
        ma_reponse_html,
        status=200,
        content_type='text/html'
    )


@app.route("/admin/rest/simulation/detecteur", methods=['POST'])
@login_required
def simulation_detecteur():

    detecteur_id = request.form.get('detecteur_id', type=int, default=None)

    sujet = request.form.get('sujet', type=str, default=None)
    corps = request.form.get('corps', type=str, default=None)

    if sujet is None:
        return jsonify({'message': _('Formulaire incomplet, manque le sujet de la source')}), 400
    if corps is None:
        return jsonify({'message': _('Formulaire incomplet, manque le corps de la source')}), 400

    if detecteur_id is None:
        return jsonify({'message': _('Formulaire incomplet, manque l\'identifiant du detecteur cible à tester')}), 400

    detecteur = db.session.query(Detecteur).get(detecteur_id)  # type: Detecteur

    if detecteur is None:
        return jsonify({'message': _('Impossible de trouver le detecteur n°{n}').format(n=str(detecteur_id))}), 404

    from hermes.source import Source as SourceNatif

    k = detecteur.transcription()

    d = SourceNatif(
        sujet,
        corps
    )

    k.lance_toi(
        d
    )

    return jsonify(
        {
            'explications': k.explain(),
            'interets': d.extraction_interet.interets
        }
    ), 200 if k.est_accomplis is True else 409


@app.route("/admin/rest/simulation/extraction-interet", methods=['POST'])
@login_required
def simulation_extraction_interet():
    sujet = request.form.get('sujet', type=str, default=None)
    corps = request.form.get('corps', type=str, default=None)

    if sujet is None:
        return jsonify({'message': _('Formulaire incomplet, manque le sujet de la source')}), 409
    if corps is None:
        return jsonify({'message': _('Formulaire incomplet, manque le corps de la source')}), 409

    mon_extraction_interet = ExtractionInteret(
        sujet,
        corps
    )

    return jsonify(
        mon_extraction_interet.interets
    ), 201


@app.route("/admin/rest/logger", methods=['GET'])
@login_required
def lecture_journal():
    offset = request.args.get('offset', type=int, default=None)

    try:
        with StringIO('\n'.join([str(el.msg) for el in mem_handler.buffer])) as fp:

            # Récupération de l'offset maximale
            fp.seek(0, 2)
            max_offset = fp.tell()

            # Revenir au début du fichier
            fp.seek(0, 1)

            if offset is not None and max_offset > offset >= 0:
                fp.seek(offset)
            return jsonify(
                {
                    'logs': fp.readlines() if offset > 0 else [],
                    'offset': fp.tell() if offset > 0 else max_offset
                }
            ), 200
    except IOError as e:
        pass

    return jsonify({'logs': [], 'offset': 0}), 204


@app.route("/admin/rest/detecteur", methods=['GET'])
@login_required
def lecture_detecteurs():
    detecteurs = db.session.query(Detecteur).all()

    return DetecteurSchema(many=True).jsonify(detecteurs), 200


@app.route("/admin/rest/automate", methods=['GET'])
@login_required
def lecture_automates():
    automates = db.session.query(Automate).all()

    return AutomateSchema(many=True).jsonify(automates), 200


@app.route("/admin/rest/legacy/automate/<int:automate_id>", methods=['GET'])
@login_required
def lecture_legacy_automate(automate_id):
    automate = db.session.query(Automate).get(automate_id)  # type: Automate
    if automate is None:
        return jsonify({'message': _('Aucun automate ne correspond à ID {id}').format(id=automate_id)}), 404
    return AutomateLegacySchema().jsonify(automate), 200


@app.route("/admin/rest/type/action_noeud", methods=['GET'])
@login_required
def lecture_liste_action_noeud_type():

    return jsonify(
        ActionNoeud.descriptifs()
    ), 200


@app.route("/admin/rest/automate/<int:automate_id>", methods=['GET'])
@login_required
def lecture_automate(automate_id):
    automate = db.session.query(Automate).get(automate_id)  # type: Automate
    if automate is None:
        return jsonify({'message': _('Aucun automate ne correspond à ID {id}').format(id=automate_id)}), 404
    return AutomateSchema().jsonify(automate), 200


@app.route("/admin/rest/automate/<int:automate_id>/action_noeud", methods=['GET'])
@login_required
def lecture_actions_automate(automate_id):
    actions = db.session.query(ActionNoeud).filter_by(automate_id=automate_id).options().all()  # type: list[ActionNoeud]
    return ActionNoeudSchema(many=True).jsonify(actions), 200


@app.route("/admin/rest/automate/<int:automate_id>/action_noeud/<int:action_noeud_id>", methods=['GET'])
@login_required
def lecture_action_automate(automate_id, action_noeud_id):
    action = db.session.query(ActionNoeud).filter_by(automate_id=automate_id, id=action_noeud_id).one()  # type: ActionNoeud

    if action is None:
        return jsonify({}), 404

    decompose_type_action = action.mapped_class_child.split("'")  # type: list[str]

    if len(decompose_type_action) != 3 or not decompose_type_action[-2].startswith('hermes_ui.models.'):
        return jsonify(
            {'message': _('Type d\'action illégale à la création: "{action_type}"').format(action_type=decompose_type_action[-2])}), 409

    target_module = modules['.'.join(decompose_type_action[-2].split('.')[0:-1])]

    try:
        target_model_class = getattr(target_module, decompose_type_action[-2].split('.')[-1])
    except AttributeError as e:
        return jsonify({'message': _('Le type d\'action demandé à la création est inexistant: {action_type}').format(
            action_type=decompose_type_action[-2].split('.')[-1])}), 400

    target_sub_action = db.session.query(target_model_class).filter_by(automate_id=automate_id, id=action_noeud_id).one()  # type: ActionNoeud

    for schema_action_noeud_class in ActionNoeudSchema.__subclasses__():

        if str(schema_action_noeud_class).split('.')[-1][0:-2].startswith(str(target_model_class).split('.')[-1][0:-2]):
            return schema_action_noeud_class().jsonify(target_sub_action), 200

    return ActionNoeudSchema().jsonify(target_sub_action), 200


@app.route("/admin/rest/automate/<int:automate_id>/action_noeud", methods=['POST'])
@login_required
def creation_action(automate_id):
    automate = db.session.query(Automate).get(automate_id)  # type: Automate

    if not request.is_json:
        return jsonify({'message': _('Aucun corps JSON présent dans la requête HTTP')}), 400

    if automate is None:
        return jsonify({'message': _('Aucun automate ne correspond à ID {id}').format(id=automate_id)}), 404

    payload = request.json  # type: dict

    if 'type' not in payload or ('parent' not in payload and 'remplacement' not in payload) or 'formulaire' not in payload:
        return jsonify({'message': _('Le JSON présent dans la requête est invalide')}), 400

    type_action = payload['type']
    parent_information = payload['parent'] if 'parent' in payload else None
    remplacement_action_noeud = payload['remplacement'] if 'remplacement' in payload else None
    formulaire = payload['formulaire']

    decompose_type_action = type_action.split("'")  # type: list[str]

    if len(decompose_type_action) != 3 or not decompose_type_action[-2].startswith('hermes_ui.models.'):
        return jsonify({'message': _('Type d\'action illégale à la création: "{action_type}"').format(action_type=decompose_type_action[-2])}), 409

    target_module = modules['.'.join(decompose_type_action[-2].split('.')[0:-1])]

    try:
        target_model_class = getattr(target_module, decompose_type_action[-2].split('.')[-1])  # type: type(ActionNoeud)
    except AttributeError as e:
        return jsonify({'message': _('Le type d\'action demandé à la création est inexistant: {action_type}').format(action_type=decompose_type_action[-2].split('.')[-1])}), 400

    for key_form in formulaire.keys():
        if isinstance(formulaire[key_form], str) and len(formulaire[key_form].strip()) == 0 and key_form in target_model_class.PARAMETRES.keys() and target_model_class.PARAMETRES[key_form]['required'] is False:
            formulaire[key_form] = None

    try:
        target_model_instance = target_model_class(**formulaire)  # type: ActionNoeud
    except AttributeError as e:
        return jsonify({'message': _('Le formulaire de création est invalide, pour cause de "{msg_err}"').format(msg_err=str(e))}), 400

    target_model_instance.mapped_class_child = str(target_model_instance.__class__)

    target_model_instance.automate = automate
    target_model_instance.automate_id = automate.id

    target_model_instance.createur = current_user
    target_model_instance.responsable_derniere_modification = current_user

    target_model_instance.date_creation = datetime.datetime.now()
    target_model_instance.date_modification = datetime.datetime.now()

    try:
        db.session.add(target_model_instance)
        db.session.commit()
    except IntegrityError as e:
        return jsonify({'message': str(e)}), 409

    if remplacement_action_noeud is None:

        if parent_information is None:
            automate.action_racine = target_model_instance
        else:
            if len(parent_information) != 2:
                return jsonify({'message': _('Les informations de votre action parente sont malformés')}), 400

            action_parente_id, etat_reussite = tuple(parent_information)
            action_noeud_parente = db.session.query(ActionNoeud).filter_by(automate_id=automate_id, id=int(action_parente_id)).one()  # type: ActionNoeud

            if action_noeud_parente is None:
                return jsonify({'message': _('L\'action parente n\'existe pas !')}), 404

            if 'ECHEC' in parent_information:
                # cas simple de non ajout
                if action_noeud_parente.action_echec is None:
                    target_model_instance.action_echec_id = action_noeud_parente.id
                else:
                    # cas insertion dans arbre
                    action_deplacement = action_noeud_parente.action_echec

                    action_noeud_parente.action_echec = target_model_instance

                    target_model_instance.action_echec = action_deplacement

            elif 'REUSSITE' in parent_information:
                if action_noeud_parente.action_reussite is None:
                    target_model_instance.action_reussite_id = action_noeud_parente.id
                else:
                    # cas insertion dans arbre
                    action_deplacement = action_noeud_parente.action_reussite

                    action_noeud_parente.action_reussite = target_model_instance

                    target_model_instance.action_reussite = action_deplacement
    else:
        noeud_a_remplacer = db.session.query(ActionNoeud).filter_by(automate_id=automate_id, id=int(remplacement_action_noeud)).one()  # type: ActionNoeud

        if noeud_a_remplacer is None:
            return jsonify({'message': _("Le noeud que vous souhaitez remplacer est inexistant")}), 404

        target_model_instance.action_echec = noeud_a_remplacer.action_echec
        target_model_instance.action_reussite = noeud_a_remplacer.action_reussite

        noeud_a_remplacer.action_echec = None
        noeud_a_remplacer.action_reussite = None

        try:
            noeud_a_mettre_niveau_r = db.session.query(ActionNoeud).filter_by(automate_id=automate_id, action_reussite=noeud_a_remplacer).one()  # type: ActionNoeud
        except NoResultFound:
            noeud_a_mettre_niveau_r = None

        try:
            noeud_a_mettre_niveau_f = db.session.query(ActionNoeud).filter_by(automate_id=automate_id, action_echec=noeud_a_remplacer).one()  # type: ActionNoeud
        except NoResultFound:
            noeud_a_mettre_niveau_f = None

        if noeud_a_mettre_niveau_r is not None:
            noeud_a_mettre_niveau_r.action_reussite = target_model_instance

        if noeud_a_mettre_niveau_f is not None:
            noeud_a_mettre_niveau_f.action_echec = target_model_instance

        if noeud_a_mettre_niveau_r is None and noeud_a_mettre_niveau_f is None:
            automate.action_racine = target_model_instance

        db.session.delete(noeud_a_remplacer)

    try:
        db.session.commit()
        db.session.flush()
    except IntegrityError as e:
        return jsonify({'message': str(e)}), 409

    return jsonify({}), 201


@app.route("/admin/rest/automate/<int:automate_id>/action_noeud/<int:action_noeud_id>", methods=['PUT', 'PATCH'])
@login_required
def modification_action(automate_id, action_noeud_id):
    automate = db.session.query(Automate).get(automate_id)  # type: Automate
    action_noeud = db.session.query(ActionNoeud).filter_by(automate_id=automate_id, id=action_noeud_id).first()  # type: ActionNoeud

    if not request.is_json:
        return jsonify({'message': _('Aucun corps JSON présent dans la requête HTTP')}), 400

    if automate is None:
        return jsonify({'message': _('Aucun automate ne correspond à ID {id}').format(id=automate_id)}), 404
    if action_noeud is None:
        return jsonify({'message': _('Aucun action noeud ne correspond à ID {action_id} pour l\'automate ID {automate_id}').format(action_id=action_noeud_id, automate_id=automate_id)}), 404

    payload = request.json  # type: dict

    if 'type' not in payload.keys() or 'formulaire' not in payload.keys():
        return jsonify({'message': _('Le JSON présent dans la requête est invalide')}), 400

    type_action = payload['type']
    formulaire = payload['formulaire']  # type: dict

    decompose_type_action = type_action.split("'")  # type: list[str]

    target_module = modules['.'.join(decompose_type_action[-2].split('.')[0:-1])]

    target_model_class = getattr(target_module, decompose_type_action[-2].split('.')[-1])
    target_model_instance = db.session.query(target_model_class).get(action_noeud.id)  # type: ActionNoeud

    for key_attr in formulaire.keys():
        try:
            getattr(target_model_instance, key_attr)
        except AttributeError as e:
            return jsonify({'message': str(e)}), 409

        if key_attr in target_model_class.PARAMETRES.keys() and target_model_class.PARAMETRES[key_attr]['format'] == 'CHECKBOX':
            formulaire[key_attr] = True if formulaire[key_attr] == 1 else False

        if isinstance(formulaire[key_attr], str) and len(formulaire[key_attr].strip()) == 0 and key_attr in target_model_class.PARAMETRES.keys() and target_model_class.PARAMETRES[key_attr]['required'] is False:
            formulaire[key_attr] = None

        setattr(target_model_instance, key_attr, formulaire[key_attr])

    try:
        db.session.commit()
        db.session.flush()
    except IntegrityError as e:
        return jsonify({'message': str(e)}), 409

    return jsonify({}), 200


@app.route("/admin/rest/automate/<int:automate_id>/action_noeud/<int:action_noeud_id>", methods=['DELETE'])
@login_required
def supprimer_action(automate_id, action_noeud_id):
    automate = db.session.query(Automate).get(automate_id)  # type: Automate
    action_noeud = db.session.query(ActionNoeud).filter_by(automate_id=automate_id,
                                                           id=action_noeud_id).one()  # type: ActionNoeud

    if automate is None:
        return jsonify({'message': _('Aucun automate ne correspond à ID {id}').format(id=automate_id)}), 404
    if action_noeud is None:
        return jsonify({'message': _('Aucun action noeud ne correspond à ID {action_id} pour l\'automate ID {automate_id}').format(action_id=action_noeud_id, automate_id=automate_id)}), 404

    cascade_delete = request.form.get('cascade', default=0, type=int)

    if automate.action_racine_id == action_noeud.id:
        automate.action_racine_id = None
        automate.action_racine = None

    if cascade_delete > 0:
        db.session.delete(action_noeud)
    else:
        try:
            noeud_a_mettre_niveau_r = db.session.query(ActionNoeud).filter_by(automate_id=automate_id, action_reussite=action_noeud).one()  # type: ActionNoeud
        except NoResultFound:
            noeud_a_mettre_niveau_r = None

        try:
            noeud_a_mettre_niveau_f = db.session.query(ActionNoeud).filter_by(automate_id=automate_id, action_echec=action_noeud).one()  # type: ActionNoeud
        except NoResultFound:
            noeud_a_mettre_niveau_f = None

        if noeud_a_mettre_niveau_r is not None:
            noeud_a_mettre_niveau_r.action_reussite = action_noeud.action_reussite
            action_noeud.action_reussite = None

        if noeud_a_mettre_niveau_f is not None:
            noeud_a_mettre_niveau_f.action_echec = action_noeud.action_echec
            action_noeud.action_echec = None

        if noeud_a_mettre_niveau_r is None and noeud_a_mettre_niveau_f is None:
            automate.action_racine = action_noeud.action_reussite or action_noeud.action_echec

        db.session.delete(action_noeud)

    db.session.commit()
    db.session.flush()

    return jsonify({}), 204


def init_db():
    logger.warning("Database will be created from scratch")

    db.drop_all()
    db.create_all()

    with app.app_context():

        super_admin_role = Role(name='superadmin')
        admin_role = Role(name='admin')

        db.session.add(super_admin_role)
        db.session.add(admin_role)

        db.session.commit()

        test_user = admins_store.create_user(
            first_name='admin',
            last_name='hermes',
            email='hermes@localhost',
            password=hash_password('admin'),
            roles=[super_admin_role, admin_role]
        )

        db.session.add(test_user)

        db.session.commit()

    logger.info("Database has been created")
    return


try:
    db.session.query(Role).all()
except NoReferencedTableError as e:
    init_db()
except NoSuchTableError as e:
    init_db()
except ProgrammingError as e:
    init_db()
except OperationalError as e:  # dirty hack..
    init_db()
except Exception as e:
    init_db()
