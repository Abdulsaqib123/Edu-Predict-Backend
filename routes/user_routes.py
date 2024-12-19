from flask import Blueprint, request, jsonify
from models.db import db
from models.user import User
from models.role import Role
from bson import ObjectId
from models.db import db
from flask_jwt_extended import jwt_required

user_bp = Blueprint('users', __name__)

@user_bp.route('/index', methods=['GET'])
def get_users():
    users = User.find()
    return jsonify({"users": users}), 200

@user_bp.route('/create', methods=['POST'])
def create_user():
    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    if not all([first_name, last_name, email, password, role]):
        return jsonify({"error": "All fields are required."}), 400

    try:
        user = User.create(first_name, last_name, email, password, role)
        user["_id"] = str(user["_id"])
        role_data = db.roles.find_one({"_id": ObjectId(user["role"])})
        if role_data:
            user["role"] = {
                "_id": str(role_data["_id"]),
                "name": role_data.get("name"),
            }
        return jsonify({"message": "Account registered successfully.", "user": user}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@user_bp.route('/delete/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user_id = ObjectId(user_id) 
    except Exception:
        return jsonify({"message": "Invalid user ID."}), 400

    user = db.users.find_one({"_id": user_id})
    if not user:
        return jsonify({"message": "User not found."}), 404

    try:
        User.delete_by_id(user_id)
        return jsonify({"message": "User deleted successfully."}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@user_bp.route('/find/<string:user_id>', methods=['GET'])
@jwt_required()
def single_user(user_id):
    try:
        user_id = ObjectId(user_id)
    except Exception:
        return jsonify({"message": "Invalid user ID."}), 400

    try:
        user = User.find_by_id(user_id)
        user["_id"] = str(user["_id"])
        role_data = db.roles.find_one({"_id": ObjectId(user["role"])})
        user["role"] = {
                "_id": str(role_data["_id"]),
                "name": role_data.get("name"),
            }
        if not user:
            return jsonify({"message": "User not found."}), 404
        
        return jsonify({"message": "User found successfully.", "user": user}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

