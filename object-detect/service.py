# Image Recognition Service
# Uses ResNet50 model with 1000 classes

import io
import struct
import cv2
import numpy as np
import torch
from torchvision.models.detection import fasterrcnn_resnet50_fpn_v2, FasterRCNN_ResNet50_FPN_V2_Weights
from torchvision.utils import draw_bounding_boxes
from torchvision.transforms.functional import to_pil_image
from torchvision.io.image import read_image


from comm import Server



# Service class
class ObjectDetect:

    def __init__(self):
        # Create model and load pre-trained weights
        weights = FasterRCNN_ResNet50_FPN_V2_Weights.COCO_V1
        self.model = fasterrcnn_resnet50_fpn_v2(weights=weights, box_score_thresh=0.9)
        self.model.eval()

        # Get the preprocess function
        self.preprocess = weights.transforms()

        # Open Class labels dictionary. (human readable label given ID)
        self.classes = weights.meta["categories"]

    def ProcessRequest(self, img):
        # convert cv2 image to tensor
        img = torch.as_tensor(img).permute(2, 0, 1) # convert from H, W, C to C, H, W
        # apply preprocess from the model itself
        batch = [self.preprocess(img)]

        # Predict
        with torch.no_grad():
            prediction = self.model(batch)[0]
            labels = [self.classes[i] for i in prediction["labels"]]
            
            box = draw_bounding_boxes(
                img, 
                boxes=prediction["boxes"],
                labels=labels,
                colors="green",
                width=4, 
                font_size=30
            )
            img = to_pil_image(box.detach(), )
            print("result", img)
            buf = io.BytesIO()
            img.save(buf, format='jpeg')

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
                    print('-->Got INIT command')
                    if not data:
                        # Default initialization
                        model = ObjectDetect()
                    else:
                        if data_type == 'binary':
                            model = ObjectDetect()
                        else:
                            service.sendError(
                                'Expected binary data, got %s' % data_type)

                    service.sendConfirm()
                    print('-->Confirmation sent.')

                elif command == 'request':
                    if data_type == 'image':
                        print('-->Got REQUEST command with image data')

                        imstr = np.fromstring(data, np.uint8)
                        img = cv2.imdecode(imstr, cv2.IMREAD_COLOR)
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        print('image size', img.shape)

                        results = model.ProcessRequest(img)
                        service.sendImageResult(results, 1, 1)

                        print('-->Request served.')

                    else:
                        service.sendError(
                            'Expected image data, got %s' % data_type)

                elif command == 'end':
                    print('-->Shutting down.')

        except Exception as e:
            service.sendError('Internal error', e)

        finally:
            service.closeConnection()
