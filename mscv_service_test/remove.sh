docker stop -t 0 mscv_service_test
docker image rm -f mscv_service_test:20.04
docker rm -f mscv_service_test &>/dev/null
