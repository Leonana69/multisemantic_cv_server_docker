# remove old container and image
docker stop -t 0 mscv-onnx-server
docker image rm -f mscv-onnx-server:0.1
docker rm -f mscv-onnx-server &>/dev/null

# build
docker build -t mscv-onnx-server:0.1 .
