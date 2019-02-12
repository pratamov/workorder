from task import Task, TaskStatus

import socket
import threading
import time
import pickle

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 9876))
server.listen(2)

def handle(conn):
    # receiving task object
    request = conn.recv(1024)
    try:
        task = pickle.loads(request)
        status_code, status_message, task_id = TaskStatus.CODE_REQUEST_SUCCESS, 'OK', task.id
    except Exception as e:
        status_code, status_message, task_id = TaskStatus.CODE_REQUEST_FAILED, str(
            e), None

    # send status
    status = TaskStatus(status_code, status_message)
    status.id = task_id
    status.args = task.args
    try:
        conn.sendall(status.serialize())
    except Exception as e:
        status_code, status_message, task_id = TaskStatus.CODE_REQUEST_FAILED, str(
            e), None

    # execute task
    if status_code == TaskStatus.CODE_REQUEST_SUCCESS:
        try:
            result_data = task.execute()
            status.code = TaskStatus.CODE_EXECUTION_SUCCESS
            status.result = result_data
            conn.sendall(status.serialize())
            print(task_id, 'success')
        except Exception as e:
            try:
                status.code = TaskStatus.CODE_EXECUTION_FAILED
                status.message = str(e)
                conn.sendall(status.serialize())
            except:
                pass

    conn.close()


while True:
    conn, addr = server.accept()
    threading.Thread(target=handle, args=(conn,)).start()
