from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
import bcrypt
from bson import ObjectId
from models.db import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = db.users.find_one({"email": email})
    
        if not user:
            return jsonify({"message": "Invalid credentials"}), 401
    
        hashed_password = user.get('password')
        if not hashed_password or not bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            return jsonify({"message": "Invalid credentials"}), 401

        role = db.roles.find_one({"_id" : user.get("role")})

        if not role:
            return jsonify({"message": "Role not found for user"}), 404

        token = create_access_token(identity=str(user["_id"]))

        user['role'] = str(user["role"])
        user['_id'] = str(user['_id'])
        user["role"] = {
            "_id": str(role["_id"]),
            "name": role.get("name"),
        }

        return jsonify({
                "message": "Login successful!",
                "token": token,
                "user": user
            }), 200

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}),500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti'] 
    db.blacklist.insert_one({"jti": jti})
    return jsonify({"msg": "Successfully logged out"}), 200
