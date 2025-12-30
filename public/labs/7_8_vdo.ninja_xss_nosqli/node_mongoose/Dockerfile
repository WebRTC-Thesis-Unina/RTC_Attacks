FROM node:iron-trixie-slim

WORKDIR /app
COPY package*.json ./
COPY . .
RUN npm i fs express https mongoose@5.7.4 dotenv

CMD ["node", "server.js"]