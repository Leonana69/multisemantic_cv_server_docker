FROM tensorflow/serving

WORKDIR /root
COPY ./src/assets/models/human_pose /models/human_pose

EXPOSE 30000
CMD ["tensorflow_model_server", "--port=8500", "--rest_api_port=30000", "--model_name=human_pose", "--model_base_path=/models/human_pose"]