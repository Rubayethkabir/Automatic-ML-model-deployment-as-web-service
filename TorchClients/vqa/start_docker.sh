# build
DOCKER_BUILDKIT=1 docker build -t imagerecog_client .

# run
docker run -it --rm -e SERVER_HOST=hi-wks1 -e SERVER_PORT=10010 -p 7860:7860 imagerecog_client  
docker run -it --rm -e SERVER_HOST=163.143.88.106 -e SERVER_PORT=10010 -p 7860:7860 imagerecog_client