FROM tensorflow/serving:latest-gpu

RUN apt update && apt install -y wget
WORKDIR /root
COPY ./src/download.sh /root/download.sh

EXPOSE 50005
