import os
from io import BytesIO
import re

from flask import Flask, request
import numpy as np
import onnxruntime as ort
import json
import base64
import sys

if len(sys.argv) != 2:
    print("Error: script expects a data type")
    exit(1)

input_dtype = np.dtype(sys.argv[1])

app = Flask(__name__)

class ImageProcessingModel():
    def __init__(self):
        self.interpreter = self.load_model()

    def load_model(self):
        file_list = os.listdir('.')
        regex = re.compile('\.onnx')
        model_path = [file for file in file_list if regex.search(file)][0]
        if model_path is None:
            raise KeyError
        EP_list = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        session = ort.InferenceSession(model_path, providers=EP_list) # "./models/movenetv2.tflite"
        return session


    def run(self, input):
        return self.interpreter.run(None, {self.interpreter.get_inputs()[0].name: input})


@app.route('/api', methods=['POST'])
def json_api():
    try:
        json_data = json.loads(request.data)
    except ValueError as e:
        return json.dumps({'results': "[ERROR] invalid json struct"})
    if "instances" not in json_data:
        return json.dumps({'results': f"[ERROR] instances not found. debug info: ${json_data}"})
    instances = json_data["instances"]
    results = []
    for instance in instances:
        try:
            decoded = base64.decodebytes(instance.encode())
            decoded_instance = np.array(json.loads(decoded), dtype=input_dtype)
            result_serialized = json.dumps(model.run(decoded_instance)[0].tolist())
            results_encoded = base64.encodebytes(result_serialized.encode()).decode()
            results.append(results_encoded)
        except Exception as e:
            results.append(f'Could not run instance with error: {e}')
    print(results)
    return json.dumps({ "results": results })


model = ImageProcessingModel()
if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=os.getenv('ONNX_SERVICE_PORT', 50009))
