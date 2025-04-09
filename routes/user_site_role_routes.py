from flask import Blueprint, request, jsonify, current_app
from flasgger import swag_from
from models.user_site_role import UserSiteRole
from models.user import User
from models.site import Site
from models.role import Role
from models import db

user_site_role_bp = Blueprint('user_site_role_bp', __name__)

@user_site_role_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['User-Site-Role'],
    'consumes': ['application/json'],
    'description': 'Crée une association entre un utilisateur, un site et un rôle. Cette association indique le rôle de l’utilisateur pour ce site.',
    'parameters': [
        {
            'in': 'body',
            'name': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['user_id', 'site_id', 'role_id'],
                'properties': {
                    'user_id': {
                        'type': 'integer',
                        'example': 1
                    },
                    'site_id': {
                        'type': 'integer',
                        'example': 2
                    },
                    'role_id': {
                        'type': 'integer',
                        'example': 3
                    }
                }
            }
        }
    ],
    'responses': {
        '201': {
            'description': "Association créée avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'Association créée avec succès.'
                    },
                    'association': {
                        'type': 'object',
                        'properties': {
                            'user_id': {'type': 'integer', 'example': 1},
                            'site_id': {'type': 'integer', 'example': 2},
                            'role_id': {'type': 'integer', 'example': 3}
                        }
                    }
                }
            }
        },
        '400': {
            'description': "Mauvaise requête (données manquantes ou association existante)."
        },
        '404': {
            'description': "Utilisateur, site ou rôle non trouvé."
        }
    }
})
def create_association():
    data = request.get_json()
    if not data or 'user_id' not in data or 'site_id' not in data or 'role_id' not in data:
        return jsonify({'error': 'Les champs "user_id", "site_id" et "role_id" sont requis.'}), 400

    user_id = data['user_id']
    site_id = data['site_id']
    role_id = data['role_id']

    # Vérifier l'existence des entités
    user = User.query.get(user_id)
    site = Site.query.get(site_id)
    role = Role.query.get(role_id)

    if not user:
        return jsonify({'error': 'Utilisateur non trouvé.'}), 404
    if not site:
        return jsonify({'error': 'Site non trouvé.'}), 404
    if not role:
        return jsonify({'error': 'Rôle non trouvé.'}), 404

    # Vérifier si l'association existe déjà
    existing = UserSiteRole.query.filter_by(user_id=user_id, site_id=site_id, role_id=role_id).first()
    if existing:
        return jsonify({'error': "Cette association existe déjà."}), 400

    association = UserSiteRole(user_id=user_id, site_id=site_id, role_id=role_id)
    db.session.add(association)
    db.session.commit()

    return jsonify({
        'message': 'Association créée avec succès.',
        'association': {
            'user_id': association.user_id,
            'site_id': association.site_id,
            'role_id': association.role_id
        }
    }), 201

@user_site_role_bp.route('/<int:user_id>/<int:site_id>', methods=['GET'])
@swag_from({
    'tags': ['User-Site-Role'],
    'description': 'Récupère toutes les associations (rôles) pour un utilisateur donné sur un site donné.',
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'utilisateur"
        },
        {
            'name': 'site_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID du site"
        }
    ],
    'responses': {
        '200': {
            'description': 'Liste des associations pour l\'utilisateur et le site donnés.',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'user_id': {'type': 'integer', 'example': 1},
                        'site_id': {'type': 'integer', 'example': 2},
                        'role_id': {'type': 'integer', 'example': 3}
                    }
                }
            }
        },
        '404': {
            'description': 'Utilisateur ou site non trouvé.'
        }
    }
})
def get_associations(user_id, site_id):
    user = User.query.get(user_id)
    site = Site.query.get(site_id)
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé.'}), 404
    if not site:
        return jsonify({'error': 'Site non trouvé.'}), 404
    associations = UserSiteRole.query.filter_by(user_id=user_id, site_id=site_id).all()
    result = [{
        'user_id': assoc.user_id,
        'site_id': assoc.site_id,
        'role_id': assoc.role_id
    } for assoc in associations]
    return jsonify(result), 200

@user_site_role_bp.route('/<int:user_id>/<int:site_id>/<int:role_id>', methods=['DELETE'])
@swag_from({
    'tags': ['User-Site-Role'],
    'description': "Supprime une association spécifique entre un utilisateur, un site et un rôle.",
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'utilisateur"
        },
        {
            'name': 'site_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID du site"
        },
        {
            'name': 'role_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID du rôle"
        }
    ],
    'responses': {
        '200': {
            'description': "Association supprimée avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'Association supprimée avec succès.'
                    }
                }
            }
        },
        '404': {
            'description': "Association non trouvée."
        }
    }
})
def delete_association(user_id, site_id, role_id):
    association = UserSiteRole.query.filter_by(user_id=user_id, site_id=site_id, role_id=role_id).first()
    if not association:
        return jsonify({'error': 'Association non trouvée.'}), 404
    db.session.delete(association)
    db.session.commit()
    return jsonify({'message': 'Association supprimée avec succès.'}), 200

@user_site_role_bp.route('/user/<int:user_id>', methods=['GET'])
@swag_from({
    'tags': ['User-Site-Role'],
    'description': "Récupère la liste des sites et des rôles associés pour un utilisateur donné.",
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'utilisateur"
        }
    ],
    'responses': {
        '200': {
            'description': "Liste des sites et rôles associés pour l'utilisateur.",
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'site_id': {'type': 'integer', 'example': 2},
                        'site_name': {'type': 'string', 'example': 'Site A'},
                        'roles': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'role_id': {'type': 'integer', 'example': 3},
                                    'role_name': {'type': 'string', 'example': 'admin'}
                                }
                            }
                        }
                    }
                }
            }
        },
        '404': {
            'description': "Utilisateur non trouvé."
        }
    }
})
def get_sites_roles_for_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé.'}), 404

    # Récupère toutes les associations pour cet utilisateur
    associations = user.user_site_roles.all()
    results = {}
    for assoc in associations:
        site_id = assoc.site_id
        site_name = assoc.site.name if assoc.site else None
        if site_id not in results:
            results[site_id] = {
                'site_id': site_id,
                'site_name': site_name,
                'roles': []
            }
        results[site_id]['roles'].append({
            'role_id': assoc.role_id,
            'role_name': assoc.role.name if assoc.role else None
        })
    return jsonify(list(results.values())), 200
