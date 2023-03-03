# remove old container and image
docker stop -t 0 mscv-custom-tensorflow-serving
docker image rm -f mscv-custom-tensorflow-serving:0.1
docker rm -f mscv-custom-tensorflow-serving &>/dev/null

# build
docker build -t mscv-custom-tensorflow-serving:0.1 .