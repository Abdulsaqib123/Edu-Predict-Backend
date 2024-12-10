from models.role import Role

def seed_roles():
    roles = [
        {"name": "admin",},
        {"name": "teacher"},
        {"name": "student"},
    ]
    for role in roles:
        try:
            Role.create(role['name'])
            print(f"Seeded role: {role['name']}")
        except ValueError as e:
            print(e)
