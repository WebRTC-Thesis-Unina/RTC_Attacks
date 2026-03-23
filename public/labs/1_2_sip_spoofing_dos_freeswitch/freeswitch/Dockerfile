FROM ubuntu:16.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential cmake automake autoconf libtool \
    libssl-dev libcurl4-openssl-dev libncurses5-dev \
    libjpeg-dev libsqlite3-dev libpcre3-dev \
    libspeex-dev libspeexdsp-dev libldns-dev \
    libedit-dev libavformat-dev libswscale-dev \
    liblua5.2-dev libopus-dev wget git \
    yasm nasm \
    libsndfile1-dev \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://files.freeswitch.org/releases/freeswitch/freeswitch-1.6.20.tar.gz \
    && tar -xzf freeswitch-1.6.20.tar.gz \
    && cd freeswitch-1.6.20 \
    && ./configure --prefix=/usr/local/freeswitch \
    && make -j$(nproc) \
    && make install \
    && make sounds-install moh-install \
    && cd .. && rm -rf freeswitch-1.6.20*

ENV PATH="/usr/local/freeswitch/bin:$PATH"

CMD ["freeswitch", "-nf", "-nonat", "-c"]