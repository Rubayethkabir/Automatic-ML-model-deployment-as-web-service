import io
import re
import os
from pathlib import Path
from itertools import product

import gradio as gr
from PIL import Image

from comm import Client

def main(client, server_host, server_port, content_file_path, style_file_path):
    # Reinitialize the model everytime with the new style image
    client.connectService(server_host, server_port)
    style_image = open(style_file_path, "rb").read()
    client.initService(style_image, 'image')
    reply = client.receiveData()
    for command, data_type, data in reply:
        print(command)

    # Send request
    content_image = open(content_file_path, "rb").read()
    client.connectService(server_host, server_port)
    client.sendImageRequest(content_image)

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

        content_image = gr.Image(type='filepath', label='Content image')
        content_examples = ['content/chicago.jpg']
        style_image = gr.Image(type='filepath', label='Style image')
        style_examples = ['style/muse.jpg', 'style/wave.jpg']
        gr.Interface(fn=lambda content_image, style_image: main(client, server_host, server_port, content_image, style_image), 
                    inputs=[content_image, style_image],
                    outputs=gr.Image(type='pil', label='Style transfer result'),
                    examples=[list(e) for e in product(content_examples, style_examples)],
                    ).launch(server_name="0.0.0.0")

    except InterruptedError:# Stop Service
        client.connectService(server_host, server_port)
        client.stopService()
        client.disconnectService()