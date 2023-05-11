import numpy
import pickle
from onnxconverter_common import data_types
from skl2onnx import to_onnx
import os, re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("type", help="data type for model input")
args = parser.parse_args()

file_list = os.listdir('.')
regex = re.compile('\.pickle')
model_path = [file for file in file_list if regex.search(file)][0]
fileReadObj = open(model_path, "rb")
ereg = pickle.load(fileReadObj)
fileReadObj.close()

feature_in_count = ereg.n_features_in_

input_type_string = args.type

if input_type_string == "float32":
    input_type = data_types.FloatTensorType([None, feature_in_count])
elif input_type_string == "float64":
    input_type = data_types.DoubleTensorType([None, feature_in_count])
elif input_type_string == "string":
    input_type = data_types.StringTensorType([None, feature_in_count])
elif input_type_string == "int64":
    input_type = data_types.Int64TensorType([None, feature_in_count])
elif input_type_string == "int32":  # noqa
    input_type = data_types.Int32TensorType([None, feature_in_count])
elif input_type_string == "uint8":
    input_type = data_types.UInt8TensorType([None, feature_in_count])
elif input_type_string == "bool":
    input_type = data_types.BooleanTensorType([None, feature_in_count])
elif input_type_string == "int8":
    input_type = data_types.Int8TensorType([None, feature_in_count])
elif input_type_string == "int16":
    input_type = data_types.Int16TensorType([None, feature_in_count])
elif input_type_string == "uint64":
    input_type = data_types.UInt64TensorType([None, feature_in_count])
elif input_type_string == "uint32":
    input_type = data_types.UInt32TensorType([None, feature_in_count])
elif input_type_string == "uint16":
    input_type = data_types.UInt16TensorType([None, feature_in_count])
elif input_type_string == "float16":
    input_type = data_types.Float16TensorType([None, feature_in_count])
elif input_type_string == "complex64":
    input_type = data_types.Complex64TensorType([None, feature_in_count])
elif input_type_string == "complex128":
    input_type = data_types.Complex128TensorType([None, feature_in_count])
else: 
    raise NotImplementedError(
        "Unsupported data_type %r."
        "" % (input_type_string))


onnx = to_onnx(ereg, initial_types=[('X', input_type)],
              target_opset=18)

with open("model.onnx", "wb") as f:
    f.write(onnx.SerializeToString())
