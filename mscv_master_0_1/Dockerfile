FROM python:3.11-slim-bullseye

RUN apt update
RUN apt install -y build-essential
RUN apt install -y libpq-dev
RUN pip install Flask Pillow numpy kubernetes
RUN pip install psycopg2
RUN pip install types-psycopg2

### dev part begins ###
### install sublime-text ###
# RUN apt update && apt install -y wget gpg
# RUN wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | gpg --dearmor | tee /etc/apt/trusted.gpg.d/sublimehq-archive.gpg > /dev/null
# RUN echo "deb https://download.sublimetext.com/ apt/stable/" | tee /etc/apt/sources.list.d/sublime-text.list
# RUN apt update
# RUN apt install -y sublime-text

### dev part ends ###

WORKDIR /root
COPY ./src ./src
EXPOSE 50001

# ENV HUMAN_POSE_SERVICE_HOST=localhost
# ENV HUMAN_POSE_SERVICE_PORT=50004

CMD ["python", "./src/app.py"]