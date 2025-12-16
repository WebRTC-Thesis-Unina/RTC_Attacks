FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y build-essential cmake git libjson-c-dev libwebsockets-dev && \
    git clone https://github.com/tsl0922/ttyd.git && \
    cd ttyd && mkdir build && cd build && \
    cmake .. && make && make install && \
    cd ../.. && rm -rf ttyd && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY key_pem.pem /
COPY key_rsa.pem /

RUN chmod 400 "key_pem.pem"
RUN chmod 400 "key_rsa.pem"