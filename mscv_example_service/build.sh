# remove old container and image
docker stop -t 0 mscv-example-service
docker image rm -f mscv-example-service:0.1
docker rm -f mscv-example-service &>/dev/null

# build
docker build -t mscv-example-service:0.1 .