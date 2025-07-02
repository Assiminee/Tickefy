FROM nvidia/cuda:12.3.2-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

ENV LD_LIBRARY_PATH="/usr/local/nvidia/lib:/usr/local/nvidia/lib64:/usr/local/cuda-12.3/lib64:/usr/lib/x86_64-linux-gnu"

RUN apt-get update && apt-get install -y \
   python3.10 \
   python3.10-venv \
   python3.10-dev \
   python3-pip \
   libgl1 \
   libglib2.0-0 \
   vim \
   curl \
   && rm -rf /var/lib/apt/lists/*
   # The removal of /var/lib/apt/lists/* reduces the final image size \
   # by eliminating temporary package lists.

RUN ln -sf /usr/bin/python3.10 /usr/bin/python && \
   ln -sf /usr/bin/pip3 /usr/bin/pip

RUN pip install --upgrade pip

WORKDIR /workspace

COPY . /workspace

RUN cp /workspace/cudnn/include/* /usr/local/cuda-12.3/include && \
   cp /workspace/cudnn/lib/* /usr/local/cuda-12.3/lib64 && rm -rf /workspace/cudnn

RUN pip install tensorflow[and-cuda]==2.16.1 tf-keras==2.16.0
RUN pip install torch==2.2.2
RUN pip install facenet-pytorch==2.6.0 \
   opencv-python \
   mtcnn==1.0.0 \
   faiss-gpu==1.7.2 \
   fastapi \
   python-multipart

RUN pip install uvicorn==0.34.0

EXPOSE 8080

CMD ["uvicorn", "api.root:app", "--host", "0.0.0.0", "--port", "8080"]