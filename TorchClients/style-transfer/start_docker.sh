# build
DOCKER_BUILDKIT=1 docker build -t styletransfer_client .

# run
docker run -it --rm -e SERVER_HOST=hi-wks1 -e SERVER_PORT=10010 -p 7860:7860 styletransfer_client  