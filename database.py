import sqlite3
import hashlib

DB_NAME = "mina_network.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabela de Usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('Admin', 'Avançado', 'Leitura'))
        )
    ''')
    
    # Tabela de Equipamentos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            ip TEXT UNIQUE NOT NULL,
            setor TEXT,
            tipo TEXT
        )
    ''')
    
    # Usuário Admin Padrão (se não existir nenhum)
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        admin_pass = hash_password("admin123")
        cursor.execute("INSERT INTO usuarios (username, password, role) VALUES (?, ?, ?)",
                       ("admin", admin_pass, "Admin"))
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
