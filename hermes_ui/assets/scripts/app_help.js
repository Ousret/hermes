const $ = require('jquery');

let create_helper_callout = (titre, corps) => {
    return `
    <div class="callout callout-info">
        <h4>${titre}</h4>
        <p>
        ${corps}
        </p>
    </div>
    `;
};

$(function () {

    // Crappy way of not running this outside of app
    if ($('.login-box').length > 0) {return; }

    let current_admin_page = $('.content-header h1').html(),
        header_section = $('section.content-header'),
        content_section = $('section.content');

    if (current_admin_page.startsWith('Clé'))
    {
        content_section.prepend(
            create_helper_callout(
                "Comprendre ce qu'est une <b>Clé</b>",
                "<ul>" +
                "<li>Une <b>Clé</b> est découverte <i>automatiquement</i> par le moteur</li>" +
                "<li>Vous pouvez les découvrir avec l'outil <b>'Analyse de message'</b> en bas à droite de l'écran</li>" +
                "<li>La valeur associée a cette <b>clé</b> peut être stockée pour être exploitée</li>" +
                "</ul>"
            )
        );
        header_section.append("<small>Permet de vérifier l'existe d'une <b>Clé</b> dans l'analyse préliminaire de votre source</small>");
    }
    else if(current_admin_page.startsWith('Identifiant'))
    {
        header_section.append("<small>Permet de vérifier la présence d'un <b>identifiant</b> au format numérique dans votre source</small>");
    }
    else if(current_admin_page.startsWith('Recherche d\'expression'))
    {
        header_section.append("<small>Permet d'extraire un ou des mot(s) sachant au moins soit la partie immédiatement à droite et/ou immédiatement à gauche</small>");
    }
    else if(current_admin_page.startsWith('Détecteur'))
    {
        header_section.append("<small>Décrire à l'aide d'une collection de règles un type de source, ou comment identifier une source en tant que</small>");

        content_section.prepend(
            create_helper_callout(
                "Comprendre ce qu'est un <b>Détecteur</b>",
                "<ul>" +
                "<li>Un <b>Détecteur</b> est une définition, elle permet d'identifier une source</li>" +
                "<li>Cette définition ce précise avec un ensemble de <b>règles</b>, celles-ci sont éditables/créables depuis le sous menu <i>Règles de détection</i></li>" +
                "<li>Finalement, votre détecteur sera utile pour déclencher les actions d'un <b>Automate</b></li>" +
                "<li>De plus un détecteur comprendra de règle, de plus le taux de faux positif sera faible</li>" +
                "</ul>"
            )
        );
    }
    else if(current_admin_page.startsWith('Expression exacte'))
    {
        header_section.append("<small>Retrouver une expression, une phrase, une suite de mots, dans votre source</small>");

        content_section.prepend(
            create_helper_callout(
                "Remarques sur la recherche <b>d'expression exacte</b>",
                "<ul>" +
                "<li>La recherche ne sera pas <i>sensible à la case</i></li>" +
                "<li>Les accents ne sont pas un critère d'égalité, eg. <i>é = e</i>, <i>à = a</i></li>" +
                "</ul>"
            )
        );
    }
    else if(current_admin_page.startsWith('Mes variables globales'))
    {
        header_section.append("<small>Stocke des variables globales disponibles à tout les automates</small>");

        content_section.prepend(
            create_helper_callout(
                "Remarques sur le stockage <b>de variable globale</b>",
                "<ul>" +
                "<li>Il est possible de stocker des informations structurées au format <i>JSON</i> ou <i>YAML</i></li>" +
                "<li>Les variables créées sont disponibles depuis le volet de droite accessible par le bouton en bas à droite</li>" +
                "<li>Pour un stockage simple sans JSON ou YAML, choissisez AUTRE dans le choix format</li>" +
                "<li>Pour mémo, les variables sont accessible en les écrivants de la forme suivante: <i>{{ ma_variable }}</i></li>" +
                "</ul>"
            )
        );
    }
    else if(current_admin_page.startsWith('Description des Automates'))
    {
        header_section.append("<small>Précise le cadre d'un automate</small>");

        content_section.prepend(
            create_helper_callout(
                "Comprendre ce qu'est une <b>Description d'Automate</b>",
                "<ul>" +
                "<li>Vous pouvez ici associer un <b>Automate</b> avec un <b>Détecteur</b></li>" +
                "<li>Cette section décrit le comportement de lancement d'un <b>Automate</b></li>" +
                "<li>Les <b>Actions</b> lancées sont éditables depuis la page principale de l'application</li>" +
                "</ul>"
            )
        );
    }
    else if(current_admin_page.startsWith('Date'))
    {
        header_section.append("<small>Recherche une date au format français ou anglais ou RFC 3339 ou RFC 2822</small>");
    }
    else if(current_admin_page.startsWith('Opération sur critères'))
    {
        header_section.append("<small>Ce critère permet de combiner UN ou PLUSIEUR autre critères et y appliquer un opérateur</small>");

        content_section.prepend(
            create_helper_callout(
                "Remarque sur <b>Opération sur Critère(s)</b>",
                "<ul>" +
                "<li>Vous pouvez utiliser un critère <b>Opération sur Critère(s)</b> en sous-critère sauf <b>lui-même</b></li>" +
                "</ul>"
            )
        );

        content_section.prepend(
            create_helper_callout(
                "Comprendre ce qu'est une <b>Opération sur Critère(s)</b>",
                "<ul>" +
                "<li>Ce critère permet de <b>combiner</b> l'existance d'autres critères</li>" +
                "<li>Ce critère doit contenir au moins <b>UN</b> sous critère</li>" +
                "<li>Les opérations possibles sont les suivantes : AND, OR, NOT, XOR</li><br>" +
                "<li><b>AND :</b> L'ensemble des sous-critères doivent être validés</li>" +
                "<li><b>OR :</b> Au moins UN des sous-critères doit être validé</li>" +
                "<li><b>NOT :</b> AUCUN des sous-critères ne doit être validé</li>" +
                "<li><b>XOR :</b> Uniquement UN SEUL des sous-critères doit être validé</li>" +
                "</ul>"
            )
        );
    }
    else if(current_admin_page.startsWith('Information balisée'))
    {
        header_section.append("<small>Recherche d'information entre balise [ MON_INFO ] ou de hashtag #MON_INFO</small>");
    }

});