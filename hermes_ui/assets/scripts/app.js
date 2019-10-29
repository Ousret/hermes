const $ = require('jquery');

global.$ = $; /* Quick fix pour jQuery et plugin ext. */
global.jQuery = $;

require('icheck/icheck');
require('fastclick');
require('bootstrap');
require('bootstrap/js/tooltip');
require('jquery-slimscroll');
require('select2');

const hljs = require('highlight.js');
let Dropzone = require('dropzone');
const Swal = require('sweetalert2');

require('./Compoments/jquery.a-tools');
require('./Compoments/jquery.asuggest');
require('./Compoments/jquery.livequery');

require('awesomplete');
const introJs = require('intro.js');

global.introJs = introJs;

require('admin-lte/dist/js/app');

require('bootstrap/dist/css/bootstrap.css');
require('admin-lte/dist/css/AdminLTE.css');
require('admin-lte/dist/css/skins/skin-green-light.css');
require('icheck/skins/square/purple.png');
require('font-awesome/css/font-awesome.css');
require('select2/dist/css/select2.css');
require('awesomplete/awesomplete.css');
require('highlight.js/styles/atelier-lakeside-dark.css');

require('../styles/hermes-surcharge.css');

const AppInterfaceInteroperabilite = require('./Compoments/hermes_ui');
Dropzone.autoDiscover = false;

global.AppInterfaceInteroperabilite = AppInterfaceInteroperabilite;

$.fn.sidebar = function(options) {

        var self = this;
        if (self.length > 1) {
            return self.each(function () {
                $(this).sidebar(options);
            });
        }

        // Width, height
        var width = self.outerWidth();
        var height = self.outerHeight();

        // Defaults
        var settings = $.extend({

            // Animation speed
            speed: 200,

            // Side: left|right|top|bottom
            side: "left",

            // Is closed
            isClosed: false,

            // Should I close the sidebar?
            close: true

        }, options);

        /*!
         *  Opens the sidebar
         *  $([jQuery selector]).trigger("sidebar:open");
         * */
        self.on("sidebar:open", function(ev, data) {
            var properties = {};
            properties[settings.side] = 0;
            settings.isClosed = null;
            self.stop().animate(properties, $.extend({}, settings, data).speed, function() {
                settings.isClosed = false;
                self.trigger("sidebar:opened");
            });
        });


        /*!
         *  Closes the sidebar
         *  $("[jQuery selector]).trigger("sidebar:close");
         * */
        self.on("sidebar:close", function(ev, data) {
            var properties = {};
            if (settings.side === "left" || settings.side === "right") {
                properties[settings.side] = -self.outerWidth();
            } else {
                properties[settings.side] = -self.outerHeight();
            }
            settings.isClosed = null;
            self.stop().animate(properties, $.extend({}, settings, data).speed, function() {
                settings.isClosed = true;
                self.trigger("sidebar:closed");
            });
        });

        /*!
         *  Toggles the sidebar
         *  $("[jQuery selector]).trigger("sidebar:toggle");
         * */
        self.on("sidebar:toggle", function(ev, data) {
            if (settings.isClosed) {
                self.trigger("sidebar:open", [data]);
            } else {
                self.trigger("sidebar:close", [data]);
            }
        });

        function closeWithNoAnimation() {
            self.trigger("sidebar:close", [{
                speed: 0
            }]);
        }

        // Close the sidebar
        if (!settings.isClosed && settings.close) {
            closeWithNoAnimation();
        }

        $(window).on("resize", function () {
            if (!settings.isClosed) { return; }
            closeWithNoAnimation();
        });

        self.data("sidebar", settings);

        return self;
    };

$(function () {

    $(".sidebarh.right").sidebar({side: "right"});

    AppInterfaceInteroperabilite.recuperation_saisie_assistee().then(
        (suggestions) => {

            AppInterfaceInteroperabilite.assistant_saisie_assistee();

            $('input[type="text"]').livequery(function () {
                AppInterfaceInteroperabilite.assistant_saisie_assistee();
            });
            $('textarea').livequery(function () {
                AppInterfaceInteroperabilite.assistant_saisie_assistee();
            });
        }
    );

    let $chatbox = $('.chatbox'),
        $chatboxTitle = $('.chatbox__title'),
        $chatboxTitleClose = $('.chatbox__title__close');

    $chatboxTitle.on('click', function() {
        $chatbox.toggleClass('chatbox--tray');
    });

    $chatboxTitleClose.on('click', function(e) {
        e.stopPropagation();
        $chatbox.addClass('chatbox--closed');
    });

    $chatbox.on('transitionend', function() {
        if ($chatbox.hasClass('chatbox--closed')) $chatbox.remove();
    });

    var myDropzone = new Dropzone(
        "#detecteur-fichier-dropzone-floatbox",
        {
            url: "/admin/rest/simulation/detecteur/fichier",
            uploadMultiple: false,
            dictDefaultMessage: 'Déposez un fichier MSG ou EML dans cette zone',

            complete: function(a) {
              let rs_template = a.xhr.response;
              Swal.fire(
                  {
                      title: '<strong>Analyse de <u>message</u></strong>',
                      type: 'info',
                      html: rs_template,
                      showCloseButton: true,
                      showCancelButton: false
                  }
              );
              hljs.initHighlightingOnLoad();
              this.removeAllFiles(true);
            }
        },

    );

    Dropzone.options.detecteurFichierDropzoneFloatbox = {
      paramName: "file", // The name that will be used to transfer the file
      maxFilesize: 5, // MB
    };

});