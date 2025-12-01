FROM debian:stretch-slim

# Repository di archivio
RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list \
    && sed -i 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list \
    && sed -i '/stretch-updates/d' /etc/apt/sources.list

RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    flex \
    bison \
    libpcap-dev \
    libxml2-dev \
    libpcre3-dev \
    libevent-dev \
    libunistring-dev \
    gdb

RUN wget https://www.kamailio.org/pub/kamailio/5.1.1/src/kamailio-5.1.1_src.tar.gz \
    && tar -xvzf kamailio-5.1.1_src.tar.gz \
    && cd kamailio-5.1.1 \
    && make all \
    && make install \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

CMD ["kamailio", "-DD", "-E"]
