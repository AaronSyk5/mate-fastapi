import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables del entorno
load_dotenv()

# Obtener URL de la base de datos desde .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Función base para obtener conexión
def obtener_conexion():
    return psycopg2.connect(DATABASE_URL)

# 🟢 Ingresos del mes actual
def obtener_ingresos_mes(empresa_id):
    conn = obtener_conexion()
    cur = conn.cursor()

    cur.execute("""
        SELECT COALESCE(SUM(monto), 0)
        FROM finanzas
        WHERE empresa_id = %s
        AND tipo_movimiento = 'Ingreso'
        AND DATE_TRUNC('month', fecha) = DATE_TRUNC('month', CURRENT_DATE)
    """, (empresa_id,))

    total = cur.fetchone()[0]
    conn.close()
    return total

# 🔴 Egresos del día actual
def obtener_egresos_dia(empresa_id):
    conn = obtener_conexion()
    cur = conn.cursor()

    cur.execute("""
        SELECT COALESCE(SUM(monto), 0)
        FROM finanzas
        WHERE empresa_id = %s
        AND tipo_movimiento = 'Egreso'
        AND fecha::date = CURRENT_DATE
    """, (empresa_id,))

    total = cur.fetchone()[0]
    conn.close()
    return total

# 📊 Flujo neto del mes (ingresos - egresos)
def obtener_flujo_mensual(empresa_id):
    conn = obtener_conexion()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            COALESCE(SUM(CASE WHEN tipo_movimiento = 'Ingreso' THEN monto ELSE 0 END), 0) -
            COALESCE(SUM(CASE WHEN tipo_movimiento = 'Egreso' THEN monto ELSE 0 END), 0) AS flujo
        FROM finanzas
        WHERE empresa_id = %s
        AND DATE_TRUNC('month', fecha) = DATE_TRUNC('month', CURRENT_DATE)
    """, (empresa_id,))

    flujo = cur.fetchone()[0]
    conn.close()
    return flujo
# 🗓️ Últimos 7 días de ingresos y egresos