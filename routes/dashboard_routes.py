from models.db import db
from flask import Blueprint, request, jsonify
from bson import ObjectId

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
def dashboard_stats():
    try:

        total_roles = db["roles"].count_documents({})
        total_students = db["users"].count_documents({"role" : ObjectId("67587c8e74cea1767a2e0583")})
        total_teachers = db["users"].count_documents({"role" : ObjectId("67587c8e74cea1767a2e0582")})

        return jsonify({"roles" : total_roles , "students" : total_students , "teachers" : total_teachers}), 200

    except Exception as e:
        return jsonify({"message": f"Error fetching summary: {str(e)}"}), 500