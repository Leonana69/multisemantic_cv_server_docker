# remove old container and image
docker stop -t 0 mscv-human-pose
docker image rm -f mscv-human-pose:0.1
docker rm -f mscv-human-pose &>/dev/null

# build
docker build -t mscv-human-pose:0.1 .