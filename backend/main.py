from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect
import aiofiles
import uuid 

app = FastAPI()

async def save_pt_file(file_data, filename):
    async with aiofiles.open(filename, "wb") as f:
        await f.write(file_data)

@app.get("/api")
def read_root():
    return {"message": "Hello from the backend!"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connection_id = str(uuid.uuid4()) 
    filename = f"received_model_{connection_id}.pt" 
    print(f"connection id is {connection_id}")
    print(f"filename is {filename}")
    try:
        while True:
            data = await websocket.receive_bytes()
            if data == b"":
                break
            await save_pt_file(data, filename)
        await websocket.send_text("File received successfully")
    except WebSocketDisconnect:
        await websocket.close()