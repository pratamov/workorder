from task import Task, TaskStatus
import threading
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
            # self.__resources.append(RemoteNode('localhost', 9876))
            return self.__resources.pop(0)

    def return_node(self, node):
        self.__resources.append(node)

    def get_pool_size(self):
        return len(self.__resources)


class Node:

    def __init__(self):
        self.timeout = 100

    def execute(self, task, args=None):
        status = TaskStatus()
        status.id = task.id
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
                status.host = self.host
                status.id = task.id
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

class Process(threading.Thread):
    def __init__(self, target, args=[], manager=[], debug=False):
        self.task = Task(target, args)
        self.manager = manager
        self.debug = debug
        threading.Thread.__init__(self)
    
    def run(self):
        pool = NodePool.get_instance()
        status = TaskStatus()

        # 10 times retry maximum until success
        for i in range(10):
            node = pool.get_node()
            status = node.execute(self.task)
            pool.return_node(node)

            if self.debug:
                print(status.to_json())

            if status.code == TaskStatus.CODE_EXECUTION_SUCCESS:
                self.manager.append(status.result)
                break

class Manager:
    def list(self):
        return []