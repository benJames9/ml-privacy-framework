from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect
import aiofiles
import uuid 

app = FastAPI()

@app.get("/api")
def read_root():
    return {"message": "Hello from the backend!"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Accept connection
    await websocket.accept()
    connection_id = str(uuid.uuid4()) 
    filename = f"received_model_{connection_id}.pt" 
    print(f"connection id is {connection_id}")
    print(f"filename is {filename}")

    # Handle messages
    try:
        message = await websocket.receive_text()
        header, data_type = message.split(':', 1)

        # Handle unexpected initial header
        if header != "dataType":
            await handle_unexpected_header(websocket, connection_id, header)
            return
        
        # Handle supported data types
        if data_type == "pt"
            await handle_pt_file(websocket)
        else if data_type == "test"
            await handle_test_message(websocket)
        else:
            handle_unsupported_type(websocket, connection_id, data_type)
            return
        
        # Success message
        await websocket.send_text("File received successfully")
    except WebSocketDisconnect:
        await websocket.close()

# Handle a test message sent over websocket
async def handle_test_message(websocket: WebSocket):
    message = await websocket.receive_text()
    message = data.decode('utf-8')
    print("Received string message:", message)
    await websocket.send_text(f"Successfully received message: {message}")

# Handle a .pt file being sent by saving to machine
async def handle_pt_file(websocket: WebSocket):
    return

# Handle unexpected header error in initial message
async def handle_unexpected_header(websocket: WebSocket, connection_id: string, header: string):
    err = f"Unexpected message from conn {connection_id}: {header}"
    print(err)
    await websocket.send_text(err)
    await websocket.close()

# Handle unsupported data type in intial message
async def handle_unsupported_type(websocket: WebSocket, connection_id: string, data_type: string):
    err = f"Unexpected data type from conn {connection_id}: {data_type}"
    print(err)
    await websocket.send_text(err)
    await websocket.close()

# Save .pt file to server
async def save_pt_file(file_data, filename):
    async with aiofiles.open(filename, "wb") as f:
        await f.write(file_data)