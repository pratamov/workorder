from task import Task, TaskStatus
import socket
import struct
import pickle

def test():
    n = 0
    for i in range(100_000_000):
        n+=1
    return n

def execute(timeout=10):
    # initialize status
    status = TaskStatus()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("localhost", 9876))

        # sending task request
        try:
            s.settimeout(1)
            task = Task(test)
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
                s.settimeout(timeout)
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

execute(100)