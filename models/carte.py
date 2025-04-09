from sqlalchemy import text

from templates.TimestampMixin import TimestampMixin
from . import db

class Carte(TimestampMixin,db.Model):
    __tablename__ = 'cartes'
    id = db.Column(db.Integer, primary_key=True)
    chemin = db.Column(db.String(255), nullable=False)
    # La carte peut être liée à un seul étage ou à un seul site (mais pas les deux)
    etage_id = db.Column(db.Integer, db.ForeignKey('etages.id'), nullable=True, unique=True)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=True, unique=True)

    # Paramètres de configuration de la carte
    center_lat = db.Column(db.Float, nullable=False, default=0.0)  # Latitude du centre de la carte
    center_lng = db.Column(db.Float, nullable=False, default=0.0)  # Longitude du centre de la carte
    zoom = db.Column(db.Float, nullable=False, default=1.0)  # Niveau de zoom de la carte

    __table_args__ = (
        db.CheckConstraint(
            '((etage_id IS NOT NULL AND site_id IS NULL) OR (etage_id IS NULL AND site_id IS NOT NULL))',
            name='ck_carte_one_relation'
        ),
    )

    def __repr__(self):
        return f"<Carte {self.chemin}>"
