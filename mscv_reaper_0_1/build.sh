# remove old container and image
docker stop -t 0 mscv-reaper
docker image rm -f mscv-reaper:0.1
docker rm -f mscv-reaper &>/dev/null

# build
docker build -t mscv-reaper:0.1 .
