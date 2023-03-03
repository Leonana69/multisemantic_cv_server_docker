import json

class MultisemanticPacket():
    mode = ['image', 'image_imu', 'deploy', 'stop', 'custom']
    function = ['pose', 'slam']
    users_list = ['duke-drone-1', 'duke-drone-2', 'web-interface', 'guojun', 'tucker']

    def __init__(self, user='none', mode='none', timestamp=0.0, function=[], data={}):
        self.user = user
        self.mode = mode
        self.timestamp = timestamp
        self.function = function
        self.data = data
        self.msg = []
        self.results = []

    def from_json_str(str_packet):
        user = ''
        mode = ''
        timestamp = 0.0
        function = []
        data = {}

        # parse client packet
        try:
            json_packet = json.loads(str_packet)
        except ValueError as e:
            msp = MultisemanticPacket()
            msp.msg.append('[ERROR] invalid json struct')
            return msp
        
        # check all fields
        if 'user' in json_packet:
            user = json_packet['user']

        if 'mode' in json_packet:
            mode = json_packet['mode']

        if 'timestamp' in json_packet:
            timestamp = json_packet['timestamp']

        if 'function' in json_packet and type(json_packet['function']) is list:
            function = json_packet['function']

        if 'data' in json_packet:
            data = json_packet['data']
        return MultisemanticPacket(user, mode, timestamp, function, data)

    def is_valid(self):
        is_valid = True
        if self.user not in MultisemanticPacket.users_list:
            self.msg.append('[ERROR] invliad user identification')
            is_valid = False

        if self.mode not in MultisemanticPacket.mode:
            self.msg.append(f'[ERROR] invalid mode: {self.mode}, the valid values are: {MultisemanticPacket.mode}')
            is_valid = False

        if self.timestamp <= 0.0:
            self.msg.append(f'[WARN] invalid timestamp')

        valid_function = []
        for f in self.function:
            if f not in MultisemanticPacket.function and self.mode != "custom":
                self.msg.append(f'[WARNING] invalid function: {f}, the valid values are: {MultisemanticPacket.function}')
            else:
                valid_function.append(f)
        self.function = valid_function
        if len(self.function) == 0 and (self.mode == 'image' or self.mode == 'image_imu'):
            self.msg.append('[ERROR] no valid function')
            is_valid = False

        if not self.data:
            self.msg.append('[WARN] data field is empty')

        return is_valid

    def get_server_packet(self):
        r_packet = {
            'user': self.user,
            'mode': self.mode,
            'timestamp': self.timestamp,
            'function': self.function,
            'msg': self.msg,
            'results': self.results,
        }
        return json.dumps(r_packet)

def parse_model_info(m_packet, model_url=True):
    if 'model_info' not in m_packet.data:
        m_packet.msg.append('[ERROR] model_info field is missing')
        return False
    model_info = m_packet.data['model_info']
    if 'name' not in model_info:
        m_packet.msg.append('[ERROR] model_info->name field is missing')
        return False
    if model_url and 'url' not in model_info:
        m_packet.msg.append('[ERROR] model_info->url field is missing')
        return False
    return True