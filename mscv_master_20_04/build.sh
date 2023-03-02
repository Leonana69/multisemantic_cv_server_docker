# remove old container and image
docker stop -t 0 mscv_master
docker image rm -f mscv_master:20.04
docker rm -f mscv_master &>/dev/null
# build
docker build -t mscv_master:20.04 .
