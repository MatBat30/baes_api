from flask import Blueprint, request, jsonify
from flasgger import swag_from
from models.user import User
from models.site import Site
from models.batiment import Batiment
from models.etage import Etage
from models.baes import Baes
from models.historique_erreur import HistoriqueErreur

general_routes_bp = Blueprint('general_routes_bp', __name__)

def historique_erreur_to_dict(err: HistoriqueErreur) -> dict:
    return {
        'id': err.id,
        'type_erreur': err.type_erreur,
        'timestamp': err.timestamp.isoformat(),
    }

def baes_to_dict(b: Baes) -> dict:
    return {
        'id': b.id,
        'name': b.name,
        'position': b.position,
        'erreurs': [historique_erreur_to_dict(e) for e in b.erreurs] if b.erreurs else [],
    }

def etage_to_dict(e: Etage) -> dict:
    return {
        'id': e.id,
        'name': e.name,
        'baes': [baes_to_dict(b) for b in e.baes] if e.baes else [],
        # Retourne uniquement l'id de la carte de l'étage, s'il existe
        'carte': {'id': e.carte.id} if e.carte else None,
    }

def batiment_to_dict(bat: Batiment) -> dict:
    return {
        'id': bat.id,
        'name': bat.name,
        'polygon_points': bat.polygon_points,
        'etages': [etage_to_dict(e) for e in bat.etages] if bat.etages else [],
    }

def site_to_dict(s: Site) -> dict:
    return {
        'id': s.id,
        'name': s.name,
        'batiments': [batiment_to_dict(bat) for bat in s.batiments] if s.batiments else [],
        # Retourne uniquement l'id de la carte du site, s'il existe
        'carte': {'id': s.carte.id} if s.carte else None,
    }

@swag_from({
    'tags': ['general'],
    'description': "Retourne pour un utilisateur donné l'ensemble des sites auxquels il a accès, "
                   "ainsi que pour chaque site, la liste de ses bâtiments, pour chaque bâtiment, la liste de ses étages, "
                   "pour chaque étage, la liste de ses BAES et, pour chaque BAES, l'historique de ses erreurs. "
                   "Pour les cartes, seule l'id est retournée.",
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "L'ID de l'utilisateur"
        }
    ],
    'responses': {
        '200': {
            'description': "Données complètes de l'utilisateur",
            'schema': {
                'type': 'object',
                'properties': {
                    'sites': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer', 'example': 1},
                                'name': {'type': 'string', 'example': "Site par défaut"},
                                'batiments': {
                                    'type': 'array',
                                    'items': {
                                        'type': 'object',
                                        'properties': {
                                            'id': {'type': 'integer', 'example': 1},
                                            'name': {'type': 'string', 'example': "Batiment A"},
                                            'polygon_points': {'type': 'object'},
                                            'etages': {
                                                'type': 'array',
                                                'items': {
                                                    'type': 'object',
                                                    'properties': {
                                                        'id': {'type': 'integer', 'example': 1},
                                                        'name': {'type': 'string', 'example': "Etage 1"},
                                                        'baes': {
                                                            'type': 'array',
                                                            'items': {
                                                                'type': 'object',
                                                                'properties': {
                                                                    'id': {'type': 'integer', 'example': 1},
                                                                    'name': {'type': 'string', 'example': "BAES 1"},
                                                                    'position': {'type': 'object'},
                                                                    'erreurs': {
                                                                        'type': 'array',
                                                                        'items': {
                                                                            'type': 'object',
                                                                            'properties': {
                                                                                'id': {'type': 'integer', 'example': 1},
                                                                                'type_erreur': {'type': 'string', 'example': "erreur_connexion"},
                                                                                'timestamp': {'type': 'string', 'example': "2025-04-03T12:34:56Z"}
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        },
                                                        'carte': {
                                                            'type': 'object',
                                                            'properties': {
                                                                'id': {'type': 'integer', 'example': 1}
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                },
                                'carte': {
                                    'type': 'object',
                                    'properties': {
                                        'id': {'type': 'integer', 'example': 1}
                                    }
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
@general_routes_bp.route('/user/<int:user_id>/alldata', methods=['GET'])
def get_all_user_site_data(user_id):
    """
    Route qui retourne pour un utilisateur donné l'ensemble des sites auxquels il a accès,
    ainsi que la hiérarchie complète :
      Site -> Batiment -> Etage -> BAES -> HistoriqueErreur
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé.'}), 404

    # Récupération des sites distincts via l'association user_site_roles
    sites = []
    seen = set()
    for assoc in user.user_site_roles.all():
        site = assoc.site
        if site and site.id not in seen:
            seen.add(site.id)
            sites.append(site)

    sites_data = [site_to_dict(site) for site in sites]
    return jsonify({'sites': sites_data}), 200
