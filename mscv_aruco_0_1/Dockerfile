FROM python:3.11-slim-bullseye
RUN pip install Flask numpy opencv-python
RUN apt update
RUN apt install -y libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev

### dev part begins ###
### install sublime-text ###
# RUN apt update && apt install -y wget gpg
# RUN wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | gpg --dearmor | tee /etc/apt/trusted.gpg.d/sublimehq-archive.gpg > /dev/null
# RUN echo "deb https://download.sublimetext.com/ apt/stable/" | tee /etc/apt/sources.list.d/sublime-text.list
# RUN apt update
# RUN apt install -y sublime-text

### dev part ends ###

ENV MAIN_PORT=50010

WORKDIR /root
COPY ./src ./src
EXPOSE $MAIN_PORT

CMD ["python", "./src/app.py"]