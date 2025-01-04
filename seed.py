from seeders.seed_roles import seed_roles
from seeders.seed_users import seed_users

if __name__ == "__main__":
    print("Seeding roles into the database...")
    seed_roles()
    print("Seeding admin user into the database...")
    seed_users()
    print("Seeding complete.")
