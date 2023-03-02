#!/usr/bin/env python3
from flask import Flask, render_template, request, send_from_directory
import os, json

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    packet = {
        'service_test': 517682,
    }
    return json.dumps(packet)

if __name__ == "__main__":
    print('start')
    app.run(host="0.0.0.0", port=50003)