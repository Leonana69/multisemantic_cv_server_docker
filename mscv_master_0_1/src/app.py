#!/usr/bin/env python3
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import os, json, urllib
import time, io, base64
import numpy as np
from PIL import Image
from multisemantic_packet import MultisemanticPacket, parse_model_info
from utils import resize_with_pad, get_pad_offset

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['UPLOAD_IMAGE_PATH'] = os.path.join(basedir, 'assets/images/')
app.config['OUTPUT_IMAGE_PATH'] = os.path.join(basedir, 'assets/outputs/')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = ['.jpg', '.jpeg', '.png']

from kubernetes import client, config
from kubernetes.client.rest import ApiException
config.load_incluster_config() # Load the kubeconfig file
api = client.AppsV1Api() # Create a Kubernetes API client object using the service account credentials

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files['filename']
        function = request.form['function']

        if file:
            extension = os.path.splitext(file.filename)[1].lower()
            if extension not in app.config['ALLOWED_EXTENSIONS']:
                return 'File is not an image.'
            
            img = file.read()

            ## seek before save
            file_name = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_IMAGE_PATH'], file_name)
            file.seek(0)
            file.save(file_path)
            
            data = {
                'image': {
                    'format': 'default',
                    'content': base64.encodebytes(img).decode()
                },
            }

            mscv_packet = MultisemanticPacket('web-interface', 'image', time.time(), function.split(','), data)
            if mscv_packet.is_valid():
                request_service(mscv_packet)

        else:
            mscv_packet = MultisemanticPacket()
    except RequestEntityTooLarge:
        return 'File exceeds the 16MB limit.'

    return render_template('index.html', images=[file_name], keypoints=mscv_packet.get_server_packet())

@app.route('/serve-image/<filename>', methods=['GET'])
def serve_image(filename):
    # TODO: change it to OUTPUT_IMAGE_PATH
    return send_from_directory(app.config['UPLOAD_IMAGE_PATH'], filename)

@app.route('/api', methods=['POST'])
def json_api():
    mscv_packet = MultisemanticPacket.from_json_str(request.data)
    if mscv_packet.is_valid():
        request_service(mscv_packet)
    return mscv_packet.get_server_packet()

def request_service(mscv_packet):
    if mscv_packet.mode == 'deploy' and parse_model_info(mscv_packet):
        model_info = mscv_packet.data['model_info']
        custom_tensorflow_serving_deployment(mscv_packet, model_info['name'], model_info['url'])
    elif mscv_packet.mode == 'stop' and parse_model_info(mscv_packet, False):
        model_info = mscv_packet.data['model_info']
        delete_custom_tensorflow_serving_deployment(mscv_packet, model_info['name'])
    elif mscv_packet.mode == 'image' or mscv_packet.mode == 'image_imu':
        # check if image data exists
        has_img = False
        if 'image' in mscv_packet.data:
            if 'format' not in mscv_packet.data['image'] or 'content' not in mscv_packet.data['image']:
                mscv_packet.msg.append('[ERROR] image should has \'format\' and \'content\' fields')
            else:
                # parse image data
                img_data = mscv_packet.data['image']
                format = img_data['format']
                content = base64.decodebytes(img_data['content'].encode())
                if format == 'raw':
                    img = content
                elif format == 'default':
                    img = Image.open(io.BytesIO(content)).convert('RGB')
                else:
                    mscv_packet.msg.append('[ERROR] unknown image format')
                    has_img = False
                has_img = True
        
        if has_img:
            call_service(mscv_packet, img)
        
    return mscv_packet.get_server_packet()

def call_service(mscv_packet, img):
    for func in mscv_packet.function:
        func_result = {
            'function': func,
            'output': ''
        }

        if func == 'pose':
            HOST = os.getenv('HUMAN_POSE_SERVICE_HOST')
            PORT = os.getenv('HUMAN_POSE_SERVICE_PORT')
            ADDR = 'v1/models/human-pose:predict'

            img_pose = resize_with_pad(img, [256, 256])
            DATA = json.dumps({ "instances": [np.array(img_pose).tolist()] }).encode('utf-8')
        elif func == 'slam':
            # TODO: change it to env variables
            # HOST = os.getenv('SLAM_SERVICE_HOST')
            # PORT = os.getenv('SLAM_SERVICE_PORT')
            if mscv_packet.user == 'duke_drone_1':
                HOST = '172.29.249.77'
                PORT = '50005'
                ADDR = 'slam'
            elif mscv_packet.user == 'duke_drone_2':
                HOST = '172.29.249.77'
                PORT = '50006'
                ADDR = 'slam'
            else:
                mscv_packet.msg.append('[ERROR] unknown user')
                continue

            DATA = json.dumps({
                'width': img.size[0],
                'height': img.size[1],
                'img': np.array(img).reshape(1, -1).tolist(),
                'timestamp': mscv_packet.timestamp,
                'reset': 1 if mscv_packet.mode == 'stop' else 0
            }).encode('utf-8')
        else:
            pass

        rq = urllib.request.Request('http://{}:{}/{}'.format(HOST, PORT, ADDR),
                                    data=DATA,
                                    headers={'Content-type' : 'application/json'})
        try:
            with urllib.request.urlopen(rq) as ret:
                if func == 'pose':
                    key_points = json.loads(ret.read().decode('utf-8'))['predictions'][0][0]
                    offset = get_pad_offset(img.size, [256, 256])
                    for p in key_points:
                        p[0] = (p[0] - offset[1]) / (1 - 2 * offset[1]) # y
                        p[1] = (p[1] - offset[0]) / (1 - 2 * offset[0]) # x
                    func_result['output'] = key_points
                elif func == 'slam':
                    func_result['output'] = json.loads(ret.read().decode('utf-8'))['output']
                else:
                    pass
                msg = '[SUCCESS] request function <{}>'.format(func)
        except Exception  as err:
            print(f'urllib.request.urlopen [FAILED] with HTTPError: {err}')
            msg = '[ERROR] function <{}> is not online'.format(func)
        mscv_packet.msg.append(msg)
        mscv_packet.results.append(func_result)


def custom_tensorflow_serving_deployment(mscv_packet, model_name, model_url):
    deployment_name = mscv_packet.user + '-' + model_name + '-deployment'
    deployment = client.V1Deployment(
        metadata = client.V1ObjectMeta(name = deployment_name),
        spec = client.V1DeploymentSpec(
            replicas = int(1),
            selector = client.V1LabelSelector(
                match_labels = {'app': deployment_name}
            ),
            template = client.V1PodTemplateSpec(
                metadata = client.V1ObjectMeta(
                    labels = {'app': deployment_name}
                ),
                spec = client.V1PodSpec(
                    containers = [
                        client.V1Container(
                            name = deployment_name,
                            image = "docker.io/library/mscv-custom-tensorflow-serving:0.1",
                            command = ["bash", "./download.sh", model_name, model_url],
                        )
                    ]
                )
            )
        )
    )

    # Create the deployment in the Kubernetes cluster
    try:
        api_response = api.create_namespaced_deployment(
            namespace = 'default',
            body = deployment
        )
        mscv_packet.msg.append('[SUCCESS] custom tensorflow serving deployment created')
    except ApiException as e:
        mscv_packet.msg.append('[ERROR] custom tensorflow serving deployment failed with exception: {}'.format(e))

    # TODO: deploy service
    pass

def delete_custom_tensorflow_serving_deployment(mscv_packet, model_name):
    deployment_name = mscv_packet.user + '-' + model_name + '-deployment'
    try:
        api_response = api.delete_namespaced_deployment(
            name = deployment_name,
            namespace = 'default',
            body = client.V1DeleteOptions(
                propagation_policy = 'Foreground',
                grace_period_seconds = 1
            )
        )
        mscv_packet.msg.append('[SUCCESS] custom tensorflow serving deployment deleted')
    except ApiException as e:
        mscv_packet.msg.append('[ERROR] custom tensorflow serving deployment failed with exception: {}'.format(e))

if __name__ == "__main__":    
    app.run(host="0.0.0.0", port=50001)
