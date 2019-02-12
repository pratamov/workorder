from task import Task, TaskStatus
import threading
import socket
import pickle
import time

class NodePool:
    __instance = None
    __resources = list()

    def __init__(self):
        if NodePool.__instance != None:
            raise NotImplementedError("This is a singleton class.")

        # unlimited local nodes
        self.local_nodes = -1

    @staticmethod
    def get_instance():
        if NodePool.__instance == None:
            NodePool.__instance = NodePool()

        return NodePool.__instance

    def add_node(self, host, port=9876):
        self.__resources.append(RemoteNode(host, port))

    def get_node(self, timeout=100):
        if len(self.__resources) > 0:
            node = self.__resources.pop(0)
            node.timeout = timeout
            return node
        else:
            if self.local_nodes == -1:
                self.__resources.append(LocalNode())
            elif self.local_nodes > 0:
                self.__resources.append(LocalNode())
                self.local_nodes -= 1
            else:
                while len(self.__resources) < 1:
                    time.sleep(1)

            node = self.__resources.pop(0)
            node.timeout = timeout
            return node

    def return_node(self, node):
        self.__resources.append(node)

    def get_pool_size(self):
        return len(self.__resources)


class Node:

    def __init__(self):
        self.timeout = 100

    def execute(self, task, args=None):
        status = TaskStatus()
        status.id = 'LOCAL-' + task.id
        status.args = args if args is not None else task.args
        try:
            result = task.execute(args)
            status.code = TaskStatus.CODE_EXECUTION_SUCCESS
            status.message = "OK"
            status.result = result
        except Exception as e:
            status.code = TaskStatus.CODE_EXECUTION_FAILED
            status.message = str(e)

        return status

class LocalNode(Node):
    def __init__(self):
        self.host = "localhost"
        super().__init__()

class RemoteNode(Node):
    def __init__(self, host, port):
        self.host = host
        self.port = int(port)
        super().__init__()

    def execute(self, task, args=None):
        # set arguments
        if args is not None:
            task.args = args

        # initialize status
        status = TaskStatus()
        status.host = self.host

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # sending task request
            try:
                s.connect((self.host, self.port))
                s.settimeout(5)
                status.id = task.id
                s.sendall(task.serialize())
                data = s.recv(1024)
                s.settimeout(self.timeout)
            except Exception as e:
                status.code = TaskStatus.CODE_REQUEST_TIME_OUT
                status.message = str(e)
                return status

            temp = None
            try:
                status = pickle.loads(data)
                status.host = self.host
                status.id = task.id
                if status.code == TaskStatus.CODE_REQUEST_SUCCESS:
                    data = s.recv(2048)
                    temp = data
                    status = pickle.loads(data)
                    status.host = self.host
                    status.id = task.id
            except Exception as e:
                status.code = TaskStatus.CODE_SERVER_ERROR
                status.message = str(e)
                print(task.id, temp)

            try:
                s.close()
            except Exception as e:
                print(str(e))

            return status

class Process(threading.Thread):
    def __init__(self, target, args=[], manager=[], debug=False, timeout=100):
        self.task = Task(target, args)
        self.manager = manager
        self.debug = debug
        self.timeout = timeout
        threading.Thread.__init__(self)
    
    def run(self):
        pool = NodePool.get_instance()
        status = TaskStatus()

        # 10 times retry maximum until success
        for i in range(10):
            node = pool.get_node(self.timeout)
            status = node.execute(self.task)
            pool.return_node(node)

            if self.debug:
                print(status.to_json())

            if status.code == TaskStatus.CODE_EXECUTION_SUCCESS:
                if status.result is not None:
                    self.manager.append(status.result)
                break

class Manager:
    def list(self):
        return []
