from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)

def test_obtener_pedido_404():
    # Ejecutar y comprobar
    respuesta = client.get("/orders/X999")
    assert respuesta.status_code == 404

def test_confirmar_pedido_conflicto_409():
    # Preparar: confirmamos la primera vez
    client.post("/orders/O013/confirm")
    
    # Ejecutar: confirmamos la segunda vez
    respuesta = client.post("/orders/O013/confirm")
    
    # Comprobar
    assert respuesta.status_code == 409

def test_envio_sin_guia():
    # Preparar: confirmamos el pedido O012 primero
    client.post("/orders/O012/confirm")
    
    # Ejecutar: enviamos sin guía
    respuesta = client.post("/orders/O012/ship", json={"tracking_number": " "})
    
    # Comprobar
    assert respuesta.status_code == 422
