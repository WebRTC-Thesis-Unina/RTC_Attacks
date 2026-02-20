# Fonte: https://dingavinga.medium.com/easiest-way-yet-to-install-snort-ids-on-ubuntu-linux-5f1e1de41fe6
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV WIRESHARK_COMMON_INSTALL_SETUID_PRIVILEGES=false

RUN apt-get update && apt-get install  -y wget build-essential libpcap-dev libpcre2-dev libnet1-dev zlib1g-dev luajit libdumbnet-dev bison flex liblzma-dev openssl libssl-dev pkg-config libhwloc-dev cmake cpputest libsqlite3-dev uuid-dev libcmocka-dev libnetfilter-queue-dev libmnl-dev autotools-dev libluajit-5.1-dev libunwind-dev libfl-dev git unzip ethtool tcpdump tshark docker-cli python3-pip && \ 
mkdir snort_install ; cd snort_install && \
git clone https://github.com/snort3/libdaq.git && \ 
cd libdaq ; \ 
./bootstrap ;\
./configure ; \ 
make && make install ; cd .. 

RUN pip3 install pandas

RUN wget https://github.com/gperftools/gperftools/releases/download/gperftools-2.9.1/gperftools-2.9.1.tar.gz && \ 
tar xzf gperftools-2.9.1.tar.gz && \ 
cd gperftools-2.9.1/ && \
./configure &&  \ 
make &&  make install && cd ..

RUN wget https://github.com/snort3/snort3/archive/refs/heads/master.zip && \
unzip master.zip && \ 
cd snort3-master && \
ls && \
./configure_cmake.sh --prefix=/usr/local --enable-tcmalloc && \ 
cd build && \
make &&  make install && ldconfig 

RUN mkdir -p /usr/local/etc/rules /usr/local/etc/so_rules/ /usr/local/etc/lists/ /var/log/snort /captures &&  \
touch /usr/local/etc/rules/local.rules /usr/local/etc/lists/default.blocklist 

COPY snort.lua /usr/local/etc/snort/snort.lua
COPY snort_defaults.lua /usr/local/etc/snort/snort_defaults.lua
COPY local.rules /usr/local/etc/rules/local.rules
COPY file_magic.rules /usr/local/etc/rules/file_magic.rules
COPY metrics.py metrics.py
COPY run.sh /usr/local/bin/run.sh

RUN chmod +x /usr/local/bin/run.sh

CMD ["/usr/local/bin/run.sh"]