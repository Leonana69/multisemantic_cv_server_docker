FROM tensorflow/serving

WORKDIR /root
COPY ./src/assets/models/human-pose /models/human-pose

EXPOSE 50004
# tensorflow_model_server --port=8500 --rest_api_port=50004 --model_name=human-pose --model_base_path=/models/human-pose
CMD ["tensorflow_model_server", "--port=8500", "--rest_api_port=50004", "--model_name=human-pose", "--model_base_path=/models/human-pose"]