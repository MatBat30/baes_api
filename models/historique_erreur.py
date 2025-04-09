from sqlalchemy import DateTime, text

from templates.TimestampMixin import TimestampMixin
from . import db
from datetime import *  # Importation de datetime

error_types = ('erreur_connexion', 'erreur_batterie')


def current_time():
    return datetime.now(timezone.utc)

class HistoriqueErreur(TimestampMixin,db.Model):
    __tablename__ = 'historique_erreur'

    id = db.Column(db.Integer, primary_key=True)
    baes_id = db.Column(db.Integer, db.ForeignKey('baes.id'), nullable=False)
    type_erreur = db.Column(db.Enum(*error_types, name='type_erreur'), nullable=False)
    is_solved = db.Column(db.Boolean, default=False, nullable=False)
    is_ignored = db.Column(db.Boolean, default=False, nullable=False)

    timestamp = db.Column(
        DateTime(timezone=True),
        default=current_time,
        nullable=False
    )

    def __repr__(self):
        return f"<HistoriqueErreur(baes_id={self.baes_id}, type_erreur={self.type_erreur}, timestamp={self.timestamp})>"
