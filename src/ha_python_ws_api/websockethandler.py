#!/usr/bin/python3

import asyncio
import json
import asyncws

import functools

import logging

logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)

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

def call_service_message(iden, domain, service, service_data):
    """Return an call_service message."""
    return {
        "id": iden,
        "type": TYPE_CALL_SERVICE,
        "domain": domain,
        "service": service,
        "service_data":service_data,
}


class WebSocketHandler:

    def __init__(self):
        self._authenticated = False
        self._connection = None
        self._iden = 0
        self._subs = {}

        self._loop = asyncio.get_event_loop()
        self._connection = self._loop.run_until_complete(
            asyncws.connect('ws://localhost:8123/api/websocket'))
        try:
            self._loop.run_until_complete(self.auth_phase())
        except Exception as e:
            _LOGGER.error(e)
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
                _LOGGER.debug("Client authenticated.")
                break
            elif msg["type"] == TYPE_AUTH_INVALID:
                raise Exception(msg["message"])


    # Subscribe to events

    def subscribe(self, event_type):
        self._iden += 1
        self._loop.run_until_complete(self.async_subscribe_events(self._iden, event_type))
        self._subs[event_type] = self._iden

    async def async_subscribe_events(self, iden, event_type):
        """Subscribe client to the event bus"""
        await self._send_message(subscribe_events_message(iden, event_type))
        while True:
            message = await (self._connection).recv()
            if message is None:
                break
            msg = json.loads(message)
            if msg["type"] == "result":
                if msg["success"] == True:
                    _LOGGER.debug("Subscription to '"+event_type+"' is active.")
                    break
                else:
                    raise Exception("Exception while subscribing event: "+msg["error"]["message"])


    # Unsubscribing from events

    def unsubscribe(self, event_type):
        self._iden += 1
        self._loop.run_until_complete(self.async_unsubscribe_events(self._iden, self._subs[event_type]))
        del self._subs[event_type]

    async def async_unsubscribe_events(self, iden, subscription_id):
        await self._send_message(unsubscribe_events_message(iden, subscription_id))
        while True:
            message = await (self._connection).recv()
            if message is None:
                break
            msg = json.loads(message)
            if msg["type"] == "result":
                if msg["success"] == True:
                    _LOGGER.debug("Unsubscribing was successful.")
                    break
                else:
                    raise Exception("Exception while unsubscribing event: "+msg["error"]["message"])    


    # Calling a service

    def call_service(self, domain, service, service_data):
        self._iden += 1
        self._loop.run_until_complete(self.async_call_service(self._iden, domain, service, service_data))

    async def async_call_service(self, iden, domain, service, service_data):
        _LOGGER.debug("Calling service '"+service+"'...")
        await self._send_message(call_service_message(iden, domain, service, service_data))
        while True:
            message = await (self._connection).recv()
            if message is None:
                break
            # print(message)
            msg = json.loads(message)
            if msg["type"] == "result":
                if msg["success"] == True:
                    _LOGGER.debug("The service is done executing.")
                    break
                else:
                    raise Exception("Exception while calling a service: "+msg["error"]["message"])
            # # wait for state change event
            # if msg["type"] == TYPE_EVENT:
            #     if domain in msg["event"]["data"]["entity_id"]:
            #         print(msg["event"]["data"]["new_state"]["state"]) 
            #         break
                
    def listen_for_message(self):
        async def wait_for_message():
            try:
                await asyncio.wait_for(self.async_listen_for_message(), timeout=60.0)
            except asyncio.TimeoutError:
                _LOGGER.warning('timeout!')
        self._loop.run_until_complete(wait_for_message())

    async def async_listen_for_message(self):
        _LOGGER.debug("Waiting for message...")
        message = await (self._connection).recv()
        # print(message)
        if message is None:
            return
        msg = json.loads(message)
        if msg["type"] == TYPE_EVENT:
            print ("handle event")


