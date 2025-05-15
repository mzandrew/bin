# written 2025-05-09 by mza
# last updated 2025-05-15 by mza

from ubuntu
workdir /root
run apt update
run apt install -y wget git vim build-essential rsync python3
run wget https://repo.anaconda.com/archive/Anaconda3-2024.10-1-Linux-x86_64.sh
run chmod +x Anaconda3-2024.10-1-Linux-x86_64.sh
run ./Anaconda3-2024.10-1-Linux-x86_64.sh -b
run wget https://raw.githubusercontent.com/fastmachinelearning/hls4ml-tutorial/refs/heads/main/environment.yml
run /root/anaconda3/bin/conda env create -f environment.yml
shell ["/root/anaconda3/bin/conda", "run", "-n", "hls4ml-tutorial", "/bin/bash", "-c"]
#run /root/anaconda3/bin/conda init
#run /root/anaconda3/bin/conda activate hls4ml-tutorial
run pip install tensorflow_model_optimization qkeras

# docker run -p 8888:8888 -v /opt/Xilinx:/opt/Xilinx -it mza:hls4ml
# . /opt/Xilinx/Vivado/2023.1/settings64.sh
# conda activate hls4ml-tutorial
# locale-gen en_US.UTF-8
# root@6065c8797ece:/lib/x86_64-linux-gnu# ln -s libtinfo.so.6 libtinfo.so.5
# jupyter-notebook --allow-root --ip=0.0.0.0
# docker container exec -it 30dcf53f90fa /bin/bash

# alternate method:
# docker run -i -t -p 8888:8888 continuumio/miniconda3 /bin/bash -c "/opt/conda/bin/conda install jupyter -y --quiet && mkdir /opt/notebooks && /opt/conda/bin/jupyter notebook --notebook-dir=/opt/notebooks --ip='*' --port=8888 --no-browser --allow-root"

