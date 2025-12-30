FROM debian:stable

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      tcpdump tshark iproute2 ca-certificates docker-cli && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

WORKDIR /opt/collector

COPY run.sh /opt/collector/run.sh
RUN chmod +x /opt/collector/run.sh