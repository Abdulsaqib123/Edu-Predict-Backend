from flask import Blueprint, request, jsonify
from bson import ObjectId
from models.db import db
from flask_jwt_extended import jwt_required, get_jwt_identity
import pandas as pd

upload_bp = Blueprint('uploads', __name__)

@upload_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    current_user = get_jwt_identity()
    if 'file' not in request.files:
        return jsonify({"message": "No file uploaded"}), 400

    file = request.files['file']
    try:
        # Handle file based on type
        if file.filename.endswith('.csv'):
            data = pd.read_csv(file)
        elif file.filename.endswith('.xlsx'):
            data = pd.read_excel(file)
        elif file.filename.endswith('.json'):
            data = pd.read_json(file)
        else:
            return jsonify({"message": "Unsupported file format"}), 400

        if not set(["student_id", "name", "attendance", "grade"]).issubset(data.columns):
            return jsonify({"message": "Invalid file format. Missing required columns."}), 400

        file_record = {
            "user_id" : ObjectId(current_user),
            "filename": file.filename,
            "data": data.to_dict(orient='records')
        }

        db['educational_data'].insert_one(file_record)
        return jsonify({"message": "File uploaded and data processed successfully"}), 200

    except Exception as e:
        return jsonify({"message": f"Error processing file: {str(e)}"}), 500