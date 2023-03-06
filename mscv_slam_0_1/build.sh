# remove old container and image
docker stop -t 0 mscv-slam
docker image rm -f mscv-slam:0.1
docker rm -f mscv-slam &>/dev/null

# build
docker build -t mscv-slam:0.1 .