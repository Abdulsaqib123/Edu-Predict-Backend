from flask import Blueprint, request, jsonify
from models.db import db
from models.role import Role
from flask_jwt_extended import jwt_required
from bson import ObjectId

role_bp = Blueprint('roles', __name__)

@role_bp.route('/create', methods=['POST'])
def create_role():
    data = request.json
    name = data.get('name')

    try:
        role = Role.create(name)
        return jsonify({"message": "Role created successfully."}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@role_bp.route('/index', methods=['GET'])
def get_roles():
    roles = Role.find()
    return jsonify({"roles": roles}), 200

@role_bp.route('/delete/<string:role_id>', methods=['DELETE'])
def delete_role(role_id):
    role_id = ObjectId(role_id) 
    try:
        Role.delete_by_id(role_id)
        return jsonify({"message": "Role deleted successfully."}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@role_bp.route('/show/<string:role_id>', methods=['GET'])
def find_role(role_id):
    role_id = ObjectId(role_id) 
    try:
        role = Role.find_by_id(role_id)
        role["_id"] = str(role["_id"])
        return jsonify({"message": "Role finded successfully.", "role" : role}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@role_bp.route('/update/<string:role_id>', methods=['PUT'])
def update_role(role_id):
    role_id = ObjectId(role_id) 
    data = request.json
    name = data.get('name')

    try:
        role = Role.update(role_id, name)
        return jsonify({"message": "Role updated successfully."}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400