const $ = require('jquery');
const Swal = require('sweetalert2');
let Dropzone = require('dropzone');
Dropzone.autoDiscover = false;

require('datatables.net-bs');
require('jquery.terminal');

const introJs = require('intro.js');
global.introJs = introJs;

const moment = require('moment');
require('moment/locale/fr');

require('datatables.net-bs/css/dataTables.bootstrap.css');
require('intro.js/introjs.css');
require('intro.js/themes/introjs-modern.css');
require('jquery.terminal/css/jquery.terminal.css');

let AppInterfaceInteroperabilite = require('./Compoments/hermes_ui');

let TABLE_EXECUTION_AUTOMATE = null,
    TABLE_EXECUTION_AUTOMATE_FIRST_FETCH = false;

$(function () {

    $('#btn-start-service').click(AppInterfaceInteroperabilite.demarrer_interoperabilite);
    $('#btn-stop-service').click(AppInterfaceInteroperabilite.arreter_interoperabilite);
    $('#btn-nouveau-noeud').click(AppInterfaceInteroperabilite.assistant_creation_noeud_action);
    $('#btn-supprimer-noeud').click(AppInterfaceInteroperabilite.supprimer_noeud_action);
    $('#btn-modifier-noeud').click(AppInterfaceInteroperabilite.assistant_modification_noeud_action);
    $('#btn-tester-automate').click(AppInterfaceInteroperabilite.assistant_test_isolation_automate);
    $('#btn-remplacer-noeud').click(AppInterfaceInteroperabilite.assistant_remplacement_noeud_action);

    $('#btn-import-data').click(
        () => {
            Swal.fire({
                title: 'Import des Automates',
                showCancelButton: false,
                confirmButtonText: 'Fermer',
                html: `<form id="swal-dropzone" action="/admin/export/automates" style="border-style: dashed; height: 90px;">
            <div class="fallback">
                <input name="file" type="file" />
            </div>
        </form>`,
                onOpen: () => {
                    new Dropzone(
                        "#swal-dropzone",
                        {
                            url: "/admin/export/automates",
                            uploadMultiple: false,
                            dictDefaultMessage: 'Déposez un fichier JSON',
                            complete: function (a) {

                                let import_resp = JSON.parse(a.xhr.response === '' ? '{}' : a.xhr.response);

                                Swal.fire(
                                    {
                                        title: '<strong>Import des <u>Automates</u></strong>',
                                        type: import_resp.message === undefined ? 'info' : 'error',
                                        text: import_resp.message === undefined ? 'Vos automates ont été importés avec succès.' : import_resp.message,
                                        showCloseButton: true,
                                        showCancelButton: false
                                    }
                                ).then(
                                    () => {
                                        location.reload(true);
                                    }
                                );

                                this.removeAllFiles(true);
                            }
                        },
                    );
                }

            });
        }
    );

    let mise_a_jour_journal = () => {

        AppInterfaceInteroperabilite.lecture_journal_evenement();

        setTimeout(
            mise_a_jour_journal,
            500
        );
    };

    let mise_a_jour_etat_service = () => {
        AppInterfaceInteroperabilite.etat_service_interoperabilite()
            .then(
                () => {
                    setTimeout(
                        mise_a_jour_etat_service,
                        1000
                    );
                }).catch(
            (jqXHR) => {
                setTimeout(
                    mise_a_jour_etat_service,
                    5000
                );
            }
        );


    };

    let mise_a_jour_stats_globales = () => {

        AppInterfaceInteroperabilite.etat_statistique_globale();

        if (TABLE_EXECUTION_AUTOMATE !== null && TABLE_EXECUTION_AUTOMATE_FIRST_FETCH === true) {
            TABLE_EXECUTION_AUTOMATE.ajax.reload(
                (data) => {
                    data = null;
                },
                false
            );
        }

        setTimeout(
            mise_a_jour_stats_globales,
            5000
        );
    };

    setTimeout(
        mise_a_jour_journal,
        1000
    );

    setTimeout(
        mise_a_jour_etat_service,
        100
    );

    setTimeout(
        mise_a_jour_stats_globales,
        1000
    );

    AppInterfaceInteroperabilite.recuperation_descriptifs_actions();

    AppInterfaceInteroperabilite.recuperer_liste_automate();

    AppInterfaceInteroperabilite.TERM = $('#terminal')
        .terminal('',
            {
                greetings: 'Hermes Copyright © 2019 GIE Sesam-Vitale. All rights reserved.\n\n',
                historySize: 40,
                outputLimit: 80,
                height: 250,
            }
        ).freeze(true);

    TABLE_EXECUTION_AUTOMATE = $('#table-executions').DataTable(
        {
            "ajax": {
                "url": "/admin/rest/automate-execution",
                "dataSrc": function (json) {
                    for (let i = 0; i < json.data.length; i++) {
                        json.data[i]['actions'] = '<a data-automate-execution-id="' + json.data[i].id.toString() + '" class="btn btn-warning btn-flat btn-automate-execution-debug"><i class="fa fa-eye"></i></a>';
                    }
                    TABLE_EXECUTION_AUTOMATE_FIRST_FETCH = true;
                    return json.data;
                }
            },
            "columns": [
                {"data": "id"},
                {
                    "data": "automate.designation",
                    render: function (data, type, row) {
                        return data.replace(/(.{90})..+/, "$1&hellip;");
                    }
                },
                {
                    "data": "date_creation",
                    render: function (data, type, row) {
                        return moment(data).format('LLLL');
                    }
                },
                {
                    "data": "sujet",
                    render: function (data, type, row) {
                        return data.replace(/(.{90})..+/, "$1&hellip;");
                    }
                },
                {
                    "data": "validation_automate",
                    render: function (data, type, row) {
                        return data === true ? '<span class="badge bg-green">Réussite</span>' : '<span class="badge bg-red">Echec</span>';
                    }
                },
                {
                    "data": "actions",
                },
            ],
            "order": [[0, "desc"]],
            "language": {
                "url": "//cdn.datatables.net/plug-ins/1.10.20/i18n/French.json"
            }
        }
    );

    TABLE_EXECUTION_AUTOMATE.on('draw', function () {
        $('.btn-automate-execution-debug').each(function () {
            let my_input = $(this),
                automate_execution_id = my_input.attr('data-automate-execution-id');

            my_input.click(function () {
                AppInterfaceInteroperabilite.lecture_execution_automate(
                    automate_execution_id
                ).then(
                    (data) => {
                        let progress_steps = ['0', '1'];

                        let queue = [
                            {
                                title: 'Rapport de lancement',
                                html: `<h4>${data.validation_automate === true ? '✅' : '❌'} ${data.automate.designation}</h4>
<br><br>Cet assistant va expliciter le lancement de votre automate.
<br>Sujet : <b>${data.sujet}</b>
<br>Date de lancement : <b>${data.date_creation}</b>
<br>Date de finalisation : <b>${data.date_finalisation}</b><br><br>
<b><u>Logs :</u></b><br>
<pre><code>${data.logs}</code></pre>`,
                                confirmButtonText: 'Critères &rarr;'
                            },
                            {
                                title: 'Critères',
                                html: `<h4>${data.validation_detecteur === true ? '✅' : '❌'} ${data.automate.detecteur.designation}</h4><br><br>
<pre><code>${data.explications_detecteur}</code></pre>`,
                                confirmButtonText: 'Actions &rarr;'
                            },
                        ];

                        for (let action_exec of data.actions_noeuds_executions) {
                            let args_debug = '';

                            if (action_exec.args_payload !== undefined && action_exec.args_payload !== '') {
                                let action_args = JSON.parse(action_exec.args_payload);

                                for (let k in action_args) {
                                    if (action_args.hasOwnProperty(k)) {
                                        args_debug += `<br>${k} : <b>${action_args[k]}</b>`
                                    }
                                }

                            }

                            queue.push(
                                {
                                    title: `${action_exec.validation_action_noeud === true ? '✅' : '❌'} Action #${action_exec.id}`,
                                    html: `<h4>${action_exec.action_noeud.designation}</h4>
<br><br>Type de l'action : <b>${action_exec.action_noeud.type}</b>
<br>Réponse de l'action : <b>${action_exec.payload}</b>
<br><h4>Argument(s)</h4>
${args_debug === '' ? '<b>Aucun argument disponible en mode debug !</b>' : args_debug}`,
                                    confirmButtonText: 'Suivant &rarr;'
                                }
                            );
                            progress_steps.push((progress_steps.length + 1).toString());
                        }

                        Swal.mixin({
                            showCancelButton: false,
                            progressSteps: progress_steps
                        }).queue(queue);

                    }
                ).catch(
                    (jqXHR) => {
                        console.warn(jqXHR);
                    }
                )
            });
        });
    });

    $('#activation-automate-production').on('change', function () {
        let automate_id = $('#selection-automate').val(),
            balise_checkbox = this;

        if (automate_id === '') {
            Swal.fire(
                'Mise en production',
                'Nous vous priions de bien vouloir choisir un automate avant de demander un changement d\'état',
                'warning'
            );
            return;
        }

        AppInterfaceInteroperabilite.changer_etat_production_automate(
            automate_id,
            balise_checkbox.checked
        ).catch(
            () => {
                Swal.fire(
                    'Mise en production',
                    'Impossible de changer l\'état de production automate',
                    'error'
                );
            }
        );

    });

    $('#selection-automate').on('change', function () {

        if (this.value === '') {
            return;
        }

        AppInterfaceInteroperabilite.automate_vers_ui(
            this.value
        ).catch(
            () => {
                Swal.fire(
                    'Impossible de lire automate',
                    'Une erreur est survenue lors de la lecture automate',
                    'error'
                );
            }
        ).then(
            () => {

                $('#btn-nouveau-noeud').removeClass('disabled');
                $('#btn-modifier-noeud').removeClass('disabled');
                $('#btn-supprimer-noeud').removeClass('disabled');
                $('#btn-tester-automate').removeClass('disabled');
                $('#btn-remplacer-noeud').removeClass('disabled');

                AppInterfaceInteroperabilite.recuperation_saisie_assistee();

            }
        )
    });

});