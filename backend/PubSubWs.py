from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketState
from asyncio import Lock, create_task, sleep
from typing import Optional
import json

WEBSOCKET_TIMEOUT_SECONDS = 600 # Timeout for websocket connections

# Websocket server for publishing attack responses to clients
class PubSubWs:
    def __init__(self) -> None:
        self._route_dict: dict[str, list[WebSocket]] = dict()
        self._last_published_data: dict[str, Optional[str]] = dict()
        self._dict_lock = Lock()

    # Setup websocket to accept connections
    def setup(self, app: FastAPI, base_route: str):
        @app.websocket(f"{base_route}/{{request_token}}")
        async def _websocket_endpoint(ws: WebSocket, request_token: str):
            # Clients should only connect to websocket after submitting attack
            # so we should already have a route for the request token
            if not request_token in self._route_dict:
                print("Attempted to connect to non existent route")
                return 401

            await ws.accept()
            
            # Set timeout for webscket connection
            create_task(self._close_websocket_after_timeout(ws, request_token))

            # Fetch the last cached response
            last_data = None
            async with self._dict_lock:
                self._route_dict[request_token].append(ws)
                last_data = self._last_published_data[request_token]

            # Re-broadcast the last published data for any new comers
            if last_data != None:
                await self.publish(request_token, last_data)

            try:
                while True:
                    await ws.receive()  # Just so we can monitor when it closes
            except Exception as e:
                error_message = self._generate_error(f"WebSocket error: {e}")
                await ws.send_text(json.dumps(error_message))
                await self._close_websocket(ws, request_token)
                    
    # Function to close the WebSocket after timeout
    async def _close_websocket_after_timeout(self, ws: WebSocket, request_token: str):
        await sleep(WEBSOCKET_TIMEOUT_SECONDS)
        
        # Send timeout message to client
        timeout_message = self._generate_error("WebSocket connection timed out")
        await ws.send_text(json.dumps(timeout_message))
        
        # Close the websocket
        await self._close_websocket(ws, request_token)
        
    # Close websocket and handle routes
    async def _close_websocket(self, ws: WebSocket, request_token: str):
        if ws.client_state != WebSocketState.DISCONNECTED:
            await ws.close()
        
        # Remove the websocket from routes
        async with self._dict_lock:
            if request_token in self._route_dict:
                if ws in self._route_dict[request_token]:
                    self._route_dict[request_token].remove(ws)
    
    # Generate JSON error message to send to client       
    def _generate_error(self, error: str):
        return {
            "message_type": "error",
            "error": error
        }

    # Publish attack responses to clients
    async def publish_serialisable_data(self, request_token: str, data):
        str_data = ""
        
        # Extract string from data
        try:
            str_data = json.dumps(data)
        except:
            pass

        try:
            str_data = data.json()
        except:
            pass

        if str_data == "":
            raise Exception("Data is not serialisable")
        await self.publish(request_token, str_data)

    # Publish serialised attack responses to clients
    async def publish(self, request_token: str, data_str: str):
        if not request_token in self._route_dict:
            raise Exception("Cannot publish to non existent route")
        
        # Cache the last published data
        async with self._dict_lock:
            self._last_published_data[request_token] = data_str

        # Broadcast the data to all clients
            for ws in self._route_dict[request_token]:
                try:
                    await ws.send_text(data_str)
                except Exception as e:
                    print(f"WebSocket may already dead: {e}")
                    pass

    # Register new routes
    async def register_route(self, request_token: str):
        if request_token in self._route_dict:
            raise Exception("Route already registered")

        async with self._dict_lock:
            self._route_dict[request_token] = []
            self._last_published_data[request_token] = None

    # Deregister routes
    async def deregister_route(self, request_token: str):
        if not request_token in self._route_dict:
            raise Exception("Route doesn't exist")

        async with self._dict_lock:
            self._route_dict.pop(request_token)
            self._last_published_data.pop(request_token)
