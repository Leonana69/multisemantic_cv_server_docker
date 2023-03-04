docker exec -it mscv-human-pose bash -c "tensorflow_model_server --port=8500 --rest_api_port=50004 --model_name=human_pose --model_base_path=/models/human_pose"
