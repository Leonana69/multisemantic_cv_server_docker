# remove old container and image
docker stop -t 0 mscv-master
docker image rm -f mscv-master:0.1
docker rm -f mscv-master &>/dev/null

# build
docker build -t mscv-master:0.1 .
