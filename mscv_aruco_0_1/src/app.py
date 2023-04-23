import cv2, os, json
import numpy as np
from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    packet = json.loads(request.data.decode('utf-8'))
    img = np.array(packet['instances']).astype(np.uint8)
    md_nuc = MarkerDetector('nuc')
    keypoints = md_nuc.detect(img)
    packet = {
        'output': []
    }

    for kp in keypoints:
        packet['output'].append(kp.pt)
    
    return json.dumps(packet)

class MarkerDetector:
    def __init__(self, type):
        # Setup SimpleBlobDetector parameters.
        params = cv2.SimpleBlobDetector_Params()
        # Change thresholds
        params.minThreshold = 180
        # Filter by Area.
        params.filterByArea = True
        # Filter by Circularity
        params.filterByCircularity = False
        # Filter by Convexity
        params.filterByConvexity = True
        params.minConvexity = 0.87
        # Filter by Inertia
        params.filterByInertia = True
        params.minInertiaRatio = 0.5
        if type == 'orin':
            # for orin
            params.minArea = 2000
            params.maxArea = 3000
        elif type == 'nuc':
            # for nuc
            params.minArea = 1000
            params.maxArea = 1500

        self.detector = cv2.SimpleBlobDetector_create(params)

    def detect(self, frame):
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        return self.detector.detect(frame_gray)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("MAIN_PORT", 50010))