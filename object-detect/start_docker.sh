# for build the image
DOCKER_BUILDKIT=1 docker build -t objectdetect_service .

# run server
nvidia-docker run -it --rm -p 10010:10000 objectdetect_service