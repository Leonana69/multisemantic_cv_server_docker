FROM python:3.9-slim-bullseye

RUN apt update
RUN apt install -y build-essential
RUN apt install -y libpq-dev
RUN apt install -y wget
# https://github.com/onnx/onnx/issues/5202
# Once new version of skl2onnx available, should upgrade onnx
RUN pip install onnx==1.13.1
RUN pip install Flask numpy onnxruntime-gpu tensorflow


ENV ONNX_SERVICE_PORT=50009

WORKDIR /root
COPY ./src ./src
COPY ./build/entrypoint.sh /root/entrypoint.sh
COPY ./build/converters /root/converters
RUN chmod +x ./entrypoint.sh
EXPOSE $ONNX_SERVICE_PORT

CMD ["https://tfhub.dev/google/movenet/singlepose/thunder/4?tf-hub-format=compressed", "tf-compressed", "-t", "int32"]
ENTRYPOINT [ "./entrypoint.sh" ]
