"""
LCM WebSocket Bridge: server application

Usage:
  First modify the SETTINGS section below to have the correct LCM setup
  Then run this script with no arguments
"""
import flask
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room, send
import json
import lcm
import threading
import thread
import random
from collections import defaultdict
import LCMNode
### SETTINGS
import settings
import forseti2
LCM_URI = settings.LCM_URI
TYPES_ROOT = forseti2
### END SETTINGS

bridge_app = Flask(__name__, template_folder='../ui/test/')
bridge_app.config['SECRET_KEY'] = 'secret!'
io = SocketIO(bridge_app)


lc = lcm.LCM(LCM_URI)

# {channel: type}
node_subscriptions = {}

# {channel: {type:lcm_type, members: [members]}}
subscriptions = defaultdict(lambda: {'type': '', 'members': []})

def send_lcm(channel, msg):
    pass
    send_random("timer")
    #io.send('dadoodle')
    #io.emit(channel, msg, namespace='/', json=True)

def lcm_callback(channel, data):
    print "received on %s" % channel
    msg = TYPES_ROOT.__getattribute__(node_subscriptions[channel]).decode(data)
    #print lcm_to_dict(msg)
    print "SENDING STUFF"
    send_lcm(channel, lcm_to_dict(msg))

def lcm_subscribe(channel, type):
    if type not in node_subscriptions:
        print "subscribing to %s for %s" % (channel, type)
        node_subscriptions[channel] = type
        lc.subscribe(channel, lcm_callback)

def add_subscription(channel, type, sid):
    lcm_subscribe(channel, type)
    # if subscriptions[channel]['type'] != type:
    #     lcm_subscribe(channel, type)
    #     subscriptions[channel]['type'] = type
    # subscriptions[channel]['members'].append(sid)

def remove_subscription(channel, type, sid):
    pass
    # if sid in subscriptions[channel]['members']:
    #     subscriptions[channel]['members'].remove(sid)

def is_lcm_object(obj):
    """
    Checks if an object is an instance of an LCM type

    LCM offers no official way to do this, so test for a uniquely-named method
    that is present in all LCM types
    """
    return '_get_packed_fingerprint' in dir(obj)

def lcm_to_dict(obj):
    """
    Converts an instance of an LCM object into a dictionary
    """

    res = {}
    for slot in obj.__slots__:
        value = obj.__getattribute__(slot)
        if is_lcm_object(value):
            res[slot] = lcm_to_dict(value)
        else:
            res[slot] = value
    return res

def dict_to_lcm(type, d):
    """
    Convert a dictionary holding data for fields into an LCM message object
    """
    msg_cls = TYPES_ROOT.__getattribute__(type)
    msg = msg_cls()

    for k, v in d.items():
        if k not in msg.__slots__:
            continue
        if type(v) == dict:
            v = dict_to_lcm(v)
        msg.__setattr__(k, v)

    return msg

def publish(channel, type, body):
    print "publishing: %s" % str(dict_to_lcm(type, body))
    lc.publish(channel, dict_to_lcm(type, body).encode())
    send_random("clicked")

@io.on('connect', namespace='/')
def client_connect():
    print "client %s connected" % (flask.request.sid)
    send_random("connected")
    #clients.append(flask.request.sid)
    
@io.on('disconnect', namespace='/')
def client_disconnect():
    print "client %s disconnected" % (flask.request.sid)
    #clients.remove(flask.request.sid)

@io.on('subscribe', namespace='/')
def subscribe_channel(data):
    join_room(data['channel'])
    add_subscription(data['channel'], data['type'], flask.request.sid)

@io.on('unsubscribe', namespace='/')
def unsubscribe_channel(data):
    leave_room(data['channel'])
    remove_subscription(data['channel'], data['type'], flask.request.sid)

@io.on('publish', namespace='/')
def client_publish(data):
    send_random("clicked")
    #publish(data['channel'], data['type'], data['body'])

@bridge_app.route('/')
def test_ui():
    return render_template('index.html')
class BridgeNode(LCMNode.LCMNode):
    def __init__(self, lc):
        self.lc = lc
        self.start_thread()

def send_random(msg):
    print "sending random for %s" % msg
    io.send(msg + ' ' + str(random.random()))

if __name__ == '__main__':
    spam_socket = threading.Timer(10, send_random)
    #spam_socket.start()
    bridge = BridgeNode(lc)
    io.run(bridge_app, debug=True)
    print "hello"
    bridge = BridgeNode(lc)
    thread.sleep(5)
    print "random stuff"
    io.emit('message', str(random.random()))
    


# class WSHandler(tornado.websocket.WebSocketHandler):
#     def open(self):
#         """
#         Called when a client opens the websocket
#         """
#         self.lc = lcm.LCM(LCM_URI)
#         self.thread = threading.Thread(target=self.lcm_loop)
#         self.thread.daemon = True
#         self.thread.start()
#         self.subscriptions = {}

#     def close(self):
#         """
#         Called when the websocket closes
#         """
#         # No thread shutdown and LCM cleanup here, because we assume that the
#         # program is quitting anyway
#         pass

#     ### Websocket-related

#     def on_message(self, message):
#         """
#         Called when a message is received over the websocket
#         """

#         obj = json.loads(message)
#         msg_type = obj["type"]
#         data = obj["data"]

#         if msg_type == "subscribe":
#             self.add_subscription(data["channel"],
#                                   data["msg_type"],
#                                   data["subscription_id"])
#         elif msg_type == "unsubscribe":
#             self.remove_subscription(data["subscription_id"])
#         elif msg_type == "publish":
#             self.lc.publish(data["channel"],
#                             self.dict_to_lcm(data["data"]).encode())
#         else:
#             raise Exception, "Invalid websocket message type: " + msg_type

#     def ws_send(self, type, data):
#         """
#         Convenience method for sending data over the websocket
#         """
#         self.write_message(json.dumps({"type": type, "data": data}))

#     ### LCM-related

#     def lcm_loop(self):
#         """
#         Runs the LCM handling loop
#         """
#         while True:
#             try:
#                 self.lc.handle()
#             except Exception as e:
#                 print "Got exception while handling lcm message", e

#     def add_subscription(self, channel, msg_type, subscription_id):
#         """
#         Creates an LCM subscription (based on data from a websocket request)
#         Forwards any LCM messages received to javascript via websockets
#         """
#         def handle(channel, data):
#             msg = TYPES_ROOT.__getattribute__(msg_type).decode(data)
#             self.ws_send("packet", {"subscription_id": subscription_id,
#                                     "msg": self.lcm_to_dict(msg)})
#         self.subscriptions[subscription_id] = self.lc.subscribe(channel, handle)

#     def remove_subscription(self, subscription_id):
#         if subscription_id not in self.subscriptions:
#             return
#         print "UNSUBSCRIBING"
#         self.lc.unsubscribe(self.subscriptions[subscription_id])
#         del self.subscriptions[subscription_id]

#     ### Data conversion

#     def is_lcm_object(self, obj):
#         """
#         Checks if an object is an instance of an LCM type

#         LCM offers no official way to do this, so test for a uniquely-named method
#         that is present in all LCM types
#         """
#         return '_get_packed_fingerprint' in dir(obj)

#     def lcm_to_dict(self, obj):
#         """
#         Converts an instance of an LCM object into a dictionary
#         """

#         res = {}
#         for slot in obj.__slots__:
#             value = obj.__getattribute__(slot)
#             if self.is_lcm_object(value):
#                 res[slot] = self.lcm_to_dict(value)
#             else:
#                 res[slot] = value
#         return res

#     def dict_to_lcm(self, d):
#         """
#         Convert a dictionary holding data for fields into an LCM message object
#         """
#         msg_cls = TYPES_ROOT.__getattribute__(d["__type__"])
#         msg = msg_cls()

#         for k, v in d.items():
#             if k not in msg.__slots__:
#                 continue
#             if type(v) == dict:
#                 v = self.dict_to_lcm(v)
#             msg.__setattr__(k, v)

#         return msg

# application = tornado.web.Application([
#     (r'/', WSHandler)
# ])



