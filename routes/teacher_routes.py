from models.db import db
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId

teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/stats', methods=['GET'])
@jwt_required()
def dashboard_stats():
    try:
        current_user_id = get_jwt_identity()
        print(current_user_id)
        total_students = db["users"].count_documents({"role" : ObjectId("67587c8e74cea1767a2e0583") , "teacher_id": ObjectId(current_user_id)})

        return jsonify({"students" : total_students}), 200

    except Exception as e:
        return jsonify({"message": f"Error fetching summary: {str(e)}"}), 500