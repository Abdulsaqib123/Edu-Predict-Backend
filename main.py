from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from pymongo import MongoClient

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'rjfkspirlsnklfro'

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client.edu_predict
users_collection = db.users
roles_collection = db.roles

# User registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    if users_collection.find_one({'email': email}):
        return jsonify({"error": "User already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = {'email': email, 'password': hashed_password, 'role': role}
    users_collection.insert_one(user)
    return jsonify({"message": "User registered successfully"}), 201

# User login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = users_collection.find_one({'email': email})
    if not user or not bcrypt.check_password_hash(user['password'], password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity={'email': user['email'], 'role': user['role']})
    return jsonify({"access_token": access_token}), 200

# Protected route
@app.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    return jsonify({"message": "Welcome to the Dashboard!"}), 200

if __name__ == '__main__':
    app.run(debug=True)
