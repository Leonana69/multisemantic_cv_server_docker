docker stop mscv_tf
docker image rm -f mscv_tf:20.04
docker rm -f mscv_tf &>/dev/null
docker build -t mscv_tf:20.04 .
# Create a new container
docker run -td --privileged --net=host --ipc=host \
    --name="mscv_tf" \
    --gpus=all \
    -e "DISPLAY=$DISPLAY" \
    -e "QT_X11_NO_MITSHM=1" \
    -v "/tmp/.X11-unix:/tmp/.X11-unix:rw" \
    -e "XAUTHORITY=$XAUTH" \
    -e ROS_IP=127.0.0.1 \
    --cap-add=SYS_PTRACE \
    -v /etc/group:/etc/group:ro \
    mscv_tf:20.04 \
    bash -it -c "cd ~/catkin_ws && rosrun mscv_pose_service run.py"