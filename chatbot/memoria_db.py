import sqlite3
from datetime import datetime

def crear_base():
    conn = sqlite3.connect('mate_memoria.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id TEXT,
            mensaje TEXT,
            respuesta TEXT,
            fecha TEXT
        )
    ''')
    conn.commit()
    conn.close()

def guardar_interaccion(empresa_id, mensaje, respuesta):
    conn = sqlite3.connect('mate_memoria.db')
    c = conn.cursor()
    fecha = datetime.now().isoformat()
    c.execute('''
        INSERT INTO mensajes (empresa_id, mensaje, respuesta, fecha)
        VALUES (?, ?, ?, ?)
    ''', (empresa_id, mensaje, respuesta, fecha))
    conn.commit()
    conn.close()

def obtener_historial(empresa_id):
    conn = sqlite3.connect('mate_memoria.db')
    c = conn.cursor()
    c.execute('''
        SELECT mensaje, respuesta FROM mensajes
        WHERE empresa_id = ?
        ORDER BY id ASC
    ''', (empresa_id,))
    historial = c.fetchall()
    conn.close()
    return historial