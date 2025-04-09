# routes/etage_routes.py
from flask import Blueprint, request, jsonify, current_app
from flasgger import swag_from
from models.etage import Etage
from models import db

etage_bp = Blueprint('etage_bp', __name__)

@etage_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['Etage CRUD'],
    'description': 'Récupère la liste de tous les étages.',
    'responses': {
        200: {
            'description': 'Liste des étages.',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'example': 1},
                        'name': {'type': 'string', 'example': 'Etage 1'},
                        'batiment_id': {'type': 'integer', 'example': 1}
                    }
                }
            }
        },
        500: {'description': 'Erreur interne.'}
    }
})
def get_etages():
    try:
        etages = Etage.query.all()
        result = [{'id': e.id, 'name': e.name, 'batiment_id': e.batiment_id} for e in etages]
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_etages: {e}")
        return jsonify({'error': str(e)}), 500

@etage_bp.route('/<int:etage_id>', methods=['GET'])
@swag_from({
    'tags': ['Etage CRUD'],
    'description': 'Récupère un étage par son ID.',
    'parameters': [
        {
            'name': 'etage_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'étage à récupérer"
        }
    ],
    'responses': {
        200: {
            'description': "Détails de l'étage.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'name': {'type': 'string', 'example': 'Etage 1'},
                    'batiment_id': {'type': 'integer', 'example': 1}
                }
            }
        },
        404: {'description': "Étage non trouvé."}
    }
})
def get_etage(etage_id):
    try:
        etage = Etage.query.get(etage_id)
        if not etage:
            return jsonify({'error': "Étage non trouvé"}), 404
        result = {'id': etage.id, 'name': etage.name, 'batiment_id': etage.batiment_id}
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_etage: {e}")
        return jsonify({'error': str(e)}), 500

@etage_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['Etage CRUD'],
    'description': "Crée un nouvel étage.",
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'Etage 1'},
                    'batiment_id': {'type': 'integer', 'example': 1}
                },
                'required': ['name', 'batiment_id']
            }
        }
    ],
    'responses': {
        201: {
            'description': "Étage créé avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'name': {'type': 'string', 'example': 'Etage 1'},
                    'batiment_id': {'type': 'integer', 'example': 1}
                }
            }
        },
        400: {'description': "Mauvaise requête."}
    }
})
def create_etage():
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'batiment_id' not in data:
            return jsonify({'error': 'Les champs name et batiment_id sont requis'}), 400
        etage = Etage(name=data['name'], batiment_id=data['batiment_id'])
        db.session.add(etage)
        db.session.commit()
        result = {'id': etage.id, 'name': etage.name, 'batiment_id': etage.batiment_id}
        return jsonify(result), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in create_etage: {e}")
        return jsonify({'error': str(e)}), 500

@etage_bp.route('/<int:etage_id>', methods=['PUT'])
@swag_from({
    'tags': ['Etage CRUD'],
    'description': "Met à jour un étage existant par son ID.",
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'etage_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'étage à mettre à jour"
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'Etage mis à jour'},
                    'batiment_id': {'type': 'integer', 'example': 2}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': "Étage mis à jour avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'name': {'type': 'string', 'example': 'Etage mis à jour'},
                    'batiment_id': {'type': 'integer', 'example': 2}
                }
            }
        },
        404: {'description': "Étage non trouvé."}
    }
})
def update_etage(etage_id):
    try:
        etage = Etage.query.get(etage_id)
        if not etage:
            return jsonify({'error': "Étage non trouvé"}), 404
        data = request.get_json()
        if 'name' in data:
            etage.name = data['name']
        if 'batiment_id' in data:
            etage.batiment_id = data['batiment_id']
        db.session.commit()
        result = {'id': etage.id, 'name': etage.name, 'batiment_id': etage.batiment_id}
        return jsonify(result), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in update_etage: {e}")
        return jsonify({'error': str(e)}), 500

@etage_bp.route('/<int:etage_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Etage CRUD'],
    'description': "Supprime un étage par son ID.",
    'parameters': [
        {
            'name': 'etage_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'étage à supprimer"
        }
    ],
    'responses': {
        200: {
            'description': "Étage supprimé avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Étage supprimé avec succès'}
                }
            }
        },
        404: {'description': "Étage non trouvé."}
    }
})
def delete_etage(etage_id):
    try:
        etage = Etage.query.get(etage_id)
        if not etage:
            return jsonify({'error': "Étage non trouvé"}), 404
        db.session.delete(etage)
        db.session.commit()
        return jsonify({'message': 'Étage supprimé avec succès'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in delete_etage: {e}")
        return jsonify({'error': str(e)}), 500
