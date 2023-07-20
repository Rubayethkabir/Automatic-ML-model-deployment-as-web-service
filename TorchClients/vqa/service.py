import re
import os
from pathlib import Path
import base64
import gradio as gr

from comm import Client

def img_to_txt(filename,s):
    msg = b"<plain_txt_msg:img>"
    with open(filename, "rb") as imageFile:
        msg = msg + base64.b64encode(imageFile.read())
    msg = msg + b"<!plain_txt_img>"
    q = b"<plain_txt_msg:str>"
    q = q + base64.b64encode(s.encode('ascii'))
    q = q + b"<!plain_txt_str>"
    msg = msg+q
    return msg


def main(client, server_host, server_port, Picture,Question):
    # Send request
    data = img_to_txt(Picture,Question)
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
    example = [['cow.jpg','What is the name of the animal ?'],\
                ['joker.jpg','What color is the jacket?'],\
                ['sushi.jpg','What is the name of the food?']]    
    server_host = os.environ['SERVER_HOST']
    server_port = int(os.environ['SERVER_PORT'])

    client = Client()
    try:
        client.connectService(server_host, server_port)
        client.initService()
        reply = client.receiveData()
        for command, data_type, data in reply:
            print(command)

        gr.Interface(fn=lambda Picture,Question: main(client, server_host, server_port, Picture,Question), 
                    inputs=[gr.Image(type="filepath"),'text'],
                    outputs=gr.Textbox(),
                    examples= example,
                    ).launch(server_name="0.0.0.0")

    except InterruptedError:# Stop Service
        client.connectService(server_host, 10010)
        client.stopService()
        client.disconnectService()
