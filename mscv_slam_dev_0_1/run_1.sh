# create a new container
docker run -td --privileged --net=host --ipc=host \
    --name="mscv-slam-dev-1" \
    -e "DISPLAY=$DISPLAY" \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    mscv-slam-dev:0.1 \