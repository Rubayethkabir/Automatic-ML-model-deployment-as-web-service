# for build the image
DOCKER_BUILDKIT=1 docker build -t styletransfer_service .

# run server
nvidia-docker run -it --rm -p 10010:10000 styletransfer_service