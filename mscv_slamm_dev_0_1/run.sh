# create a new container
docker run -td --privileged --net=host --ipc=host \
    --memory=8g \
    --name="mscv-slamm-dev" \
    -e "DISPLAY=$DISPLAY" \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v /home/gc635/Downloads/duke_drone:/duke_drone \
    -v /home/gc635/Downloads/data_odometry_gray/dataset/sequences:/data_odometry_gray/dataset/sequences \
    mscv-slamm-dev:0.1 \