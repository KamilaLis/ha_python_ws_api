#!/usr/bin/python3

import asyncio
import json
import asyncws

# import logging
# _LOGGER = logging.getLogger(__name__)

TYPE_AUTH = 'auth'
TYPE_AUTH_INVALID = 'auth_invalid'
TYPE_AUTH_OK = 'auth_ok'
TYPE_AUTH_REQUIRED = 'auth_required'

# FIX
ACCESS_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIyMThmYmM0NWI1N2M0YjVmODAyYzM0YzE5NTM2ZjQxMyIsImlhdCI6MTU1MjM5NTEwMSwiZXhwIjoxODY3NzU1MTAxfQ.IdADGngytDQlYPfFZsbUc-BhLxkSeLe_KG9DKgefPfA'

def auth_message():
    """Return an auth message."""
    return {
        'type': TYPE_AUTH,
        'access_token': ACCESS_TOKEN,
}

def subscribe_events_message(iden):
    """Return an subscribe_events message."""
    return {
        'id': iden, 
        'type': 'subscribe_events', 
        'event_type': 'state_changed',
}

def unsubscribe_events_message(iden, subscription_id):
    """Return an unsubscribe_events message."""
    return {
        'id': iden, 
        'type': 'unsubscribe_events', 
        'subscription': subscription_id,
}

def call_service_message(iden, domain, service):
    """Return an call_service message."""
    return {
        "id": iden,
        "type": "call_service",
        "domain": domain,
        "service": service,
}


class WebSocketHandler:

    def __init__(self):
        self._authenticated = False
        self._connection = None
        self._iden = 0

    async def _send_message(self, message):
        await (self._connection).send(json.dumps(message))

    async def auth(self):
        """Authorize connection."""
        await self._send_message(auth_message())

    async def subscribe_events(self, iden):
        await self._send_message(subscribe_events_message(iden))

    async def create_connection(self):
        """Simple WebSocket client for Home Assistant."""
        self._connection = await asyncws.connect('ws://localhost:8123/api/websocket')

        await self.auth()
        await self.subscribe_events(1)

        while True:
            message = await (self._connection).recv()
            if message is None:
                break
            print (message)
            msg = json.loads(message)
            if msg["type"] == TYPE_AUTH_OK:
                self._authenticated = True
                print("_authenticated")
            if msg["type"] == "event":
                print("hadle event")

    def start(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.create_connection())
        loop.close()

        # asyncio.run()

async def auth(websocket):
    """Authorize connection."""
    await websocket.send(json.dumps(auth_message()))

async def subscribe_events(websocket, iden):
    await websocket.send(json.dumps(subscribe_events_message(iden)))

async def create_connection():
    """Simple WebSocket client for Home Assistant."""
    return await asyncws.connect('ws://localhost:8123/api/websocket')

    # await auth(websocket)
    # await subscribe_events(websocket, 1)
async def handle_messages():
    while True:
        message = await websocket.recv()
        if message is None:
            break
        print (message)

def start():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(connect())
    loop.close()

# start()
wsh = WebSocketHandler()
wsh.start()