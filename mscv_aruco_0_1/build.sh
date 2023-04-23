# remove old container and image
docker stop -t 0 mscv-aruco
docker image rm -f mscv-aruco:0.1
docker rm -f mscv-aruco &>/dev/null

# build
docker build -t mscv-aruco:0.1 .
