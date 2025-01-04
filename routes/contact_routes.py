from flask import Blueprint, request, jsonify
from models.db import db
import bcrypt
from bson import ObjectId
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

contact_bp = Blueprint('contacts', __name__)

feedback_collection = db['feedback']

@contact_bp.route("/add", methods=["POST"])
def add_feedback():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        name = data.get("name")
        email = data.get("email")
        message = data.get("message")

        if not name or not email or not message:
            return jsonify({"message": "All fields are required!"}), 400

        feedback_data = {
            "user_id": ObjectId(user_id) if user_id != "unknown" else "unknown",
            "name": name,
            "email": email,
            "message": message,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        feedback_collection.insert_one(feedback_data)
        return jsonify({"message": "Feedback submitted successfully!"}), 201
    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500
