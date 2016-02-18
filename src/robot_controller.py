import json
import lcm
import settings
import forseti2
import LCMNode
LCMNode = LCMNode.LCMNode

from socketIO_client import SocketIO, BaseNamespace

class Namespace(BaseNamespace):
    def on_connect(self):
        print('[Connected]')

blue0 = ("localhost", 5000)
blue1 = ("localhost", 5000)
gold0 = ("localhost", 5000)
gold1 = ("localhost", 5000)
robots = [blue0]#, blue1, gold0, gold1]
print "connecting"
sockets = [SocketIO(ip, port, Namespace, wait_for_connection=True) for ip, port in robots]
print "connected"
# def updateRobot(robot, ip, port):
#     curr_ip, curr_port = robots[robot]
#     if (curr_ip, curr_port) != (ip, port):
#         robots[robot] = (ip, port)
#         sockets[robot].disconnect()
#         sockets[robot] = SocketIO(ip, port, BaseNamespace)
#         print "connecting"
while True:
    pass
# socketIO = SocketIO('localhost', 5000, Namespace, wait_for_connection=False)
# stop = {"header": {"msg_type": 'stop'}, 'content': ''}
# socketIO.send(json.dumps(stop))
# hello_world = {"header": {"msg_type": 'execute'}, 'content': {"code": "print \"hello world \""}}
# socketIO.send(json.dumps(hello_world))
#socketIO.wait()