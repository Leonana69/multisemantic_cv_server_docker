import torch
import onnxruntime
import sys
import json

if len(sys.argv) < 2:
    print("Usage: python script.py <shape>")
    sys.exit(1)

shape = json.loads(sys.argv[1])
# 10, 3, 224, 224
dummy_input = torch.randn(shape)
model_torchscript = torch.jit.load("model.pt")
torch.onnx.export(model_torchscript, dummy_input, "model.onnx", opset_version=18)