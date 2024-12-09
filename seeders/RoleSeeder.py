def seed_roles():
    roles = [
        {"name": "admin", "description": "Administrator with full access"},
        {"name": "teacher", "description": "Teacher with limited access to manage students"},
        {"name": "student", "description": "Student with access to educational resources"},
    ]

    for role in roles:
        if not roles_collection.find_one({"name": role["name"]}):
            roles_collection.insert_one(role)
            print(f"Seeded role: {role['name']}")
