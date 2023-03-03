# remove old container and image
docker stop -t 0 mscv-slam-dev-1 mscv-slam-dev-2
docker image rm -f mscv-slam-dev:0.1
docker rm -f mscv-slam-dev-1 mscv-slam-dev-2 &>/dev/null

# build
docker build -t mscv-slam-dev:0.1 .