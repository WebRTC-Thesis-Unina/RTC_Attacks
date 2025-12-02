FROM ubuntu:16.04

# Build non interattiva e timezone
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Rome

RUN apt-get update && \
    apt-get install -y asterisk --no-install-recommends tzdata && \
    cp -r /usr/share/asterisk /etc/asterisk && \
    apt-get clean && rm -rf /var/lib/apt/lists/*