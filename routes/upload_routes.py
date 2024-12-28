from flask import Blueprint, request, jsonify
from bson import ObjectId
from models.db import db
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

upload_bp = Blueprint('uploads', __name__)

def process_data(data, dataset_type):
    """
    Handle missing data and detect anomalies in the dataset.
    """
    if dataset_type == "academic_records":
        data['grade'] = pd.to_numeric(data['grade'], errors='coerce').fillna("Incomplete")

        data['grade'] = data['grade'].apply(lambda x: "Incomplete" if isinstance(x, float) and pd.isna(x) else x)

    elif dataset_type == "student_demographics":
        data['age'] = pd.to_numeric(data['age'], errors='coerce')
        data['age'] = data['age'].fillna(data['age'].mean())

    anomalies = data[(data.select_dtypes(include=['number']) < 0).any(axis=1)]
    if not anomalies.empty:
        print("Anomalies detected:", anomalies)

    return data

def identify_dataset_type(data, column_sets):
    """
    Determine the dataset type based on column matches.
    """
    for dataset_type, required_columns in column_sets.items():
        if required_columns.issubset(data.columns):
            return dataset_type
    return None

def parallel_process_data(data, dataset_type, num_threads=4):
    """
    Split data for parallel processing and process them concurrently.
    """
    num_threads = min(num_threads, len(data))

    chunk_size = max(1, len(data) // num_threads)
    chunks = [data.iloc[i:i+chunk_size] for i in range(0, len(data), chunk_size)]

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        processed_chunks = list(executor.map(lambda chunk: process_chunk(chunk, dataset_type), chunks))

    return pd.concat(processed_chunks, ignore_index=True)

def process_chunk(chunk, dataset_type):
    """
    Process individual chunk of data.
    """
    return process_data(chunk, dataset_type)

@upload_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """
    API endpoint for uploading datasets and processing them.
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

        dataset_type = identify_dataset_type(data, column_sets)
        if not dataset_type:
            return jsonify({"message": "Invalid file format. Columns do not match any known dataset types."}), 400

        processed_data = parallel_process_data(data, dataset_type)

        records = processed_data.to_dict(orient='records')
        for record in records:
            record["teacher_id"] = ObjectId(current_teacher_id)

            if 'student_id' in record:
                try:
                    record["student_id"] = ObjectId(record["student_id"])
                except Exception as e:
                    return jsonify({"message": f"Invalid student_id format: {str(e)}"}), 400

        db['educational_data'].insert_one({
            "teacher_id": ObjectId(current_teacher_id),
            "dataset_type": dataset_type,
            "filename": file.filename,
            "data": records,
            "uploaded_at": datetime.utcnow()
        })

        student_ids = [record['student_id']]
        notifications = []
        for student_id in student_ids:
            notifications.append({
                "user_id": student_id,
                "teacher_id": ObjectId(current_teacher_id),
                "dataset_type": dataset_type,
                "message": f"A new {dataset_type} file has been uploaded by your teacher.",
                "read": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            })

        db['notifications'].insert_many(notifications)

        return jsonify({
            "message": f"{dataset_type.capitalize()} file uploaded and processed successfully."
        }), 200

    except pd.errors.EmptyDataError:
        return jsonify({"message": "The uploaded file is empty."}), 400

    except KeyError as e:
        return jsonify({"message": f"Missing required data: {str(e)}"}), 400

    except Exception as e:
        return jsonify({"message": f"Error processing file: {str(e)}"}), 500
