from json import dumps
from time import sleep
from datetime import datetime, timedelta
import threading

from imapclient.exceptions import LoginError, ProtocolError

from hermes_ui.db import db
from hermes_ui.models import BoiteAuxLettresImap, Automate, ActionNoeud, AutomateExecution, ActionNoeudExecution, Configuration

from hermes.logger import logger
from hermes.session import Session
from hermes.detecteur import AucuneObligationInteretException

from hermes_ui.incident import NotificationIncident


class InstanceInteroperabilite:

    current_thread = None
    stop_instruction = None

    liste_attente_test = list()  # type: list[int]
    liste_attente_test_lock = threading.Lock()

    @staticmethod
    def thread():

        logger.info("Chargement des variables globales passées en base de données")
        configurations = db.session.query(Configuration).all()  # type: list[Configuration]

        for configuration in configurations:
            logger.info("Chargement de la configuration <'{}'::{}>", configuration.designation, configuration.format)
            try:
                Session.charger_input(
                    configuration.designation,
                    configuration.valeur,
                    configuration.format
                )
            except TypeError as e:
                logger.error("Impossible de charger la configuration <'{}'::{}> car '{}'", configuration.designation, configuration.format, str(e))

        logger.info("Démarrage de la boucle de surveillance des automates sur les boîtes IMAP4")

        InstanceInteroperabilite.liste_attente_test_lock.acquire()
        est_une_sequence_test = len(InstanceInteroperabilite.liste_attente_test) > 0

        if not est_une_sequence_test:
            InstanceInteroperabilite.liste_attente_test_lock.release()

        while InstanceInteroperabilite.stop_instruction is None:

            boites_aux_lettres = db.session.query(BoiteAuxLettresImap).all()  # type: list[BoiteAuxLettresImap]
            mail_factories = []

            for el in boites_aux_lettres:
                try:
                    mail_factories.append(
                        el.get_mailtoolbox()
                    )
                except LoginError as e:
                    logger.error("Impossible de démarrer l'usine "
                                                        "à production de source '{}' car '{}'", el.designation, str(e))
                except Exception as e:
                    logger.error("Impossible de démarrer l'usine "
                                                        "à production de source '{}' car '{}'", el.designation, str(e))

            if len(mail_factories) == 0:
                logger.warning("Aucune usine à production de source n'est active, "
                                                      "impossible de continuer")
                break

            logger.debug("{} usine à production de source sont actives", len(mail_factories))

            if est_une_sequence_test:
                models_automates = db.session.query(Automate).filter_by(production=False).all()  # type: list[Automate]
            else:
                models_automates = db.session.query(Automate).filter_by(production=True).all()  # type: list[Automate]

            models_automates.sort(key=lambda x: x.priorite, reverse=True)

            if len(models_automates) == 0:
                logger.warning(
                    "Aucune automate à traitement de source n'est actif, impossible de continuer")
                break

            logger.debug("{} automates en production sont actifs", len(models_automates))

            for mail_factory in mail_factories:

                logger.debug("Ouverture de la BAL '{}'@'{}'", mail_factory.nom_utilisateur, mail_factory.hote_imap)

                if InstanceInteroperabilite.stop_instruction is not None:
                    logger.info("Arrêt du service interopérabilité, fin de boucle")
                    return

                sources = mail_factory.extraire()

                logger.debug("{} sources ont été extraites de l'usine à production '{}'", len(sources), str(mail_factory))

                for source in sources:

                    logger.debug("Vérification du message électronique '{}'", source.titre)

                    for model in models_automates:

                        automate = model.transcription()

                        if InstanceInteroperabilite.stop_instruction is not None:
                            logger.info("Arrêt du service interopérabilité, fin de boucle")
                            return

                        if est_une_sequence_test and model.id not in InstanceInteroperabilite.liste_attente_test:
                            logger.debug("Séquence de test ne conserne pas '{}'.", model.designation)
                            continue

                        date_depart_automate = datetime.now()

                        # On vérifie les conditions pour anti-spam
                        nb_execution_heure = db.session.query(AutomateExecution).filter(
                            AutomateExecution.automate == model,
                            AutomateExecution.sujet == source.titre,
                            AutomateExecution.corps == source.corps,
                            # AutomateExecution.validation_automate == False,
                            AutomateExecution.date_creation >= (date_depart_automate - timedelta(hours=1))
                        ).count()

                        if nb_execution_heure >= (model.limite_par_heure if model.limite_par_heure is not None else 100):
                            logger.warning(
                                "L'automate '{}' ne va pas traiter la source '{}' car celle ci  "
                                "dépasse la limite de {} lancement(s) par heure.",
                                automate.designation,
                                source.titre,
                                (model.limite_par_heure if model.limite_par_heure is not None else 100)
                            )
                            continue

                        nb_execution_echec_heure = db.session.query(AutomateExecution).filter(
                            AutomateExecution.automate == model,
                            AutomateExecution.sujet == source.titre,
                            AutomateExecution.corps == source.corps,
                            AutomateExecution.validation_automate == False,
                            AutomateExecution.date_creation >= (date_depart_automate - timedelta(hours=1))
                        ).count()

                        if nb_execution_echec_heure >= (model.limite_echec_par_heure if model.limite_echec_par_heure is not None else 10):
                            logger.warning(
                                "L'automate '{}' ne va pas traiter la source '{}' car celle ci  "
                                "dépasse la limite en échec de {} lancement(s) par heure.",
                                automate.designation,
                                source.titre,
                                (model.limite_echec_par_heure if model.limite_echec_par_heure is not None else 10)
                            )
                            continue

                        try:
                            etat_final_automate = automate.lance_toi(source)

                            if etat_final_automate is True:
                                logger.info(
                                    "L'automate '{}' vient de traiter avec succès la source '{}'",
                                    automate.designation,
                                    source.titre
                                )
                            elif etat_final_automate is False and automate.detecteur.est_accomplis is True:
                                logger.warning(
                                    "L'automate '{}' vient de traiter avec au moins une erreur la source '{}'",
                                    automate.designation,
                                    source.titre
                                )

                                if model.notifiable is True:
                                    NotificationIncident.prevenir(
                                        model,
                                        source,
                                        "L'automate '{}' n'a pas réussi à aboutir, au moins une action est en échec".format(automate.designation),
                                        "Vous recevez ce message car votre automate '{}' est configurée "
                                        "pour émettre une notification dans ce cas. \n\n"
                                        "En PJ les élements nécessaires à l'analyse des évènements. "
                                        "L'automate est toujours actif. \n\n".format(
                                            automate.designation,
                                        )
                                    )

                        except AucuneObligationInteretException as e:
                            logger.error(
                                "L'automate '{}' ne dispose pas d'un détecteur contraignant, "
                                "il est nécessaire d'avoir au moins une règle avec obligation. "
                                "Désactivation de l'automate.",
                                automate.designation
                            )
                            model.production = False
                            db.session.commit()
                            db.session.flush()
                            continue
                        except KeyError as e:
                            logger.error(
                                "L'automate '{}' est en erreur grave, "
                                "une variable est non résolue: '{}'",
                                automate.designation,
                                str(e)
                            )
                            NotificationIncident.prevenir(
                                model,
                                source,
                                "L'automate '{}' est en erreur grave, une variable est non résolue !".format(
                                    automate.designation),
                                "Vous recevez ce message car votre automate '{}' n'est pas en mesure d'aboutir. \n\n"
                                "Une variable est non résolue. Veuillez revenir en conception. "
                                "L'automate <b>a été désactivé</b> par précaution. \n\n"
                                "Information technique: \n\n"
                                "<pre class='code code-html'><label></label><code>{}</code></pre>".format(
                                    automate.designation,
                                    str(e)
                                )
                            )

                            model.production = False

                            db.session.commit()
                            db.session.flush()

                            continue
                        except Exception as e:

                            from sys import exc_info
                            from os import path
                            import traceback

                            exc_type, exc_obj, exc_tb = exc_info()

                            logger.critical(
                                "L'automate '{}' est en erreur critique, "
                                "une exception est soulevée: '{}'",
                                automate.designation,
                                str(e)
                            )

                            fname = path.split(exc_tb.tb_frame.f_code.co_filename)[1]

                            logger.critical(
                                "Informations complémentaires '{}', '{}' à la ligne {}.", str(exc_type), str(fname), str(exc_tb.tb_lineno)
                            )

                            logger.critical(
                                traceback.format_exc()
                            )

                            NotificationIncident.prevenir(
                                model,
                                source,
                                "L'automate '{}' est en erreur critique, une exception est soulevée !".format(automate.designation),

                                "Vous recevez ce message car votre automate '{}' n'est pas en mesure d'aboutir. \n\n"
                                "Une exception est non résolue. Veuillez revenir en conception. "
                                "L'automate a été désactivé par précaution. \n\n"
                                "Information technique: \n\n"
                                "<pre class='code code-html'><label>Logs</label><code>{}</code></pre>".format(automate.designation, traceback.format_exc())
                            )

                            model.production = False

                            db.session.commit()
                            db.session.flush()

                            continue

                        if automate.detecteur.est_accomplis is True:

                            automate_execution = AutomateExecution(
                                automate=model,
                                sujet=source.titre if len(source.titre) < 255 else source[1:250]+'..',
                                corps=source.corps,
                                date_creation=date_depart_automate,
                                detecteur=model.detecteur,
                                validation_detecteur=automate.detecteur.est_accomplis,
                                validation_automate=etat_final_automate,
                                explications_detecteur=automate.detecteur.explain(),
                                date_finalisation=datetime.now(),
                                logs=automate.logs
                            )

                            for action_lancee in automate.actions_lancees:

                                action_noeud_execution = ActionNoeudExecution(
                                    automate_execution=automate_execution,
                                    action_noeud=db.session.query(ActionNoeud).filter_by(designation=action_lancee.designation, automate_id=model.id).one(),
                                    validation_action_noeud=action_lancee.est_reussite,
                                    payload=str(action_lancee.payload),
                                    args_payload=dumps(action_lancee.snapshot)
                                )

                                db.session.add(action_noeud_execution)

                            db.session.add(automate_execution)
                            db.session.commit()

                            break  # La source a été traitée. Pas besoin d'y appliquer un autre automate.

                db.session.flush()

            if est_une_sequence_test:
                InstanceInteroperabilite.liste_attente_test.clear()
                InstanceInteroperabilite.liste_attente_test_lock.release()
                break

            sleep(1 if len(mail_factories) > 0 else 10)

        logger.info("Fin de surveillance continue des automates sur les boîtes IMAP4")
        InstanceInteroperabilite.current_thread = None

    @staticmethod
    def demarrer():
        if InstanceInteroperabilite.current_thread is None:
            InstanceInteroperabilite.stop_instruction = None
            InstanceInteroperabilite.current_thread = threading.Thread(target=InstanceInteroperabilite.thread, args=())
            InstanceInteroperabilite.current_thread.start()
            return True
        return False

    @staticmethod
    def arreter():
        if InstanceInteroperabilite.current_thread is not None:
            InstanceInteroperabilite.stop_instruction = True
            InstanceInteroperabilite.current_thread = None
            return True
        return False
