const express = require("express");
const http = require('http');
const mongoose = require('mongoose');
const { startInstance, stopInstance } = require('./ec2/ec2');
const os = require('os');
const SSH2Promise  = require("ssh2-promise");
const fs = require("fs");

const app = express();
app.use(express.static("public"))
app.use(express.json())

require('dotenv').config(); 
mongoose.connect(process.env.MONGODB_URI)

const scenarioSchema = new mongoose.Schema({
    id: Number,
    name: String,
    description: String,
    images: Array,
    steps: String
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

        res.json({name: scenario.name, description: scenario.description, steps: scenario.steps});
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

    try {
        global.ssh = new SSH2Promise({
            host: ip,
            username: hostname,
            privateKey: fs.readFileSync("./ttyd/"+key)
        });
        
        
        const ssh = global.ssh;
        await ssh.connect();
        
        await ssh.exec(`
            cd ~/RTC_Attacks && \
            make start SSH_IP=${ip} SSH_KEY=${key} SSH_HOSTNAME=${hostname} && \
            cd ~/RTC_Attacks/public/labs/${id} && \
            make start
        `);

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
    
    try {
        const ssh = global.ssh;
        await ssh.connect();

        await ssh.exec("cd ~/RTC_Attacks && make stop")
        res.json({ ok: true }); 
    } catch (error) {
        res.status(500).json({ ok: false, message: "Problem in SSH connection" });
    }
    
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

app.get("/search", async(req, res) => {
    const name = req.query.name;
    try {
        // Ricerca parziale
        const scenarios = await Scenario.find({ name:{ $regex: name, $options: "i" }});
        if (scenarios.length === 0) {
            return res.status(404).json({ error: "Scenario not found" });
        }
        res.json(scenarios)
    } catch (error){
        console.error("Error:", err);
    }
})