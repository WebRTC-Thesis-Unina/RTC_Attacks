FROM node:iron-trixie-slim

RUN apt-get update -y \
    && apt-get install -y wget python3 python3-cryptography \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . ./node