# This is an auto generated Dockerfile for ros:robot
# generated from docker_images/create_ros_image.Dockerfile.em
FROM ros:noetic-ros-base-focal

# install ros packages
RUN apt update && apt install -y --no-install-recommends \
    ros-noetic-desktop=1.5.0-1* \
    && rm -rf /var/lib/apt/lists/*

RUN echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc
RUN echo "source /opt/ros/noetic/setup.bash" >> ~/.bash_profile
    
RUN apt update && apt install -y git \
    cmake \
    build-essential \
    python3-pip \
    nano \
    wget

RUN pip3 install flask tensorflow

# install sublime-text
RUN wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | gpg --dearmor | tee /etc/apt/trusted.gpg.d/sublimehq-archive.gpg > /dev/null
RUN echo "deb https://download.sublimetext.com/ apt/stable/" | tee /etc/apt/sources.list.d/sublime-text.list
RUN apt update
RUN apt install sublime-text

RUN mkdir -p ~/catkin_ws/assets/models &&\
    wget -O ~/catkin_ws/assets/models/movenetv2.tflite https://tfhub.dev/google/lite-model/movenet/singlepose/thunder/3?lite-format=tflite

ADD https://api.github.com/repos/Leonana69/multisemantic_ros_server/git/refs/heads/main version.json

RUN /bin/bash -c 'source /opt/ros/noetic/setup.bash &&\
    mkdir -p ~/catkin_ws/src &&\
    cd ~/catkin_ws/src &&\
    git clone https://github.com/Leonana69/multisemantic_ros_server &&\
    cp -r ./multisemantic_ros_server/examples/mscv_pose_service ./mscv_pose_service &&\
    chmod +x ./mscv_pose_service/scripts/run.py &&\
    cd ~/catkin_ws &&\
    catkin_make &&\
    source ~/catkin_ws/devel/setup.bash'

RUN echo "source ~/catkin_ws/devel/setup.bash" >> ~/.bashrc

WORKDIR /root/catkin_ws
CMD ["bash"]