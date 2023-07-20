import re
import os
from pathlib import Path

import gradio as gr

from comm import Client

def main(client, server_host, server_port, file_path):
    # Send request
    data = open(file_path, "rb").read()
    client.connectService(server_host, server_port)
    client.sendImageRequest(data)
    #  Display result
    reply = client.receiveData()
    out = {}
    for command, data_type, data in reply:
        match = re.search(r".*:\s(.*)\s\((.*)\%\)", data)
        if match is not None:
            out[match.group(1)] = float(match.group(2))
    return out

if __name__ == "__main__":
    server_host = os.environ['SERVER_HOST']
    server_port = int(os.environ['SERVER_PORT'])

    client = Client()
    try:
        client.connectService(server_host, server_port)
        client.initService()
        reply = client.receiveData()
        for command, data_type, data in reply:
            print(command)

        gr.Interface(fn=lambda file_path: main(client, server_host, server_port, file_path), 
                    inputs=gr.Image(type="filepath", label="Input image"),
                    outputs=gr.Label(label="Image recognition result"),
                    examples=["car.jpg"],
                    ).launch(server_name="0.0.0.0")

    except InterruptedError:# Stop Service
        client.connectService(server_host, server_port)
        client.stopService()
        client.disconnectService()