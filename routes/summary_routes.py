from models.db import db
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId

summary_bp = Blueprint('summary', __name__)

@summary_bp.route('/data-ingestion', methods=['GET'])
@jwt_required()
def data_summary():
    try:
        user_id = ObjectId(get_jwt_identity())

        total_files = db['educational_data'].count_documents({"user_id": user_id})

        files = db['educational_data'].find({"user_id": user_id})

        file_summaries = []
        total_records = 0
        total_students = 0
        total_attendance = 0
        total_demographics = 0

        for file in files:
            data = file.get("data", [])
            total_records += len(data)
            total_students += len(set(record.get("student_id") for record in data))
            
            total_attendance += len(set(record.get("attendance" , 0) for record in data))

            total_demographics += len(set(record.get("demographics") for record in data if "demographics" in record))

            file_summary = {
                "file_id": str(file["_id"]),
                "filename": file["filename"],
                "total_records": len(data),
                "total_students": len(set(record.get("student_id") for record in data)),
                "total_attendance": len(set(record.get("attendance" , 0) for record in data)),
                "total_demographics": len(set(record.get("demographics") for record in data if "demographics" in record))
            }
            file_summaries.append(file_summary)

        print("Total Attendance : ", total_attendance)
        summary = {
            "total_files": total_files,
            "files": file_summaries,
            "total_records" : total_records,
            "total_students" : total_students,
            "total_attendance" : total_attendance,
            "total_demographics" : total_demographics
        }

        return jsonify({"summary" : summary}), 200
    except Exception as e:
        return jsonify({"message": f"Error fetching summary: {str(e)}"}), 500