from flask import Blueprint, request, jsonify,url_for
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
import bcrypt
from bson import ObjectId
from models.db import db
from datetime import timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid
import smtplib
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'personalwork270@gmail.com'
SMTP_PASSWORD = 'pgzxiozsffnldutq'
FRONTEND_URL = 'http://localhost:3000'

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

        token = create_access_token(identity=str(user["_id"]), expires_delta=timedelta(days=1))

        user['role'] = str(user["role"])
        user['_id'] = str(user['_id'])
        user["role"] = {
            "_id": str(role["_id"]),
            "name": role.get("name"),
        }
        if "teacher_id" in user and user["teacher_id"] is not None:
            user["teacher_id"] = str(user['teacher_id'])
        else:
            user["teacher_id"] = None

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
    return jsonify({"message": "Successfully logged out"}), 200


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        email = data.get('email')
        user = db.users.find_one({"email": email})

        if not user:
            return jsonify({"message": "User not found"}), 404

        reset_token = str(uuid.uuid4())
        reset_token_expires = datetime.utcnow() + timedelta(hours=1)

        db.users.update_one(
            {"email": email},
            {"$set": {"resetPasswordToken": reset_token, "resetPasswordExpires": reset_token_expires}}
        )

        # Send reset link via email
        reset_url = f"{FRONTEND_URL}/reset-password/{reset_token}"
        subject = "Password Reset Request"
        body = f"Click the link to reset your password: {reset_url}"

        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, email, msg.as_string())
        server.quit()

        return jsonify({"message": "Password reset email sent"}), 200

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    try:
        data = request.get_json()
        new_password = data.get('new_password')

        user = db.users.find_one({"resetPasswordToken": token})

        if not user or user.get("resetPasswordExpires") < datetime.utcnow():
            return jsonify({"message": "Token is invalid or expired"}), 400

        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"password": hashed_password, "resetPasswordToken": None, "resetPasswordExpires": None}}
        )

        return jsonify({"message": "Password successfully reset"}), 200

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500
