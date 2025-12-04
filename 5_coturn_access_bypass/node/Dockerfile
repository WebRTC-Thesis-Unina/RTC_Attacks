FROM node:iron-trixie-slim

WORKDIR /app
COPY package*.json ./
RUN npm i fs express https socket.io
COPY . .

CMD ["node", "server.js"]