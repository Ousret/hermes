const $ = require('jquery');
const JSONEditor = require('jsoneditor');

const ClipboardJS = require('clipboard');
const Swal = require('sweetalert2');

const Awesomplete = require('awesomplete');

require('jstree');
require('../../styles/jstree/proton/style.css');
require('jsoneditor/dist/jsoneditor.css');

class AppInterfaceInteroperabilite {

    static recuperer_liste_automate() {
        $.get(
            `/admin/rest/automate`
        ).done(
            (automates) => {

                let select_automate = $('#selection-automate');

                for (let automate of automates) {
                    select_automate.append($('<option/>', {
                        value: automate.id,
                        text: automate.designation
                    }));
                }

            }
        ).fail(
            (jqXHR) => {
                console.log(jqXHR);
            }
        )
    }

    static creation_action_noeud(automate_id, choix_type, information_parent, formulaire) {
        return new Promise(
            function (resolve, reject) {

                $.ajax({
                    type: "POST",
                    data: JSON.stringify({
                        'type': choix_type,
                        'parent': information_parent,
                        'formulaire': formulaire
                    }),
                    url: `/admin/rest/automate/${automate_id}/action_noeud`,
                    contentType: "application/json"
                }).done(
                    resolve
                ).fail(
                    reject
                );

            }
        );
    }

    static remplacer_action_noeud(automate_id, choix_type, information_cible_remplace, formulaire) {

        return new Promise(
            function (resolve, reject) {

                $.ajax({
                    type: "POST",
                    data: JSON.stringify({
                        'type': choix_type,
                        'remplacement': information_cible_remplace,
                        'formulaire': formulaire
                    }),
                    url: `/admin/rest/automate/${automate_id}/action_noeud`,
                    contentType: "application/json"
                }).done(
                    resolve
                ).fail(
                    reject
                );

            }
        );

    }

    /**
     *
     * @param automate_execution_id
     * @returns {Promise<unknown>}
     */
    static lecture_execution_automate(automate_execution_id)
    {
        return new Promise(
            function (resolve, reject) {

                $.ajax({
                    type: "GET",
                    url: `/admin/rest/automate-execution/${automate_execution_id}`,
                    contentType: "application/json"
                }).done(
                    resolve
                ).fail(
                    reject
                );

            }
        );
    }

    static mise_a_jour_action_noeud(automate_id, action_noeud_id, type_action, formulaire)
    {
        return new Promise(
            function (resolve, reject) {

                $.ajax({
                    type: "PUT",
                    data: JSON.stringify({
                        'type': type_action,
                        'formulaire': formulaire
                    }),
                    url: `/admin/rest/automate/${automate_id}/action_noeud/${action_noeud_id}`,
                    contentType: "application/json"
                }).done(
                    resolve
                ).fail(
                    reject
                );

            }
        );
    }

    static assistant_suppression_noeud_action() {
        return new Promise(
            function (resolve, reject) {

                if (AppInterfaceInteroperabilite.AUTOMATE_EDITEUR.actions.length === 0) {
                    Swal.fire(
                        'Supprimer Action',
                        'Aucune action n\'est supprimable',
                        'error'
                    );

                    reject();
                    return;
                }

                let inputOptions = {};

                for (let action of AppInterfaceInteroperabilite.AUTOMATE_EDITEUR.actions) {
                    inputOptions[action.id.toString()] = action.designation;
                }

                Swal.fire({
                    title: 'Supprimer une action',
                    input: 'select',
                    inputOptions: inputOptions,
                    inputPlaceholder: 'Votre action à retirer',
                    showCancelButton: true,
                }).then(
                    resolve
                );

            }
        )
    }

    static supprimer_noeud_action() {
        AppInterfaceInteroperabilite.assistant_suppression_noeud_action()
            .then(
                (mon_action_id) => {
                    if (!mon_action_id.value) {
                        return;
                    }
                    AppInterfaceInteroperabilite.supprimer_action_noeud(
                        AppInterfaceInteroperabilite.AUTOMATE_EDITEUR.id,
                        mon_action_id.value
                    ).then(
                        () => {
                            Swal.fire(
                                'Action',
                                'Votre action a été supprimée avec succès',
                                'success'
                            ).then(
                                () => {
                                    AppInterfaceInteroperabilite.automate_vers_ui(
                                        AppInterfaceInteroperabilite.AUTOMATE_EDITEUR.id
                                    );
                                }
                            )
                        }
                    ).catch(
                        (jqXHR) => {
                            Swal.fire(
                                'Action',
                                'Votre action n\'a pas pu être supprimée ! ',
                                'error'
                            );
                        }
                    );
                }
            )
    }

    static supprimer_action_noeud(automate_id, action_noeud_id) {
        return new Promise(
            function (resolve, reject) {

                $.ajax(
                    {
                        url: `/admin/rest/automate/${automate_id}/action_noeud/${action_noeud_id}`,
                        method: 'DELETE'
                    }
                ).done(
                    resolve
                ).fail(
                    reject
                );

            }
        )
    }

    static changer_etat_production_automate(automate_id, nouvel_etat) {

        return new Promise(
            function (resolve, reject) {

                $.ajax({
                    type: "POST",
                    data: {
                        'list_form_pk': automate_id,
                        'production': nouvel_etat
                    },
                    url: `/admin/automate/ajax/update/`,
                }).done(
                    resolve
                ).fail(
                    reject
                );

            }
        )
    }

    static creation_test_isolation_automate(automate_id) {
        return new Promise(
            function (resolve, reject) {

                $.ajax({
                    type: "POST",
                    data: {
                        'automate_id': automate_id
                    },
                    url: `/admin/service/test`,
                }).done(
                    resolve
                ).fail(
                    reject
                );

            }
        );
    }

    static assistant_test_isolation_automate() {
        Swal.fire({
            confirmButtonText: 'Je test &rarr;',
            showCancelButton: true,
            text: 'Voulez-vous créer un lancement d\'automate isolé ? Soyez sûr que le message à tester soit dans votre dossier IMAP configuré.',
        }).then(
            (r) => {
                AppInterfaceInteroperabilite.creation_test_isolation_automate(
                    AppInterfaceInteroperabilite.AUTOMATE_EDITEUR.id
                ).then(
                    () => {
                        Swal.fire(
                            'Parfait !',
                            'Votre automate "'+AppInterfaceInteroperabilite.AUTOMATE_EDITEUR.designation+'" est dans la file d\'attente pour être testé.',
                            'success'
                        );
                    }
                ).catch((jqXHR) => {
                    Swal.fire(
                        'Attention !',
                        jqXHR.responseJSON ? jqXHR.responseJSON.message : 'Une erreur inatendue est survenue',
                        'warning'
                    );
                });
            }
        );
    }

    static assistant_remplacement_noeud_action() {
        let inputOptions = {},
            div_visu_actions = $("#visu-automate"),
            noeud_action_selection = div_visu_actions.jstree("get_selected", true).length === 1 ? div_visu_actions.jstree("get_selected", true)[0]['li_attr']['data-action-noeud-id'] : null;

        if (noeud_action_selection === null)
        {
            Swal.fire(
                {
                    title: 'Aucune action selectionnée',
                    text: "Vous devez choisir une action pour pouvoir effectuer un remplacement",
                    type: "warning"
                }
            );

            return;
        }

        AppInterfaceInteroperabilite.choisir_action_noeud_type().then(
            (choix) => {
                if (!choix.value) {
                    return;
                }


                for (let i = 0; i < AppInterfaceInteroperabilite.ACTIONS_DESCRIPTIFS.length; i++) {
                        let descriptif = AppInterfaceInteroperabilite.ACTIONS_DESCRIPTIFS[i];

                        if (descriptif.type === choix.value) {
                            AppInterfaceInteroperabilite.generer_assistant_swal_queue(
                                AppInterfaceInteroperabilite.ACTIONS_DESCRIPTIFS[i]
                            ).then(
                                (result) => {

                                    let formulaireOptions = {},
                                        i = 0;

                                    for (let nom_champ_formulaire in descriptif.formulaire) {
                                        if (descriptif.formulaire.hasOwnProperty(nom_champ_formulaire)) {
                                            formulaireOptions[nom_champ_formulaire] = result.value[i];
                                            i += 1;
                                        }
                                    }

                                    AppInterfaceInteroperabilite.remplacer_action_noeud(
                                        AppInterfaceInteroperabilite.AUTOMATE_EDITEUR.id,
                                        choix.value,
                                        noeud_action_selection,
                                        formulaireOptions
                                    ).then(
                                        () => {
                                            Swal.fire(
                                                'Parfait!',
                                                'Votre nouvelle action a été créée en remplacement',
                                                'success'
                                            ).then(
                                                () => {
                                                    AppInterfaceInteroperabilite.automate_vers_ui(
                                                        AppInterfaceInteroperabilite.AUTOMATE_EDITEUR.id
                                                    );
                                                }
                                            )
                                        }
                                    ).catch(
                                        (jqXHR) => {
                                            Swal.fire(
                                                'Remplacement action',
                                                jqXHR.responseJSON ? jqXHR.responseJSON.message : 'Une erreur inatendue est survenue durant le processus de remplacement',
                                                'error'
                                            );
                                        }
                                    )
                                }
                            );
                            break;
                        }
                    }

            }
        )
    }

    static assistant_modification_noeud_action() {
        let inputOptions = {},
            div_visu_actions = $("#visu-automate"),
            modification_fn = (choix_action_modification) => {

                $.get(
                    '/admin/rest/automate/'+AppInterfaceInteroperabilite.AUTOMATE_EDITEUR.id+'/action_noeud/'+choix_action_modification.value
                ).done(
                    (action_noeud) => {

                        for (let i = 0; i < AppInterfaceInteroperabilite.ACTIONS_DESCRIPTIFS.length; i++) {
                            let descriptif = AppInterfaceInteroperabilite.ACTIONS_DESCRIPTIFS[i];

                            if (descriptif.type === action_noeud.mapped_class_child) {

                                AppInterfaceInteroperabilite.generer_assistant_swal_queue(
                                    AppInterfaceInteroperabilite.ACTIONS_DESCRIPTIFS[i],
                                    action_noeud
                                ).then(
                                    (saisies_formulaire) => {

                                        console.log(saisies_formulaire);

                                        if (!saisies_formulaire.value) {
                                            return;
                                        }

                                        let formulaireOptions = {},
                                            i = 0;

                                        for (let nom_champ_formulaire in descriptif.formulaire) {
                                            if (descriptif.formulaire.hasOwnProperty(nom_champ_formulaire)) {
                                                formulaireOptions[nom_champ_formulaire] = saisies_formulaire.value[i];
                                                i += 1;
                                            }
                                        }

                                        AppInterfaceInteroperabilite.mise_a_jour_action_noeud(
                                            AppInterfaceInteroperabilite.AUTOMATE_EDITEUR.id,
                                            action_noeud.id,
                                            action_noeud.mapped_class_child,
                                            formulaireOptions
                                        ).then(
                                            () => {

                                                Swal.fire(
                                                    'Mise à jour',
                                                    'Votre action a été mise à jour avec succès',
                                                    'success'
                                                ).then(
                                                    () => {
                                                        AppInterfaceInteroperabilite.automate_vers_ui(
                                                            AppInterfaceInteroperabilite.AUTOMATE_EDITEUR.id
                                                        );
                                                    }
                                                );

                                            }
                                        ).catch(
                                            (jqXHR) => {

                                                Swal.fire(
                                                    'Mise à jour',
                                                    jqXHR.responseJSON ? jqXHR.responseJSON.message : 'Une erreur inatendue est survenue durant la mise à jour',
                                                    'error'
                                                );

                                            }
                                        )

                                    }
                                )

                            }

                        }

                    }
                ).fail(
                    (jqXHR) => {

                    }
                );



            },
            noeud_action_selection = div_visu_actions.jstree("get_selected", true).length === 1 ? div_visu_actions.jstree("get_selected", true)[0]['li_attr']['data-action-noeud-id'] : null;

        for (let action of AppInterfaceInteroperabilite.AUTOMATE_EDITEUR.actions) {

            let type_noeud_class = action.mapped_class_child.replace('<', '').replace('>', '').replace("'", '').replace('hermes_ui.models.automate.', '').replace('class', '');

            if (action.id) {
                inputOptions[action.id.toString()] = '<' + type_noeud_class + '> ' + action.designation;
            }

        }

        if (noeud_action_selection !== null)
        {
            modification_fn({value: noeud_action_selection});
        }
        else
        {
            // Selectionner l'action père et le chemin à prendre
            Swal.fire({
                confirmButtonText: 'Je modifie &rarr;',
                showCancelButton: true,
                text: 'Veuillez choisir votre action a modifier',
                input: 'select',
                inputOptions: inputOptions
            }).then(
                modification_fn
            );
        }


    }

    static assistant_creation_noeud_action() {
        AppInterfaceInteroperabilite.choisir_action_noeud_type().then(
            (choix) => {

                if (!choix.value) {
                    return;
                }

                if (AppInterfaceInteroperabilite.AUTOMATE_EDITEUR.action_racine !== null) {

                    let inputOptions = {};

                    for (let action of AppInterfaceInteroperabilite.AUTOMATE_EDITEUR.actions) {

                        let type_noeud_class = action.mapped_class_child.replace('<', '').replace('>', '').replace("'", '').replace('hermes_ui.models.automate.', '').replace('class', '');

                        if (action.id) {
                            inputOptions[action.id.toString()] = '<' + type_noeud_class + '> ' + action.designation;
                        }

                    }

                    // Selectionner l'action père et le chemin à prendre
                    Swal.mixin({
                        title: 'Association de votre nouvelle action',
                        confirmButtonText: 'Suivant &rarr;',
                        showCancelButton: true,
                        progressSteps: ['1', '2']
                    }).queue([
                        {
                            text: 'Veuillez choisir le père de votre nouvelle action',
                            input: 'select',
                            inputOptions: inputOptions
                        },
                        {
                            text: 'Dites nous dans quelle cas lancer cette action à partir du père',
                            input: 'radio',
                            inputOptions: {
                                'ECHEC': 'En cas d\'echec du parent',
                                'REUSSITE': 'En cas de réussite du parent',
                            }
                        }
                    ]).then((choix_associations) => {

                        if (!choix_associations.value) {
                            return;
                        }

                        for (let action of AppInterfaceInteroperabilite.AUTOMATE_EDITEUR.actions) {
                            if (action.id === parseInt(choix_associations.value[0]))
                            {
                                if (choix_associations.value[1] === 'REUSSITE' && action.action_reussite)
                                {
                                    Swal.fire(
                                        'Association impossible',
                                        "L'action parente dispose déjà d'un cas de réussite, veuillez le supprimer avant !",
                                        'warning'
                                    );

                                    return;
                                }

                                if (choix_associations.value[1] === 'ECHEC' && action.action_echec)
                                {
                                    Swal.fire(
                                        'Association impossible',
                                        "L'action parente dispose déjà d'un cas d'échec, veuillez le supprimer avant !",
                                        'warning'
                                    );

                                    return;
                                }

                                break;
                            }
                        }

                        for (let i = 0; i < AppInterfaceInteroperabilite.ACTIONS_DESCRIPTIFS.length; i++) {
                            let descriptif = AppInterfaceInteroperabilite.ACTIONS_DESCRIPTIFS[i];

                            if (descriptif.type === choix.value) {
                                AppInterfaceInteroperabilite.generer_assistant_swal_queue(
                                    AppInterfaceInteroperabilite.ACTIONS_DESCRIPTIFS[i]
                                ).then(
                                    (result) => {

                                        if (!result.value) {
                                            return;
                                        }

                                        let formulaireOptions = {},
                                            i = 0;

                                        for (let nom_champ_formulaire in descriptif.formulaire) {
                                            if (descriptif.formulaire.hasOwnProperty(nom_champ_formulaire)) {
                                                formulaireOptions[nom_champ_formulaire] = result.value[i];
                                                i += 1;
                                            }
                                        }

                                        AppInterfaceInteroperabilite.creation_action_noeud(
                                            AppInterfaceInteroperabilite.AUTOMATE_EDITEUR.id,
                                            choix.value,
                                            choix_associations.value,
                                            formulaireOptions
                                        ).then(
                                            () => {
                                                Swal.fire(
                                                    'Parfait!',
                                                    'Votre nouvelle action a été créée',
                                                    'success'
                                                ).then(
                                                    () => {
                                                        AppInterfaceInteroperabilite.automate_vers_ui(
                                                            AppInterfaceInteroperabilite.AUTOMATE_EDITEUR.id
                                                        );
                                                    }
                                                )
                                            }
                                        ).catch(
                                            (jqXHR) => {
                                                Swal.fire(
                                                    'Création action',
                                                    jqXHR.responseJSON ? jqXHR.responseJSON.message : 'Une erreur inatendue est survenue durant le processus de création',
                                                    'error'
                                                );
                                            }
                                        )
                                    }
                                );
                                break;
                            }
                        }

                    });

                } else {
                    for (let i = 0; i < AppInterfaceInteroperabilite.ACTIONS_DESCRIPTIFS.length; i++) {
                        let descriptif = AppInterfaceInteroperabilite.ACTIONS_DESCRIPTIFS[i];

                        if (descriptif.type === choix.value) {
                            AppInterfaceInteroperabilite.generer_assistant_swal_queue(
                                AppInterfaceInteroperabilite.ACTIONS_DESCRIPTIFS[i]
                            ).then(
                                (result) => {

                                    let formulaireOptions = {},
                                        i = 0;

                                    for (let nom_champ_formulaire in descriptif.formulaire) {
                                        if (descriptif.formulaire.hasOwnProperty(nom_champ_formulaire)) {
                                            formulaireOptions[nom_champ_formulaire] = result.value[i];
                                            i += 1;
                                        }
                                    }

                                    AppInterfaceInteroperabilite.creation_action_noeud(
                                        AppInterfaceInteroperabilite.AUTOMATE_EDITEUR.id,
                                        choix.value,
                                        null,
                                        formulaireOptions
                                    ).then(
                                        () => {
                                            Swal.fire(
                                                'Parfait!',
                                                'Votre nouvelle action a été créée',
                                                'success'
                                            ).then(
                                                () => {
                                                    AppInterfaceInteroperabilite.automate_vers_ui(
                                                        AppInterfaceInteroperabilite.AUTOMATE_EDITEUR.id
                                                    );
                                                }
                                            )
                                        }
                                    ).catch(
                                        (jqXHR) => {
                                            Swal.fire(
                                                'Création action',
                                                jqXHR.responseJSON ? jqXHR.responseJSON.message : 'Une erreur inatendue est survenue durant le processus de création',
                                                'error'
                                            );
                                        }
                                    )
                                }
                            );
                            break;
                        }
                    }
                }


            }
        );
    }

    static generer_assistant_swal_queue(descriptif, action_noeud) {
        return new Promise(function (resolve) {

            let mixin_kwargs = {
                input: 'text',
                title: action_noeud === undefined ? 'Assistant création' : 'Assistant mise à jour',
                confirmButtonText: 'Suivant &rarr;',
                showCancelButton: true,
                progressSteps: []
            };

            let queue_args = [];

            for (let nom_champ_formulaire in descriptif.formulaire) {
                if (descriptif.formulaire.hasOwnProperty(nom_champ_formulaire)) {

                    mixin_kwargs.progressSteps.push((mixin_kwargs.progressSteps.length + 1).toString());

                    if (descriptif.formulaire[nom_champ_formulaire].format === 'JSON') {
                        queue_args.push(
                            {
                                input: '',
                                html:
                                    '<b>' + descriptif.formulaire[nom_champ_formulaire].help + '</b>' +
                                    '<div id="swal-json-editor" style="width: 100%; height: 400px;"></div>',
                                preConfirm: () => {
                                    return JSON.stringify(AppInterfaceInteroperabilite.EDITEUR_JSON.get(), null, 4)
                                },
                                onOpen: (a) => {
                                    let container = document.getElementById("swal-json-editor");
                                    AppInterfaceInteroperabilite.EDITEUR_JSON = new JSONEditor(
                                        container,
                                        {
                                            autocomplete: {
                                                getOptions: function () {
                                                    return AppInterfaceInteroperabilite.SUGGESTIONS_SAISIE;
                                                }
                                            }
                                        }
                                    );

                                    if (action_noeud !== undefined && action_noeud[nom_champ_formulaire]) {
                                        AppInterfaceInteroperabilite.EDITEUR_JSON.set(
                                            JSON.parse(action_noeud[nom_champ_formulaire])
                                        );
                                    }

                                }
                            }
                        );
                    } else if (descriptif.formulaire[nom_champ_formulaire].format === 'AUTOMATE') {

                        let inputOptions = {};

                        for (let opt of $('#selection-automate option'))
                        {
                            if (opt.value !== '' && parseInt(opt.value) !== AppInterfaceInteroperabilite.AUTOMATE_EDITEUR.id)
                            {
                                inputOptions[opt.value] = opt.innerText;
                            }
                        }

                        queue_args.push(
                            {
                                input: 'select',
                                html: '<b>' + nom_champ_formulaire + '</b>' + (descriptif.formulaire[nom_champ_formulaire].required === true ? '<sup class="color: red;">*</sup>' : '') + '<br>' + descriptif.formulaire[nom_champ_formulaire].help,
                                inputOptions: inputOptions,
                                inputValue: action_noeud !== undefined ? (action_noeud[nom_champ_formulaire] ? action_noeud[nom_champ_formulaire] : '') : '',
                            }
                        );

                    } else if (descriptif.formulaire[nom_champ_formulaire].format === 'SELECT') {
                        let inputOptions = {};

                        for (let choix of descriptif.formulaire[nom_champ_formulaire].choix) {
                            inputOptions[choix] = choix;
                        }

                        queue_args.push(
                            {
                                input: descriptif.formulaire[nom_champ_formulaire].format.toLowerCase(),
                                html: '<b>' + nom_champ_formulaire + '</b>' + (descriptif.formulaire[nom_champ_formulaire].required === true ? '<sup class="color: red;">*</sup>' : '') + '<br>' + descriptif.formulaire[nom_champ_formulaire].help,
                                inputOptions: inputOptions,
                                inputValue: action_noeud !== undefined ? (action_noeud[nom_champ_formulaire] ? action_noeud[nom_champ_formulaire] : '') : '',
                            }
                        );
                    } else {
                        queue_args.push(
                            {
                                input: descriptif.formulaire[nom_champ_formulaire].format.toLowerCase(),
                                html: '<b>' + nom_champ_formulaire + '</b>' + (descriptif.formulaire[nom_champ_formulaire].required === true ? '<sup class="color: red;">*</sup>' : '') + '<br>' + descriptif.formulaire[nom_champ_formulaire].help,
                                inputValidator: (value) => {
                                    return new Promise((resolve) => {

                                        if (['TEXTAREA', 'SELECT', 'CHECKBOX', 'RADIO'].indexOf(descriptif.formulaire[nom_champ_formulaire].format) !== -1)
                                        {
                                            if (descriptif.formulaire[nom_champ_formulaire].format === 'CHECKBOX')
                                            {
                                                value = $('#swal2-'+descriptif.formulaire[nom_champ_formulaire].format.toLowerCase()).val();
                                            }
                                            else
                                            {
                                                value = $('.swal2-'+descriptif.formulaire[nom_champ_formulaire].format.toLowerCase()).val();
                                            }
                                        }
                                        else
                                        {
                                            value = $('.swal2-input').val();
                                        }

                                        if (descriptif.formulaire[nom_champ_formulaire].required === true && value.length > 0) {
                                            resolve()
                                        } else if (descriptif.formulaire[nom_champ_formulaire].required === true && value.length === 0) {
                                            resolve('La saisie est obligatoire pour ce champs !')
                                        }

                                        resolve();
                                    });
                                },
                                preConfirm: () => {

                                    if (['TEXTAREA', 'SELECT', 'CHECKBOX', 'RADIO'].indexOf(descriptif.formulaire[nom_champ_formulaire].format) !== -1)
                                    {
                                        if (descriptif.formulaire[nom_champ_formulaire].format === 'CHECKBOX')
                                        {
                                            return $('#swal2-'+descriptif.formulaire[nom_champ_formulaire].format.toLowerCase()).checked;
                                        }

                                        return $('.swal2-'+descriptif.formulaire[nom_champ_formulaire].format.toLowerCase()).val();
                                    }

                                    return $('.swal2-input').val();
                                },
                                inputValue: action_noeud !== undefined ? (action_noeud[nom_champ_formulaire] ? action_noeud[nom_champ_formulaire]: '') : '',
                            }
                        );
                    }

                }
            }

            Swal.mixin(mixin_kwargs).queue(queue_args).then(resolve);

        });

    }

    static ui_construire_liste(action_noeud, icone) {
        if (action_noeud === null) {
            return '';
        }

        let my_liste = '<ul>',
            type_noeud_condition = icone === undefined ? 'Racine' : (icone === 'fa fa-check-square' ? 'SI Réussite' : 'SI Echec'),
            type_noeud_class = action_noeud.mapped_class_child.replace('<', '').replace('>', '').replace("'", '').replace('hermes_ui.models.automate.', '').replace('class', '');


        my_liste += '<li data-action-noeud-id="'+action_noeud.id+'" data-jstree=\'{"opened":true, "icon":"' + (icone === undefined ? 'fa fa-tree' : icone) + '"}\'><b>' + type_noeud_condition + '</b>' + type_noeud_class + '<small>' + action_noeud.designation + '</small>';

        if (action_noeud.action_reussite) {
            my_liste += AppInterfaceInteroperabilite.ui_construire_liste(
                action_noeud.action_reussite,
                'fa fa-check-square'
            );
        }

        if (action_noeud.action_echec) {
            my_liste += AppInterfaceInteroperabilite.ui_construire_liste(
                action_noeud.action_echec,
                'fa fa-bolt'
            );
        }

        my_liste += '</ul>';

        return my_liste;
    }

    static recuperation_liste_detecteur() {
        return new Promise(
            function (resolve, reject) {
                $.get(
                    '/admin/rest/detecteur'
                ).done(
                    resolve
                ).fail(
                    reject
                );
            }
        );
    }

    static selection_detecteur() {
        return new Promise(
            function (resolve, reject) {

                AppInterfaceInteroperabilite.recuperation_liste_detecteur()
                    .then(
                        (detecteurs) => {

                            if (detecteurs.length === 0)
                            {
                                Swal.fire(
                                    'Liste de détecteur',
                                    'Aucun détecteur n\'est disponible à la selection',
                                    'warning'
                                );

                                reject();

                                return;
                            }
                            let inputOptions = {};

                            for (let detecteur of detecteurs) {
                                inputOptions[detecteur.id.toString()] = detecteur.designation;
                            }

                            Swal.fire({
                                title: 'Nous vous priions de bien vouloir choisir un détecteur',
                                input: 'select',
                                inputOptions: inputOptions,
                                inputPlaceholder: 'Selectionnez un détecteur',
                                showCancelButton: true,
                            }).then(
                                resolve
                            );
                        }
                    )

            }
        )
    }

    static assistant_simulation_detecteur() {
        AppInterfaceInteroperabilite.selection_detecteur().then(
            (selection) => {

                if (!selection.value)
                {
                    return;
                }

                Swal.fire(
                    {
                        title: 'Simulation analyse de texte',
                        html:
                            '<b>Communiquez-nous le sujet et corps de votre source, eg. mail</b>' +
                            '<input id="swal-input1" class="swal2-input" placeholder="Sujet de votre source">' +
                            '<textarea id="swal-input2" class="swal2-input" rows="10" placeholder="Corps de votre source, CTRL+C / +V" style="height: auto">',
                        confirmButtonText: 'Analyser &rarr;',
                        showCancelButton: true,
                        showLoaderOnConfirm: true,
                        preConfirm: () => {
                            return new Promise(
                                function (resolve, reject) {

                                    $.post(
                                        `/admin/rest/simulation/detecteur`,
                                        {
                                            sujet: document.getElementById('swal-input1').value,
                                            corps: document.getElementById('swal-input2').value,
                                            detecteur_id: selection.value
                                        }
                                    ).done(
                                        (response) => {
                                            resolve(response);
                                        }
                                    ).fail(
                                        (jqXHR) => {
                                            resolve(JSON.parse(
                                                jqXHR.responseText
                                            ));
                                        }
                                    );

                                }
                            )
                        },
                        allowOutsideClick: () => !Swal.isLoading(),
                    }
                ).then((result) => {
                    if (result.value) {
                        Swal.fire({
                            title: 'Simulation Détecteur',
                            html:
                                'Votre analyse: <pre><code>' +
                                JSON.stringify(result.value.interets, null, 4) +
                                '</code></pre>'+'<br><pre><code>' +
                                result.value.explications +
                                '</code>' +
                                '</pre>',
                            confirmButtonText: 'Parfait!'
                        });
                    }
                });

            }
        )
    }

    static automate_vers_ui(automate_id) {
        return new Promise(
            function (resolve, reject) {

                $.get(
                    '/admin/rest/automate/' + automate_id
                ).done(
                    (automate) => {

                        AppInterfaceInteroperabilite.AUTOMATE_EDITEUR = automate;

                        $('#activation-automate-production').prop("checked", automate.production);

                        let div_visu_automate = $('#visu-automate');
                        $('#visionneuse-automate-titre').html('Editeur <b>d\'Actions</b> : "' + automate.designation + '"');

                        if (automate.action_racine === null) {
                            div_visu_automate.html('<h3 style="text-align: center">Aucune action n\'est encore configurée, pour commencer ajoutez-en une</h3>');
                            resolve();
                        } else {

                            div_visu_automate.jstree("destroy");

                            div_visu_automate.html(
                                AppInterfaceInteroperabilite.ui_construire_liste(
                                    automate.action_racine
                                )
                            );

                            div_visu_automate.jstree({
                                "core": {
                                    "themes": {
                                        'name': 'proton',
                                        'responsive': true,
                                        "variant": "large",
                                        "dots": true
                                    }
                                },
                                "checkbox": {
                                    "keep_selected_style": false
                                },

                            });

                            resolve();
                        }

                    }
                ).fail(
                    reject
                );

            }
        )
    }

    static choisir_action_noeud_type() {
        // TODO:
        // Etape 1) Choisir le type de noeud
        // Etape 2) Si racine existante, choisir le père et le cas (OK, KO)
        // Etape 3) Lancer l'assistant de création
        return new Promise(
            function (resolve) {

                let inputOptions = {};

                for (let descriptif of AppInterfaceInteroperabilite.ACTIONS_DESCRIPTIFS) {
                    inputOptions[descriptif.type] = descriptif.description;
                }

                Swal.fire({
                    title: 'Veuillez choisir un nouveau type action à créer',
                    input: 'select',
                    inputOptions: inputOptions,
                    showCancelButton: true,
                }).then(
                    resolve
                );

            }
        )
    }

    static recuperation_descriptifs_actions() {
        $.get(
            `/admin/rest/type/action_noeud`
        ).done(
            (descriptifs) => {

                AppInterfaceInteroperabilite.ACTIONS_DESCRIPTIFS = descriptifs;

            }
        ).fail(
            (jqXHR) => {
                console.log(jqXHR);
            }
        );
    }

    static lecture_journal_evenement() {
        $.get(
            `/admin/rest/logger`,
            {
                offset: AppInterfaceInteroperabilite.LAST_SEEK_LOGS
            }
        ).done(
            (data) => {

                // if (data.offset < AppInterfaceInteroperabilite.LAST_SEEK_LOGS)
                // {
                //     term.clear();
                // }

                AppInterfaceInteroperabilite.LAST_SEEK_LOGS = data.offset;

                for (let line of data.logs) {
                    AppInterfaceInteroperabilite.TERM.echo(
                        line.replace('\n', ''),
                        {
                            finalize: function(div) {

                                if (line.includes('| INFO'))
                                {
                                    div.css("color", "green");
                                }
                                else if(line.includes('| DEBUG'))
                                {
                                    div.css("color", "white");
                                }
                                else if(line.includes('| WARNING'))
                                {
                                    div.css("color", "yellow");
                                }
                                else if(line.includes('| ERROR'))
                                {
                                    div.css("color", "red");
                                }
                                else if(line.includes('| ERROR'))
                                {
                                    div.css("color", "red");
                                }
                                else if(line.includes('| CRITICAL') || line.includes('| FATAL'))
                                {
                                    div.css("color", "purple");
                                }
                            }
                        }
                    );


                }

            }
        ).fail(
            (jqXHR) => {
                console.log(jqXHR);
            }
        );
    }

    static etat_service_interoperabilite() {
        return new Promise(
            function (resolve, reject) {

                $.get(
                    `/admin/service`,
                    {}
                ).done(
                    (data, b) => {

                        let btn_start = $('#btn-start-service'),
                            btn_stop = $('#btn-stop-service');

                        if (b !== 'nocontent') {
                            if (!btn_start.hasClass('disabled')) {
                                btn_start.addClass('disabled');
                            }

                            if (btn_stop.hasClass('disabled')) {
                                btn_stop.removeClass('disabled');
                            }

                        } else {
                            if (btn_start.hasClass('disabled')) {
                                btn_start.removeClass('disabled');
                            }

                            if (!btn_stop.hasClass('disabled')) {
                                btn_stop.addClass('disabled');
                            }
                        }

                        resolve();

                    }
                ).fail(
                    reject
                );

            }
        )
    }

    static etat_statistique_globale() {
        $.get(
            `/admin/rest/statistique`
        ).done(
            (data) => {

                $('#nb-automate').html(data.automate);
                $('#nb-execution-reussite').html(data.reussites.toString()+'<sup>/'+data.executions.toString()+'</sup>');
                $('#nb-execution-echec').html(data.echecs.toString()+'<sup>/'+data.executions.toString()+'</sup>');
                $('#nb-critere').html(data.criteres);

            }
        ).fail(
            (jqXHR) => {
                console.log(jqXHR);
            }
        );
    }

    static demarrer_interoperabilite() {
        $.post(
            `/admin/service`,
            {}
        ).done(
            () => {
                Swal.fire(
                    'Service',
                    'Le service interoperabilité va démarrer',
                    'success'
                );
            }
        ).fail(
            (jqXHR) => {
                Swal.fire(
                    'Service',
                    'Le service interoperabilité ne peux pas démarrer',
                    'error'
                );
            }
        );
    }

    static arreter_interoperabilite() {
        $.ajax(
            {
                url: `/admin/service`,
                method: 'DELETE'
            }
        ).done(
            () => {
                Swal.fire(
                    'Service',
                    'Le service interoperabilité va s\'arrêter',
                    'success'
                );
            }
        ).fail(
            (jqXHR) => {
                Swal.fire(
                    'Service',
                    'Le service interoperabilité ne peux pas s\'arrêter',
                    'error'
                );
            }
        );
    }

    static assistant_simulation_extraction_interet() {

        Swal.fire(
            {
                title: 'Simulation analyse de texte',
                html:
                    '<b>Communiquez-nous le sujet et corps de votre source, eg. mail</b>' +
                    '<input id="swal-input1" class="swal2-input" placeholder="Sujet de votre source">' +
                    '<textarea id="swal-input2" class="swal2-input" rows="10" placeholder="Corps de votre source, CTRL+C / +V" style="height: auto">',
                confirmButtonText: 'Analyser &rarr;',
                showCancelButton: true,
                showLoaderOnConfirm: true,
                preConfirm: () => {
                    return $.post(
                        `/admin/rest/simulation/extraction-interet`,
                        {
                            sujet: document.getElementById('swal-input1').value,
                            corps: document.getElementById('swal-input2').value
                        }
                    ).done(
                        (response) => {
                            return response;
                        }
                    ).fail(
                        (jqXHR) => {
                            Swal.showValidationMessage(
                                `Erreur dans le traitement: ${jqXHR.statusText}`
                            )
                        }
                    );
                },
                allowOutsideClick: () => !Swal.isLoading(),
            }
        ).then((result) => {
            if (result.value) {
                Swal.fire({
                    title: 'Simulation analyse de texte',
                    html:
                        'Votre analyse: <pre><code>' +
                        JSON.stringify(result.value, null, 4) +
                        '</code></pre>',
                    confirmButtonText: 'Parfait!'
                })
            }
        });

    }

    static recuperation_saisie_assistee() {
        return new Promise(function (resolve, reject) {

            $.get(
                '/admin/rest/assistance-saisie'
            ).done(
                (data) => {

                    if (AppInterfaceInteroperabilite.AUTOMATE_EDITEUR !== null)
                    {
                        $.get(
                            '/admin/rest/assistance-saisie/automate/'+AppInterfaceInteroperabilite.AUTOMATE_EDITEUR.id
                        ).done(
                            (data_focus_automate) => {

                                let div_session_variable_globale = $('#session-variables-globales'),
                                    div_session_variable_locale = $('#session-variables-locales'),
                                    div_session_filtre = $('#session-filtre');

                                div_session_variable_globale.html('');
                                div_session_variable_locale.html('');
                                div_session_filtre.html('');

                                for (let el of AppInterfaceInteroperabilite.SUGGESTIONS_SAISIE)
                                {
                                    if (el.startsWith('{{') === true)
                                    {
                                        div_session_variable_globale.append(
                                            '<li><a class="clipboard-copy" data-clipboard-text="'+el+'" href="#">'+el+'</a></li>'
                                        );
                                    }
                                    else
                                    {
                                        div_session_filtre.append(
                                            '<li><a class="clipboard-copy" data-clipboard-text="'+el+'" href="#">'+el+'</a></li>'
                                        );
                                    }

                                }

                                for (let el_loc of data_focus_automate)
                                {
                                    div_session_variable_locale.append(
                                        '<li><a class="clipboard-copy" data-clipboard-text="'+el_loc+'" href="#">'+el_loc+'</a></li>'
                                    );
                                }

                                new ClipboardJS('.clipboard-copy');

                                AppInterfaceInteroperabilite.SUGGESTIONS_SAISIE = data.concat(data_focus_automate);

                                resolve(data);
                            }
                        ).fail(
                            (jqXHR) => {
                                console.log(jqXHR);
                                reject(jqXHR);
                            }
                        )
                    }else{
                        AppInterfaceInteroperabilite.SUGGESTIONS_SAISIE = data;
                        let div_session_variable_globale = $('#session-variables-globales'),
                            div_session_variable_locale = $('#session-variables-locales'),
                            div_session_filtre = $('#session-filtre');

                        div_session_variable_globale.html('');
                        div_session_filtre.html('');
                        div_session_variable_locale.html('<li><a href="#">Aucune</a></li>');

                        for (let el of AppInterfaceInteroperabilite.SUGGESTIONS_SAISIE)
                        {
                            if (el.startsWith('{{') === true)
                            {
                                div_session_variable_globale.append(
                                    '<li><a class="clipboard-copy" data-clipboard-text="'+el+'" href="#">'+el+'</a></li>'
                                );
                            }
                            else
                            {
                                div_session_filtre.append(
                                    '<li><a class="clipboard-copy" data-clipboard-text="'+el+'" href="#">'+el+'</a></li>'
                                );
                            }

                        }

                        new ClipboardJS('.clipboard-copy');

                        resolve(data);
                    }
                }
            ).fail(
                (jqXHR) => {
                    console.log(jqXHR);
                    reject(jqXHR);
                }
            );

        })
    }

    static assistant_saisie_assistee() {

        let all_text_input = $('input[type=text]'),
            all_text_area = $('textarea');

        all_text_input.each(
            function () {
                if ($(this).parent().hasClass('awesomplete') === false)
                {
                    new Awesomplete(this, {

                        list: AppInterfaceInteroperabilite.SUGGESTIONS_SAISIE,

                        item: function(text, input) {
                            return Awesomplete.ITEM(text, input.match(/[^\s]*$/)[0]);
                        },

                        replace: function(text) {

                            let before_match = this.input.value.match(/.*\s/);
                            let before = before_match ? before_match[0]: '';

                            this.input.value = before + text;
                        },

                        filter: function(text, input) {
                            return Awesomplete.FILTER_CONTAINS(text, input.match(/[^\s]*$/)[0]);
                        },
                    });
                }

            }
        );

        all_text_area.each(function () {
            let my_input = $(this);
            my_input.asuggest(AppInterfaceInteroperabilite.SUGGESTIONS_SAISIE);
        });

        setTimeout(AppInterfaceInteroperabilite.assistant_saisie_assistee, 1000);
    }
}

AppInterfaceInteroperabilite.ACTIONS_DESCRIPTIFS = [];
AppInterfaceInteroperabilite.EDITEUR_JSON = null;
AppInterfaceInteroperabilite.SUGGESTIONS_SAISIE = [];
AppInterfaceInteroperabilite.AUTOMATE_EDITEUR = null;
AppInterfaceInteroperabilite.LAST_SEEK_LOGS = -1;
AppInterfaceInteroperabilite.TERM = null;

module.exports = AppInterfaceInteroperabilite;
