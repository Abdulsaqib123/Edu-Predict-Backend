from seeders.seed_roles import seed_roles

if __name__ == "__main__":
    print("Seeding roles into the database...")
    seed_roles()
    print("Seeding complete.")
