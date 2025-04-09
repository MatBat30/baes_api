# routes/site_routes.py
from flask import Blueprint, request, jsonify, current_app
from flasgger import swag_from
from models.site import Site
from models import db

site_bp = Blueprint('site_bp', __name__)

@site_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['Site CRUD'],
    'description': 'Récupère la liste de tous les sites.',
    'responses': {
        200: {
            'description': 'Liste des sites.',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'example': 1},
                        'name': {'type': 'string', 'example': 'Site 1'},
                    }
                }
            }
        },
        500: {'description': 'Erreur interne.'}
    }
})
def get_sites():
    try:
        sites = Site.query.all()
        result = [{'id': s.id, 'name': s.name} for s in sites]
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_sites: {e}")
        return jsonify({'error': str(e)}), 500

@site_bp.route('/<int:site_id>', methods=['GET'])
@swag_from({
    'tags': ['Site CRUD'],
    'description': 'Récupère un site par son ID.',
    'parameters': [
        {
            'name': 'site_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID du site à récupérer'
        }
    ],
    'responses': {
        200: {
            'description': 'Détails du site.',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'name': {'type': 'string', 'example': 'Site 1'},
                }
            }
        },
        404: {'description': 'Site non trouvé.'}
    }
})
def get_site(site_id):
    try:
        site = Site.query.get(site_id)
        if not site:
            return jsonify({'error': 'Site non trouvé'}), 404
        result = {'id': site.id, 'name': site.name}
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_site: {e}")
        return jsonify({'error': str(e)}), 500

@site_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['Site CRUD'],
    'description': "Crée un nouveau site.",
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'Site 1'},
                },
                'required': ['name']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Site créé avec succès.',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'name': {'type': 'string', 'example': 'Site 1'},
                }
            }
        },
        400: {'description': 'Mauvaise requête.'}
    }
})
def create_site():
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Les champs name est requis'}), 400
        site = Site(name=data['name'])
        db.session.add(site)
        db.session.commit()
        result = {'id': site.id, 'name': site.name}
        return jsonify(result), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in create_site: {e}")
        return jsonify({'error': str(e)}), 500

@site_bp.route('/<int:site_id>', methods=['PUT'])
@swag_from({
    'tags': ['Site CRUD'],
    'description': "Met à jour un site existant.",
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'site_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID du site à mettre à jour"
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'Site mis à jour'},
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Site mis à jour avec succès.',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'name': {'type': 'string', 'example': 'Site mis à jour'},
                }
            }
        },
        404: {'description': 'Site non trouvé.'}
    }
})
def update_site(site_id):
    try:
        site = Site.query.get(site_id)
        if not site:
            return jsonify({'error': 'Site non trouvé'}), 404
        data = request.get_json()
        if 'name' in data:
            site.name = data['name']
        db.session.commit()
        result = {'id': site.id, 'name': site.name}
        return jsonify(result), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in update_site: {e}")
        return jsonify({'error': str(e)}), 500

@site_bp.route('/<int:site_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Site CRUD'],
    'description': "Supprime un site par son ID.",
    'parameters': [
        {
            'name': 'site_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID du site à supprimer"
        }
    ],
    'responses': {
        200: {
            'description': 'Site supprimé avec succès.',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Site supprimé avec succès'}
                }
            }
        },
        404: {'description': 'Site non trouvé.'}
    }
})
def delete_site(site_id):
    try:
        site = Site.query.get(site_id)
        if not site:
            return jsonify({'error': 'Site non trouvé'}), 404
        db.session.delete(site)
        db.session.commit()
        return jsonify({'message': 'Site supprimé avec succès'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in delete_site: {e}")
        return jsonify({'error': str(e)}), 500
