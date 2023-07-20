import re
import os
import numpy as np
from pathlib import Path
import io
import base64
import gradio as gr
from PIL import Image
from comm import Client
import cv2

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

def decode_img(msg):
    msg1 = msg[msg.find(b"<plain_txt_msg:img>")+len(b"<plain_txt_msg:img>"):
              msg.find(b"<!plain_txt_img>")]
    msg1 = base64.b64decode(msg1)

    jpg_as_np = np.frombuffer(msg1, dtype=np.uint8)
    img = cv2.imdecode(jpg_as_np, flags=1)

    return img


def main(client, server_host, server_port, Picture,Question):
    # Send request
    data = img_to_txt(Picture,Question)
    client.connectService(server_host, server_port)
    client.sendImageRequest(data)
    #  Display result
    reply = client.receiveData()
    out = []
    for command, data_type, data in reply:

        out.append(decode_img(data))
    if len(out) == 1:
        out = out[0]
    return out

if __name__ == "__main__":
    example = [['pokemons.jpg','a lizard with fire on its tail'],\
                ['one_piece.jpg','a man in a straw hat and a red dress'],\
                ['flowers.jpg','a white vase and pink flowers']]    
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
                    outputs='image',
                    examples= example,
                    ).launch(server_name="0.0.0.0")

    except InterruptedError:# Stop Service
        client.connectService(server_host, 10010)
        client.stopService()
        client.disconnectService()
