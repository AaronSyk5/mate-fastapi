from fastapi import FastAPI, Request
from pydantic import BaseModel
from utils.respuesta import responder_mate
from utils.memoria_db import crear_base, guardar_interaccion, obtener_historial

app = FastAPI()

class Mensaje(BaseModel):
    empresa_id: str
    mensaje: str

@app.post("/mate")
async def mate_endpoint(data: Mensaje):
    respuesta = responder_mate(data.empresa_id, data.mensaje)
    return {"respuesta": respuesta}
