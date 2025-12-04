FROM node:iron-trixie-slim

WORKDIR /app
COPY package*.json ./
RUN npm i fs express https mongoose@5.7.4
COPY . .

CMD ["node", "server.js"]