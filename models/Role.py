from .db import db

roles_collection = db['roles']

class Role:
    @staticmethod
    def find_by_name(name):
        return roles_collection.find_one({"name": name})

    @staticmethod
    def find_all():
        return list(roles_collection.find({}, {"_id": 0}))

    @staticmethod
    def create(name):
        if roles_collection.find_one({"name": name}):
            raise ValueError(f"Role '{name}' already exists.")
        roles_collection.insert_one({"name": name})

    @staticmethod
    def delete_by_name(name):
        result = roles_collection.delete_one({"name": name})
        if result.deleted_count == 0:
            raise ValueError(f"Role '{name}' not found.")
