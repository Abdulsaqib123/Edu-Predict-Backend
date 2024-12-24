from flask import Blueprint, request, jsonify
from models.db import db
import bcrypt
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

students_bp = Blueprint('students', __name__)

users_collection = db['users']

@students_bp.route('/index', methods=['GET'])
@jwt_required()
def get_students_by_teacher():
    try:
        current_user_id = get_jwt_identity()
        teacher = users_collection.find_one({"_id": ObjectId(current_user_id)})

        students = users_collection.find({"role": ObjectId("67587c8e74cea1767a2e0583"), "teacher_id": ObjectId(current_user_id)})
        student_list = [
            {
                "_id": str(student["_id"]),
                "first_name": student["first_name"],
                "last_name": student["last_name"],
                "email": student["email"],
                "role": str(student["role"]),
                "teacher_id": str(student["teacher_id"]),
                "created_at" : student['created_at'],
                "updated_at" : student['updated_at'],
            }
            for student in students
        ]

        return jsonify({
            "message": "Students fetched successfully.",
            "students": student_list
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@students_bp.route('/create', methods=['POST'])
@jwt_required()
def create_student():
    try:

        current_user_id = get_jwt_identity()

        data = request.get_json()
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        password = data.get("password")
        teacher_id = data.get("teacher_id")
        role = data.get("role")

        if not all([first_name, last_name, email, password]):
            return jsonify({"message": "All fields (first_name, last_name, email, password) are required."}), 400

        if users_collection.find_one({"email": email}):
            return jsonify({"error": f"User with email '{email}' already exists."}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        current_time = datetime.utcnow()

        student_data = {
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
            "email": email.strip(),
            "password": hashed_password.decode('utf-8'),
            "role": ObjectId(role),
            "teacher_id": ObjectId(current_user_id),
            "created_at": current_time,
            "updated_at": current_time
        }

        users_collection.insert_one(student_data)

        send_student_email(email, first_name + " " + last_name, email, password)

        return jsonify({"message": "Student created successfully."}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def send_student_email(recipient_email, student_name, email, password):
    try:
        smtp_host = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "personalwork270@gmail.com"
        sender_password = "pgzxiozsffnldutq"

        subject = "Welcome to the Platform"
        body = f"""
        Hi {student_name},

        Welcome to the edutics! Here are your login credentials:

        Email: {email}
        Password: {password}

        Please log in and change your password for security purposes.

        Best regards,
        Your Team
        """

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())

        print(f"Email sent successfully to {recipient_email}")
    except Exception as e:
        print(f"Failed to send email to {recipient_email}. Error: {str(e)}")

@students_bp.route('/edit/<string:student_id>', methods=['PUT'])
@jwt_required()
def update_student(student_id):
    try:
        current_user_id = get_jwt_identity()
        teacher = users_collection.find_one({"_id": ObjectId(current_user_id)})

        student = users_collection.find_one({"_id": ObjectId(student_id), "teacher_id": ObjectId(current_user_id)})
        if not student:
            return jsonify({"error": "Student not found or not associated with the current teacher."}), 404

        data = request.json
        first_name = data.get("first_name", student.get("first_name"))
        last_name = data.get("last_name", student.get("last_name"))
        email = data.get("email", student.get("email"))
        password = data.get("password", None)

        update_data = {
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
            "email": email.strip(),
            "updated_at": datetime.utcnow(),
        }

        if password:
            update_data["password"] = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        users_collection.update_one({"_id": ObjectId(student_id)}, {"$set": update_data})

        return jsonify({"message": "Student updated successfully."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@students_bp.route('/delete/<string:student_id>', methods=['DELETE'])
@jwt_required()
def delete_student(student_id):
    try:
        current_user_id = get_jwt_identity()

        student = users_collection.find_one({"_id": ObjectId(student_id), "teacher_id": ObjectId(current_user_id)})

        if not student:
            return jsonify({"error": "Student not found or not associated with the current teacher."}), 404

        users_collection.delete_one({"_id": ObjectId(student_id)})

        return jsonify({"message": "Student deleted successfully."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@students_bp.route('/find/<string:student_id>', methods=['GET'])
@jwt_required()
def get_student_details(student_id):
    try:
        current_user_id = get_jwt_identity()
        teacher = users_collection.find_one({"_id": ObjectId(current_user_id)})

        student = users_collection.find_one({"_id": ObjectId(student_id), "teacher_id": ObjectId(current_user_id)})
        if not student:
            return jsonify({"error": "Student not found or not associated with the current teacher."}), 404

        student["_id"] = str(student["_id"])
        student["teacher_id"] = str(student["teacher_id"])
        student["role"] = str(student["role"])

        return jsonify({"message": "Student details fetched successfully.", "student": student}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

