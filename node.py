from task import Task, TaskStatus

import asyncio
import socket
import pickle

class NodePool:
    __instance = None
    __resources = list()

    def __init__(self):
        if NodePool.__instance != None:
            raise NotImplementedError("This is a singleton class.")
    
    @staticmethod
    def get_instance():
        if NodePool.__instance == None:
            NodePool.__instance = NodePool()
        
        return NodePool.__instance

    def get_node(self):
        if len(self.__resources) > 0:
            return self.__resources.pop(0)
        else:
            self.__resources.append(LocalNode())
            return self.__resources.pop(0)

    def return_node(self, node):
        self.__resources.append(node)
    
    def get_pool_size(self):
        return len(self.__resources)

class Node:

    async def execute(self, task, args):
        status = TaskStatus()
        try:
            result = task.execute(args)
            status.code = TaskStatus.CODE_EXECUTION_SUCCESS
            status.result = result
        except Exception as e:
            status.code = TaskStatus.CODE_EXECUTION_FAILED
            status.message = str(e)
        
        return status

class LocalNode(Node):
    pass

class RemoteNode(Node):
    def __init__(self, host, port):
        self.host = host
        self.port = int(port)
        self.timeout = 100

    def execute(self, task, args):
        # set arguments
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
                return status

            try:
                status = pickle.loads(data)
                if status.code == TaskStatus.CODE_REQUEST_SUCCESS:
                    s.settimeout(self.timeout)
                    data = s.recv(1024)
                    status = pickle.loads(data)
            except Exception as e:
                status.code = TaskStatus.CODE_SERVER_ERROR
                status.message = str(e)

            try:
                s.close()
            except:
                pass

            return status
