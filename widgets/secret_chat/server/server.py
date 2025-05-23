from fastapi import FastAPI, WebSocket
import uvicorn
from typing import List

app = FastAPI()

# Храним активные соединения
active_connections = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    if len(active_connections) >= 2:
        await websocket.send_text("Сервер заполнен. Подключение невозможно.")
        await websocket.close(code=4000)
        return

    active_connections.append(websocket)
    print(f"Новое подключение ({len(active_connections)})")

    try:
        while True:
            data = await websocket.receive_text()
            # Пересылаем всем, кроме себя
            for conn in active_connections:
                if conn != websocket:
                    await conn.send_text(data)
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        active_connections.remove(websocket)
        print("Клиент отключен")


def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    run_server()