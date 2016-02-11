import json
import lcm
import settings
import forseti2
import LCMNode
LCMNode = LCMNode.LCMNode

from socketIO_client import SocketIO, BaseNamespace

# class Namespace(BaseNamespace):

#     def on_connect(self):
#         print('[Connected]')
#         self.emit('message', "{header:{msg_type:'execute'}, content:'print \"hello world\"'}")

socketIO = SocketIO('localhost', 5000, BaseNamespace)
stop = {"header": {"msg_type": 'stop'}, 'content': ''}
socketIO.send(json.dumps(stop))
hello_world = {"header": {"msg_type": 'execute'}, 'content': {"code": "print \"hello world \""}}
socketIO.send(json.dumps(hello_world))
#socketIO.wait()