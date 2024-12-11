from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
import bcrypt
from bson import ObjectId
from models.db import db

auth_bp = Blueprint('auth', __name__)

def serialize_user(user):
    if not user:
        return None
    user["_id"] = str(user["_id"])
    return user

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Fetch user from the database
    user = db.users.find_one({"email": email})
    
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    
    # Check hashed password
    hashed_password = user.get('password')
    if not hashed_password or not bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
        return jsonify({"error": "Invalid credentials"}), 401

    # Convert ObjectId to string for JSON compatibility
    user["_id"] = str(user["_id"])

    # Generate the token
    token = create_access_token(identity={
        "id": user["_id"],
        "email": email,
        "role": user.get('role')
    })

    # Return the response
    return jsonify({"access_token": token}), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti'] 
    db.blacklist.insert_one({"jti": jti})
    return jsonify({"msg": "Successfully logged out"}), 200
