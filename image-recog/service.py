# Image Recognition Service

import struct
import cv2
import numpy as np
import torch
from torchvision.models import efficientnet_v2_s, EfficientNet_V2_S_Weights
import dl_translate as dlt

from comm import Server



# Service class
class ImageRecog:

    def __init__(self, topN=5):

        print('-->Initializing with topN=%i' % (topN))

        # Return top N results
        self.topN = topN

        # Create model and load pre-trained weights
        weights = EfficientNet_V2_S_Weights.IMAGENET1K_V1
        self.model = efficientnet_v2_s(weights=weights)
        self.model.eval()

        # Get the preprocess function
        self.preprocess = weights.transforms()

        # Open Class labels dictionary. (human readable label given ID)
        self.classes = weights.meta["categories"]

        self.translator = dlt.TranslationModel()

    def ProcessRequest(self, img):
        # convert cv2 image to tensor
        img = torch.as_tensor(img).permute(2, 0, 1)
        # apply preprocess from the model itself
        img = self.preprocess(img)
        # add the batch dimension
        img = torch.unsqueeze(img, dim=0)

        # Predict
        try:
            with torch.no_grad():
                preds = self.model(img)
                preds = torch.squeeze(preds, dim=0)
                preds = torch.nn.functional.softmax(preds, dim=-1)
                values, indices = torch.topk(preds, k=self.topN)
                scores = [value.item() for value in values]
                labels = [self.classes[idx.item()] for idx in indices]
                # translate the labels into Japanese
                labels = self.translator.translate(labels, source=dlt.lang.ENGLISH, target=dlt.lang.JAPANESE)
                for i, (score, label) in enumerate(zip(scores, labels)):
                    msg = ('Result %i: %s (%5.2f%%)' % (i + 1, label, score))
                    yield msg

        except Exception as e:
            print(e)


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
                        imrec = ImageRecog()
                    else:
                        if data_type == 'binary':
                            # Get initial parameter as 1 int:
                            # topN
                            topN = struct.unpack('1i', data)
                            imrec = ImageRecog(topN)
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
                        print('image size', img.shape)

                        results = imrec.ProcessRequest(img)
                        n = 1
                        for res in results:
                            service.sendTextResult(res, n, imrec.topN)
                            n += 1

                        print('-->Request served.')

                    else:
                        service.sendError(
                            'Expected image data, got %s' % data_type)

                elif command == 'end':
                    print('-->Sutting down.')

        except:
            service.sendError('Interrnal error')

        finally:
            service.closeConnection()
