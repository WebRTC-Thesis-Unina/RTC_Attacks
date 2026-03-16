FROM debian:bookworm-slim

ENV GOPHISH_VERSION=0.12.1

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    tar \
    bzip2 \
    ca-certificates

RUN wget https://github.com/gophish/gophish/releases/download/v${GOPHISH_VERSION}/gophish-v${GOPHISH_VERSION}-linux-64bit.zip \
    && apt-get install -y unzip \
    && unzip gophish-v${GOPHISH_VERSION}-linux-64bit.zip -d /opt/gophish \
    && chmod +x /opt/gophish/gophish \
    && rm gophish-v${GOPHISH_VERSION}-linux-64bit.zip

WORKDIR /opt/gophish

COPY config.json /opt/gophish/config.json