FROM pytorch/pytorch:1.12.0-cuda11.3-cudnn8-devel

MAINTAINER Ace

USER root

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

# Install h5py and OpenCV
RUN pip install opencv-python dl-translate

# Add service scripts
COPY common/comm.py /root/
COPY service.py /root/

# Add service start script
COPY common/start-service.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/start-service.sh

EXPOSE 10000

# Configure container startup
CMD ["start-service.sh"]
