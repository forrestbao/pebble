#!/bin/bash

# On AWS 
# UBUNTUYEAR=24
# PYTHON3DOT=12
# CUDA12DOT=6

# On Paper space 
UBUNTUYEAR=22
PYTHON3DOT=10
CUDA12DOT=6


wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu${UBUNTUYEAR}04/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update	
sudo apt-get -y install cuda-toolkit-12-$CUDA12DOT nvidia-open

echo "export CUDA_HOME=/usr/local/cuda" >> ~/.bashrc
echo "export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:\$CUDA_HOME/lib64" >> ~/.bashrc
echo "export PATH=\$PATH:\$CUDA_HOME/bin" >> ~/.bashrc

echo "export PATH=\$PATH:/home/paperspace/.local/bin" >> ~/.bashrc
echo "export PATH=\$PATH:/home/ubuntu/.local/bin" >> ~/.bashrc

sudo apt install -y python3-pip ipython3 nvtop cifs-utils libopenmpi-dev python3.$PYTHON3DOT-venv

if [ "$PYTHON3DOT" -eq 12 ]; then
    python3 -m venv baoml
    source baoml/bin/activate
fi

# Install torch 
source ~/.bashrc
pip3 install numpy packaging
pip3 install torch --index-url https://download.pytorch.org/whl/cu12$CUDA12DOT

python3 -c "import torch; print (torch.cuda.is_available())" # test Torch installation 

pip3 install psutil wheel
pip3 install flash_attn --no-build-isolation
