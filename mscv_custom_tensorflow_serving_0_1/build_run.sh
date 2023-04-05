# build
bash ./build.sh
# Create a new container
docker run -td --privileged --net=host --ipc=host \
    --name="mscv-custom-tensorflow-serving" \
    mscv-custom-tensorflow-serving:0.1