#!/bin/bash -e

# written 2023-05-21 by mza
# based on https://github.com/RadeonOpenCompute/ROCm/blob/develop/docs/deploy/linux/install.md
# and https://askubuntu.com/a/1124256
# last updated 2023-05-21 by mza

function linux_firmware {
	cd
	mkdir -p build
	cd build
	if [ -e linux-firmware ]; then
		cd linux-firmware
		git pull
		cd ..
	else
		git clone git://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git
	fi
	sudo cp -a linux-firmware/amdgpu/* /lib/firmware/amdgpu/
}

function amdgpu_dkms {
	sudo apt install -y curl
	curl -fsSL https://repo.radeon.com/rocm/rocm.gpg.key | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/rocm-keyring.gpg
	echo 'deb [arch=amd64 signed-by=/etc/apt/trusted.gpg.d/rocm-keyring.gpg] https://repo.radeon.com/amdgpu/5.4.3/ubuntu jammy main' | sudo tee /etc/apt/sources.list.d/amdgpu.list
	sudo apt update
	sudo apt install -y amdgpu-dkms
}

function rocm_hip_sdk {
	for ver in 5.4.3; do
		echo "deb [arch=amd64 signed-by=/etc/apt/trusted.gpg.d/rocm-keyring.gpg] https://repo.radeon.com/rocm/apt/$ver jammy main" | sudo tee /etc/apt/sources.list.d/rocm.list
	done
	echo -e 'Package: *\nPin: release o=repo.radeon.com\nPin-Priority: 600' | sudo tee /etc/apt/preferences.d/rocm-pin-600
	sudo apt update
	sudo apt install rocm-hip-sdk
	sudo tee --append /etc/ld.so.conf.d/rocm.conf <<EOF
/opt/rocm/lib
/opt/rocm/lib64
EOF
	sudo ldconfig
}

function show_status {
	#echo 'export PATH=$PATH:/opt/rocm/bin' >> ~/.bashrc
	export PATH=$PATH:/opt/rocm/bin
	/opt/rocm/bin/rocminfo
	dkms status
	/opt/rocm/bin/rocm-smi
}

#linux_firmware
amdgpu_dkms
#sudo reboot now
rocm_hip_sdk
show_status

