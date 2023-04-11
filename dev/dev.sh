docker run -it --privileged  -v /lib/modules:/lib/modules:ro  -v /usr/src:/usr/src:ro  -v /boot:/boot:ro  -v /sys/kernel/debug:/sys/kernel/debug  lecurry/bcc:prod bash
#ln -s /usr/bin/python3 /usr/bin/python
#/usr/share/bcc/tools/tcptop
#wget https://fr1.teddyvps.com/kernel/el7/kernel-ml-devel-5.12.2-1.el7.elrepo.x86_64.rpm && yum intall devel-$(uname -r).rpm  安装对应内核头文件
#wget https://fr1.teddyvps.com/kernel/el7/kernel-ml-devel-$(uname -r).rpm && yum -y install devel-$(uname -r).rpm
#curl -o kernel-ml-devel-$(uname -r).rpm https://fr1.teddyvps.com/kernel/el7/kernel-ml-devel-$(uname -r).rpm && yum -y install kernel-ml-devel-$(uname -r).rpm
