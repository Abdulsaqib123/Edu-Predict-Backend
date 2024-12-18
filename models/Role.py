from .db import db
from bson import ObjectId

roles_collection = db['roles']

class Role:
    def find(name=None):
        query = {"name": name} if name else {}
        roles = roles_collection.find(query)
        return [Role.serialize_role(role) for role in roles]

    @staticmethod
    def find_by_id(role_id):
        _id = ObjectId(role_id)
        return roles_collection.find_one({"_id": _id})

    @staticmethod
    def create(name):
        if roles_collection.find_one({"name": name}):
            raise ValueError(f"Role '{name}' already exists.")
        roles_collection.insert_one({"name": name})

    @staticmethod
    def update(role_id, new_name):
        _id = ObjectId(role_id)
        result = roles_collection.update_one({"_id": _id}, {"$set": {"name": new_name}})
        if result.matched_count == 0:
            raise ValueError(f"Role with ID '{role_id}' not found.")

    @staticmethod
    def delete_by_id(role_id):
        _id = ObjectId(role_id)
        result = roles_collection.delete_one({"_id": _id})
        if result.deleted_count == 0:
            raise ValueError(f"Role with ID '{role_id}' not found.")

    @staticmethod
    def serialize_role(role):
        """Convert MongoDB document to a serializable dictionary."""
        role["_id"] = str(role["_id"])
        return role
