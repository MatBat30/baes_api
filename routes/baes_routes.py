# routes/baes_routes.py
from flask import Blueprint, request, jsonify, current_app
from flasgger import swag_from
from models.batiment import Batiment
from models import db


baes_bp = Blueprint('baes_bp', __name__)