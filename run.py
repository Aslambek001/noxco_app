import os
from dotenv import load_dotenv, find_dotenv
from app import create_app

# Zoek en laad het .env bestand
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)
    print(f"DEBUG (run.py): .env loaded from: {dotenv_path}")
else:
    print("WARNING (run.py): .env file not found!")

# Debug output voor DATABASE_URL voor app creatie
print(f"DEBUG (run.py): DATABASE_URL from os.environ BEFORE create_app: {os.getenv('DATABASE_URL')}")

# Creëer de Flask applicatie
app = create_app()

if __name__ == '__main__':
    # Start de Flask ontwikkelingsserver
    app.run(debug=True, port=5001)


