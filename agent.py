from task import Task, TaskStatus

import asyncio
import socket
import pickle

import math

async def handle_client(client):
    request = (await loop.sock_recv(client, 2048))
    # unpickle task object
    try:
        task = pickle.loads(request)
        status_code, status_message, task_id = TaskStatus.CODE_REQUEST_SUCCESS, 'OK', task.id
    except Exception as e:
        status_code, status_message, task_id = TaskStatus.CODE_REQUEST_FAILED, str(e), None

    # send status
    status = TaskStatus(status_code, status_message)
    status.id = task_id
    await loop.sock_sendall(client, status.serialize())

    # execute task
    if status_code == TaskStatus.CODE_REQUEST_SUCCESS:
        try:
            result_data = task.execute()
            status.code = TaskStatus.CODE_EXECUTION_SUCCESS
            status.result = result_data
            await loop.sock_sendall(client, status.serialize())
        except Exception as e:
            status.code = TaskStatus.CODE_EXECUTION_FAILED
            status.message = str(e)
            await loop.sock_sendall(client, status.serialize())

async def run():
    while True:
        try:
            client, _ = await loop.sock_accept(server)
            loop.create_task(handle_client(client))
        except Exception as e:
            print("ERROR", str(e))

loop = asyncio.get_event_loop()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', 9876))
server.listen(8)
server.setblocking(False)
loop.run_until_complete(run())
