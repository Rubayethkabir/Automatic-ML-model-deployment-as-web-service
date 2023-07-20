import re
import os
from pathlib import Path
import base64
import gradio as gr

from comm import Client

def img_to_txt(filename):
    msg = b"<plain_txt_msg:img>"
    with open(filename, "rb") as imageFile:
        msg = msg + base64.b64encode(imageFile.read())
    msg = msg + b"<!plain_txt_msg>"
    return msg

def main(client, server_host, server_port, file_path):
    # Send request
    data = img_to_txt(file_path)
    client.connectService(server_host, server_port)
    client.sendImageRequest(data)
    #  Display result
    reply = client.receiveData()
    out = []
    for command, data_type, data in reply:
        out.append(data)
    if len(out) == 1:
        out = out[0]
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
                    inputs=gr.Image(type="filepath"),
                    outputs=gr.Textbox(),
                    examples=['cow.jpg',"car.jpg", "elephant.jpg"],
                    ).launch(server_name="0.0.0.0")

    except InterruptedError:# Stop Service
        client.connectService(server_host, 10010)
        client.stopService()
        client.disconnectService()
