from fastapi import FastAPI, Body
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
import sqlite3
import logging
import os

app = FastAPI()
# Usar ruta absoluta para la base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), "demo.db")

# Configuración del logger
log_dir = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, "server.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

@app.middleware("http")
async def log_requests(request, call_next):
    response = await call_next(request)
    logging.info(f"{request.method} {request.url} - Status: {response.status_code}")
    return response

def run_query(query, params=(), commit=False):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if commit:
            conn.commit()
        return cursor.fetchall()

# === ENDPOINTS DE CONSULTA ===

@app.post("/existe_abonado", operation_id="existe_abonado")
async def existe_abonado(dni: str = Body(..., embed=True)):
    result = run_query("SELECT 1 FROM abonados WHERE dni = ?", (dni,))
    return {"existe": bool(result)}

@app.post("/direccion_abonado", operation_id="direccion_abonado")
async def direccion_abonado(dni: str = Body(..., embed=True)):
    result = run_query("SELECT direccion FROM abonados WHERE dni = ?", (dni,))
    return {"direccion": result[0][0] if result else None}

@app.post("/estado_pagos", operation_id="estado_pagos")
async def estado_pagos(dni: str = Body(..., embed=True)):
    result = run_query("SELECT estado FROM facturas WHERE dni_abonado = ?", (dni,))
    return {"estados": [r[0] for r in result]}

@app.post("/ultimo_pago", operation_id="ultimo_pago")
async def ultimo_pago(dni: str = Body(..., embed=True)):
    result = run_query(
        "SELECT fecha, importe FROM facturas WHERE dni_abonado = ? AND estado = 'Pagado' ORDER BY fecha DESC LIMIT 1",
        (dni,)
    )
    return {"ultimo_pago": {"fecha": result[0][0], "importe": result[0][1]} if result else None}

@app.post("/deuda_total", operation_id="deuda_total")
async def deuda_total(dni: str = Body(..., embed=True)):
    result = run_query(
        "SELECT SUM(importe) FROM facturas WHERE dni_abonado = ? AND estado != 'Pagado'",
        (dni,)
    )
    deuda = result[0][0] if result[0][0] else 0
    return {"deuda": deuda}

@app.post("/facturas_pendientes", operation_id="facturas_pendientes")
async def facturas_pendientes(dni: str = Body(..., embed=True)):
    result = run_query(
        "SELECT fecha, estado, importe FROM facturas WHERE dni_abonado = ? AND estado != 'Pagado'",
        (dni,)
    )
    return {
        "facturas": [
            {
                "fecha": r[0],
                "estado": r[1],
                "importe": r[2]
            } for r in result
        ]
    }

@app.post("/todas_las_facturas", operation_id="todas_las_facturas")
async def todas_las_facturas(dni: str = Body(..., embed=True)):
    result = run_query(
        "SELECT id,fecha, estado, importe FROM facturas WHERE dni_abonado = ? ORDER BY fecha DESC",
        (dni,)
    )
    return {"facturas": [{"identificador":r[0],"fecha": r[1], "estado": r[2], "importe": r[3]} for r in result]}

class DatosAbonadoInput(BaseModel):
    dni: Optional[str] = None
    poliza: Optional[str] = None

@app.post("/datos_abonado", operation_id="datos_abonado")
async def datos_abonado(data: DatosAbonadoInput):
    dni = data.dni
    poliza = data.poliza

    if not dni and not poliza:
        return {"error": "Debe proporcionar un DNI o una póliza"}

    if dni:
        result = run_query(
            "SELECT nombre, dni, direccion, email, telefono, poliza FROM abonados WHERE dni = ?",
            (dni,)
        )
    else:
        result = run_query(
            "SELECT nombre, dni, direccion, email, telefono, poliza FROM abonados WHERE poliza = ?",
            (poliza,)
        )

    if result:
        nombre, dni, direccion, correo, telefono, poliza = result[0]
        return {
            "nombre": nombre,
            "dni": dni,
            "direccion": direccion,
            "correo": correo,
            "telefono": telefono,
            "poliza": poliza
        }
    else:
        return {"error": "Abonado no encontrado"}

@app.post("/crear_incidencia", operation_id="crear_incidencia")
async def crear_incidencia(
    dni: str = Body(..., embed=True),
    ubicacion: str = Body(..., embed=True),
    descripcion: str = Body(..., embed=True),
    estado: str = Body("Abierto", embed=True)
):
    # Buscar el usuario_id usando el DNI
    result = run_query("SELECT id FROM abonados WHERE dni = ?", (dni,))
    if not result:
        return {"error": "No se encontró un abonado con el DNI proporcionado."}

    usuario_id = result[0][0]
    
    # Capitalizar la primera letra de la ubicación
    ubicacion = ubicacion.strip().capitalize()

    # Inserta la incidencia en la base de datos
    run_query(
        "INSERT INTO incidencias (usuario_id, ubicacion, descripcion, estado) VALUES (?, ?, ?, ?)",
        (usuario_id, ubicacion, descripcion, estado),
        commit=True
    )
    return {"message": f"Incidencia creada exitosamente para el abonado con DNI {dni}"}

@app.post("/incidencias_por_dni", operation_id="incidencias_por_dni")
async def incidencias_por_dni(dni: str = Body(..., embed=True)):
    
    result = run_query("SELECT id FROM abonados WHERE dni = ?", (dni,))
    if not result:
        return {"error": "No se encontró un abonado con el DNI proporcionado."}

    usuario_id = result[0][0]

    incidencias = run_query(
        "SELECT ubicacion, descripcion, estado FROM incidencias WHERE usuario_id = ?",
        (usuario_id,)
    )
    return {"incidencias": [{"ubicacion": r[0], "descripcion": r[1], "estado": r[2]} for r in incidencias]}

@app.post("/incidencias_por_nombre", operation_id="incidencias_por_nombre")
async def incidencias_por_nombre(nombre: str = Body(..., embed=True)):
    result = run_query(
        "SELECT ubicacion, descripcion, estado FROM incidencias WHERE usuario_id IN (SELECT id FROM abonados WHERE nombre = ?)",
        (nombre,)
    )
    return {"incidencias": [{"ubicacion": r[0], "descripcion": r[1], "estado": r[2]} for r in result]}



@app.post("/actualizar_factura", operation_id="actualizar_estado_factura")
async def actualizar_factura(
    dni:str = Body(..., embed=True),
    identificador: int = Body(..., embed=True),
    nuevo_estado: str = Body(..., embed=True)   
):
    # Buscar el usuario_id usando el DNI
    result = run_query("SELECT id FROM abonados WHERE dni = ?", (dni,))
    if not result:
        return {"error": "No se encontró un abonado con el DNI proporcionado."}
    usuario_id = result[0][0]
    
    # Actualizar el estado de la última factura del abonado
    run_query(
        "UPDATE facturas SET estado = ? WHERE dni_abonado = ? AND id = ?",
        (nuevo_estado, dni,identificador),
        commit=True
    )
    return {"¡Atención!": f"Estado de la última factura del abonado {dni} actualizado a '{nuevo_estado}'"}


@app.post("/actualizar_estado_incidencia", operation_id="actualizar_estado_incidencia")
async def actualizar_estado_incidencia(
    dni: str = Body(..., embed=True),
    ubicacion: str = Body(..., embed=True),
    nuevo_estado: str = Body(..., embed=True)
):
    # Buscar el usuario_id usando el DNI
    result = run_query("SELECT id FROM abonados WHERE dni = ?", (dni,))
    if not result:
        return {"error": "No se encontró un abonado con el DNI proporcionado."}
    usuario_id = result[0][0]
    # Capitalizar la ubicación para evitar problemas de mayúsculas/minúsculas
    ubicacion = ubicacion.strip().capitalize()
    # Busca la incidencia por usuario y ubicación
    incidencia = run_query(
        "SELECT id FROM incidencias WHERE usuario_id = ? AND ubicacion = ? ORDER BY id DESC LIMIT 1",
        (usuario_id, ubicacion)
    )
    if not incidencia:
        return {"error": "No se encontró ninguna incidencia para el abonado en esa ubicación."}
    incidencia_id = incidencia[0][0]
    run_query(
        "UPDATE incidencias SET estado = ? WHERE id = ?",
        (nuevo_estado, incidencia_id),
        commit=True
    )
    return {"¡Atención!": f"Estado de la incidencia {incidencia_id} del abonado {dni} actualizado a '{nuevo_estado}'"}

@app.post("/incidencias_pendientes", operation_id="incidencias_pendientes")
async def incidencias_pendientes():
    # Devuelve solo las incidencias pendientes
    result = run_query("SELECT ubicacion, descripcion, estado FROM incidencias WHERE estado = 'Pendiente'")
    return {"incidencias": [{"ubicacion": r[0], "descripcion": r[1], "estado": r[2]} for r in result]}

@app.post("/incidencias_por_ubicacion", operation_id="incidencias_por_ubicacion")
async def incidencias_por_ubicacion(ubicacion: str = Body(..., embed=True)):
    # Capitalizar solo la primera letra
    ubicacion = ubicacion.capitalize()
    result = run_query(
        "SELECT ubicacion, descripcion, estado FROM incidencias WHERE ubicacion = ?",
        (ubicacion,)
    )
    return {"incidencias": [{"ubicacion": r[0], "descripcion": r[1], "estado": r[2]} for r in result]}

@app.post("/weather_foo", operation_id="weather_foo")
async def weather_foo(direccion: str = Body(..., embed=True)):
    return {"clima": f"35 grados despejado en {direccion}"}

@app.get("/herramientas_disponibles", operation_id="herramientas_disponibles")
async def herramientas_disponibles():
    return [
        {"endpoint": "/existe_abonado", "descripcion": "Verifica si un abonado existe por DNI."},
        {"endpoint": "/direccion_abonado", "descripcion": "Obtiene la dirección de un abonado por DNI."},
        {"endpoint": "/estado_pagos", "descripcion": "Consulta el estado de los pagos de un abonado por DNI."},
        {"endpoint": "/ultimo_pago", "descripcion": "Obtiene el último pago realizado por un abonado por DNI."},
        {"endpoint": "/deuda_total", "descripcion": "Calcula la deuda total de un abonado por DNI."},
        {"endpoint": "/facturas_pendientes", "descripcion": "Lista las facturas pendientes de un abonado por DNI."},
        {"endpoint": "/todas_las_facturas", "descripcion": "Muestra todas las facturas de un abonado por DNI."},
        {"endpoint": "/datos_abonado", "descripcion": "Obtiene los datos completos de un abonado por DNI o póliza."},
        {"endpoint": "/crear_incidencia", "descripcion": "Crea una nueva incidencia para un abonado por DNI."},
        {"endpoint": "/incidencias_por_dni", "descripcion": "Consulta las incidencias asociadas a un abonado por DNI."},
        {"endpoint": "/incidencias_por_nombre", "descripcion": "Consulta las incidencias registradas por nombre de usuario."},
        {"endpoint": "/incidencias_por_ubicacion", "descripcion": "Consulta todas las incidencias registradas en una ubicación específica."},
        {"endpoint": "/actualizar_estado_incidencia", "descripcion": "Actualiza el estado de una incidencia por ID."},
        {"endpoint": "/incidencias_pendientes", "descripcion": "Muestra todas las incidencias pendientes."},
        {"endpoint": "/weather_foo", "descripcion": "Devuelve un clima simulado para una dirección."}
    ]
