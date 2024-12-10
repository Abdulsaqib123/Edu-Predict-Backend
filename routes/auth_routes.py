from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from werkzeug.security import check_password_hash
from models.db import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Fetch user from the database by email
    user = db.users.find_one({"email": email})
    
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    
    # Check if the password is correct
    hashed_password = user.get('password')
    if not hashed_password or not check_password_hash(hashed_password, password):
        return jsonify({"error": "Invalid credentials"}), 401

    # Generate JWT token
    token = create_access_token(identity={"email": email, "role": user.get('role')})
    return jsonify({"access_token": token}), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti'] 
    db.blacklist.insert_one({"jti": jti})
    return jsonify({"msg": "Successfully logged out"}), 200
