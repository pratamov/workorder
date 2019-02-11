from task import Task, TaskStatus

from enum import Enum
from task import Task
import socket
import pickle

class Node:

    def execute(self, task, args=None):
        status = TaskStatus()
        try:
            result = task.execute(args)
            status.code = TaskStatus.CODE_EXECUTION_SUCCESS
            status.result = result
        except Exception as e:
            status.code = TaskStatus.CODE_EXECUTION_FAILED
            status.message = str(e)

class LocalNode(Node):
    pass

class RemoteNode(Node):
    def __init__(self, host="localhost", port=9876):
        self.host = host
        self.port = int(port)
        self.timeout = 100

    def execute(self, task, args=None):
        # set arguments
        if args is not None:
            task.args = args

        # initialize status
        status = TaskStatus()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # sending task request
            try:
                s.connect((self.host, self.port))
                s.settimeout(1)
                status.id = task.id
                s.sendall(task.serialize())
                data = s.recv(1024)
            except Exception as e:
                status.code = TaskStatus.CODE_REQUEST_TIME_OUT
                status.message = str(e)
                print(status.to_json())
                return status

            try:
                status = pickle.loads(data)
                print(status.to_json())
                if status.code == TaskStatus.CODE_REQUEST_SUCCESS:
                    s.settimeout(self.timeout)
                    data = s.recv(1024)
                    status = pickle.loads(data)
                    print(status.to_json())
            except Exception as e:
                status.code = TaskStatus.CODE_SERVER_ERROR
                status.message = str(e)
                print(status.to_json())

            try:
                s.close()
            except:
                pass

            return status

class Registry(object):
    def __init__(self, REMOTE_HOSTNAME=None, REMOTE_PORT=None):
        self.nodes = []

    def add_node(self, node):
        try:
            if node.ping():
                self.nodes.append(node)
        except:
            pass

class Manager(object):
    def __init__(self, target):
        self.task = Task(target)
        self.inputs = []
        self.registry = Registry()

    def add_input(self, args):
        self.inputs.append(args)

    def start(self):
        task_serialized = self.task.serialize()
        print(task_serialized)
        for args in self.inputs:
            print(args)
