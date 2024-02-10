from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

from asyncio import Lock

class PubSubWs:
  def __init__(self, app: FastAPI, base_route: str) -> None:
    self._route_dict: dict[str, list[WebSocket]] = dict()
    self._dict_lock = Lock()
    
    @app.websocket(f"{base_route}/{{id_token}}")
    async def _websocket_endpoint(ws: WebSocket, id_token: str):
      if not id_token in self._route_dict:
        return 500
      
      await ws.accept()
      
      print("we accept the connection...")
      
      async with self._dict_lock:
        self._route_dict[id_token].append(ws)
      
      try:
        while True:
          await ws.receive() # just so we can monitor when it closes
      except:
        await ws.close()

        async with self._dict_lock:
          self._route_dict[id_token].remove(ws)
  
  async def publish(self, id_token: str, data_str):
    if not id_token in self._route_dict:
      raise Exception("Cannot publish to non existent route")
    
    async with self._dict_lock:
      for ws in self._route_dict[id_token]:
        try:
          await ws.send_text(data_str)
        except:
          print("WebSocket already dead")
          pass
  
  async def register_route(self, id_token: str):
    if id_token in self._route_dict:
      raise Exception("Route already registered")

    async with self._dict_lock:
      self._route_dict[id_token] = []
  
  async def deregister_route(self, id_token: str):
    if not id_token in self._route_dict:
      raise Exception("Route doesn't exist")

    async with self._dict_lock:
      self._route_dict.pop(id_token)
