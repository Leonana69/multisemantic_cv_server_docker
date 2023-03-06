# build image
bash ./build.sh
# create a new container
docker run -td --privileged --net=host --ipc=host \
    --name="mscv-slam" \
    mscv-slam:0.1 \