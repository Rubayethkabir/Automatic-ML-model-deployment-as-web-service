# Image Recognition Service
# Uses ResNet50 model with 1000 classes

import struct
import os
import io
from datetime import datetime



# Data utilities
import numpy as np

# Image utilities
from PIL import Image
import cv2 

# Clip Model
import torch

# Style Transfer Model
import paddlehub as hub

os.system("hub install stylepro_artistic==1.0.1")

from comm import Server


# Service class
class StyleTransfer:

    def __init__(self, style_image):
        # Create model and load pre-trained weights
        self.stylepro_artistic = hub.Module(name="stylepro_artistic")

        imstr = np.fromstring(style_image, np.uint8)
        img = cv2.imdecode(imstr, cv2.IMREAD_COLOR)
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        print('style image size', img.shape)
        self.style_image = img

    def ProcessRequest(self, content_image):
        results = self.stylepro_artistic.style_transfer(
            images=[{
                "content": content_image,
                "styles": [self.style_image]
            }])
        result = results[0]['data']
        image = Image.fromarray(result[:,:,::-1]).convert("RGB")
        buf = io.BytesIO()
        image.save(buf, format='jpeg')

        return buf.getvalue()

if __name__ == '__main__':

    service = Server()
    command = None

    while command != 'end':
        service.waitConnection()

        try:
            messages = service.receiveData()
            for command, data_type, data in messages:
                if command == 'init':
                    print('--> Got INIT command')
                    if data_type == 'image':
                        # Initialization
                        model = StyleTransfer(data)
                    else:
                        service.sendError(
                            'Expected image data with INIT command!')

                    service.sendConfirm()
                    print('-->Confirmation sent.')

                elif command == 'request':
                    if data_type == 'image':
                        print('-->Got REQUEST command with image data')

                        imstr = np.fromstring(data, np.uint8)
                        img = cv2.imdecode(imstr, cv2.IMREAD_COLOR)
                        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        print('content image size', img.shape)

                        results = model.ProcessRequest(img)
                        service.sendImageResult(results, 1, 1)

                        print('-->Request served.')

                    else:
                        service.sendError(
                            'Expected image data, got %s' % data_type)

                elif command == 'end':
                    print('-->Shutting down.')

        except:
            service.sendError('Internal error')

        finally:
            service.closeConnection()
