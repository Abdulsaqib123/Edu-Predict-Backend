from flask import Blueprint, request, jsonify
from bson import ObjectId
from models.db import db
from flask_jwt_extended import jwt_required, get_jwt_identity
import pandas as pd

upload_bp = Blueprint('uploads', __name__)

@upload_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """
    API endpoint for teachers to upload diverse educational datasets.
    Supports academic records, student demographics, LMS data, and attendance records.
    """
    try:
        current_teacher_id = get_jwt_identity()

        if 'file' not in request.files:
            return jsonify({"message": "No file uploaded"}), 400

        file = request.files['file']

        if file.filename.endswith('.csv'):
            data = pd.read_csv(file)
        elif file.filename.endswith('.xlsx'):
            data = pd.read_excel(file)
        else:
            return jsonify({"message": "Unsupported file format. Only CSV and Excel files are allowed."}), 400

        column_sets = {
            "academic_records": {"student_id", "subject", "grade"},
            "student_demographics": {"student_id", "name", "age", "gender"},
            "lms_data": {"student_id", "module", "progress", "score"},
            "attendance_records": {"student_id", "date", "attendance_status"}
        }

        dataset_type = None
        for data_type, required_columns in column_sets.items():
            if required_columns.issubset(data.columns):
                dataset_type = data_type
                break

        if not dataset_type:
            return jsonify({"message": "Invalid file format. Columns do not match any known dataset types."}), 400

        records = data.to_dict(orient='records')
        for record in records:
            record["teacher_id"] = ObjectId(current_teacher_id)

            # Convert student_id to ObjectId if it is a valid ID
            if 'student_id' in record:
                try:
                    record["student_id"] = ObjectId(record["student_id"])
                except Exception as e:
                    return jsonify({"message": f"Invalid student_id format: {str(e)}"}), 400

        file_record = {
            "teacher_id": ObjectId(current_teacher_id),
            "dataset_type": dataset_type,
            "filename": file.filename,
            "data": records
        }

        db['educational_data'].insert_one(file_record)

        return jsonify({
            "message": f"File uploaded and {dataset_type} data processed successfully."
        }), 200

    except pd.errors.EmptyDataError:
        return jsonify({"message": "The uploaded file is empty."}), 400

    except KeyError as e:
        return jsonify({"message": f"Missing required data: {str(e)}"}), 400

    except Exception as e:
        return jsonify({"message": f"Error processing file: {str(e)}"}), 500