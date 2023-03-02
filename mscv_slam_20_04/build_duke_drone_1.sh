# UI permisions
# XSOCK=/tmp/.X11-unix
# XAUTH=/tmp/.docker.xauth
# touch $XAUTH
# xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f $XAUTH nmerge -

# xhost +local:docker

docker stop mscv_slam_dd1
docker image rm -f mscv_slam_dd1:20.04
docker rm -f mscv_slam_dd1 &>/dev/null
docker build -t mscv_slam_dd1:20.04 .
# Create a new container
docker run -td --privileged --net=host --ipc=host \
    --name="mscv_slam_dd1" \
    --gpus=all \
    -e "DISPLAY=$DISPLAY" \
    -e "QT_X11_NO_MITSHM=1" \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -e "XAUTHORITY=$XAUTH" \
    --cap-add=SYS_PTRACE \
    -v /etc/group:/etc/group:ro \
    mscv_slam_dd1:20.04 \
    bash -it -c "cd ~/catkin_ws && roslaunch mscv_slam_service run_duke_drone_1.launch"