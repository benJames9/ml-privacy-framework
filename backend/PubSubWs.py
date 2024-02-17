from fastapi import FastAPI, WebSocket

from asyncio import Lock


class PubSubWs:
    def __init__(self) -> None:
        self._route_dict: dict[str, list[WebSocket]] = dict()
        self._dict_lock = Lock()

    def setup(self, app: FastAPI, base_route: str):
        @app.websocket(f"{base_route}/{{request_token}}")
        async def _websocket_endpoint(ws: WebSocket, request_token: str):
            if not request_token in self._route_dict:
                return 500

            await ws.accept()

            async with self._dict_lock:
                self._route_dict[request_token].append(ws)

            try:
                while True:
                    await ws.receive()  # just so we can monitor when it closes
            except:
                # Handle the case where the websocket is closed or errored
                await ws.close()

                async with self._dict_lock:
                    self._route_dict[request_token].remove(ws)

    async def publish(self, request_token: str, data_str):
        if not request_token in self._route_dict:
            raise Exception("Cannot publish to non existent route")

        async with self._dict_lock:
            for ws in self._route_dict[request_token]:
                try:
                    await ws.send_text(data_str)
                except:
                    print("WebSocket already dead")
                    pass

    async def register_route(self, request_token: str):
        if request_token in self._route_dict:
            raise Exception("Route already registered")

        async with self._dict_lock:
            self._route_dict[request_token] = []

    async def deregister_route(self, request_token: str):
        if not request_token in self._route_dict:
            raise Exception("Route doesn't exist")

        async with self._dict_lock:
            self._route_dict.pop(request_token)
