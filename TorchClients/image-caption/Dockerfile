FROM python:3.7

MAINTAINER Ace

USER root

RUN pip install gradio

# Add service scripts
COPY common/comm.py /root/
COPY service.py /root/
COPY test/*.jpg /root/

# Add service start script
COPY common/start-service.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/start-service.sh

EXPOSE 7860

# Configure container startup
CMD ["start-service.sh"]
