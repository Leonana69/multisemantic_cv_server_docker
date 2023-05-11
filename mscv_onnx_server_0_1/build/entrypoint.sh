#!/bin/bash

remove_tar_contents() {
    local tarfile="$1"

    # Check if the tarfile exists
    if [ ! -f "$tarfile" ]; then
        echo "Error: File not found: $tarfile"
        return 1
    fi

    # List the contents of the tar file
    local contents=$(tar -tf "$tarfile")

    # Reverse the order of the contents
    local reverse_contents=$(echo "$contents" | tac)

    # Remove each file or directory in reverse order
    while read -r item; do
        if [ "$item" == "./" ] || [ "$item" == "." ]; then
            continue
        fi

        if [ -e "$item" ]; then
            echo "Removing: $item"
            rm -rf "$item"
        fi
    done <<< "$reverse_contents"

    echo "All files and directories created by '$tarfile' have been removed."
}

# Check if the script received exactly two arguments
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 url model-type [flags: -t for type, -s for shape]"
    exit 1
fi

url="$1"
model_type="$2"
t_flag_used=false
s_flag_used=false

shift 2

while getopts ":t:s:" opt; do
    case $opt in
        t)
            type="$OPTARG"
            t_flag_used=true
            ;;
        s)
            shape="$OPTARG"
            s_flag_used=true
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            exit 1
            ;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            exit 1
            ;;
    esac
done

if ! $t_flag_used; then
    echo "type must be given"
    exit 1
fi

case "$model_type" in
    "tflite")
        wget -O model.tflite "$url" && \
        pip install -U tf2onnx && \
        python -m tf2onnx.convert --tflite model.tflite --opset 18 --output model.onnx && \
        rm model.tflite
        ;;

    "tf" | "keras")
        wget -O model.pb "$url" && \
        pip install -U tf2onnx && \
        python -m tf2onnx.convert --saved-model . --opset 18 --output model.onnx && \
        rm model.pb
        ;;

    "tf-compressed" | "keras-compressed")
        wget -O model.tar.gz "$url" && \
        tar -xvf ./model.tar.gz && \
        pip install -U tf2onnx && \
        python -m tf2onnx.convert --saved-model . --opset 18 --output model.onnx && \
        remove_tar_contents "model.tar.gz" && \
        rm ./model.tar.gz
        ;;
    "sklearn")
        if ! $t_flag_used; then
            echo "-t flag must be passed for sklearn model"
            exit 1
        fi
        wget -O model.pickle "$url" && \
        pip install -U skl2onnx && \
        python converters/sklearn_converter.py "$type" && \
        rm model.pickle
        ;;
    "pytorch")
        if ! $s_flag_used; then
            echo "-s flag must be passed for pytorch model"
        fi
        wget -O model.pt "$url" && \
        pip install -U torch && \
        python converters/pytorch_converter.py "$shape" && \
        rm model.pt
    ;;

    *)
        echo "Invalid value for model-type $model_type. URL is $url. Supported values: tflite|tf|tf-compressed|keras-compressed|sklearn|pytorch"
        exit 1
        ;;
esac

python src/app.py "$type"

