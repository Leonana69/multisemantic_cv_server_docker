#!/usr/bin/env python3
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import os, json, urllib
import time, base64
from multisemantic_packet import MultisemanticPacket

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
        extension = os.path.splitext(file.filename)[1].lower()
        output = {}

        if file:
            if extension not in app.config['ALLOWED_EXTENSIONS']:
                return 'File is not an image.'
            
            img = file.read()
            print(img)

            ## seek before save
            file_name = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_IMAGE_PATH'], file_name)
            file.seek(0)
            file.save(file_path)
            
            data = {
                'image': {
                    'format': 'b64_str',
                    'content': base64.b64encode(img).decode('utf-8')
                },
            }

            m_packet = MultisemanticPacket('web_interface', 'single_image', time.time(), function.split(','), data)
            if m_packet.is_valid():
                request_service(m_packet)

            # marked_image = draw_pose_keypoints(image['data'], np.array(m_packet.result[0]['output']))
            # cv2.imwrite(os.path.join(app.config['OUTPUT_IMAGE_PATH'], secure_filename(file.filename)), marked_image)
            # cv2.imwrite(os.path.join(app.config['UPLOAD_IMAGE_PATH'], secure_filename(file.filename)), image['data'])
        else:
            m_packet = MultisemanticPacket()
    except RequestEntityTooLarge:
        return 'File exceeds the 16MB limit.'

    

    # headers = {'Content-type' : 'application/json'}
    # r = urllib.request.Request('http://{}:{}/'.format(os.getenv('EXAMPLE_SERVICE_HOST', '0.0.0.0'), os.getenv('EXAMPLE_SERVICE_PORT', 50003)), data=json.dumps({'1': 1}).encode('utf-8'), headers=headers)
    
    # try:
    #     with urllib.request.urlopen(r) as f:
    #         output = f.read().decode('utf-8')
    #     print(output)
    # except urllib.error.HTTPError as err:
    #     print(f'urllib.request.urlopen [FAILED] with HTTPError: {err}')
    # except urllib.error.URLError as err:
    #     print(f'urllib.request.urlopen [FAILED] with URLError: {err}')
    # except:
    #     print(f'urllib.request.urlopen [FAILED]')

    return render_template('index.html', images=[file_name], keypoints=m_packet.msg)
    # result_list = [secure_filename(file.filename)]
    # return render_template('index.html', images=result_list, keypoints=json.dumps(m_packet.result))

@app.route('/serve-image/<filename>', methods=['GET'])
def serve_image(filename):
    # TODO: change it to OUTPUT_IMAGE_PATH
    return send_from_directory(app.config['UPLOAD_IMAGE_PATH'], filename)

# @app.route('/api', methods=['POST'])
# def json_api():
#     m_packet = MultisemanticPacket.from_json_str(request.data)
#     if m_packet.is_valid():
#         multisemantic_handle.run(m_packet)

#     return m_packet.get_server_packet()

def request_service(m_packet):
    for f in m_packet.function:
        result = {
            'function': f,
            'output': ''
        }

        print(type(m_packet.data['image']['content']))
        print(m_packet.data['image']['content'])

        if f == 'pose':
            HOST = os.getenv('HUMAN_POSE_SERVICE_HOST')
            PORT = os.getenv('HUMAN_POSE_SERVICE_PORT')
            DATA = json.dumps(m_packet.data).encode('utf-8')
        elif f == 'slam':
            pass
        
        print(json.dumps(m_packet.data))
        print(type(DATA))
        r = urllib.request.Request('http://{}:{}/'.format(HOST, PORT),
                                       data=DATA,
                                       headers={'Content-type' : 'application/json'})
        try:
            with urllib.request.urlopen(r) as f:
                result['output'] = f.read().decode('utf-8')
                m_packet.msg.append('[MSG] function <{}> request [SUCCESS]'.format(f))
        except urllib.error.HTTPError as err:
            m_packet.msg.append('[ERROR] function <{}> is not online'.format(f))
            print(f'urllib.request.urlopen [FAILED] with HTTPError: {err}')
        except urllib.error.URLError as err:
            m_packet.msg.append('[ERROR] function <{}> is not online'.format(f))
            print(f'urllib.request.urlopen [FAILED] with URLError: {err}')
        except:
            m_packet.msg.append('[ERROR] function <{}> is not online'.format(f))
            print('urllib.request.urlopen [FAILED]')

        m_packet.results.append(result)
    return m_packet.get_server_packet()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=50002)
