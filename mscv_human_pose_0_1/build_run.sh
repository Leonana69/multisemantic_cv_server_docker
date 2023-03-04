# build
bash ./build.sh
# Create a new container
docker run -td --privileged --net=host --ipc=host \
    --name="mscv-human-pose" \
    mscv-human-pose:0.1