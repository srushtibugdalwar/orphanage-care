from app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        try:
            print("Attempting to add 'email' column to 'caretaker' table...")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE caretaker ADD COLUMN email VARCHAR(120) UNIQUE AFTER username"))
                conn.commit()
            print("Successfully added 'email' column.")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("Column 'email' already exists.")
            else:
                print(f"Error migrating database: {e}")

if __name__ == "__main__":
    migrate()
