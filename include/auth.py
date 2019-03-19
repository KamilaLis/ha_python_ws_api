#!/usr/bin/python3

import asyncio
import functools
import json

import asyncws


TYPE_AUTH = 'auth'
TYPE_AUTH_INVALID = 'auth_invalid'
TYPE_AUTH_OK = 'auth_ok'
TYPE_AUTH_REQUIRED = 'auth_required'

# FIX
ACCESS_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIyMThmYmM0NWI1N2M0YjVmODAyYzM0YzE5NTM2ZjQxMyIsImlhdCI6MTU1MjM5NTEwMSwiZXhwIjoxODY3NzU1MTAxfQ.IdADGngytDQlYPfFZsbUc-BhLxkSeLe_KG9DKgefPfA'
# ACCESS_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiI3ZDg2Mzc3NzIwYjQ0M2YyOWI2MzE2ZTdmMjI3Njc0OCIsImlhdCI6MTU0MzYwMTY1OCwiZXhwIjoxODU4OTYxNjU4fQ.uSatzdHOC-ozC9OnI0pUk63Mtuawy7bauRG6k-swP9g'

def auth_message():
    """Return an auth message."""
    return {
        'type': TYPE_AUTH_OK,
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

def get_states_message(iden):
    """Return an auth message."""
    return {
        "id": iden,
        "type": "get_states",
}

class ActiveConnection:

    def __init__(self):
        self._authenticated = False
        self._connection = None
        self._iden = 0

    async def call_service(self,domain, service):
        """Call devices services."""
        await self._connection.send(call_service_message(++self._iden, domain, service))

    async def subscribe_events(self):
        await self._connection.send(subscribe_events_message(++self._iden))

    async def auth(self):
        """Authorize connection."""
        await self._connection.send(auth_message()) 

        while True:
            message = await self._connection.recv()
            if message is None:
                break
            print (message)

    def start():
        loop = asyncio.get_event_loop()
        loop.run_until_complete(auth())
        loop.close()

async def createConnection():
    ac = ActiveConnection()
    ac._connection = await asyncws.connect('ws://localhost:8123/api/websocket')


# async def listen_for_message():
#     while True:
#         message = await websocket.recv()
#         if message is None:
#             break
#         print (message)

# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
# loop.close()

    # async def message_handler(loop):
    #     print('Event handler called')
    #     message = await self._connection.recv()
    #     print (message)
    #     if message is None:
    #         loop.stop()

    # def start():
    #     self._connection = await asyncws.connect('ws://localhost:8123/api/websocket')
    #     loop = asyncio.get_event_loop()
    #     try:
    #         loop.call_soon(functools.partial(message_handler, loop))
    #         print('starting event loop')
    #         loop.run_forever()
    #     finally:
    #         print('closing event loop')
    #         loop.close()
