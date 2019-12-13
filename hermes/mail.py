import binascii
from os.path import exists

from imapclient import IMAPClient
from imapclient.exceptions import CapabilityError, IMAPClientError, IMAPClientAbortError, IMAPClientReadOnlyError
from base64 import b64decode
import email
from ssl import CERT_NONE, SSLContext, PROTOCOL_TLS, OP_ALL
from email.header import decode_header
from quopri import decodestring
from email.parser import HeaderParser
from email.utils import parseaddr

from slugify import slugify
from tqdm import tqdm
from hermes.source import Source, SourceFactory, ManipulationSourceException, ExtractionSourceException
from hermes.session import Session

from dateutil.parser import parse

from msg_parser import MsOxMessage
from msg_parser.email_builder import EmailFormatter


class Mail(Source):

    def __init__(self, message_id, subject, bodies, attachements, from_=None, to=None, current_folder='INBOX',
                 flags=None, bal_internal_id=None, date_received=None, raw_content=None):
        """

        :param str subject:
        :param list[MailBody] bodies:
        :param list[MailAttachement] attachements:
        """

        self._message_id = message_id
        self.subject = subject.replace('\n', ' ').replace('\r', '')
        self._bodies = bodies
        self._attachements = attachements

        self._from = from_
        self._to = to

        self._folder = current_folder
        self._flags = flags

        self._bal_internal_id = bal_internal_id

        self._date_received = date_received

        self._raw = raw_content

        super().__init__(subject, self.extract_body())

        self._extraction_interet.injecter_interet(
            'expediteur',
            self.expediteur
        )

        self._extraction_interet.injecter_interet(
            'destinataire',
            self.destinataire
        )

        self._extraction_interet.injecter_interet(
            'corps',
            self.extract_body('plain')
        )

        self._extraction_interet.injecter_interet(
            'pieces-jointes',
            [el.filename for el in self._attachements]
        )

        self._extraction_interet.injecter_interet(
            'pieces-jointes-types',
            [el.content_type for el in self._attachements]
        )

        self._extraction_interet['Date de réception'] = date_received

    @property
    def attachements(self):
        return self._attachements

    @property
    def nom_fichier(self):
        return slugify(self.titre)+'.eml'

    @property
    def raw(self):
        return self._raw

    @property
    def titre(self):
        return self.subject

    @property
    def corps(self):
        return self.extract_body()

    @property
    def bal_internal_id(self):
        return self._bal_internal_id

    @bal_internal_id.setter
    def bal_internal_id(self, new_value):
        if isinstance(new_value, int):
            self._bal_internal_id = new_value

    @property
    def folder(self):
        return self._folder

    @property
    def flags(self):
        return self._flags

    @folder.setter
    def folder(self, new_folder):
        self._folder = new_folder

    @flags.setter
    def flags(self, new_flags):
        self._flags = new_flags

    @property
    def id(self):
        return self._message_id

    @property
    def bodies(self):
        return self._bodies

    def extract_body(self, prefer='plain', strict=False):
        if len(self.bodies) == 0:
            return ''

        bodies = list()

        for bd in self.bodies:
            if bd.content_type == 'text/{}'.format(prefer):
                bodies.append(str(bd))

        if len(bodies) > 0:
            return '\n'.join(bodies)
        if strict is True:
            return ''

        return '\n'.join([str(bd) for bd in self.bodies])

    @staticmethod
    def from_file(file_path):
        """
        :param str file_path:
        :return:
        """
        if file_path.endswith('.eml') is False:
            raise IOError("Impossible de lire un fichier pour convertir en objet Mail si ext. hors (.eml)")
        if exists(file_path) is False:
            raise FileNotFoundError(file_path)
        with open(file_path, 'rb') as fp:
            f_content = fp.read()  # type: bytes
        return Mail.from_eml(f_content)

    @staticmethod
    def from_eml(eml_content):
        """
        :param bytes eml_content:
        :return:
        """
        if isinstance(eml_content, bytes) is False:
            raise TypeError
        return Mail.from_message(
            email.message_from_bytes(eml_content)
        )

    @staticmethod
    def from_msg(msg_content):
        """
        :param bytes msg_content:
        :return:
        """

        return Mail.from_eml(
            bytes(
                EmailFormatter(
                    MsOxMessage(msg_content)
                ).build_email(),
                'utf-8'
            )
        )

    @staticmethod
    def from_message(message):

        subject, encoding = str(), None

        for element in decode_header(message.get('Subject')):
            partials, partials_encoding = element
            if isinstance(partials, str):
                subject += partials
            if isinstance(partials, bytes):
                subject += partials.decode(partials_encoding if partials_encoding is not None else 'utf-8', errors='ignore')
            if encoding is None and partials_encoding is not None:
                encoding = partials_encoding

        bodies = list()
        attachements = list()

        if isinstance(subject, bytes):
            raise ValueError('This case should never ever happen !')
            # charset_detector = detect(subject)
            # try:
            #     subject = subject.decode('utf-8')
            # except UnicodeDecodeError as e:
            #     subject = subject.decode(charset_detector['encoding'], errors='ignore')

        header_parser = HeaderParser()

        for message_part in message.walk():

            charset_declared = None
            content_transfert_encoding_declared = None
            headers = header_parser.parsestr(message_part.as_string()).items()

            content_type = message_part.get_content_type()

            for message_part_header, message_part_header_value in headers:

                if message_part_header.lower() == 'content-type':
                    if 'charset=' in message_part_header_value.lower():
                        charset_declared = message_part_header_value.split('=')[-1].replace('"', '')
                if message_part_header.lower() == 'content-transfer-encoding':
                    content_transfert_encoding_declared = message_part_header_value

            raw_body = message_part.as_string()
            raw_body_lines = raw_body.split('\n')

            concerned_body = "\n".join(raw_body_lines[raw_body_lines.index(''):])

            if content_type == 'multipart/mixed' or content_type == 'multipart/related':

                for sub_message_part in message_part.walk():
                    sub_content_transfert_encoding_declared = None
                    sub_charset_declared = None

                    sub_content_type = sub_message_part.get_content_type()
                    sub_headers = header_parser.parsestr(sub_message_part.as_string()).items()

                    sub_raw_body = sub_message_part.as_string()
                    sub_raw_body_lines = sub_raw_body.split('\n')

                    sub_concerned_body = "\n".join(sub_raw_body_lines[sub_raw_body_lines.index(''):])

                    for message_part_header, message_part_header_value in sub_headers:

                        if message_part_header.lower() == 'content-type':
                            if 'charset=' in message_part_header_value.lower():
                                sub_charset_declared = message_part_header_value.split('=')[-1].replace('"', '')
                        if message_part_header.lower() == 'content-transfer-encoding':
                            sub_content_transfert_encoding_declared = message_part_header_value

                    if sub_content_type == 'text/plain' or sub_content_type == 'text/html':

                        bodies.append(
                            MailBody(
                                sub_headers,
                                sub_content_type,
                                sub_concerned_body if sub_content_transfert_encoding_declared is not None and 'quoted-printable' not in sub_content_transfert_encoding_declared else decodestring(sub_concerned_body).decode(sub_charset_declared if sub_charset_declared is not None else 'utf-8', errors='ignore')
                            )
                        )

            elif message_part.get_content_type() == 'text/plain' or message_part.get_content_type() == 'text/html':

                bodies.append(
                    MailBody(
                        header_parser.parsestr(raw_body).items(),
                        content_type,
                        concerned_body if content_transfert_encoding_declared is not None and 'quoted-printable' not in content_transfert_encoding_declared else decodestring(concerned_body).decode(charset_declared if charset_declared is not None else 'utf-8', errors='ignore')
                    )
                )

            elif content_type != 'multipart/mixed' and content_type != 'multipart/related':
                if 'Content-Type' not in dict(headers):
                    continue

                real_content_type = ''.join([el.decode(enc) if enc is not None else (el.decode('ascii') if isinstance(el, bytes) else el) for el, enc in decode_header(dict(headers)['Content-Type'])])

                filename = None

                if message_part.get('Content-Disposition') is not None:
                    for attr in message_part.get('Content-Disposition').split(';'):
                        if 'filename=' in attr:
                            filename = attr.split('"')[-2]
                else:
                    for attr in message_part.get('Content-Type').split(';'):
                        if 'name=' in attr:
                            filename = attr.split('"')[-2]

                if filename is not None:
                    attachements.append(
                        MailAttachement(
                            filename,
                            real_content_type,
                            "\n".join(raw_body_lines[raw_body_lines.index(''):])
                        )
                    )

        try:
            date_parse = parse(message.get('Date')).strftime('%Y/%m/%d %H:%M:%S %z')
        except:
            date_parse = message.get('Date')

        return Mail(
            message.get('Message-ID'),
            str(subject, encoding) if encoding and not isinstance(subject, str) is not None else subject,
            bodies,
            attachements,
            parseaddr(message.get('From')),
            parseaddr(message.get('To')),
            raw_content=bytes(message),
            date_received=date_parse
        )

    @property
    def expediteur(self):
        return list(
            filter(
                len,
                list(dict.fromkeys(list(self._from)))
            )
        )

    @property
    def destinataire(self):
        return list(
            filter(
                len,
                list(dict.fromkeys(list(self._to)))
            )
        )

    @property
    def is_seen(self):
        return b'\\Seen' in list(self.flags)


class MailBody:

    def __init__(self, headers, content_type, source):
        """

        :param dict headers:
        :param str content_type:
        :param str source:
        """
        self.headers = headers
        self.content_type = content_type
        if isinstance(source, bytes):
            raise TypeError('MailBody ne peut être construit avec un corps non décodé')
        self._source = source

    def has_head(self, target_header):
        """

        :param str target_header:
        :return:
        """
        for it in self.headers:
            head, value = it
            if head.lower() == target_header.lower():
                return True
        return False

    def get_head(self, target_header):
        """

        :param str target_header:
        :return:
        """
        for it in self.headers:
            head, value = it
            if head.lower() == target_header.lower():
                return value
        return None

    def __str__(self):
        if self.get_head('Content-Transfer-Encoding') == 'base64':

            charset_declared = None

            try:
                charset_declared = self.content_type.split('=')[-1].replace('"', '')
            except:
                pass

            try:
                decoded_content = str(b64decode(self._source + '=' * (-len(self._source) % 4)), charset_declared if charset_declared is not None else 'utf-8', 'ignore')
                decoded_content = decoded_content.replace('\\\\', '\\')
                return decoded_content[2:-1] if decoded_content.startswith("b'") else decoded_content
            except binascii.Error as e:
                pass

        return self._source


class MailAttachement:

    def __init__(self, filename, content_type, b64_content):
        self._filename = filename
        self._content_type = content_type
        self._b64_content = b64_content

    @property
    def filename(self):
        if self._filename is None:
            for el in self._content_type.split(';'):
                if 'name="' in el:
                    return el.replace('name=', '')[2:-1]
        return self._filename

    @property
    def content_type(self):
        return self._content_type.split(';')[0]

    @property
    def b64_content(self):
        return self._b64_content

    @property
    def content(self):
        return b64decode(self.b64_content)


class MailToolbox(SourceFactory):

    def __init__(self, hote_imap, nom_utilisateur, mot_de_passe, dossier_cible='INBOX', verify_peer=True, use_secure_socket=True, legacy_secure_protocol=False):

        super().__init__('IMAPFactory via {}'.format(hote_imap))

        self._ssl_context = SSLContext(protocol=PROTOCOL_TLS) if use_secure_socket else None
        self._use_secure_socket = use_secure_socket

        if verify_peer is False and use_secure_socket is True:
            # don't check if certificate hostname doesn't match target hostname
            self._ssl_context.check_hostname = False
            # don't check if the certificate is trusted by a certificate authority
            self._ssl_context.verify_mode = CERT_NONE

        if legacy_secure_protocol and use_secure_socket:
            self._ssl_context.options = OP_ALL

        self._hote_imap = Session.UNIVERSELLE.retranscrire(hote_imap)
        self._client = IMAPClient(host=self._hote_imap, port=993 if self._use_secure_socket else 143, ssl=self._use_secure_socket, ssl_context=self._ssl_context)
        self._nom_utilisateur = Session.UNIVERSELLE.retranscrire(nom_utilisateur)
        self._verify_peer = verify_peer
        self._dossier_cible = dossier_cible
        self._mot_de_passe = mot_de_passe

        self._client.login(self._nom_utilisateur, Session.UNIVERSELLE.retranscrire(self._mot_de_passe))

        self._echec = False

        MailToolbox.INSTANCES.append(self)

    @property
    def est_hors_service(self):
        return self._echec

    def reset(self):

        try:
            self._client.logout()
        except IMAPClientError as e:
            pass
        except OSError as e:
            pass

        self._client = IMAPClient(host=self._hote_imap, port=993 if self._use_secure_socket else 143, ssl=self._use_secure_socket, ssl_context=self._ssl_context)
        self._client.login(self._nom_utilisateur, Session.UNIVERSELLE.retranscrire(self._mot_de_passe))

        self._echec = False

    @property
    def dossier_cible(self):
        return self._dossier_cible

    @dossier_cible.setter
    def dossier_cible(self, nouveau_dossier_cible):
        if isinstance(nouveau_dossier_cible, str):
            self._dossier_cible = nouveau_dossier_cible

    @property
    def hote_imap(self):
        return self._hote_imap

    @property
    def nom_utilisateur(self):
        return self._nom_utilisateur

    @staticmethod
    def fetch_instance(hote_imap, nom_utilisateur):
        hote_imap, nom_utilisateur = Session.UNIVERSELLE.retranscrire(hote_imap), Session.UNIVERSELLE.retranscrire(nom_utilisateur)

        for inst in MailToolbox.INSTANCES:
            if isinstance(inst, MailToolbox) is True and inst.nom_utilisateur == nom_utilisateur and inst.hote_imap == hote_imap:
                return inst
        return None

    def extraire(self, no_progress_bar=True):

        if self.est_hors_service is True:
            self.reset()

        try:
            self._client.select_folder(self._dossier_cible)
        except IMAPClientError as e:
            raise ExtractionSourceException('IMAPClientError: '+str(e))
        except IMAPClientAbortError as e:
            raise ExtractionSourceException('IMAPClientAbortError: '+str(e))
        except IMAPClientReadOnlyError as e:
            raise ExtractionSourceException('IMAPClientReadOnlyError: '+str(e))
        finally:
            self._echec = True

        # fetch selectors are passed as a simple list of strings.
        responses = self._client.fetch(
            self._client.search(
                [
                    'NOT',
                    'DELETED'
                ]
            ),
            ['UID', 'ENVELOPE', 'BODY', 'RFC822']
        )

        extractions = list()  # type: list[Mail]

        for id_response in tqdm(responses.keys(), unit=' message') if no_progress_bar is False else responses.keys():

            email_message = email.message_from_bytes(responses[id_response][b'RFC822'])

            mail = Mail.from_message(email_message)

            mail.folder = self._dossier_cible
            mail.flags = responses[id_response][b'FLAGS'] if b'FLAGS' in responses[id_response].keys() else tuple()
            mail.bal_internal_id = id_response

            extractions.append(
                mail
            )

            mail.factory = self

        return extractions

    def copier(self, mail, dossier_dest):
        """

        :param Mail mail:
        :param str dossier_dest:
        :return:
        """
        if self.est_hors_service is True:
            self.reset()

        try:
            if self._client.folder_exists(dossier_dest) is False:
                raise FileNotFoundError('Le dossier "{}" n\'existe pas sur le serveur IMAP distant !')

            self._client.select_folder(mail.folder)

            self._client.copy([mail.bal_internal_id], dossier_dest)
        except IMAPClientError as e:
            raise ManipulationSourceException('IMAPClientError: '+str(e))
        except IMAPClientAbortError as e:
            raise ManipulationSourceException('IMAPClientAbortError: '+str(e))
        except IMAPClientReadOnlyError as e:
            raise ManipulationSourceException('IMAPClientReadOnlyError: '+str(e))
        finally:
            self._echec = True

    def deplacer(self, mail, dossier_dest):

        if self.est_hors_service is True:
            self.reset()

        try:
            if self._client.folder_exists(dossier_dest) is False:
                raise FileNotFoundError('Le dossier "{}" n\'existe pas sur le serveur IMAP distant !')

            self._client.select_folder(mail.folder)

            try:
                self._client.move([mail.bal_internal_id], dossier_dest)
            except CapabilityError as e:
                self.copier(mail, dossier_dest)
                self.supprimer(mail)
        except IMAPClientError as e:
            raise ManipulationSourceException('IMAPClientError: '+str(e))
        except IMAPClientAbortError as e:
            raise ManipulationSourceException('IMAPClientAbortError: '+str(e))
        except IMAPClientReadOnlyError as e:
            raise ManipulationSourceException('IMAPClientReadOnlyError: '+str(e))
        finally:
            self._echec = True

    def supprimer(self, mail):

        if self.est_hors_service is True:
            self.reset()

        try:
            self._client.select_folder(mail.folder)

            self._client.delete_messages([mail.bal_internal_id], silent=True)
            self._client.expunge([mail.bal_internal_id])
        except IMAPClientError as e:
            raise ManipulationSourceException('IMAPClientError: '+str(e))
        except IMAPClientAbortError as e:
            raise ManipulationSourceException('IMAPClientAbortError: '+str(e))
        except IMAPClientReadOnlyError as e:
            raise ManipulationSourceException('IMAPClientReadOnlyError: '+str(e))
        finally:
            self._echec = True
