const fs = require('fs');
const express = require('express');
const https = require('https');
const { Server } = require('socket.io');

const app = express();
app.use(express.static('node/public'));

const server = https.createServer({
  key: fs.readFileSync('node/key.pem'),
  cert: fs.readFileSync('node/cert.pem')
},app);
const io = new Server(server, { cors: { origin: "*" } });

io.on('connection', socket => {
  console.log('Client connesso:', socket.id);

  socket.on('offer', data => socket.broadcast.emit('offer', data));
  socket.on('answer', data => socket.broadcast.emit('answer', data));
  socket.on('candidate', data => socket.broadcast.emit('candidate', data));
});

server.listen(8443, () => console.log("Signaling server in ascolto sulla porta 8443"));
