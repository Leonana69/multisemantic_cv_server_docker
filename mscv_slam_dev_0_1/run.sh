# create a new container
docker run -td --privileged --net=host --ipc=host \
    --name="mscv-slam-dev" \
    -e "DISPLAY=$DISPLAY" \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v /home/gc635/Downloads/duke_drone:/duke_drone \
    mscv-slam-dev:0.1 \