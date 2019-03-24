#!/usr/bin/python3
from websockethandler import *

wsh = WebSocketHandler()
try:
    wsh.subscribe(EVENT_STATE_CHANGED)
    wsh.call_service("rosrobot", "locate")
    # print(result)
    wsh.listen_for_message()
    wsh.unsubscribe(EVENT_STATE_CHANGED)
except Exception as e:
    print(e)
finally:
    wsh.close()