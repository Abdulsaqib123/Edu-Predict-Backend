from bson import ObjectId
from models.db import db

def seed_roles():
    roles = [
        {"_id": ObjectId("67587c8e74cea1767a2e0581") , "name": "admin",},
        {"_id": ObjectId("67587c8e74cea1767a2e0582") , "name": "teacher",},
        {"_id": ObjectId("67587c8e74cea1767a2e0583") , "name": "student",},
    ]
    for role in roles:
        try:
            db.roles.insert_one(role)
            print(f"Seeded role: {role['name']}")
        except ValueError as e:
            print(e)
