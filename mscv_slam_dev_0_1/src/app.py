#!/usr/bin/env python3
from flask import Flask, request
import json, base64, io
from PIL import Image

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    img_data = json.loads(request.data.decode('utf-8'))
    img_bytes = base64.b64decode(img_data['content'])
    img = Image.open(io.BytesIO(img_bytes))
    print(img.size)

    packet = {
        'slam_service': 'guojun.chen@yale.edu',
    }
    return json.dumps(packet)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=50005)