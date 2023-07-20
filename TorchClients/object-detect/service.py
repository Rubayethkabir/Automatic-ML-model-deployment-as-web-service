import io
import re
import os
from pathlib import Path

import gradio as gr
from PIL import Image

from comm import Client

def main(client, server_host, server_port, file_path):
    # Send request
    data = open(file_path, "rb").read()
    client.connectService(server_host, server_port)
    client.sendImageRequest(data)
    #  Display result
    reply = client.receiveData()
    out = []
    for command, data_type, data in reply:
        if data_type == 'image':
            out.append(Image.open(io.BytesIO(data)))
    
    return out[0]
            

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
                    outputs=gr.Image(type='pil', label='Object detection result'),
                    examples=["small_image2.jpg"],
                    ).launch(server_name="0.0.0.0")

    except InterruptedError:# Stop Service
        client.connectService(server_host, server_port)
        client.stopService()
        client.disconnectService()