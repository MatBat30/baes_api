from sqlalchemy import text

from templates.TimestampMixin import TimestampMixin
from . import db


class Baes(TimestampMixin,db.Model):
    __tablename__ = 'baes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    position = db.Column(db.JSON, nullable=False)

    # La clé étrangère est optionnelle (nullable=True) car une BAES ne peut pas ne pas être affectée à un étage.
    etage_id = db.Column(db.Integer, db.ForeignKey('etages.id'), nullable=False)
    # Relation one-to-many : Une BAES a plusieurs historiques d'erreurs.
    erreurs = db.relationship('HistoriqueErreur', backref='baes', lazy=True)


    def __repr__(self):
        return f"<BAES {self.name}>"
