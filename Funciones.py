import sqlite3
import os
import csv
from datetime import datetime, timedelta

DB_PATH = os.path.join("MGF", "gastos.db")

def conectar_db():
    """Establece conexión con la base de datos"""
    return sqlite3.connect(DB_PATH)

def agregar_ingreso(fecha, monto, descripcion, usuario="Familia", notas=""):
    """Agrega un nuevo ingreso a la base de datos"""
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO ingresos (fecha, monto, descripcion, usuario, notas) 
            VALUES (?, ?, ?, ?, ?)
        ''', (fecha, monto, descripcion, usuario, notas))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error al agregar ingreso: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def agregar_gasto(fecha, categoria, monto, descripcion, usuario="Familia", notas=""):
    """Agrega un nuevo gasto a la base de datos"""
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO gastos (fecha, categoria, monto, descripcion, usuario, notas) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (fecha, categoria, monto, descripcion, usuario, notas))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error al agregar gasto: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def obtener_ingresos(periodo="Todos"):
    """Obtiene ingresos filtrados por período"""
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        start, end = calculate_period_dates(periodo)
        cursor.execute('''
            SELECT fecha, monto, descripcion, usuario 
            FROM ingresos 
            WHERE fecha BETWEEN ? AND ?
            ORDER BY fecha DESC
        ''', (start, end))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error al obtener ingresos: {e}")
        return []
    finally:
        conn.close()

def obtener_gastos(periodo="Todos"):
    """Obtiene gastos filtrados por período"""
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        start, end = calculate_period_dates(periodo)
        cursor.execute('''
            SELECT fecha, categoria, monto, descripcion, usuario 
            FROM gastos 
            WHERE fecha BETWEEN ? AND ?
            ORDER BY fecha DESC
        ''', (start, end))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error al obtener gastos: {e}")
        return []
    finally:
        conn.close()

def obtener_total_gastos(periodo="Todos"):
    """Calcula el total de gastos para un período"""
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        start, end = calculate_period_dates(periodo)
        cursor.execute('''
            SELECT SUM(monto) 
            FROM gastos 
            WHERE fecha BETWEEN ? AND ?
        ''', (start, end))
        total = cursor.fetchone()[0] or 0.0
        return float(total)
    except sqlite3.Error as e:
        print(f"Error al calcular total de gastos: {e}")
        return 0.0
    finally:
        conn.close()

def obtener_total_por_categoria_periodo(inicio, fin):
    """Obtiene gastos agrupados por categoría en un período"""
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT categoria, SUM(monto) 
            FROM gastos 
            WHERE fecha BETWEEN ? AND ? 
            GROUP BY categoria
            ORDER BY SUM(monto) DESC
        ''', (inicio, fin))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error al obtener gastos por categoría: {e}")
        return []
    finally:
        conn.close()

def exportar_reportes(periodo="Todos", tipo="ambos"):
    """Exporta datos a CSV"""
    inicio, fin = calculate_period_dates(periodo)
    conn = conectar_db()
    cursor = conn.cursor()
    
    try:
        if tipo == "ingresos":
            query = """
                SELECT fecha, monto, descripcion, usuario, notas
                FROM ingresos
                WHERE fecha BETWEEN ? AND ?
                ORDER BY fecha
            """
            cursor.execute(query, (inicio, fin))
            filename = "reporte_ingresos.csv"
        elif tipo == "gastos":
            query = """
                SELECT fecha, categoria, monto, descripcion, usuario, notas
                FROM gastos
                WHERE fecha BETWEEN ? AND ?
                ORDER BY fecha
            """
            cursor.execute(query, (inicio, fin))
            filename = "reporte_gastos.csv"
        else:
            query = """
                SELECT i.fecha, 'Ingreso', i.monto, i.descripcion, i.usuario, i.notas
                FROM ingresos i
                WHERE i.fecha BETWEEN ? AND ?
                UNION ALL
                SELECT g.fecha, 'Gasto', g.monto, g.descripcion, g.usuario, g.notas
                FROM gastos g
                WHERE g.fecha BETWEEN ? AND ?
                ORDER BY fecha
            """
            cursor.execute(query, (inicio, fin, inicio, fin))
            filename = "reporte_completo.csv"
        
        rows = cursor.fetchall()
        
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if tipo == "ingresos":
                writer.writerow(["Fecha", "Monto", "Descripción", "Usuario", "Notas"])
            elif tipo == "gastos":
                writer.writerow(["Fecha", "Categoría", "Monto", "Descripción", "Usuario", "Notas"])
            else:
                writer.writerow(["Fecha", "Tipo", "Monto", "Descripción", "Usuario", "Notas"])
            writer.writerows(rows)
        
        return filename
    except Exception as e:
        print(f"Error al exportar reporte: {e}")
        return None
    finally:
        conn.close()

def calculate_period_dates(period):
    """Calcula fechas de inicio y fin para un período dado"""
    today = datetime.now().date()
    if period == "Hoy":
        start = today.strftime("%Y-%m-%d")
        end = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    elif period == "Semana":
        start = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        end = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    elif period == "Mes":
        start = today.replace(day=1).strftime("%Y-%m-%d")
        end = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    elif period == "Año":
        start = today.replace(month=1, day=1).strftime("%Y-%m-%d")
        end = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    else:  # Todos
        start = "2000-01-01"
        end = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    return start, end