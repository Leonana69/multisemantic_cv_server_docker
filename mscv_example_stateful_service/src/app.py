#!/usr/bin/env python3
from flask import Flask, request
import json

app = Flask(__name__)

previous_request_users = []

@app.route('/', methods=['POST', 'GET'])
def index():
    json_data = json.loads(request.data)
    previous_request_users.append(json_data['user'])
    print(previous_request_users)
    packet = {
        'example_service': previous_request_users,
    }
    return json.dumps(packet)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=30000)