const express = require("express");
const https = require("https");
const ws = require("ws").Server;
const fs = require("fs");
const path = require("path");

const app = express();
app.use(express.static('public'));
app.use(express.json({ limit: '500mb' }));

function checkDirectory(dirPath) {
    if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
    }
}

const server = https.createServer({
    key: fs.readFileSync('key.pem'),
    cert: fs.readFileSync('cert.pem')
}, app);

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
    const imgDir   = path.join(__dirname, "data", "images");

    checkDirectory(audioDir);
    checkDirectory(imgDir);

    // Audio
    const audioBase64 = req.body.audio.replace(/^data:audio\/webm;base64,/, "");
    const audioBuffer = Buffer.from(audioBase64, "base64");
    const audioName = `audio_${Date.now()}.webm`;

    fs.writeFileSync(path.join(audioDir, audioName), audioBuffer);

    // Screenshoot
    const imgBase64 = req.body.image.replace(/^data:image\/png;base64,/, "");
    const imgBuffer = Buffer.from(imgBase64, "base64");
    const imgName = `screenshot_${Date.now()}.png`;

    fs.writeFileSync(path.join(imgDir, imgName), imgBuffer);

    res.json({ saved: true });
});

server.listen(443, () => console.log("Server in ascolto sulla porta 443"));