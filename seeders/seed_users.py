from bson import ObjectId
from models.db import db

def seed_users():
    users = [
        {"_id": ObjectId("676331320645db08dc0587b0") ,"role" : ObjectId("67587c8e74cea1767a2e0581"), "first_name": "Admin", "last_name": "Divi", "email" : "admin@divistack.com" , "password" : "$2b$12$uwYmrogixNUqW/wKdMC3beNlYXAtUM33GWcAVG577bFhmbrXev.0W" , "created_at" : "2024-12-18T20:31:46.713+00:00" , "updated_at" : "2024-12-18T20:31:46.713+00:00"},
    ]
    for user in users:
        try:
            db.users.insert_one(user)
            print(f"Seeded user: {user['email']}")
        except ValueError as e:
            print(e)
