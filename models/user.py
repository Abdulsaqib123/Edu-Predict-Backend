from .db import db
from bson.objectid import ObjectId
import bcrypt
from datetime import datetime

users_collection = db['users']
roles_collection = db['roles']

class User:
    def find(email=None, role_id=None):
        query = {}
        if email:
            query["email"] = email
        if role_id:
            query["role"] = role_id
        users = users_collection.find(query)
        print("Role ID : ", role_id)
        return [User.serialize_user(user) for user in users]

    @staticmethod
    def find_by_id(user_id):
        _id = ObjectId(user_id)
        return users_collection.find_one({"_id": _id})

    @staticmethod
    def create(first_name, last_name, email, password, role):
        if not all([first_name, last_name, email, password]):
            raise ValueError("All fields (first_name, last_name, email, password) are required.")

        if not isinstance(email, str) or "@" not in email:
            raise ValueError("Invalid email address.")

        if users_collection.find_one({"email": email}):
            raise ValueError(f"User with email '{email}' already exists.")

        if not ObjectId.is_valid(role):
            raise ValueError("Invalid role ID.")

        role_data = roles_collection.find_one({"_id": ObjectId(role)})
        if not role_data:
            raise ValueError(f"Role with ID '{role}' does not exist.")

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        current_time = datetime.utcnow()

        user_data = {
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
            "email": email.strip(),
            "password": hashed_password.decode('utf-8'),
            "role": ObjectId(role),
            "created_at": current_time,
            "updated_at": current_time,
        }
        users_collection.insert_one(user_data)

        return user_data

    @staticmethod
    def update(user_id , first_name , last_name , email , password , role):
        if not all([first_name, last_name, email, role]):
            raise ValueError("All fields (first_name, last_name, email, role) are required.")

        if not isinstance(email, str) or "@" not in email:
            raise ValueError("Invalid email address.")

        if not ObjectId.is_valid(role):
            raise ValueError("Invalid role ID.")

        role_data = roles_collection.find_one({"_id": ObjectId(role)})
        if not role_data:
            raise ValueError(f"Role with ID '{role}' does not exist.")

        update_data = {
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
            "email": email.strip(),
            "role": ObjectId(role),
            "updated_at": datetime.utcnow(),
        }

        if password:
            update_data["password"] = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        result = users_collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": update_data},
            return_document=True
        )

        if not result:
            raise ValueError(f"User with ID '{user_id}' not found.")

        return User.serialize_user(result)

    @staticmethod
    def delete_by_id(user_id):
        _id = ObjectId(user_id)
        result = users_collection.delete_one({"_id": _id})
        if result.deleted_count == 0:
            raise ValueError(f"User with ID '{user_id}' not found.")

    @staticmethod
    def serialize_user(user):
        """Convert MongoDB document to a serializable dictionary."""
        user["_id"] = str(user["_id"])
        user["role"] = str(user['role'])
        if "teacher_id" in user and user["teacher_id"] is not None:
            user["teacher_id"] = str(user['teacher_id'])
        else:
            user["teacher_id"] = None
        return user