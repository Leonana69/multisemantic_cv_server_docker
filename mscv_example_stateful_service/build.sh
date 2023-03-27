# remove old container and image
docker stop -t 0 mscv-example-stateful-service
docker image rm -f mscv-example-stateful-service:0.1
docker rm -f mscv-example-stateful-service &>/dev/null

# build
docker build -t mscv-example-stateful-service:0.1 .