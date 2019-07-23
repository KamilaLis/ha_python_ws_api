#!/usr/bin/python3
# from websockethandler import *
from ha_python_ws_api import websockethandler

wsh = websockethandler.WebSocketHandler()
try:
    wsh.subscribe(websockethandler.EVENT_STATE_CHANGED)
    # wsh.call_service("rosrobot", "locate")
    wsh.call_service("persistent_notification", "create", 
        {
            "notification_id": "1234",
            "title": "Sample notification",
            "message": "This is a sample text"
        })
    # print(result)
    # wsh.listen_for_message()
    wsh.unsubscribe(websockethandler.EVENT_STATE_CHANGED)
except Exception as e:
    print(e)
finally:
    wsh.close()