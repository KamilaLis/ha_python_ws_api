#!/usr/bin/python3

import asyncio
import json
import asyncws

import functools

TYPE_AUTH = 'auth'
TYPE_AUTH_INVALID = 'auth_invalid'
TYPE_AUTH_OK = 'auth_ok'
TYPE_AUTH_REQUIRED = 'auth_required'

TYPE_CALL_SERVICE = 'call_service'
TYPE_EVENT = 'event'
TYPE_GET_CONFIG = 'get_config'
TYPE_GET_SERVICES = 'get_services'
TYPE_GET_STATES = 'get_states'
TYPE_PING = 'ping'
TYPE_PONG = 'pong'
TYPE_SUBSCRIBE_EVENTS = 'subscribe_events'
TYPE_UNSUBSCRIBE_EVENTS = 'unsubscribe_events'

EVENT_STATE_CHANGED = 'state_changed'

# FIX: fetch token
ACCESS_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIyMThmYmM0NWI1N2M0YjVmODAyYzM0YzE5NTM2ZjQxMyIsImlhdCI6MTU1MjM5NTEwMSwiZXhwIjoxODY3NzU1MTAxfQ.IdADGngytDQlYPfFZsbUc-BhLxkSeLe_KG9DKgefPfA'

def auth_message():
    """Return an auth message."""
    return {
        'type': TYPE_AUTH,
        'access_token': ACCESS_TOKEN,
}

def subscribe_events_message(iden, event_type):
    """Return an subscribe_events message."""
    return {
        'id': iden, 
        'type': TYPE_SUBSCRIBE_EVENTS, 
        'event_type': event_type,
}

def unsubscribe_events_message(iden, subscription_id):
    """Return an unsubscribe_events message."""
    return {
        'id': iden, 
        'type': TYPE_UNSUBSCRIBE_EVENTS, 
        'subscription': subscription_id,
}

def call_service_message(iden, domain, service):
    """Return an call_service message."""
    return {
        "id": iden,
        "type": TYPE_CALL_SERVICE,
        "domain": domain,
        "service": service,
}


class WebSocketHandler:

    def __init__(self):
        self._authenticated = False
        self._connection = None
        self._iden = 0

        self._loop = asyncio.get_event_loop()
        self._connection = self._loop.run_until_complete(
            asyncws.connect('ws://localhost:8123/api/websocket'))
        try:
            self._loop.run_until_complete(self.auth_phase())
        except Exception as e:
            print(e)
            self._loop.run_until_complete(self._connection.close())
        # finally:
        #     self._loop.close()

    def close(self):
        if self._loop.is_running():
            self._loop.close()

    async def _send_message(self, message):
        """Send message via websocket"""
        await (self._connection).send(json.dumps(message))

    async def auth_phase(self):
        """Authorize connection."""
        await self._send_message(auth_message())
        while True:
            message = await (self._connection).recv()
            if message is None:
                break
            # print (message)
            msg = json.loads(message)
            if msg["type"] == TYPE_AUTH_OK:
                self._authenticated = True
                print("authenticated")
                break
            elif msg["type"] == TYPE_AUTH_INVALID:
                raise Exception(msg["message"])


    # Subscribe to events
    # TODO: map event type -> subscription id
    def subscribe(self, iden, event_type):
        self._loop.run_until_complete(self.subscribe_events(iden, event_type))

    async def subscribe_events(self, iden, event_type):
        """Subscribe client to the event bus"""
        await self._send_message(subscribe_events_message(iden, event_type))
        while True:
            message = await (self._connection).recv()
            if message is None:
                break
            msg = json.loads(message)
            if msg["type"] == "result":
                if msg["success"] == True:
                    print("Subscription to "+event_type+" is active.")
                    break
                else:
                    raise Exception("Exception while subscribing event: "+msg["error"]["message"])


    # Unsubscribing from events

    def unsubscribe(self, iden, subscription_id):
        self._loop.run_until_complete(self.unsubscribe_events(iden, subscription_id))

    async def unsubscribe_events(self, iden, subscription_id):
        await self._send_message(unsubscribe_events_message(iden, subscription_id))
        while True:
            message = await (self._connection).recv()
            if message is None:
                break
            msg = json.loads(message)
            if msg["type"] == "result":
                if msg["success"] == True:
                    print("Unsubscribing was successful.")
                    break
                else:
                    raise Exception("Exception while unsubscribing event: "+msg["error"]["message"])    


    # Calling a service

    def call_service(self, iden, domain, service):
        self._loop.run_until_complete(self.call_ha_service(iden, domain, service))

    async def call_ha_service(self, iden, domain, service):
        await self._send_message(call_service_message(iden, domain, service))
        while True:
            message = await (self._connection).recv()
            if message is None:
                break
            print(message)
            msg = json.loads(message)
            if msg["type"] == "result":
                if msg["success"] == True:
                    print("the service is done executing.")
                    # break
                else:
                    raise Exception("Exception while calling a service: "+msg["error"]["message"])

        # asyncio.run() Python 3.7

    async def listen_for_message(self):
        print("in listen_for_message")
        message = await (self._connection).recv()
        print(message)
        if message is None:
            return
        # msg = json.loads(message)
        # if msg["type"] == "event":
        #     print ("handle event")

    # def event_handler(self, stop=False):
    #     print('Event handler called')
    #     if stop:
    #         print('stopping the loop')
    #         self._loop.stop()


    # def test(self):
    #     self._loop.call_soon(functools.partial(self.event_handler))
    #     print('starting event loop')
    #     self._loop.call_soon(functools.partial(self.event_handler, stop=True))
 
    #     self._loop.run_forever()



wsh = WebSocketHandler()
try:
    wsh.subscribe(1, EVENT_STATE_CHANGED)
    wsh.call_service(2, "rosrobot", "locate")
    # wsh._loop.run_until_complete(wsh.listen_for_message())
    wsh.unsubscribe(3, 1)
except Exception as e:
    print(e)
finally:
    wsh.close()
