import tensorflow as tf
import numpy as np

class PoseTF():
    def __init__(self):
        self.interpreter = self.load_model()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.offset_h = 0.0
        self.offset_w = 0.0

    def load_model(self):
        interpreter = tf.lite.Interpreter(model_path="./assets/models/movenetv2.tflite")
        interpreter.allocate_tensors()
        return interpreter

    def get_offset(self, image_size, model_input_size):
        ratio_h = image_size[0] / model_input_size[0]
        ratio_w = image_size[1] / model_input_size[1]
        if ratio_h > ratio_w:
            self.offset_h = 0
            self.offset_w = (1 - image_size[1] / ratio_h / model_input_size[1]) / 2.0
        else:
            self.offset_w = 0
            self.offset_h = (1 - image_size[0] / ratio_w / model_input_size[0]) / 2.0

    def run(self, image):
        self.get_offset(image.shape[0:2], (256, 256))
        input = tf.expand_dims(image, axis=0)
        # Resize and pad the image to keep the aspect ratio and fit the expected size.
        input = tf.image.resize_with_pad(input, 256, 256)
        # TF Lite format expects tensor type of float32.
        input_image = tf.cast(input, dtype=tf.float32)
        # print(input_image.numpy().shape)

        self.interpreter.set_tensor(self.input_details[0]['index'], input_image.numpy())
        self.interpreter.invoke()
        # Output is a [1, 1, 17, 3] numpy array.
        keypoints = self.interpreter.get_tensor(self.output_details[0]['index'])[0][0]
        for p in keypoints:
            p[0] = (p[0] - self.offset_h) / (1 - 2 * self.offset_h)
            p[1] = (p[1] - self.offset_w) / (1 - 2 * self.offset_w)
        return keypoints