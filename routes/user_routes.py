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
    email = request.args.get('email')
    role_id = request.args.get('role_id')

    if role_id:
            try:
                role_id = ObjectId(role_id)
            except Exception:
                return jsonify({"message": "Invalid role ID"}), 400

    users = User.find(email=email, role_id=role_id)
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

        role_name = role_data.get("name").capitalize() if role_data else "User"
        success_message = f"{role_name} account registered successfully."
        return jsonify({"message": success_message, "user": user}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@user_bp.route('/edit/<string:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        user_id = ObjectId(user_id) 
    except Exception:
        return jsonify({"message": "Invalid user ID."}), 400

    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    try:

        role_data = db.roles.find_one({"_id": ObjectId(role)})
        role_name = role_data.get("name").capitalize() if role_data else "User"
        message = f"{role_name} account updated successfully."
        user = User.update(user_id , first_name, last_name , email , password , role)

        return jsonify({"message": message, "user": user}), 201
        # return jsonify({"message": "User updated successfully."}), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@user_bp.route('/delete/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user_id = ObjectId(user_id)
    except Exception:
        return jsonify({"error": "Invalid user ID."}), 400

    user = db.users.find_one({"_id": user_id})
    if not user:
        return jsonify({"error": "User not found."}), 404

    try:
        role_id = user.get("role")
        role = db.roles.find_one({"_id": ObjectId(role_id)}) if role_id else None
        role_name = role.get("name", "User").lower() if role else "user"

        User.delete_by_id(user_id)

        message = f"{role_name.capitalize()} account deleted successfully."
        return jsonify({"message": message}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

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
        if "teacher_id" in user and user["teacher_id"] is not None:
            user["teacher_id"] = str(user['teacher_id'])
        else:
            user["teacher_id"] = None
        if not user:
            return jsonify({"message": "User not found."}), 404
        
        return jsonify({"message": "User found successfully.", "user": user}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

