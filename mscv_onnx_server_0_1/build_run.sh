# build image
bash ./build.sh
# create a new container
docker run -td --privileged --net=host --ipc=host \
    --name="mscv-onnx-server" \
    mscv-onnx-server:0.1
