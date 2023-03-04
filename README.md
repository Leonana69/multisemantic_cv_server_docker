# multisemantic_server_docker

docker run -p 50004:50004 \
  --name="tf-pose" \
  --mount type=bind,source=./src/assets/models/human_pose/,target=/models/human_pose \
  -e MODEL_NAME=human_pose -t tensorflow/serving