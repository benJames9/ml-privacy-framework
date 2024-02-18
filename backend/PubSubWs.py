from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketState
from asyncio import Lock
from typing import Optional
import json


class PubSubWs:
    def __init__(self) -> None:
        self._route_dict: dict[str, list[WebSocket]] = dict()
        self._last_published_data: dict[str, Optional[str]] = dict()
        self._dict_lock = Lock()

    def setup(self, app: FastAPI, base_route: str):
        @app.websocket(f"{base_route}/{{request_token}}")
        async def _websocket_endpoint(ws: WebSocket, request_token: str):
            if not request_token in self._route_dict:
                print("Attempted to connect to non existent route")
                return 401

            await ws.accept()

            last_data = None
            async with self._dict_lock:
                self._route_dict[request_token].append(ws)
                last_data = self._last_published_data[request_token]

            # rebroadcast the last published data for any new comers
            if last_data != None:
                await self.publish(request_token, last_data)

            try:
                while True:
                    await ws.receive()  # just so we can monitor when it closes
            except Exception as e:
                # Handle the case where the websocket is closed or errored
                if ws.client_state != WebSocketState.DISCONNECTED:
                    await ws.close()

                async with self._dict_lock:
                    self._route_dict[request_token].remove(ws)

    async def publish_serialisable_data(self, request_token: str, data):
        str_data = ""

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

    async def publish(self, request_token: str, data_str: str):
        if not request_token in self._route_dict:
            raise Exception("Cannot publish to non existent route")

        async with self._dict_lock:
            self._last_published_data[request_token] = data_str

            for ws in self._route_dict[request_token]:
                try:
                    await ws.send_text(data_str)
                except Exception as e:
                    print(f"WebSocket may already dead: {e}")
                    pass

    async def register_route(self, request_token: str):
        if request_token in self._route_dict:
            raise Exception("Route already registered")

        async with self._dict_lock:
            self._route_dict[request_token] = []
            self._last_published_data[request_token] = None

    async def deregister_route(self, request_token: str):
        if not request_token in self._route_dict:
            raise Exception("Route doesn't exist")

        async with self._dict_lock:
            self._route_dict.pop(request_token)
            self._last_published_data.pop(request_token)
