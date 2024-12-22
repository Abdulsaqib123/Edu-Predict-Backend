from models.db import db
from flask import Blueprint, request, jsonify
from bson import ObjectId

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
def dashboard_stats():
    try:

        total_roles = db["roles"].count_documents({})
        total_users = db["users"].count_documents({})

        return jsonify({"roles" : total_roles , "users" : total_users}), 200

    except Exception as e:
        return jsonify({"message": f"Error fetching summary: {str(e)}"}), 500