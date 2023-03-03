# build
bash ./build.sh
# Create a new container
docker run -td --privileged --net=host --ipc=host \
    --name="mscv-example-service" \
    mscv-example-service:0.1
