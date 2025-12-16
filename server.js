const express = require("express");
const http = require('http');
const mongoose = require('mongoose');
const { exec } = require("child_process");
const { startInstance, stopInstance } = require('./ec2/ec2');
const os = require('os');
const SSH2Promise  = require("ssh2-promise");
const fs = require("fs");

const app = express();
app.use(express.static("public"))
app.use(express.json())

mongoose.connect("mongodb://192.168.1.100:27017/RTP_Attacks")

const scenarioSchema = new mongoose.Schema({
    id: Number,
    name: String,
    description: String,
});

const Scenario = mongoose.model("scenario", scenarioSchema);

const server = http.createServer(app)

server.listen(8888, () => console.log("Server listen on port 8888"));

app.get("/scenarios",async (req, res)=>{
    try {
        const scenarios = await Scenario.find().sort({id: 1});

        const names = scenarios.map(s => s.name);
        const ids = scenarios.map(s => s.id);

        res.json({names: names, ids: ids});    
    } catch (error) {
        console.error(error);
    }
})

app.get("/scenario/:id", async(req, res) => {
    const id = parseInt(req.params.id);
    try {
        const scenario = await Scenario.findOne({id: id})

        if (!scenario) {
            return res.status(404).json({ error: "Scenario not found" });
        }

        res.json({description: scenario.description});
    } catch (error) {
        console.error(error);
    }
})

function getVMIP() {
  const interfaces = os.networkInterfaces();
  for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
      if (iface.family === 'IPv4' && !iface.internal) {
        return iface.address;
      }
    }
  }
  return 'IP not found';
}

app.get("/make-start/:ip/:hostname/:key/:id", async(req, res) => {
    let ip = req.params.ip;
    let hostname = req.params.hostname;
    const key = req.params.key;
    const id = req.params.id;

    if(hostname === "none"){
        hostname = os.hostname();
    }
    if(ip === "none"){
        ip = getVMIP()
    }

    exec(`make start SSH_IP=${ip} SSH_KEY=${key} SSH_HOSTNAME=${hostname}`, (err) => {
        if(err){
            res.status(500).json({ ok: false, message: "SSH key not found" });
        }
    })

    try {
        global.ssh = new SSH2Promise({
            host: ip,
            username: hostname,
            privateKey: fs.readFileSync(key)
        });
    
        const ssh = global.ssh;
        await ssh.connect();
    
        await ssh.exec(`cd ~/RTC_Attacks/public/labs/${id} && make start`);
        res.json({ ok: true});
    } catch(err){
        console.error(err);
        res.status(500).json({ok: false, err: err.message});
    }
})

app.get("/make-stop/:id", async(req, res) => {
    const id = req.params.id;

    try {
        const ssh = global.ssh;
    
        await ssh.connect();
    
        await ssh.exec(`cd ~/RTC_Attacks/public/labs/${id} && make stop`);
        res.json({ ok: true});
    } catch(err){
        console.error(err);
        res.status(500).json({ok: false, err: err.message});
    }
})

app.get("/make-stop-ttyd", async(req, res) => {
    exec("make stop", (err) => {
        if (err) {
            console.error("Error:", err);
            return res.status(500).json({ ok: false, error: err.message });
        }
        res.json({ ok: true });
    }); 
})

app.get("/start-ec2", async(req, res) => {
    try {
        const info = await startInstance();
        res.json({ ok: true, ip: info.publicIp, region: info.region });
    } catch (error) {
        console.error("Error: ", error);
    }
})

app.get("/stop-ec2", async(req, res) => {
    try {
        const info = await stopInstance();
        res.json({ ok: true, ip: info.publicIp });
    } catch (error) {
        console.error("Error: ", error);
    }
})