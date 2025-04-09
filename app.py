from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flasgger import Swagger
from models import db
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = 'ta_clé_secrète_unique_et_complexe'
CORS(app)

# Configuration de la base de données, etc.
# (Ta configuration existante reste inchangée)
import urllib
import logging
import pyodbc

connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=127.0.0.1;"
    "DATABASE=master;"
    "UID=Externe;"
    "PWD=Secur3P@ssw0rd!"
)
params = urllib.parse.quote_plus(connection_string)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mssql+pyodbc:///?odbc_connect={params}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True

# Configuration pour l'upload
import os
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

# Initialisation des extensions
db.init_app(app)
migrate = Migrate(app, db)
swagger = Swagger(app)

# Configuration de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'  # Indique la route de login (voir ci-dessous)

# Fonction de chargement de l'utilisateur
from models.user import User
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Enregistrement des blueprints (incluant celui de l'authentification)
from routes import init_app as init_routes
init_routes(app)

# ... Reste de ton code (création des données par défaut, etc.)


# Fonction pour créer les données par défaut
def create_default_data():
    app.logger.debug("Création des données par défaut...")

    # 1. Création des rôles par défaut
    default_roles = ['user', 'technicien', 'admin', 'super-admin']
    roles = {}
    from models.role import Role
    for role_name in default_roles:
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name)
            db.session.add(role)
            app.logger.debug("Création du rôle %s", role_name)
        roles[role_name] = role
    db.session.commit()

    # 2. Création d'un site par défaut
    from models.site import Site
    default_site_name = "Site par défaut"
    site = Site.query.filter_by(name=default_site_name).first()
    if not site:
        site = Site(name=default_site_name)
        db.session.add(site)
        app.logger.debug("Création du site %s", default_site_name)
    db.session.commit()

    # 3. Création des utilisateurs par défaut et association via UserSiteRole
    default_users = {
        'user': {'login': 'user', 'password': 'user_password'},
        'technicien': {'login': 'technicien', 'password': 'tech_password'},
        'admin': {'login': 'admin', 'password': 'admin_password'},
        'super-admin': {'login': 'superadmin', 'password': 'superadmin_password'},
    }
    from models.user import User
    from models.user_site_role import UserSiteRole
    for role_name, user_data in default_users.items():
        # Vérifie si l'utilisateur existe déjà
        user = User.query.filter_by(login=user_data['login']).first()
        if not user:
            user = User(login=user_data['login'])
            user.set_password(user_data['password'])  # Hachage du mot de passe
            db.session.add(user)
            app.logger.debug("Création de l'utilisateur %s", user_data['login'])
            db.session.commit()  # Commit ici pour obtenir l'ID de l'utilisateur
        # Création de l'association s'il n'existe pas déjà
        association = UserSiteRole.query.filter_by(
            user_id=user.id,
            site_id=site.id,
            role_id=roles[role_name].id
        ).first()
        if not association:
            association = UserSiteRole(
                user_id=user.id,
                site_id=site.id,
                role_id=roles[role_name].id
            )
            db.session.add(association)
            app.logger.debug("Association de l'utilisateur %s au rôle %s sur le site %s", user.login, role_name, site.name)
    db.session.commit()


if __name__ == '__main__':
    app.logger.debug("Démarrage de l'application et test de connexion à la base...")
    print("Pilotes ODBC installés :", pyodbc.drivers())
    with app.app_context():
        try:
            connection = db.engine.connect()
            connection.close()
            app.logger.debug("Connexion réussie à la base de données.")
        except Exception as e:
            app.logger.error("Erreur de connexion à la base de données : %s", e)
        create_default_data()
    app.run(debug=True)
