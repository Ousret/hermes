from hermes.analysis import ExtractionInteret
from hermes.session import Session
from hashlib import sha512
from pickle import dumps


class ManipulationSourceException(Exception):
    pass


class ExtractionSourceException(Exception):
    pass


class SourceFactory:

    INSTANCES = list()  # type: list[SourceFactory]

    def __init__(self, designation):
        self._designation = designation

    @property
    def designation(self):
        return self._designation

    def extraire(self):
        """

        :return: List of extracted Source
        :rtype list[Source]
        """
        raise NotImplemented

    def copier(self, source, destination):
        raise NotImplemented

    def deplacer(self, source, destination):
        raise NotImplemented

    def supprimer(self, source):
        raise NotImplemented

    def __repr__(self):
        return "<SourceFactory::'{}'>".format(self.designation)


class Source:

    def __init__(self, titre, corps):
        """
        Une source est obligatoirement composée d'un titre et d'un corps
        :param str titre:
        :param str corps:
        """
        self._extraction_interet = ExtractionInteret(titre, corps)  # type: ExtractionInteret

        self._session = Session()
        self._factory = None  # type: SourceFactory

    @property
    def factory(self):
        return self._factory

    @factory.setter
    def factory(self, new_attached_factory):
        if isinstance(new_attached_factory, SourceFactory):
            self._factory = new_attached_factory

    @property
    def raw(self):
        raise NotImplemented

    @property
    def session(self):
        return self._session

    @property
    def extraction_interet(self):
        return self._extraction_interet

    @property
    def titre(self):
        raise NotImplemented

    @property
    def corps(self):
        raise NotImplemented

    @property
    def nom_fichier(self):
        raise NotImplemented

    @property
    def hash(self):
        return sha512(bytes(dumps(self))).hexdigest()
