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

def convert_objectid_to_str(data):
    if isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_objectid_to_str(value) for key, value in data.items()}
    elif isinstance(data, ObjectId):
        return str(data)
    return data

@students_bp.route('/stats', methods=['GET'])
@jwt_required()
def dashboard_stats():
    try:
        current_user_id = get_jwt_identity()

        current_user_id = ObjectId(current_user_id)

        # educational_data_cursor = db['educational_data'].find({
        #     "data.student_id": current_user_id
        # }, {
        #     "data": {
        #         "$elemMatch": {"student_id": current_user_id}
        #     }
        # })

        educational_data_cursor = db['educational_data'].aggregate([
            {
                "$match": {
                    "data.student_id": current_user_id
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "teacher_id": 1,
                    "dataset_type": 1,
                    "filename": 1,
                    "uploaded_at": 1,
                    "data": {
                        "$filter": {
                            "input": "$data",
                            "as": "item",
                            "cond": { "$eq": ["$$item.student_id", current_user_id] }
                        }
                    }
                }
            }
        ])

        educational_data_list1 = list(educational_data_cursor)

        educational_data_list = convert_objectid_to_str(educational_data_list1)

        return jsonify({
            "educational_data": educational_data_list
        })

    except Exception as e:
        return jsonify({"error": f"Error retrieving stats: {str(e)}"}), 500

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
        age = data.get("age")
        gender = data.get("gender")
        teacher_id = data.get("teacher_id")
        role = data.get("role")

        if not all([first_name, last_name, email, password , age , gender]):
            return jsonify({"error": "All fields (first_name, last_name, email, password , age , gender) are required."}), 400

        if users_collection.find_one({"email": email}):
            return jsonify({"error": f"Student with email '{email}' already exists."}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        current_time = datetime.utcnow()

        student_data = {
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
            "email": email.strip(),
            "password": hashed_password.decode('utf-8'),
            "age" : age.strip(),
            "gender" : gender.strip(),
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

        subject = "Welcome to the Edutics"
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
        age = data.get("age", student.get("age"))
        gender = data.get("gender", student.get("gender"))
        password = data.get("password", None)

        update_data = {
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
            "email": email.strip(),
            "age": age.strip(),
            "gender": gender.strip(),
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

        educational_data_cursor = db['educational_data'].aggregate([
            {
                "$match": {
                    "data.student_id": ObjectId(str(student['_id']))
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "teacher_id": 1,
                    "dataset_type": 1,
                    "filename": 1,
                    "uploaded_at": 1,
                    "data": {
                        "$filter": {
                            "input": "$data",
                            "as": "item",
                            "cond": { "$eq": ["$$item.student_id", ObjectId(str(student['_id']))] }
                        }
                    }
                }
            }
        ])

        educational_data_list1 = list(educational_data_cursor)

        educational_data_list = convert_objectid_to_str(educational_data_list1)

        if not student:
            return jsonify({"error": "Student not found or not associated with the current teacher."}), 404

        student["_id"] = str(student["_id"])
        student["teacher_id"] = str(student["teacher_id"])
        student["role"] = str(student["role"])

        return jsonify({"message": "Student details fetched successfully.", "student": student , "educational_data_list" : educational_data_list}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

