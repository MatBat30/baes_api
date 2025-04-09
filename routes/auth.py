from flask import Blueprint, request, jsonify, redirect, url_for, render_template
from flask_login import login_user, logout_user, login_required
from flasgger import swag_from
from models.user import User
from models import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'description': 'Connexion de l\'utilisateur via JSON. Fournissez "login" et "password" dans le corps de la requête.',
    'consumes': ['application/json'],
    'parameters': [
        {
            'in': 'body',
            'name': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['login', 'password'],
                'properties': {
                    'login': {'type': 'string', 'example': 'monlogin'},
                    'password': {'type': 'string', 'example': 'monmotdepasse'}
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Utilisateur connecté avec succès',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Connecté'},
                    'user_id': {'type': 'integer', 'example': 1},
                    'sites': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer', 'example': 3},
                                'name': {'type': 'string', 'example': 'Site A'},
                                'roles': {
                                    'type': 'array',
                                    'items': {
                                        'type': 'object',
                                        'properties': {
                                            'id': {'type': 'integer', 'example': 2},
                                            'name': {'type': 'string', 'example': 'admin'}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        '401': {
            'description': 'Identifiants invalides',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Identifiants invalides'}
                }
            }
        }
    }
})
def login():
    data = request.get_json()
    if not data or 'login' not in data or 'password' not in data:
        return jsonify({'error': 'Les champs "login" et "password" sont requis'}), 400

    login_input = data.get('login')
    password = data.get('password')
    user = User.query.filter_by(login=login_input).first()
    if user and user.check_password(password):
        login_user(user)  # L'utilisateur est connecté et stocké dans la session

        # Récupérer la liste des associations via le backref user_site_roles
        # et grouper par site avec leurs rôles associés.
        sites_dict = {}
        for assoc in user.user_site_roles.all():
            if assoc.site:
                sid = assoc.site.id
                if sid not in sites_dict:
                    sites_dict[sid] = {
                        'id': assoc.site.id,
                        'name': assoc.site.name,
                        'roles': []
                    }
                if assoc.role:
                    # Ajoute le rôle s'il n'est pas déjà présent
                    if assoc.role.id not in [r['id'] for r in sites_dict[sid]['roles']]:
                        sites_dict[sid]['roles'].append({
                            'id': assoc.role.id,
                            'name': assoc.role.name
                        })

        return jsonify({
            'message': 'Connecté',
            'user_id': user.id,
            'sites': list(sites_dict.values())
        }), 200
    else:
        return jsonify({'error': 'Identifiants invalides'}), 401

@auth_bp.route('/logout', methods=['GET'])
@swag_from({
    'tags': ['Authentication'],
    'description': 'Déconnecte l\'utilisateur connecté.',
    'responses': {
        '200': {
            'description': 'Utilisateur déconnecté avec succès',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Déconnecté'}
                }
            }
        }
    }
})
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Déconnecté'}), 200
