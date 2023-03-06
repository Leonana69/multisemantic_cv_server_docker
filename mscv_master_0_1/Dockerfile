FROM python:3.8-slim-bullseye

RUN pip install --no-cache-dir Flask==2.0.2 Pillow numpy

### dev part begins ###
### install sublime-text ###
# RUN apt update && apt install -y wget gpg
# RUN wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | gpg --dearmor | tee /etc/apt/trusted.gpg.d/sublimehq-archive.gpg > /dev/null
# RUN echo "deb https://download.sublimetext.com/ apt/stable/" | tee /etc/apt/sources.list.d/sublime-text.list
# RUN apt update
# RUN apt install -y sublime-text

# ENV HUMAN_POSE_SERVICE_HOST=localhost
# ENV HUMAN_POSE_SERVICE_PORT=50004

### dev part ends ###

WORKDIR /root
COPY ./src ./src
WORKDIR /root/src
EXPOSE 50002
CMD ["python", "./app.py"]