from flask import Blueprint, request, jsonify, current_app
from flasgger import swag_from
from models.user import User
from models import db

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['User CRUD'],
    'description': 'Récupère la liste de tous les utilisateurs avec leurs sites et rôles associés.',
    'responses': {
        '200': {
            'description': 'Liste des utilisateurs avec leurs sites et rôles.',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'example': 1},
                        'login': {'type': 'string', 'example': 'user1'},
                        'roles': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'example': ['admin', 'user']
                        },
                        'sites': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer', 'example': 3},
                                    'name': {'type': 'string', 'example': 'Site test 1'}
                                }
                            },
                            'example': [
                                {'id': 3, 'name': 'Site test 1'},
                                {'id': 4, 'name': 'Site test 2'}
                            ]
                        }
                    }
                }
            }
        },
        '500': {'description': 'Erreur interne.'}
    }
})
def get_users():
    try:
        users = User.query.all()
        result = []
        for user in users:
            # Récupérer les rôles distincts via l'association
            roles_set = {assoc.role.name for assoc in user.user_site_roles if assoc.role}
            # Récupérer les sites distincts via l'association
            sites = []
            sites_ids = set()
            for assoc in user.user_site_roles:
                if assoc.site and assoc.site.id not in sites_ids:
                    sites.append({'id': assoc.site.id, 'name': assoc.site.name})
                    sites_ids.add(assoc.site.id)
            result.append({
                'id': user.id,
                'login': user.login,
                'roles': list(roles_set),
                'sites': sites
            })
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_users: {e}")
        return jsonify({'error': str(e)}), 500


@user_bp.route('/<int:user_id>', methods=['GET'])
@swag_from({
    'tags': ['User CRUD'],
    'description': "Récupère un utilisateur par son ID avec ses sites et rôles associés.",
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'utilisateur à récupérer"
        }
    ],
    'responses': {
        '200': {
            'description': "Détails de l'utilisateur.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'login': {'type': 'string', 'example': 'user1'},
                    'roles': {'type': 'array', 'items': {'type': 'string'}},
                    'sites': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer', 'example': 3},
                                'name': {'type': 'string', 'example': 'Site test 1'}
                            }
                        }
                    }
                }
            }
        },
        '404': {'description': "Utilisateur non trouvé."},
        '500': {'description': "Erreur interne."}
    }
})
def get_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        roles_set = {assoc.role.name for assoc in user.user_site_roles if assoc.role}
        sites = []
        sites_ids = set()
        for assoc in user.user_site_roles:
            if assoc.site and assoc.site.id not in sites_ids:
                sites.append({'id': assoc.site.id, 'name': assoc.site.name})
                sites_ids.add(assoc.site.id)
        result = {
            'id': user.id,
            'login': user.login,
            'roles': list(roles_set),
            'sites': sites
        }
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_user: {e}")
        return jsonify({'error': str(e)}), 500


@user_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['User CRUD'],
    'consumes': ['application/json'],
    'description': "Crée un nouvel utilisateur et associe éventuellement des rôles et sites via l'association.",
    'parameters': [
        {
            'in': 'body',
            'name': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['login', 'password'],
                'properties': {
                    'login': {
                        'type': 'string',
                        'example': 'nouveluser'
                    },
                    'password': {
                        'type': 'string',
                        'example': 'motdepasse'
                    },
                    'roles': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'example': ['admin', 'user']
                    },
                    'sites': {
                        'type': 'array',
                        'items': {'type': 'integer'},
                        'example': [3, 4]
                    }
                }
            }
        }
    ],
    'responses': {
        '201': {
            'description': "Utilisateur créé avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'login': {'type': 'string', 'example': 'nouveluser'},
                    'roles': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'example': ['admin', 'user']
                    },
                    'sites': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer', 'example': 3},
                                'name': {'type': 'string', 'example': 'Site test 1'}
                            }
                        }
                    }
                }
            }
        },
        '400': {'description': "Mauvaise requête."}
    }
})
def create_user():
    data = request.get_json()
    if not data or 'login' not in data or 'password' not in data:
        return jsonify({'error': 'Les champs "login" et "password" sont requis'}), 400

    login = data['login']
    password = data['password']

    if User.query.filter_by(login=login).first():
        return jsonify({'error': 'Cet utilisateur existe déjà'}), 400

    user = User(login=login)
    user.set_password(password)

    # Association facultative des rôles
    if 'roles' in data:
        from models.role import Role
        role_names = data['roles']
        roles = Role.query.filter(Role.name.in_(role_names)).all()
        user.roles.extend(roles)
    # Si la relation 'sites' est définie (ou si vous souhaitez ajouter des associations via le modèle d'association UserSiteRole,
    # vous devrez adapter ici en créant des entrées dans la table d'association)
    if 'sites' in data and hasattr(user, 'sites'):
        from models.site import Site
        site_ids = data['sites']
        sites = Site.query.filter(Site.id.in_(site_ids)).all()
        user.sites.extend(sites)

    db.session.add(user)
    db.session.commit()

    result = {
        'id': user.id,
        'login': user.login,
        'roles': [role.name for role in user.roles] if hasattr(user, 'roles') else [],
        'sites': [{'id': site.id, 'name': site.name} for site in user.sites] if hasattr(user, 'sites') else []
    }
    return jsonify(result), 201


@user_bp.route('/<int:user_id>', methods=['PUT'])
@swag_from({
    'tags': ['User CRUD'],
    'description': "Met à jour un utilisateur existant par son ID.",
    'consumes': ["application/json"],
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'utilisateur à mettre à jour"
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'login': {'type': 'string', 'example': 'updateduser'},
                    'password': {'type': 'string', 'example': 'updatedpassword'},
                    'roles': {
                        'type': 'array',
                        'items': {'type': 'string', 'example': 'admin'},
                        'description': 'Liste des noms de rôles à associer (optionnel)'
                    }
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': "Utilisateur mis à jour avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'login': {'type': 'string', 'example': 'updateduser'},
                    'roles': {'type': 'array', 'items': {'type': 'string'}}
                }
            }
        },
        '404': {'description': "Utilisateur non trouvé."},
        '500': {'description': "Erreur interne."}
    }
})
def update_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        data = request.get_json()
        if 'login' in data:
            user.login = data['login']
        if 'password' in data:
            user.set_password(data['password'])
        if 'roles' in data:
            from models.role import Role
            role_names = data['roles']
            roles = Role.query.filter(Role.name.in_(role_names)).all()
            user.roles = roles
        db.session.commit()
        result = {
            'id': user.id,
            'login': user.login,
            'roles': [role.name for role in user.roles] if hasattr(user, 'roles') else []
        }
        return jsonify(result), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in update_user: {e}")
        return jsonify({'error': str(e)}), 500


@user_bp.route('/<int:user_id>', methods=['DELETE'])
@swag_from({
    'tags': ['User CRUD'],
    'description': "Supprime un utilisateur par son ID.",
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'utilisateur à supprimer"
        }
    ],
    'responses': {
        '200': {
            'description': "Utilisateur supprimé avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Utilisateur supprimé avec succès'}
                }
            }
        },
        '404': {'description': "Utilisateur non trouvé."},
        '500': {'description': "Erreur interne."}
    }
})
def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'Utilisateur supprimé avec succès'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in delete_user: {e}")
        return jsonify({'error': str(e)}), 500
