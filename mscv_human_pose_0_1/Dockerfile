FROM tensorflow/serving

# RUN pip install --no-cache-dir Flask==2.0.2
# RUN pip install numpy Pillow tensorflow

### dev part begins ###
### install sublime-text ###
# RUN apt update && apt install -y wget gpg
# RUN wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | gpg --dearmor | tee /etc/apt/trusted.gpg.d/sublimehq-archive.gpg > /dev/null
# RUN echo "deb https://download.sublimetext.com/ apt/stable/" | tee /etc/apt/sources.list.d/sublime-text.list
# RUN apt update
# RUN apt install -y sublime-text
### dev part ends ###

WORKDIR /root
COPY ./src/assets/models/human_pose /models/human_pose

EXPOSE 50004
# CMD ["python", "./app.py"]