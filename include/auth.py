#!/usr/bin/python3

import asyncio
import json

import asyncws


TYPE_AUTH = 'auth'
TYPE_AUTH_INVALID = 'auth_invalid'
TYPE_AUTH_OK = 'auth_ok'
TYPE_AUTH_REQUIRED = 'auth_required'

# FIX
ACCESS_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiI3ZDg2Mzc3NzIwYjQ0M2YyOWI2MzE2ZTdmMjI3Njc0OCIsImlhdCI6MTU0MzYwMTY1OCwiZXhwIjoxODU4OTYxNjU4fQ.uSatzdHOC-ozC9OnI0pUk63Mtuawy7bauRG6k-swP9g'

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

    def call_service(domain, service):
        """Call """
        await _connection.send(call_service_message(++self._iden, domain, service))


def auth():
    """Authorize connection."""
    _connection = await asyncws.connect('ws://localhost:8123/api/websocket')
    await _connection.send(auth_message()) 

