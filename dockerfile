FROM ubuntu:22.04
RUN apt-get update && apt install -y arping netperf iperf bison build-essential cmake flex git libedit-dev \
libllvm14 zip llvm-14-dev libclang-14-dev python3 zlib1g-dev libelf-dev libfl-dev python3-distutils python3-pip &&  apt-get clean
RUN pip3 install prometheus_client flask_basicauth flask redis && ln -s /usr/bin/python3 /usr/bin/python
RUN git clone https://github.com/iovisor/bcc.git && mkdir bcc/build; cd bcc/build && \
    cmake .. && make && make install && \
    cmake -DPYTHON_CMD=python3 ..
RUN  cd bcc/build/src/python/ && make && make install
ADD . /app/wo-bcc
WORKDIR /app/wo-bcc
CMD python main.py
