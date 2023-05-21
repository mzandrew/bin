#!/bin/bash -e

# written 2023-05-21 by mza
# based on https://github.com/RadeonOpenCompute/ROCm/blob/develop/docs/deploy/linux/install.md
# last updated 2023-05-21 by mza

curl -fsSL https://repo.radeon.com/rocm/rocm.gpg.key | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/rocm-keyring.gpg
echo 'deb [arch=amd64 signed-by=/etc/apt/trusted.gpg.d/rocm-keyring.gpg] https://repo.radeon.com/amdgpu/5.4.3/ubuntu jammy main' | sudo tee /etc/apt/sources.list.d/amdgpu.list
sudo apt update
sudo apt install amdgpu-dkms
# reboot

for ver in 5.0.2 5.1.4 5.2.5 5.3.3 5.4.3; do
	echo "deb [arch=amd64 signed-by=/etc/apt/trusted.gpg.d/rocm-keyring.gpg] https://repo.radeon.com/rocm/apt/$ver jammy main" | sudo tee -a /etc/apt/sources.list.d/rocm.list
done
echo -e 'Package: *\nPin: release o=repo.radeon.com\nPin-Priority: 600' | sudo tee /etc/apt/preferences.d/rocm-pin-600
sudo apt update
sudo apt install rocm-hip-sdk
sudo tee --append /etc/ld.so.conf.d/rocm.conf <<EOF
/opt/rocm/lib
/opt/rocm/lib64
EOF
sudo ldconfig
export PATH=$PATH:/opt/rocm-5.4.3/bin:/opt/rocm-5.4.3/opencl/bin
/opt/rocm/bin/rocminfo
/opt/rocm/opencl/bin/clinfo

