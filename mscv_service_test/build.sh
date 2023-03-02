bash ./remove.sh
# build
docker build -t mscv_service_test:20.04 .
# Create a new container
docker run -td --privileged --net=host --ipc=host \
    --name="mscv_service_test" \
    mscv_service_test:20.04
