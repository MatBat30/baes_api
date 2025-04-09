from .batiment_routes import batiment_bp
from .etage_carte_routes import etage_carte_bp
from .etage_routes import etage_bp
from .site_carte_routes import site_carte_bp
from .site_routes import site_bp
from .carte_routes import carte_bp
from .user_role_routes import user_role_bp
from .user_routes import user_bp
from .user_site_routes import user_site_bp
from .baes_routes import baes_bp
from .historique_erreur_routes import historique_erreur_bp
from .auth import auth_bp  # Si tu as aussi ton blueprint d'authentification
from .role_routes import role_bp  # Ajout du blueprint des rôles
from .user_site_role_routes import user_site_role_bp
from .general_routes import general_routes_bp

def init_app(app):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(role_bp, url_prefix='/roles')
    app.register_blueprint(carte_bp, url_prefix='/cartes')
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(user_site_bp, url_prefix='/users/sites')
    app.register_blueprint(site_bp, url_prefix='/sites')
    app.register_blueprint(batiment_bp, url_prefix='/batiments')
    app.register_blueprint(etage_bp, url_prefix='/etages')
    app.register_blueprint(etage_carte_bp, url_prefix='/etages/carte')
    app.register_blueprint(site_carte_bp, url_prefix='/sites/carte')
    app.register_blueprint(user_role_bp, url_prefix='/role/users')
    app.register_blueprint(baes_bp, url_prefix='/baes')
    app.register_blueprint(historique_erreur_bp, url_prefix='/erreurs')
    app.register_blueprint(user_site_role_bp, url_prefix='/user_site_role')
    app.register_blueprint(general_routes_bp, url_prefix='/general')
