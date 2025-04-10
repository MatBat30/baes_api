from sqlalchemy import text, Index
from templates.TimestampMixin import TimestampMixin
from . import db

class Carte(TimestampMixin, db.Model):
    __tablename__ = 'cartes'
    id = db.Column(db.Integer, primary_key=True)
    chemin = db.Column(db.String(255), nullable=False)

    # Retirez unique=True ici
    etage_id = db.Column(db.Integer, db.ForeignKey('etages.id'), nullable=True)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=True)

    # Paramètres de configuration de la carte
    center_lat = db.Column(db.Float, nullable=False, default=0.0)
    center_lng = db.Column(db.Float, nullable=False, default=0.0)
    zoom = db.Column(db.Float, nullable=False, default=1.0)

    __table_args__ = (
        db.CheckConstraint(
            '((etage_id IS NOT NULL AND site_id IS NULL) OR (etage_id IS NULL AND site_id IS NOT NULL))',
            name='ck_carte_one_relation'
        ),
        # Ces index garantissent l'unicité pour les valeurs non-NULL
        Index('uq_cartes_etage_id', 'etage_id', unique=True, mssql_where=text("etage_id IS NOT NULL")),
        Index('uq_cartes_site_id', 'site_id', unique=True, mssql_where=text("site_id IS NOT NULL"))
    )

    def __repr__(self):
        return f"<Carte {self.chemin}>"
