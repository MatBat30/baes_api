from flask import Blueprint, request, jsonify, current_app
from models.role import Role
from models import db

role_bp = Blueprint('role_bp', __name__)

@role_bp.route('/', methods=['POST'])
def create_role():
    """
    Crée un rôle.
    ---
    tags:
      - Roles
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
              example: admin
    responses:
      201:
        description: Rôle créé avec succès.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Rôle créé"
            role:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                name:
                  type: string
                  example: admin
      400:
        description: Mauvaise requête (rôle existant ou champ manquant).
    """
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Le champ "name" est requis'}), 400
    name = data['name']
    if Role.query.filter_by(name=name).first():
        return jsonify({'error': 'Ce rôle existe déjà'}), 400
    role = Role(name=name)
    db.session.add(role)
    db.session.commit()
    return jsonify({'message': 'Rôle créé', 'role': {'id': role.id, 'name': role.name}}), 201
