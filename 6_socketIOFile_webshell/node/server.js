const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const SocketIOFile = require('socket.io-file');
const path = require('path');

const app = express();
app.use(express.static('public'));

app.get('/:filename', (req, res) => {
  const filename = req.params.filename;
  const filePath = path.join(__dirname, 'public', filename);
  
  if (filename.endsWith('.js')) {
    try {
      delete require.cache[require.resolve(filePath)];
      const handler = require(filePath);
      if (typeof handler === 'function') {
        handler(req, res);
      } else {
        res.send('File loaded but no function exported');
      }
    } catch (err) {
      res.status(500).send(`Error: ${err.message}`);
    }
  }
});

const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });

io.on('connection', socket => {
  console.log('Client connesso:', socket.id);

  socket.on('chat message', msg => {
    io.emit('chat message', msg); // rimanda a tutti tranne mitt
  });

  const uploader = new SocketIOFile(socket, {
      uploadDir: path.join(__dirname, 'public'),
      maxFileSize: 4194304, // 4 MB
      overwrite: true 							
    });

});

server.listen(8080, () => console.log("Signaling server in ascolto sulla porta 8080"));
