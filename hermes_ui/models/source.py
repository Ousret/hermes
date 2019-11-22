from hermes.mail import MailToolbox
from hermes_ui.db import db
from hermes_ui.models import User


class BoiteAuxLettresImap(db.Model):

    id = db.Column(db.Integer(), primary_key=True)
    designation = db.Column(db.String(255), nullable=False)

    activation = db.Column(db.Boolean(), default=False)

    hote_distante = db.Column(db.String(255), nullable=False)
    nom_utilisateur = db.Column(db.String(255), nullable=False)
    mot_de_passe = db.Column(db.String(255), nullable=False)
    dossier_cible = db.Column(db.String(255), nullable=False, default='INBOX')

    enable_tls = db.Column(db.Boolean(), nullable=False, default=True)
    verification_certificat = db.Column(db.Boolean(), nullable=False, default=True)
    legacy_tls_support = db.Column(db.Boolean(), nullable=False, default=False)

    createur_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    createur = db.relationship(User, primaryjoin="User.id==BoiteAuxLettresImap.createur_id")

    date_creation = db.Column(db.DateTime(timezone=True), nullable=False)
    date_modification = db.Column(db.DateTime(timezone=True), nullable=False)

    responsable_derniere_modification_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    responsable_derniere_modification = db.relationship(User,
                                                        primaryjoin="User.id==BoiteAuxLettresImap.responsable_derniere_modification_id")

    def get_mailtoolbox(self):
        """
        :return:
        :rtype: MailToolbox
        """
        existant = MailToolbox.fetch_instance(self.hote_distante, self.nom_utilisateur)
        if existant is None:
            return MailToolbox(
                self.hote_distante,
                self.nom_utilisateur,
                self.mot_de_passe,
                dossier_cible=self.dossier_cible,
                verify_peer=self.verification_certificat,
                use_secure_socket=self.enable_tls,
                legacy_secure_protocol=self.legacy_tls_support
            )
        return existant
