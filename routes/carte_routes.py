# routes/carte_routes.py

import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from flasgger import swag_from
from models.carte import Carte
from models import db

carte_bp = Blueprint('carte_bp', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@carte_bp.route('/upload-carte', methods=['POST'])
@swag_from({
    'tags': ['Carte CRUD'],
    'description': "Upload d'une carte avec ses paramètres (centre, zoom) et son association à un site ou un étage. "
                   "Vous devez fournir l'ID du site (`site_id`) ou l'ID de l'étage (`etage_id`), mais pas les deux ni aucun.",
    'consumes': ['multipart/form-data'],
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'Fichier image de la carte (png, jpg, etc.)'
        },
        {
            'name': 'center_lat',
            'in': 'formData',
            'type': 'number',
            'required': False,
            'default': 0.0,
            'description': 'Latitude du centre de la carte'
        },
        {
            'name': 'center_lng',
            'in': 'formData',
            'type': 'number',
            'required': False,
            'default': 0.0,
            'description': 'Longitude du centre de la carte'
        },
        {
            'name': 'zoom',
            'in': 'formData',
            'type': 'number',
            'required': False,
            'default': 1.0,
            'description': 'Niveau de zoom de la carte'
        },
        {
            'name': 'site_id',
            'in': 'formData',
            'type': 'integer',
            'required': False,
            'description': 'ID du site auquel la carte sera associée (si la carte est liée à un site)'
        },
        {
            'name': 'etage_id',
            'in': 'formData',
            'type': 'integer',
            'required': False,
            'description': 'ID de l\'étage auquel la carte sera associée (si la carte est liée à un étage)'
        }
    ],
    'responses': {
        200: {
            'description': 'Fichier uploadé et carte sauvegardée avec succès.',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Fichier uploadé avec succès'},
                    'carte': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer', 'example': 1},
                            'chemin': {'type': 'string', 'example': '/path/to/image.png'},
                            'center_lat': {'type': 'number', 'example': 48.8566},
                            'center_lng': {'type': 'number', 'example': 2.3522},
                            'zoom': {'type': 'number', 'example': 1.0},
                            'etage_id': {'type': 'integer', 'example': None},
                            'site_id': {'type': 'integer', 'example': 3}
                        }
                    }
                }
            }
        },
        400: {'description': 'Erreur de requête, fichier non fourni, paramètres invalides ou aucune association renseignée.'}
    }
})
def upload_carte():
    # Vérifier la présence du fichier dans la requête
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nom de fichier vide'}), 400

    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Extension de fichier non autorisée'}), 400

    filename = secure_filename(file.filename)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)

    # Récupérer les paramètres de configuration de la carte depuis request.form
    try:
        center_lat = float(request.form.get('center_lat', 0.0))
        center_lng = float(request.form.get('center_lng', 0.0))
        zoom = float(request.form.get('zoom', 1.0))
    except ValueError:
        return jsonify({'error': 'Paramètres invalides pour la configuration de la carte'}), 400

    # Récupérer les paramètres d'association
    site_id = request.form.get('site_id')
    etage_id = request.form.get('etage_id')

    # Convertir en int s'ils sont renseignés
    site_id = int(site_id) if site_id is not None and site_id != '' else None
    etage_id = int(etage_id) if etage_id is not None and etage_id != '' else None

    # Vérifier que exactement l'un des deux est renseigné.
    if (site_id is None and etage_id is None) or (site_id is not None and etage_id is not None):
        return jsonify({'error': 'Vous devez fournir soit site_id, soit etage_id (mais pas les deux)'}), 400

    # Créer l'objet Carte en renseignant la bonne association
    carte = Carte(
        chemin=file_path,
        center_lat=center_lat,
        center_lng=center_lng,
        zoom=zoom,
        site_id=site_id,
        etage_id=etage_id
    )
    try:
        db.session.add(carte)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la sauvegarde de la carte: {str(e)}'}), 500

    return jsonify({
        'message': 'Fichier uploadé avec succès',
        'carte': {
            'id': carte.id,
            'chemin': file_path,
            'center_lat': carte.center_lat,
            'center_lng': carte.center_lng,
            'zoom': carte.zoom,
            'site_id': carte.site_id,
            'etage_id': carte.etage_id
        }
    }), 200
