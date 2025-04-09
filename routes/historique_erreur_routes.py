# routes/historique_erreur_routes.py
from flask import Blueprint, request, jsonify, current_app
from flasgger import swag_from
from models.batiment import Batiment
from models import db


historique_erreur_bp = Blueprint('historique_erreur_bp', __name__)