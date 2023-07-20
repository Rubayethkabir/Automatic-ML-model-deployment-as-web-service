# for build the image
DOCKER_BUILDKIT=1 docker build -t imagerecog_service .

# run server
nvidia-docker run -it --rm -p 10010:10000 imagerecog_service