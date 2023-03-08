#!/usr/bin/env python3
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import os, json, urllib
import time, io, base64
import numpy as np
from PIL import Image
from multisemantic_packet import MultisemanticPacket
from utils import resize_with_pad, get_pad_offset

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['UPLOAD_IMAGE_PATH'] = os.path.join(basedir, 'assets/images/')
app.config['OUTPUT_IMAGE_PATH'] = os.path.join(basedir, 'assets/outputs/')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = ['.jpg', '.jpeg', '.png']

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

            m_packet = MultisemanticPacket('web_interface', 'single_image', time.time(), function.split(','), data)
            if m_packet.is_valid():
                request_service(m_packet)

        else:
            m_packet = MultisemanticPacket()
    except RequestEntityTooLarge:
        return 'File exceeds the 16MB limit.'

    return render_template('index.html', images=[file_name], keypoints=m_packet.get_server_packet())

@app.route('/serve-image/<filename>', methods=['GET'])
def serve_image(filename):
    # TODO: change it to OUTPUT_IMAGE_PATH
    return send_from_directory(app.config['UPLOAD_IMAGE_PATH'], filename)

@app.route('/api', methods=['POST'])
def json_api():
    m_packet = MultisemanticPacket.from_json_str(request.data)
    if m_packet.is_valid():
        request_service(m_packet)
    return m_packet.get_server_packet()

def request_service(m_packet):
    has_img = False
    if 'image' not in m_packet.data:
        m_packet.msg.append('[ERROR] request without image')
    elif 'format' not in m_packet.data['image'] or 'content' not in m_packet.data['image']:
        m_packet.msg.append('[ERROR] image should has \'format\' and \'content\' fields')
    else:
        has_img = True

    if has_img:
        img_data = m_packet.data['image']
        format = img_data['format']
        content = base64.decodebytes(img_data['content'].encode())

        if format == 'raw':
            img = content
        elif format == 'default':
            img = Image.open(io.BytesIO(content)).convert('RGB')

        for f in m_packet.function:
            result = {
                'function': f,
                'output': ''
            }

            if f == 'pose':
                HOST = os.getenv('HUMAN_POSE_SERVICE_HOST')
                PORT = os.getenv('HUMAN_POSE_SERVICE_PORT')
                ADDR = 'v1/models/human_pose:predict'

                img_pose = resize_with_pad(img, [256, 256])
                DATA = json.dumps({ "instances": [np.array(img_pose).tolist()] }).encode('utf-8')
            elif f == 'slam':
                # HOST = os.getenv('SLAM_SERVICE_HOST')
                # PORT = os.getenv('SLAM_SERVICE_PORT')
                HOST = 'localhost'
                PORT = '50005'
                ADDR = 'slam_1'

                DATA = json.dumps({ 'width': img.size[0], 'height': img.size[1], 'img': np.array(img).reshape(1, -1).tolist()}).encode('utf-8')
            else:
                pass

            rq = urllib.request.Request('http://{}:{}/{}'.format(HOST, PORT, ADDR),
                                        data=DATA,
                                        headers={'Content-type' : 'application/json'})
            try:
                with urllib.request.urlopen(rq) as ret:
                    if f == 'pose':
                        key_points = json.loads(ret.read().decode('utf-8'))['predictions'][0][0]
                        offset = get_pad_offset(img.size, [256, 256])
                        for p in key_points:
                            p[0] = (p[0] - offset[1]) / (1 - 2 * offset[1]) # y
                            p[1] = (p[1] - offset[0]) / (1 - 2 * offset[0]) # x
                        result['output'] = key_points
                    elif f == 'slam':
                        print(ret.read().decode('utf-8'))
                    else:
                        pass
                    msg = '[SUCCESS] request function <{}>'.format(f)
            except Exception  as err:
                print(f'urllib.request.urlopen [FAILED] with HTTPError: {err}')
                msg = '[ERROR] function <{}> is not online'.format(f)
            m_packet.msg.append(msg)
            m_packet.results.append(result)
    return m_packet.get_server_packet()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=30000)
