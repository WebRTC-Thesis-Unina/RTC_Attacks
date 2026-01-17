FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libxt6 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    libpulse0

RUN wget -O /tmp/firefox.tar.bz2 "https://ftp.mozilla.org/pub/firefox/releases/68.0esr/linux-x86_64/en-US/firefox-68.0esr.tar.bz2" && \
    tar -xjf /tmp/firefox.tar.bz2 -C /opt/ && \
    ln -s /opt/firefox/firefox /usr/bin/firefox

RUN mkdir -p /opt/firefox/distribution && \
    echo '{ "policies": { "DisableAppUpdate": true } }' > /opt/firefox/distribution/policies.json

WORKDIR /root