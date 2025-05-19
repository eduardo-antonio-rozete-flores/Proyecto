
import sqlite3
import os

# Define la database path
DB_PATH = os.path.join("MGF", "gastos.db")

def create_database():
    """Creates the database and necessary tables if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Connecta a la database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create  table de ingresos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingresos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            monto REAL NOT NULL,
            descripcion TEXT,
            usuario TEXT,
            notas TEXT
        )
    """)
    
    # Create  tabla gastos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            categoria TEXT NOT NULL,
            monto REAL NOT NULL,
            descripcion TEXT,
            usuario TEXT,
            notas TEXT
        )
    """)
    
   
    conn.commit()
    conn.close()

def connect_db():
    """Establishes a connection to the database."""
    return sqlite3.connect(DB_PATH)

if __name__ == "__main__":
    create_database()
    print(f"Database initialized at {DB_PATH}")
