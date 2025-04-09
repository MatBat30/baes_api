from . import db
from templates.TimestampMixin import TimestampMixin

class UserSiteRole(TimestampMixin, db.Model):
    __tablename__ = 'user_site_role'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True)

    # Définition des relations avec des backrefs explicites et uniques
    site = db.relationship('Site', backref=db.backref('user_site_roles', lazy='dynamic'))
    role = db.relationship('Role', backref=db.backref('user_site_roles', lazy='dynamic'))

    def __repr__(self):
        return f"<UserSiteRole user_id={self.user_id}, site_id={self.site_id}, role_id={self.role_id}>"
