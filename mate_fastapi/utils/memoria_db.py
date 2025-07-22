# memoria_db.py

import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def crear_base():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS memoria_conversacion (
                id SERIAL PRIMARY KEY,
                empresa_id TEXT NOT NULL,
                mensaje TEXT NOT NULL,
                respuesta TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        print("🧠 Tabla de memoria lista.")
    except Exception as e:
        print("❌ Error al crear tabla:", e)


def guardar_interaccion(empresa_id, mensaje, respuesta):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO memoria_conversacion (empresa_id, mensaje, respuesta)
            VALUES (%s, %s, %s)
        """, (empresa_id, mensaje, respuesta))
        conn.commit()
        conn.close()
    except Exception as e:
        print("❌ Error al guardar interacción:", e)


def obtener_historial(empresa_id, limite=10):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            SELECT mensaje, respuesta
            FROM memoria_conversacion
            WHERE empresa_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """, (empresa_id, limite))
        resultados = cur.fetchall()
        conn.close()
        return list(reversed(resultados))  # Orden cronológico
    except Exception as e:
        print("❌ Error al obtener historial:", e)
        return []