## Image recognition service

This is the client to call API from a service [PyTorch implementation of ResNet50 model](https://pytorch.org/vision/stable/models.html).

### Building the image

```
docker build -t imagerecog_client .
```

### Running the service

Manually, this service can be started this way:
```
docker run -it --rm -e SERVER_HOST=<the server host ip> -e SERVER_PORT=<the server host port> -p 7861:7860 imagerecog_client
```
It will listen to the port 7861 of host it is running on.