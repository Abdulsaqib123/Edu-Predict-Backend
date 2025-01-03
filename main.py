
from flask import Flask
from routes import register_routes
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from flask_cors import CORS

app = Flask(__name__)

CORS(app)
app.config['JWT_SECRET_KEY'] = '1340af4a470821b23ffcb1ea41b2fee14190d70ff7eacc283007db1a45e4f88f8e683a64051ac47ea2d20c1806ac59315e5d1ecca0007600e1c01fbfdf389f62'

client = MongoClient('mongodb://localhost:27017/')
db = client['edu_predict'] 

JWTManager(app)

register_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
