#!/usr/bin/env python3
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import logging
import os, json, urllib
from urllib.error import URLError
import time, io, base64
import numpy as np
from PIL import Image
from multisemantic_packet import MultisemanticPacket, parse_model_info
from utils import resize_with_pad, get_pad_offset
import psycopg2
from psycopg2.extras import DictCursor

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['UPLOAD_IMAGE_PATH'] = os.path.join(basedir, 'assets/images/')
app.config['OUTPUT_IMAGE_PATH'] = os.path.join(basedir, 'assets/outputs/')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = ['.jpg', '.jpeg', '.png']

from kubernetes import client, config
from kubernetes.client.rest import ApiException
config.load_incluster_config() # Load the kubeconfig file
# Create a Kubernetes API client objects using the service account credentials
apps_api = client.AppsV1Api()
core_api = client.CoreV1Api()
autoscaling_api = client.AutoscalingV1Api()

active_custom_deployments = {}

def get_db_connection():
    return psycopg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME")
    )

def find_service(deployment_name, db_cursor):
    split_service = deployment_name.split("-")
    user = split_service[0] 
    func = split_service[1]
    db_cursor.execute("SELECT * FROM services WHERE service_user=%s AND func=%s", [user, func])
    return db_cursor.fetchone()

def refresh_service_last_touched(service_entry_id, db_conn, db_cursor):
    db_cursor.execute("UPDATE services SET last_touched=NOW() WHERE id=%s", [service_entry_id])
    db_conn.commit()

def create_new_service(user, func, db_conn, db_cursor):
    db_cursor.execute("INSERT INTO services (service_user, func, last_touched) VALUES (%s, %s, NOW())", [user, func])
    db_conn.commit()

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
    elif mscv_packet.mode == "custom":
        # TODO: remove image logic
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
            call_custom_service(mscv_packet, img)
        
    return mscv_packet.get_server_packet()

def call_custom_service(mscv_packet, img):
    for func in mscv_packet.function:
        func_result = {
            'function': func,
            'output': ''
        }

        model_info = mscv_packet.data['model_info']
        service_name = mscv_packet.user + '-' + func + '-svc'
        custom_tensorflow_serving_deployment(mscv_packet, func, model_info['url'])

        HOST = service_name
        PORT = os.getenv('TF_SERVICE_PORT')
        ADDR = f'v1/models/{model_info["name"]}:predict'

        img_pose = resize_with_pad(img, [256, 256])
        DATA = json.dumps({ "instances": [np.array(img_pose).tolist()] }).encode('utf-8')

            

        rq = urllib.request.Request('http://{}:{}/{}'.format(HOST, PORT, ADDR),
                                    data=DATA,
                                    headers={'Content-type' : 'application/json'})
        timeout = time.time() + 5
        while timeout > time.time():
            try:
                with urllib.request.urlopen(rq) as ret:
                    key_points = json.loads(ret.read().decode('utf-8'))['predictions'][0][0]
                    offset = get_pad_offset(img.size, [256, 256])
                    for p in key_points:
                        p[0] = (p[0] - offset[1]) / (1 - 2 * offset[1]) # y
                        p[1] = (p[1] - offset[0]) / (1 - 2 * offset[0]) # x
                    func_result['output'] = key_points
                    msg = '[SUCCESS] request function <{}>'.format(func)
                break
            except Exception  as err:
                msg = '[ERROR] function <{}> is not online'.format(func)
                if isinstance(err, URLError) and isinstance(err.reason, ConnectionRefusedError):
                    continue
                logging.error(f'urllib.request.urlopen [FAILED] with HTTPError: {err}')
                break


        mscv_packet.msg.append(msg)
        mscv_packet.results.append(func_result)

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
            logging.error(f'urllib.request.urlopen [FAILED] with HTTPError: {err}')
            msg = '[ERROR] function <{}> is not online'.format(func)


        mscv_packet.msg.append(msg)
        mscv_packet.results.append(func_result)


def custom_tensorflow_serving_deployment(mscv_packet, func, model_url):
    deployment_name = mscv_packet.user + '-' + func + '-deployment'
    model_info = mscv_packet.data['model_info']
    db_conn = get_db_connection()
    db_cursor = db_conn.cursor(cursor_factory=DictCursor)
    service_entry = find_service(deployment_name, db_cursor)
    if service_entry is not None:
        refresh_service_last_touched(service_entry["id"], db_conn, db_cursor)
        mscv_packet.msg.append('[SUCCESS] custom tensorflow serving deployment created')
        return

    deployment = client.V1Deployment(
        api_version = "apps/v1",
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
                            command = ["bash", "./download.sh", func, model_url],
                            resources = client.V1ResourceRequirements(limits = { "nvidia.com/gpu": 1 })
                        )
                    ]
                )
            )
        )
    )

    # Create the deployment in the Kubernetes cluster
    try:
        api_response = apps_api.create_namespaced_deployment(
            namespace = 'default',
            body = deployment
        )
        mscv_packet.msg.append('[SUCCESS] custom tensorflow serving deployment created')
    except ApiException as e:
        mscv_packet.msg.append('[ERROR] custom tensorflow serving deployment failed with exception: {}'.format(e))
        return
    
    # Add entry here so deployment will still be deleted if other resource creation fails.
    create_new_service(mscv_packet.user, func, db_conn, db_cursor)


    hpa_name = mscv_packet.user + '-' + func + '-hpa'
    autoscaler = client.V1HorizontalPodAutoscaler(
        api_version = "autoscaling/v1",
        kind = "HorizontalPodAutoscaler",
        metadata = client.V1ObjectMeta(name = hpa_name),
        spec = client.V1HorizontalPodAutoscalerSpec(
            scale_target_ref = client.V1CrossVersionObjectReference(
                api_version = "apps/v1",
                kind = "Deployment",
                name = deployment_name,
            ),
            min_replicas = int(1),
            max_replicas = int(10),
            target_cpu_utilization_percentage = int(20),
        )
    )

    try:
        api_response = autoscaling_api.create_namespaced_horizontal_pod_autoscaler(
            namespace = 'default',
            body = autoscaler
        )
        mscv_packet.msg.append('[SUCCESS] custom tensorflow hpa created')
    except ApiException as e:
        mscv_packet.msg.append('[ERROR] custom tensorflow hpa failed with exception: {}'.format(e))
        delete_custom_tensorflow_serving_deployment(mscv_packet, func)
    
    # Save after deployment in case failure to delete deployment on service failure. Will allow reaper to be aware of deployment.
    active_custom_deployments[deployment_name] = model_info['url']

    service_name = mscv_packet.user + '-' + func + '-svc'
    service = client.V1Service(
        api_version = "v1",
        kind = "Service",
        metadata = client.V1ObjectMeta(name = service_name),
        spec = client.V1ServiceSpec(
            selector = {'app': deployment_name},
            type = "ClusterIP",
            ports = [
                client.V1ServicePort(
                    protocol = "TCP",
                    port = 50004,
                    target_port = 50005,
                )
            ]
        ),
    )

    try:
        api_response = core_api.create_namespaced_service(
            namespace = 'default',
            body = service
        )
        mscv_packet.msg.append('[SUCCESS] custom tensorflow serving service created')
    except ApiException as e:
        mscv_packet.msg.append('[ERROR] custom tensorflow serving service failed with exception: {}'.format(e))
        delete_custom_tensorflow_serving_deployment(mscv_packet, func)

def delete_custom_tensorflow_serving_deployment(mscv_packet, model_name):
    deployment_name = mscv_packet.user + '-' + model_name + '-deployment'
    try:
        api_response = apps_api.delete_namespaced_deployment(
            name = deployment_name,
            namespace = 'default',
            body = client.V1DeleteOptions(
                propagation_policy = 'Foreground',
                grace_period_seconds = 1
            )
        )
        del active_custom_deployments[deployment_name]
        mscv_packet.msg.append('[SUCCESS] custom tensorflow serving deployment deleted')
    except ApiException as e:
        mscv_packet.msg.append('[ERROR] custom tensorflow serving deployment failed with exception: {}'.format(e))

if __name__ == "__main__":    
    app.run(host="0.0.0.0", port=50001)
