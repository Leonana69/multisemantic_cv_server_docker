# UI permisions
XSOCK=/tmp/.X11-unix
XAUTH=/tmp/.docker.xauth
touch $XAUTH
xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f $XAUTH nmerge -

xhost +local:docker

# remove old container and image
docker stop -t 0 mscv-slamm-dev
docker image rm -f mscv-slamm-dev:0.1
docker rm -f mscv-slamm-dev &>/dev/null

# build
docker build -t mscv-slamm-dev:0.1 .