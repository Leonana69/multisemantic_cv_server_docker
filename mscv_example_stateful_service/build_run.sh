# build
bash ./build.sh
# Create a new container
docker run -td --privileged --net=host --ipc=host \
    --name="mscv-example-stateful-service" \
    mscv-example-stateful-service:0.1
