# remove old container and image
docker stop -t 0 mscv-slam-dev
docker image rm -f mscv-slam-dev:0.1
docker rm -f mscv-slam-dev &>/dev/null

# build
docker build -t mscv-slam-dev:0.1 .