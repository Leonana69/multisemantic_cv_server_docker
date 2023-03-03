# build image
bash ./build.sh
# create a new container
docker run -td --privileged --net=host --ipc=host \
    --name="mscv-master" \
    mscv-master:0.1