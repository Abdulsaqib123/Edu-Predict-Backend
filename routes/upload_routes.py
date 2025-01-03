from flask import Blueprint, request, jsonify
from bson import ObjectId
from models.db import db
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import os
from werkzeug.utils import secure_filename
import pickle

UPLOAD_FOLDER = './uploads'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, '..', 'models', 'kmeans_model_attributes.pkl')  # Update to pickle model

def load_model():
    """
    Load the pre-trained model from the given path using pickle.
    """
    model_filename = MODEL_PATH  # Path to the saved model file
    if not os.path.exists(model_filename):
        raise FileNotFoundError(f"Model file not found: {model_filename}")

    # Load the model using pickle
    with open(model_filename, 'rb') as file:
        model = pickle.load(file)

    # Ensure the model has the 'predict' method (or 'transform' if you're using clustering)
    # if not hasattr(model, 'predict') and not hasattr(model, 'transform'):
    #     raise ValueError("Loaded object does not have a 'predict' or 'transform' method")
    
    return model


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

        # Updated column sets for handling the CSV file format
        column_sets = {
            "academic_records": {"student_id", "first_name", "last_name", "email", "age", "gender", "module", "attendance_status", "teacher_id", "created_at", "updated_at", "grade", "progress", "score", "date", "english", "urdu", "math", "science", "social_studies", "computer", "literature"},
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

        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        db['educational_data'].insert_one({
            "teacher_id": ObjectId(current_teacher_id),
            "dataset_type": dataset_type,
            "filename": file.filename,
            "data": records,
            "uploaded_at": datetime.utcnow()
        })

        student_ids = set(record['student_id'] for record in records)  # Collect all unique student IDs
        notifications = []
        reports = []

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

            reports.append({
                "user_id": student_id,
                "teacher_id": ObjectId(current_teacher_id),
                "file_name": filename,
                "file_path": file_path,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            })

        db['notifications'].insert_many(notifications)
        db['reports'].insert_many(reports)

        return jsonify({
            "message": f"{dataset_type.capitalize()} file uploaded and processed successfully."
        }), 200

    except pd.errors.EmptyDataError:
        return jsonify({"message": "The uploaded file is empty."}), 400

    except KeyError as e:
        return jsonify({"message": f"Missing required data: {str(e)}"}), 400

    except Exception as e:
        return jsonify({"message": f"Error processing file: {str(e)}"}), 500


@upload_bp.route('/predict/filepath', methods=['POST'])
def predict_from_filepath():
    try:
        # Load the trained model
        model = load_model()

        # Get file path from request body
        data = request.get_json()
        # file_path = data.get("file_path")
        file_path = "uploads/student_data (1).csv"

        if not file_path or not os.path.exists(file_path):
            return jsonify({"message": "Invalid or missing file path"}), 400

        # Load data from the provided file path
        if file_path.endswith('.csv'):
            data = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            data = pd.read_excel(file_path)
        else:
            return jsonify({"message": "Unsupported file format. Only CSV and Excel files are allowed."}), 400

        # Optional: Process data if necessary
        processed_data = process_data(data, "academic_records")

        # Prepare data for prediction (numeric data only)
        features = processed_data.select_dtypes(include=['number']).fillna(0)

        # Make predictions
        predictions = model.transform(features)  # Use transform if the model is a clustering model
        # OR if the model is a classifier/regressor, use model.predict(features)

        # Add predictions to the results dataframe
        results = processed_data.copy()
        results['prediction'] = predictions.tolist()

        return jsonify({"predictions": results.to_dict(orient='records')}), 200

    except Exception as e:
        return jsonify({"message": f"Error during prediction: {str(e)}"}), 500
