#!/usr/bin/env python3
from flask import Flask
import json

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    packet = {
        'human_pose_service': 'guojun.chen@yale.edu',
    }
    return json.dumps(packet)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=50004)