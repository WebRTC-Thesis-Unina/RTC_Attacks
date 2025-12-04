FROM node:iron-trixie-slim

RUN apt-get update -y \
    && apt-get install -y wget python3 python3-cryptography \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY package*.json ./
RUN npm i express http socket.io socket.io-file@2.0.31 path
COPY . .

CMD ["node", "server.js"]