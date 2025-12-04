FROM node:iron-trixie-slim

WORKDIR /app
COPY package*.json ./
RUN npm i express https ws fs path
COPY . .

CMD ["node", "server.js"]