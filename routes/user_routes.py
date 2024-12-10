from flask import Blueprint, request, jsonify
from models.db import db
from models.user import User
from models.role import Role
from bson import ObjectId

user_bp = Blueprint('users', __name__)

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
        User.create(first_name, last_name, email, password, role)
        return jsonify({"message": "User created successfully."}), 201
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
def single_user(user_id):
    try:
        user_id = ObjectId(user_id)
    except Exception:
        return jsonify({"message": "Invalid user ID."}), 400

    try:
        user = User.find_by_id(user_id)
        # if not user:
        #     return jsonify({"message": "User not found."}), 404
        
        user["_id"] = str(user["_id"])
        return jsonify({"message": "User found successfully.", "user": user}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

