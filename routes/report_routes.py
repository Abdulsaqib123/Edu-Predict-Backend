from flask import Blueprint, request, jsonify
from models.db import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime

reports_bp = Blueprint('reports', __name__)

reports_collection = db['reports']

@reports_bp.route('/index', methods=['GET'])
@jwt_required()
def get_reports():
    try:

        user_id = request.args.get('user_id')

        query = {}

        if user_id:
            if not ObjectId.is_valid(user_id):
                return jsonify({"message": "Invalid user_id parameter."}), 400
            query["user_id"] = ObjectId(user_id)

        reports = reports_collection.find(query)

        response = []
        for report in reports:
            teacher_data = db.users.find_one({"_id" : ObjectId(report["teacher_id"])})
            response.append({
                "_id": str(report["_id"]),
                "user_id": str(report["user_id"]),
                "teacher_id": str(report["teacher_id"]),
                "teacher" : {
                    "username" : teacher_data.get("first_name") + " " + teacher_data.get("last_name"),
                    "email" : teacher_data.get("email")
                },
                "file_name": report.get("file_name", False),
                "file_path": report.get("file_path", False),
                "created_at": report.get("created_at", "").isoformat() if report.get("created_at") else None
            })

        return jsonify({"message" : "Reports fetched successfully!", "reports": response}), 200

    except Exception as e:
        return jsonify({"message": f"Error retrieving reports: {str(e)}"}), 500