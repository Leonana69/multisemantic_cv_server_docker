mkdir -p $1/1 && cd $1/1 && \
wget -O ./$1.tar.gz $2 && \
tar -xvf ./$1.tar.gz && \
rm ./$1.tar.gz

# bash download.sh human-pose https://tfhub.dev/google/movenet/singlepose/thunder/4?tf-hub-format=compressed
tensorflow_model_server --port=8500 --rest_api_port=50005 --model_name=$1 --model_base_path=/root/$1