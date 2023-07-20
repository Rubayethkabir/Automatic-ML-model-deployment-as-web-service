## Image recognition service

This is based on [PyTorch implementation of ResNet50 model](https://pytorch.org/vision/stable/models.html).

### Building the image

```
docker build -t imagerecog_service .
```

### Running the service

Manually, this service can be started this way:
```
nvidia-docker run -it --rm -p 10010:10000 imagerecog_service
```
It will listen to the port 10010 of host it is running on.