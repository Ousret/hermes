from hermes.mail import MailToolbox
from hermes_ui.db import db
from hermes_ui.models import User


class BoiteAuxLettresImap(db.Model):

    id = db.Column(db.Integer(), primary_key=True)
    designation = db.Column(db.String(255), nullable=False)

    activation = db.Column(db.Boolean(), default=False)

    hote_distante = db.Column(db.String(255), nullable=False)
    nom_utilisateur = db.Column(db.String(), nullable=False)
    mot_de_passe = db.Column(db.String(), nullable=False)
    dossier_cible = db.Column(db.String(), nullable=False, default='INBOX')

    verification_certificat = db.Column(db.Boolean(), nullable=False, default=True)

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
                verify_peer=self.verification_certificat
            )
        return existant
