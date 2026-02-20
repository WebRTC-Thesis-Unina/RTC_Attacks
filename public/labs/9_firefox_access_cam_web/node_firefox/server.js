const express = require("express");
const http = require("http");
const ws = require("ws").Server;
const fs = require("fs");
const path = require("path");

const app = express();
app.use(express.static('public'));
app.use(express.json({ limit: '500mb' }));

const server = http.createServer(app);

const wss = new ws({
    server: server
});

wss.on("connection", ws => {
    ws.on("message", data => {
        const msg = data.toString();
        wss.clients.forEach(client => {
            client.send(msg);
        });
    })
})

app.post("/save-capture", (req, res) => {

    const audioDir = path.join(__dirname, "data", "audio");

    if (!fs.existsSync(audioDir)) {
        fs.mkdirSync(audioDir, { recursive: true });
    }

    const audioBase64 = req.body.audio.replace(/^data:audio\/webm;base64,/, "");
    const audioBuffer = Buffer.from(audioBase64, "base64");
    const audioName = `audio_${Date.now()}.webm`;

    fs.writeFileSync(path.join(audioDir, audioName), audioBuffer);

    res.json({ saved: true });
});

server.listen(80, () => console.log("Server in ascolto sulla porta 80"));