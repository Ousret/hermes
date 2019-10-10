from hermes.logger import logger


class MoteurInteroperabilite:

    def __init__(self):
        raise NotImplemented

    @staticmethod
    def run(factories, automates):
        """
        :param list[gie_interoperabilite.source.SourceFactory] factories:
        :param list[gie_interoperabilite.automate.Automate] automates:
        """

        logger.info("Démarrage du moteur interopérabilité")

        for factory in factories:

            logger.info("Extraction des sources depuis %s ..", str(factory))

            sources = factory.extraire()

            logger.info("%i sources ont été découverte depuis %s", len(sources), str(factory))

            for source in sources:

                logger.info("Traitement de la source '%s'", source.titre)

                for automate in automates:

                    automate.lance_toi(source)

