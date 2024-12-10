from .db import db
from bson import ObjectId

roles_collection = db['roles']

class Role:
    def find(name=None):
        if name:
            return list(roles_collection.find({"name": name}, {"_id": 0}))
        else:
            return list(roles_collection.find({}, {"_id": 0}))

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
