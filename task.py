import math
import random
import inspect
import pickle
import uuid
import time
import itertools

from json import dumps

class Task(object):

    def __init__(self, target, args=[]):
        self.script = inspect.getsource(target)
        self.function_name = target.__name__
        self.args = args
        self.id = str(uuid.uuid4())

    def execute(self, args=None):
        if args is None:
            args = self.args
        exec(self.script)
        return locals()[self.function_name](*args)

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data):
        return pickle.loads(data)

    def to_json(self):
        return dumps({
            "function_name": self.function_name,
            "script": self.script,
            "args": self.args
        })

class TaskStatus(object):
    CODE_IDLE = 100

    # indicate the task request to node is received and ready to handle
    CODE_REQUEST_SUCCESS = 201

    # indicate the task request to node is failed,
    # perhaps the serialized task is unable to unpicle
    CODE_REQUEST_FAILED = 401

    # indicate the node is time out on request session
    CODE_REQUEST_TIME_OUT = 408

    # indicate the task is handled and success
    CODE_EXECUTION_SUCCESS = 200

    # indicate the task is failed to execute
    CODE_EXECUTION_FAILED = 400

    # There is something wrong / bugs
    CODE_SERVER_ERROR = 500

    def __init__(self, code=CODE_IDLE, message=None, result=None):
        self.code = code
        self.message = message
        self.result = result
        
        self.id = None
        self.host = "localhost"
        self.args = None

    def serialize(self):
        return pickle.dumps(self)
        
    def to_json(self):
        return dumps({
            "id": self.id,
            "host": self.host,
            "code": self.code,
            "message": self.message,
            "args": self.args,
            "result": self.result
        })
